import json
import os


PROVIDERS_MODELS = {
    "openai": [
                "gpt-4o-mini",
                "gpt-4o-mini-search-preview", 
                "gpt-4o",
                "gpt-4o-search-preview",
                "gpt-4.1-nano",
                "gpt-4.1-mini",
                "gpt-4.1",
    ],
    "google": [
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.5-flash-lite-preview-06-17", 
                "gemini-2.5-flash-preview-04-17", 
                "gemini-2.5-flash","gemini-2.5-pro"
    ],
    "xai": [
        "grok-3-mini-fast",
            "grok-3-mini",
            "grok-3",
    ],
    "deepseek": [
                "deepseek-chat",
                "deepseek-reasoner"
    ],
}

EMBEDDING_MODELS = {
    "openai": [
        "text-embedding-3-small",
        "text-embedding-3-large",
    ]
}

PURPOSE_TAGS = [
    "chat",
    "coder",
    "labeller",
    "classifier"   
]


# Read-only model descriptions for LLM-profile builder
# -----------------------------------------------------------------------------
MODEL_DESCRIPTIONS = {
    # OpenAI
    "gpt-4o":"Multimodal powerhouse; $5.00/1M input, $15.00/1M output. Best for high-fidelity chat, complex reasoning & image tasks.",
    "gpt-4o-mini":"Cost-efficient multimodal; $0.15/1M input, $0.60/1M output. Ideal for prototyping vision+text apps on a budget.",
    "gpt-4.1":"Top general-purpose (1M-token context); $2.00/1M in, $8.00/1M out. Excels at large-doc comprehension, coding, reasoning.",
    "gpt-4.1-mini":"Balanced speed/intel (1M-token context); $0.40/1M in, $1.60/1M out. Great for apps needing wide context at moderate cost.",
    "gpt-4.1-nano":"Ultra-fast low-cost (1M-token); $0.10/1M in, $0.40/1M out. Perfect for high-throughput, low-latency tasks.",
    "gpt-o3":"High-accuracy reasoning (200K-token); $2.00/1M in, $8.00/1M out. Best for math, code gen, structured data outputs.",
    "gpt-o4-mini":"Fast lean reasoning (200K-token); $1.10/1M in, $4.40/1M out. Ideal for vision+code when o3 is overkill.",
    "gpt-o4-mini-high":"Enhanced mini-engine; $2.50/1M in (est.), $10.00/1M out (est.). Suited for interactive assistants with visual reasoning.",

    # Google
    "gemini-2.0-flash-lite":"Google Gemini 2.0 Flash Lite; $0.50/1M (est.). Best for quick Q&A & lightweight summarization.",
    "gemini-2.0-flash":"Google Gemini 2.0 Flash; $1.00/1M (est.). General-purpose chat & assistant with sub-second responses.",
    "gemini-2.5-flash-lite-preview-06-17":"Google Gemini 2.5 Flash Lite; $0.75/1M (est.). Good for high-accuracy summarization & code refactoring.",
    "gemini-2.5-flash-preview-06-17":"Google Gemini 2.5 Flash; $1.50/1M (est.). Strong at retrieval, Q&A & light reasoning.",
    "gemini-2.5-pro-preview-06-17":"Google Gemini 2.5 Pro; $3.00/1M (est.). Advanced analytics, detailed reports & multi-step reasoning.",

    # XAI
    "grok-3-mini-fast": "XAI Grok 3 Mini Fast; $0.20/1M (est.). Ultra-low latency chat, real-time monitoring & streaming apps.",
    "grok-3-mini":      "XAI Grok 3 Mini; $0.40/1M (est.). Budget-friendly chat & assistant tasks with good accuracy.",
    "grok-3":           "XAI Grok 3; $1.00/1M (est.). General-purpose chat & content gen with balanced speed/quality.",
    "grok-4":           "XAI Grok 4; $2.00/1M (est.). High-accuracy reasoning, code gen & long-form content creation.",

    # DeepSeek
    "deepseek-chat":    "DeepSeek Chat; $1.20/1M (est.). Optimized for private-data Q&A, enterprise search & document ingestion.",
}

