"""
Plagiarism Detection Engine
Uses sentence-transformers for semantic similarity comparison.
Splits documents into sentences, compares against reference corpus,
and generates similarity scores with source citations.
"""

import re
import time
import numpy as np
from typing import List, Dict, Tuple

# Lazy-loaded model
_model = None
_corpus_embeddings = None
_corpus_sentences = None
_corpus_map = None  # maps sentence index -> corpus source


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        print("[Plagiarism Engine] Loading sentence-transformers model...")
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[Plagiarism Engine] Model loaded successfully.")
        except Exception as e:
            print(f"[Plagiarism Engine] Model load failed: {e}")
            _model = "FAILED"
    return _model if _model != "FAILED" else None


def _build_corpus_index():
    """Build embeddings for the reference corpus (one-time operation)."""
    global _corpus_embeddings, _corpus_sentences, _corpus_map

    if _corpus_embeddings is not None:
        return

    from backend.seed_corpus import get_corpus
    corpus = get_corpus()

    model = _get_model()
    if model is None:
        return

    all_sentences = []
    sentence_to_source = {}

    for item in corpus:
        sentences = split_into_sentences(item['text'])
        for sent in sentences:
            idx = len(all_sentences)
            all_sentences.append(sent)
            sentence_to_source[idx] = {
                'id': item['id'],
                'title': item['title'],
                'author': item['author'],
                'source': item['source'],
                'url': item['url']
            }

    print(f"[Plagiarism Engine] Building index for {len(all_sentences)} corpus sentences...")
    _corpus_sentences = all_sentences
    _corpus_map = sentence_to_source
    _corpus_embeddings = model.encode(all_sentences, convert_to_numpy=True, show_progress_bar=False)
    print("[Plagiarism Engine] Corpus index built.")


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using regex."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs."""
    paragraphs = re.split(r'\n\s*\n|\n', text.strip())
    return [p.strip() for p in paragraphs if len(p.strip()) > 20]


def detect_plagiarism(text: str, threshold: float = 0.75) -> Dict:
    """
    Main plagiarism detection function.

    Args:
        text: The document text to analyze
        threshold: Similarity threshold (0-1) above which text is flagged

    Returns:
        Dict with plagiarism scores, matched sources, and heatmap data
    """
    start_time = time.time()

    model = _get_model()

    # If model failed to load, return simulated results
    if model is None:
        return _simulate_plagiarism_results(text, start_time)

    _build_corpus_index()

    # Split input into sentences
    paragraphs = split_into_paragraphs(text)
    if not paragraphs:
        paragraphs = [text]

    all_results = []
    matched_sources = {}
    paragraph_scores = []
    sentence_heatmap = []

    for p_idx, paragraph in enumerate(paragraphs):
        sentences = split_into_sentences(paragraph)
        if not sentences:
            paragraph_scores.append({
                'paragraph_index': p_idx,
                'text': paragraph[:100] + '...' if len(paragraph) > 100 else paragraph,
                'score': 0.0,
                'flagged': False,
                'sentences': []
            })
            continue

        # Encode input sentences
        input_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)

        sent_results = []
        para_score_sum = 0.0

        for s_idx, (sent, sent_emb) in enumerate(zip(sentences, input_embeddings)):
            # Compute cosine similarity with all corpus sentences
            from sentence_transformers import util
            cos_scores = util.cos_sim(sent_emb.reshape(1, -1), _corpus_embeddings)[0].numpy()

            # Find best match
            best_idx = int(np.argmax(cos_scores))
            best_score = float(cos_scores[best_idx])

            is_flagged = best_score >= threshold
            source_info = None

            if is_flagged and _corpus_map and best_idx in _corpus_map:
                src = _corpus_map[best_idx]
                source_info = {
                    'id': src['id'],
                    'title': src['title'],
                    'author': src['author'],
                    'source': src['source'],
                    'url': src['url'],
                    'matched_text': _corpus_sentences[best_idx],
                    'similarity': round(best_score * 100, 1)
                }

                # Track unique matched sources
                if src['id'] not in matched_sources:
                    matched_sources[src['id']] = {
                        **src,
                        'match_count': 0,
                        'avg_similarity': 0.0,
                        'similarities': []
                    }
                matched_sources[src['id']]['match_count'] += 1
                matched_sources[src['id']]['similarities'].append(best_score)

            sent_result = {
                'sentence_index': s_idx,
                'text': sent,
                'similarity_score': round(best_score * 100, 1),
                'flagged': is_flagged,
                'source': source_info,
                'heatmap_color': _score_to_color(best_score)
            }
            sent_results.append(sent_result)
            para_score_sum += best_score

            sentence_heatmap.append({
                'paragraph': p_idx,
                'sentence': s_idx,
                'text': sent,
                'score': round(best_score * 100, 1),
                'color': _score_to_color(best_score),
                'flagged': is_flagged
            })

        para_avg = (para_score_sum / len(sentences) * 100) if sentences else 0
        paragraph_scores.append({
            'paragraph_index': p_idx,
            'text': paragraph[:150] + '...' if len(paragraph) > 150 else paragraph,
            'score': round(para_avg, 1),
            'flagged': para_avg >= threshold * 100,
            'sentences': sent_results,
            'sentence_count': len(sentences),
            'flagged_count': sum(1 for s in sent_results if s['flagged'])
        })

    # Compute overall plagiarism score
    all_scores = [s['score'] for s in sentence_heatmap]
    overall_score = round(np.mean(all_scores), 1) if all_scores else 0.0
    flagged_percentage = round(
        sum(1 for s in sentence_heatmap if s['flagged']) / len(sentence_heatmap) * 100, 1
    ) if sentence_heatmap else 0.0

    # Finalize matched sources
    for src_id in matched_sources:
        sims = matched_sources[src_id]['similarities']
        matched_sources[src_id]['avg_similarity'] = round(np.mean(sims) * 100, 1)
        del matched_sources[src_id]['similarities']

    processing_time = round(time.time() - start_time, 2)

    return {
        'overall_score': overall_score,
        'flagged_percentage': flagged_percentage,
        'total_sentences': len(sentence_heatmap),
        'flagged_sentences': sum(1 for s in sentence_heatmap if s['flagged']),
        'paragraph_analysis': paragraph_scores,
        'matched_sources': list(matched_sources.values()),
        'heatmap': sentence_heatmap,
        'processing_time': processing_time,
        'threshold_used': threshold * 100
    }


