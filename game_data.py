# game_data.py
import random

# --- AI JOURNALIST PERSONALITIES ---
JOURNALISTS = [
    {"name": "Tracy Chen", "personality": "Analytical"},
    {"name": "Mike Reynolds", "personality": "Skeptical"},
    {"name": "Elena Rodriguez", "personality": "Empathetic"},
]

# --- FALLBACK INTERVIEW PROMPTS (if AI fails) ---
INTERVIEW_PROMPTS = [
    "What makes your candidate uniquely qualified to be President?",
    "How would your candidate address the current economic challenges facing American families?",
    "Can you explain your candidate's position on healthcare reform?",
    "What specific policies would your candidate implement to address climate change?",
    "How does your candidate plan to heal the divisions in our country?",
]
