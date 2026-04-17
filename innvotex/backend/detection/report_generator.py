"""
Report Generator
Combines plagiarism + AI detection results into a faculty-facing
summary report with confidence levels and risk classification.
"""

import time
from datetime import datetime
from typing import Dict


def generate_report(plagiarism_results: Dict, ai_results: Dict, document_info: Dict) -> Dict:
    """
    Generate a comprehensive faculty-facing summary report.

    Args:
        plagiarism_results: Output from plagiarism_engine.detect_plagiarism()
        ai_results: Output from ai_detector.detect_ai_content()
        document_info: Document metadata (filename, word_count, etc.)

    Returns:
        Complete analysis report with risk classification and recommendations
    """
    # Calculate overall risk
    plag_score = plagiarism_results.get('overall_score', 0)
    ai_score = ai_results.get('overall_ai_score', 0)
    combined_risk = (plag_score * 0.5 + ai_score * 0.5)

    risk_level = classify_risk(plag_score, ai_score)

    # Build confidence assessment
    confidence = assess_confidence(plagiarism_results, ai_results)

    # Generate recommendations
    recommendations = generate_recommendations(plag_score, ai_score, risk_level)

    # Total processing time
    total_time = (
        plagiarism_results.get('processing_time', 0) +
        ai_results.get('processing_time', 0)
    )

    report = {
        'report_id': f"RPT-{int(time.time())}",
        'generated_at': datetime.now().isoformat(),
        'document': {
            'filename': document_info.get('filename', 'Unknown'),
            'word_count': document_info.get('word_count', 0),
            'paragraph_count': ai_results.get('total_paragraphs', 0),
            'sentence_count': plagiarism_results.get('total_sentences', 0)
        },
        'summary': {
            'overall_risk_level': risk_level,
            'combined_risk_score': round(combined_risk, 1),
            'plagiarism_score': round(plag_score, 1),
            'ai_content_score': round(ai_score, 1),
            'flagged_sentences': plagiarism_results.get('flagged_sentences', 0),
            'total_sentences': plagiarism_results.get('total_sentences', 0),
            'high_risk_paragraphs': ai_results.get('high_risk_paragraphs', 0),
            'total_paragraphs': ai_results.get('total_paragraphs', 0)
        },
        'confidence': confidence,
        'plagiarism_detail': {
            'score': round(plag_score, 1),
            'flagged_percentage': plagiarism_results.get('flagged_percentage', 0),
            'matched_sources': plagiarism_results.get('matched_sources', []),
            'paragraph_breakdown': _simplify_paragraphs(
                plagiarism_results.get('paragraph_analysis', [])
            ),
            'threshold_used': plagiarism_results.get('threshold_used', 75)
        },
        'ai_detection_detail': {
            'score': round(ai_score, 1),
            'verdict': ai_results.get('overall_verdict', ''),
            'confidence_level': ai_results.get('overall_confidence', 'unknown'),
            'model_used': ai_results.get('model_used', 'unknown'),
            'paragraph_breakdown': _simplify_ai_paragraphs(
                ai_results.get('paragraph_analysis', [])
            ),
            'burstiness': ai_results.get('document_burstiness', {}),
            'perplexity': ai_results.get('document_perplexity', {})
        },
        'heatmap_data': plagiarism_results.get('heatmap', []),
        'ai_heatmap_data': [
            {
                'paragraph': p.get('paragraph_index', 0),
                'text': p.get('text', ''),
                'score': p.get('ai_probability', 0),
                'color': p.get('heatmap_color', '#10B981'),
                'verdict': p.get('verdict', '')
            }
            for p in ai_results.get('paragraph_analysis', [])
        ],
        'recommendations': recommendations,
        'metrics': {
            'total_processing_time': round(total_time, 2),
            'plagiarism_processing_time': plagiarism_results.get('processing_time', 0),
            'ai_detection_processing_time': ai_results.get('processing_time', 0),
            'meets_target': total_time < 20.0
        }
    }

    return report


def classify_risk(plag_score: float, ai_score: float) -> str:
    """Classify overall risk level."""
    max_score = max(plag_score, ai_score)
    avg_score = (plag_score + ai_score) / 2

    if max_score >= 80 or avg_score >= 70:
        return 'critical'
    elif max_score >= 60 or avg_score >= 50:
        return 'high'
    elif max_score >= 40 or avg_score >= 30:
        return 'medium'
    else:
        return 'low'