def _simulate_plagiarism_results(text: str, start_time: float) -> Dict:
    """Fallback simulated results when model isn't available."""
    import random
    paragraphs = split_into_paragraphs(text)
    if not paragraphs:
        paragraphs = [text]

    sentence_heatmap = []
    paragraph_scores = []

    for p_idx, para in enumerate(paragraphs):
        sentences = split_into_sentences(para)
        sent_results = []
        for s_idx, sent in enumerate(sentences):
            score = random.uniform(5, 45)
            is_flagged = score > 75
            sent_result = {
                'sentence_index': s_idx,
                'text': sent,
                'similarity_score': round(score, 1),
                'flagged': is_flagged,
                'source': None,
                'heatmap_color': _score_to_color(score / 100)
            }
            sent_results.append(sent_result)
            sentence_heatmap.append({
                'paragraph': p_idx,
                'sentence': s_idx,
                'text': sent,
                'score': round(score, 1),
                'color': _score_to_color(score / 100),
                'flagged': is_flagged
            })

        para_avg = np.mean([s['similarity_score'] for s in sent_results]) if sent_results else 0
        paragraph_scores.append({
            'paragraph_index': p_idx,
            'text': para[:150] + '...',
            'score': round(para_avg, 1),
            'flagged': para_avg > 75,
            'sentences': sent_results,
            'sentence_count': len(sentences),
            'flagged_count': sum(1 for s in sent_results if s['flagged'])
        })

    all_scores = [s['score'] for s in sentence_heatmap]
    overall = round(np.mean(all_scores), 1) if all_scores else 0.0

    return {
        'overall_score': overall,
        'flagged_percentage': 0.0,
        'total_sentences': len(sentence_heatmap),
        'flagged_sentences': 0,
        'paragraph_analysis': paragraph_scores,
        'matched_sources': [],
        'heatmap': sentence_heatmap,
        'processing_time': round(time.time() - start_time, 2),
        'threshold_used': 75,
        'note': 'Simulated results - AI model not loaded'
    }


def _score_to_color(score: float) -> str:
    """Convert a similarity score (0-1) to a hex color for heatmap."""
    if score >= 0.85:
        return '#EF4444'   # Red - high plagiarism
    elif score >= 0.75:
        return '#F59E0B'   # Orange - moderate plagiarism
    elif score >= 0.60:
        return '#FBBF24'   # Yellow - low concern
    elif score >= 0.40:
        return '#A3E635'   # Light green - likely original
    else:
        return '#10B981'   # Green - original
