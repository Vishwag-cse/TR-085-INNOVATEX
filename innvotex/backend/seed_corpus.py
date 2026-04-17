"""
Reference corpus for plagiarism comparison.
Contains academic passages across multiple disciplines.
"""

REFERENCE_CORPUS = [
    {
        "id": "src_001",
        "title": "Introduction to Data Structures",
        "author": "Cormen, T.H. et al.",
        "source": "Introduction to Algorithms, 4th Edition",
        "url": "https://mitpress.mit.edu/algorithms",
        "text": "A data structure is a particular way of organizing and storing data in a computer so that it can be accessed and modified efficiently. More precisely, a data structure is a collection of data values, the relationships among them, and the functions or operations that can be applied to the data. Different types of data structures are suited to different kinds of applications, and some are highly specialized to specific tasks."
    },
    {
        "id": "src_002",
        "title": "Machine Learning Fundamentals",
        "author": "Mitchell, T.",
        "source": "Machine Learning, McGraw-Hill",
        "url": "https://www.cs.cmu.edu/~tom/mlbook.html",
        "text": "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves. The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future based on the examples that we provide."
    },
    {
        "id": "src_003",
        "title": "Neural Networks and Deep Learning",
        "author": "Goodfellow, I. et al.",
        "source": "Deep Learning, MIT Press",
        "url": "https://www.deeplearningbook.org/",
        "text": "Deep learning is a class of machine learning algorithms that uses multiple layers to progressively extract higher-level features from the raw input. For example, in image processing, lower layers may identify edges, while higher layers may identify the concepts relevant to a human such as digits or letters or faces. Deep learning allows computational models that are composed of multiple processing layers to learn representations of data with multiple levels of abstraction."
    },
    {
        "id": "src_004",
        "title": "Database Management Systems",
        "author": "Ramakrishnan, R. & Gehrke, J.",
        "source": "Database Management Systems, 3rd Edition",
        "url": "https://pages.cs.wisc.edu/~dbbook/",
        "text": "A database management system is a software system designed to allow the definition, creation, querying, update, and administration of databases. A database is an organized collection of data stored and accessed electronically. Database management systems are categorized according to their data structures or types. The relational model, first proposed in 1970 by Edgar F. Codd, stores data in tables with rows and columns, and has become the most widely used model for database management."
    },
    {
        "id": "src_005",
        "title": "Operating Systems Concepts",
        "author": "Silberschatz, A. et al.",
        "source": "Operating System Concepts, 10th Edition",
        "url": "https://www.os-book.com/",
        "text": "An operating system is system software that manages computer hardware, software resources, and provides common services for computer programs. The operating system acts as an intermediary between the user of a computer and the computer hardware. Operating systems are found on many devices that contain a computer, from cellular phones and video game consoles to web servers and supercomputers. Process management, memory management, file system management, and device management are the primary functions of an operating system."
    },
    {
        "id": "src_006",
        "title": "Computer Networks",
        "author": "Kurose, J. & Ross, K.",
        "source": "Computer Networking: A Top-Down Approach",
        "url": "https://gaia.cs.umass.edu/kurose_ross/index.php",
        "text": "Computer networking refers to interconnected computing devices that can exchange data and share resources with each other. These networked devices use a system of rules, called communications protocols, to transmit information over physical or wireless technologies. The Internet is a global system of interconnected computer networks that uses the TCP/IP protocol suite to communicate between networks and devices. The TCP/IP model consists of four layers: the application layer, transport layer, internet layer, and network access layer."
    },
    {
        "id": "src_007",
        "title": "Software Engineering Principles",
        "author": "Sommerville, I.",
        "source": "Software Engineering, 10th Edition",
        "url": "https://software-engineering-book.com/",
        "text": "Software engineering is the systematic application of engineering approaches to the development of software. Software engineering is a discipline that is concerned with all aspects of software production from the early stages of system specification through to maintaining the system after it has gone into use. The software development life cycle is a process for planning, creating, testing, and deploying an information system. Common SDLC methodologies include waterfall, agile, spiral, and DevOps approaches."
    },
    {
        "id": "src_008",
        "title": "Artificial Intelligence: A Modern Approach",
        "author": "Russell, S. & Norvig, P.",
        "source": "Artificial Intelligence: A Modern Approach, 4th Edition",
        "url": "https://aima.cs.berkeley.edu/",
        "text": "Artificial intelligence is the study of agents that receive percepts from the environment and perform actions. Each such agent implements a function that maps percept sequences to actions. We study several types of these functions, including simple reflex agents, model-based agents, goal-based agents, and utility-based agents. AI encompasses a variety of subfields, including machine learning, natural language processing, computer vision, robotics, and expert systems."
    },
    {
        "id": "src_009",
        "title": "Cybersecurity Fundamentals",
        "author": "Stallings, W.",
        "source": "Network Security Essentials",
        "url": "https://williamstallings.com/",
        "text": "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people, and attackers are becoming more innovative. A comprehensive cybersecurity strategy requires multiple layers of protection spread across computers, networks, programs, and data."
    },
    {
        "id": "src_010",
        "title": "Cloud Computing Architecture",
        "author": "Erl, T. et al.",
        "source": "Cloud Computing: Concepts, Technology & Architecture",
        "url": "https://www.cloudschool.com/",
        "text": "Cloud computing is the on-demand delivery of computing services including servers, storage, databases, networking, software, analytics, and intelligence over the Internet to offer faster innovation, flexible resources, and economies of scale. Cloud service models include Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). Cloud deployment models include public cloud, private cloud, hybrid cloud, and community cloud."
    },
    {
        "id": "src_011",
        "title": "Natural Language Processing",
        "author": "Jurafsky, D. & Martin, J.",
        "source": "Speech and Language Processing, 3rd Edition",
        "url": "https://web.stanford.edu/~jurafsky/slp3/",
        "text": "Natural language processing is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language. The goal is to enable computers to understand, interpret, and generate human languages in a way that is both meaningful and useful. NLP combines computational linguistics with statistical, machine learning, and deep learning models. Key NLP tasks include text classification, named entity recognition, sentiment analysis, machine translation, and question answering."
    },
    {
        "id": "src_012",
        "title": "Blockchain Technology",
        "author": "Narayanan, A. et al.",
        "source": "Bitcoin and Cryptocurrency Technologies",
        "url": "https://www.lopp.net/bitcoin-information.html",
        "text": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records called blocks, which are linked and secured using cryptographic hash functions. Each block contains a cryptographic hash of the previous block, a timestamp, and transaction data. By design, a blockchain is resistant to modification of its data because once recorded, the data in any given block cannot be altered retroactively without alteration of all subsequent blocks. Blockchain technology forms the basis of cryptocurrencies like Bitcoin and Ethereum."
    },
    {
        "id": "src_013",
        "title": "Plagiarism in Academic Settings",
        "author": "Park, C.",
        "source": "Journal of Higher Education, Vol 74",
        "url": "https://doi.org/10.1080/13562510309399",
        "text": "Plagiarism is defined as the act of taking another person's writing, conversation, song, or even idea and passing it off as your own. This includes information from web pages, books, songs, television shows, email messages, interviews, articles, artworks, or any other medium. Whenever you paraphrase, summarize, or take words, phrases, or sentences from another person's work, it is necessary to indicate the source of the information within your paper using an internal citation."
    },
    {
        "id": "src_014",
        "title": "Research Methodology",
        "author": "Creswell, J.W.",
        "source": "Research Design: Qualitative, Quantitative and Mixed Methods",
        "url": "https://us.sagepub.com/en-us/nam/author/john-w-creswell",
        "text": "Research methodology refers to the systematic method consisting of enunciating the problem, formulating a hypothesis, collecting the facts or data, analyzing the facts and reaching certain conclusions either in the form of solution towards the concerned problem or in certain generalizations for some theoretical formulation. Quantitative research involves the collection and analysis of numerical data, while qualitative research focuses on understanding concepts, thoughts, or experiences through non-numerical data."
    },
    {
        "id": "src_015",
        "title": "Ethics in Computing",
        "author": "Quinn, M.J.",
        "source": "Ethics for the Information Age, 8th Edition",
        "url": "https://www.pearson.com/en-us/subject-catalog/p/ethics-for-the-information-age/",
        "text": "Computer ethics is a branch of applied ethics that considers ethical questions that arise from the use of computers and computing technology. Ethical issues related to computing include privacy and surveillance, intellectual property rights, the digital divide, software piracy, artificial intelligence ethics, and the social impact of automation on employment. As technology continues to evolve rapidly, new ethical challenges emerge that require careful consideration of the balance between innovation and individual rights."
    }
]


def get_corpus():
    """Return the reference corpus."""
    return REFERENCE_CORPUS


def get_corpus_texts():
    """Return just the text content from the corpus."""
    return [item['text'] for item in REFERENCE_CORPUS]


def get_corpus_metadata():
    """Return metadata for source citations."""
    return {
        item['id']: {
            'title': item['title'],
            'author': item['author'],
            'source': item['source'],
            'url': item['url']
        }
        for item in REFERENCE_CORPUS
    }
