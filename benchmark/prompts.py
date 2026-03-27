# benchmark/prompts.py
#
# 15 prompts across 3 task categories.
# Same prompts are sent to ALL 3 models — this makes the comparison fair.
# Each prompt has an 'id', 'category', and 'text'.

PROMPTS = [

    # ── CATEGORY 1: Reasoning ──────────────────────────────────────────────
    # Tests multi-step thinking, logic, and cause-and-effect
    {
        "id": "r1",
        "category": "reasoning",
        "text": "If a train travels 60 km in 45 minutes, what is its speed in km/h? Show your working step by step.",
    },
    {
        "id": "r2",
        "category": "reasoning",
        "text": "A farmer has 17 sheep. All but 9 die. How many sheep does the farmer have left? Explain your reasoning.",
    },
    {
        "id": "r3",
        "category": "reasoning",
        "text": "You have a 3-litre jug and a 5-litre jug. How do you measure exactly 4 litres of water? List each step.",
    },
    {
        "id": "r4",
        "category": "reasoning",
        "text": "What comes next in this sequence: 2, 6, 12, 20, 30, ___? Explain the pattern.",
    },
    {
        "id": "r5",
        "category": "reasoning",
        "text": "If it takes 5 machines 5 minutes to make 5 widgets, how long does it take 100 machines to make 100 widgets?",
    },

    # ── CATEGORY 2: Summarisation ─────────────────────────────────────────
    # Tests ability to compress information clearly and accurately
    {
        "id": "s1",
        "category": "summarisation",
        "text": (
            "Summarise the following in exactly 3 sentences:\n\n"
            "Machine learning is a subset of artificial intelligence that enables systems to learn and improve "
            "from experience without being explicitly programmed. It focuses on developing computer programs "
            "that can access data and use it to learn for themselves. The process begins with observations or "
            "data, such as examples, direct experience, or instruction, so that computers can look for patterns "
            "in data and make better decisions in the future. The primary aim is to allow computers to learn "
            "automatically without human intervention and adjust actions accordingly."
        ),
    },
    {
        "id": "s2",
        "category": "summarisation",
        "text": (
            "Summarise the following in exactly 3 sentences:\n\n"
            "The Internet of Things (IoT) describes physical objects with sensors, processing ability, software "
            "and other technologies that connect and exchange data with other devices and systems over the Internet "
            "or other communications networks. IoT involves extending internet connectivity beyond standard devices "
            "such as desktops, laptops, smartphones and tablets to any range of traditionally dumb or non-internet "
            "enabled physical devices and everyday objects. Embedded with technology, these devices can communicate "
            "and interact over the internet, and they can be remotely monitored and controlled."
        ),
    },
    {
        "id": "s3",
        "category": "summarisation",
        "text": (
            "Summarise the following in exactly 3 sentences:\n\n"
            "Quantum computing is a type of computation that harnesses collective properties of quantum states, "
            "such as superposition, interference, and entanglement, to perform calculations. The devices that "
            "perform quantum computations are known as quantum computers. Quantum computers are believed to be "
            "able to solve certain computational problems substantially faster than classical computers. "
            "The study of quantum computing is a subfield of quantum information science."
        ),
    },
    {
        "id": "s4",
        "category": "summarisation",
        "text": (
            "Summarise the following in exactly 3 sentences:\n\n"
            "Docker is a set of platform as a service products that use OS-level virtualisation to deliver "
            "software in packages called containers. Containers are isolated from one another and bundle their "
            "own software, libraries and configuration files; they can communicate with each other through "
            "well-defined channels. All containers are run by a single operating-system kernel and are thus "
            "more lightweight than virtual machines."
        ),
    },
    {
        "id": "s5",
        "category": "summarisation",
        "text": (
            "Summarise the following in exactly 3 sentences:\n\n"
            "Retrieval-Augmented Generation (RAG) is a technique that grants generative artificial intelligence "
            "models information retrieval capabilities. It modifies interactions with a large language model so "
            "that the model responds to user queries with reference to a specified set of documents, using this "
            "information in preference to information drawn from its own vast training data. RAG allows LLMs to "
            "provide more accurate, up-to-date answers and cite sources, reducing hallucinations."
        ),
    },

    # ── CATEGORY 3: Code generation ───────────────────────────────────────
    # Tests ability to write correct, working Python code
    {
        "id": "c1",
        "category": "code",
        "text": "Write a Python function called `is_palindrome(s)` that returns True if a string is a palindrome, False otherwise. Include 3 example calls.",
    },
    {
        "id": "c2",
        "category": "code",
        "text": "Write a Python function called `flatten(lst)` that takes a nested list like [[1,2],[3,[4,5]]] and returns a flat list [1,2,3,4,5]. Use recursion.",
    },
    {
        "id": "c3",
        "category": "code",
        "text": "Write a Python class called `Stack` with push(), pop(), peek(), and is_empty() methods. Add a short docstring to each method.",
    },
    {
        "id": "c4",
        "category": "code",
        "text": "Find the bug in this Python code and fix it:\n\ndef calculate_average(numbers):\n    total = 0\n    for n in numbers:\n        total =+ n\n    return total / len(numbers)\n\nprint(calculate_average([10, 20, 30]))",
    },
    {
        "id": "c5",
        "category": "code",
        "text": "Write a Python function called `word_frequency(text)` that takes a string and returns a dictionary of each word and how many times it appears. Make it case-insensitive.",
    },
]