def assess_confidence(plagiarism_results: Dict, ai_results: Dict) -> Dict:
    """Assess confidence in the detection results."""
    factors = []

    # More sentences analyzed = higher confidence
    total_sentences = plagiarism_results.get('total_sentences', 0)
    if total_sentences >= 20:
        factors.append({'factor': 'Sample size', 'level': 'high', 'detail': f'{total_sentences} sentences analyzed'})
    elif total_sentences >= 10:
        factors.append({'factor': 'Sample size', 'level': 'medium', 'detail': f'{total_sentences} sentences analyzed'})
    else:
        factors.append({'factor': 'Sample size', 'level': 'low', 'detail': f'Only {total_sentences} sentences - limited analysis'})

    # AI model availability
    model_used = ai_results.get('model_used', 'unknown')
    if 'roberta' in model_used:
        factors.append({'factor': 'AI Model', 'level': 'high', 'detail': 'RoBERTa classifier active'})
    else:
        factors.append({'factor': 'AI Model', 'level': 'low', 'detail': 'Using heuristic fallback'})

    # Consistency between signals
    plag = plagiarism_results.get('overall_score', 0)
    ai = ai_results.get('overall_ai_score', 0)
    diff = abs(plag - ai)
    if diff < 15:
        factors.append({'factor': 'Signal consistency', 'level': 'high', 'detail': 'Plagiarism and AI scores are consistent'})
    elif diff < 30:
        factors.append({'factor': 'Signal consistency', 'level': 'medium', 'detail': 'Some divergence between signals'})
    else:
        factors.append({'factor': 'Signal consistency', 'level': 'low', 'detail': 'Significant divergence - manual review recommended'})

    # Overall confidence
    levels = [f['level'] for f in factors]
    if levels.count('high') >= 2:
        overall = 'high'
    elif levels.count('low') >= 2:
        overall = 'low'
    else:
        overall = 'medium'

    return {
        'overall_confidence': overall,
        'factors': factors
    }


def generate_recommendations(plag_score: float, ai_score: float, risk_level: str) -> list:
    """Generate actionable recommendations for faculty."""
    recs = []

    if risk_level == 'critical':
        recs.append({
            'priority': 'critical',
            'icon': 'fa-exclamation-triangle',
            'title': 'Immediate Review Required',
            'detail': 'Document shows strong indicators of plagiarism and/or AI-generated content. Schedule a meeting with the student for discussion.'
        })

    if plag_score >= 60:
        recs.append({
            'priority': 'high',
            'icon': 'fa-copy',
            'title': 'High Plagiarism Detected',
            'detail': f'Plagiarism similarity score of {plag_score:.0f}% detected. Review matched source citations and compare with original sources.'
        })
    elif plag_score >= 30:
        recs.append({
            'priority': 'medium',
            'icon': 'fa-search',
            'title': 'Moderate Similarity Found',
            'detail': f'Some text sections show {plag_score:.0f}% similarity. Verify proper citation and paraphrasing.'
        })

    if ai_score >= 70:
        recs.append({
            'priority': 'high',
            'icon': 'fa-robot',
            'title': 'AI Content Highly Probable',
            'detail': f'AI detection score of {ai_score:.0f}% suggests significant AI-generated content. Review paragraph-level breakdown for specifics.'
        })
    elif ai_score >= 40:
        recs.append({
            'priority': 'medium',
            'icon': 'fa-question-circle',
            'title': 'Possible AI Assistance',
            'detail': f'AI detection score of {ai_score:.0f}% indicates possible AI assistance. May warrant further investigation.'
        })

    if risk_level == 'low':
        recs.append({
            'priority': 'low',
            'icon': 'fa-check-circle',
            'title': 'No Significant Issues',
            'detail': 'Document appears to be original, human-written work. No immediate action required.'
        })

    recs.append({
        'priority': 'info',
        'icon': 'fa-info-circle',
        'title': 'Review Disclaimer',
        'detail': 'AI detection scores are probabilistic estimates. Use these results as a guide for further review, not as definitive proof. Always consider context and the student\'s writing history.'
    })

    return recs


def _simplify_paragraphs(paragraphs: list) -> list:
    """Simplify paragraph data for the report."""
    return [
        {
            'index': p.get('paragraph_index', 0),
            'score': p.get('score', 0),
            'flagged': p.get('flagged', False),
            'sentence_count': p.get('sentence_count', 0),
            'flagged_count': p.get('flagged_count', 0),
            'text_preview': p.get('text', '')[:100] + '...'
        }
        for p in paragraphs
    ]


def _simplify_ai_paragraphs(paragraphs: list) -> list:
    """Simplify AI paragraph data for the report."""
    return [
        {
            'index': p.get('paragraph_index', 0),
            'ai_probability': p.get('ai_probability', 0),
            'confidence_level': p.get('confidence_level', 'unknown'),
            'verdict': p.get('verdict', ''),
            'word_count': p.get('word_count', 0),
            'color': p.get('heatmap_color', '#10B981'),
            'text_preview': p.get('text', '')[:100] + '...'
        }
        for p in paragraphs
    ]
