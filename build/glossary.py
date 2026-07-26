#!/usr/bin/env python3
"""Light auto-correct for whisper transcripts of Indradyumna Swami lectures.
Only DISTINCTIVE, unambiguous mis-hears of ISKCON / Gaudiya Vaishnava terms are
corrected, to avoid collateral damage. Applied to note transcripts; the raw
whisper .txt in build/transcripts/ is kept untouched as source of truth.
Each entry: (regex pattern [IGNORECASE], replacement). Order matters."""
import re

# (pattern, replacement) — patterns are matched case-insensitively with \b guards
_RULES = [
    # --- Srila Prabhupada (clear garbles; 'Prabhupada' itself is usually fine) ---
    (r"\bPrabhba\b", "Prabhupada"),
    (r"\bAshwita Prabhupada\b", "Srila Prabhupada"),
    (r"\bSiddha(?:rtha)? Prabhupada\b", "Srila Prabhupada"),
    (r"\bSrta\.? Prabhupada\b", "Srila Prabhupada"),
    (r"\bSri Rupa Bhupada\b", "Srila Prabhupada"),
    (r"\bRupa Bhupada\b", "Srila Prabhupada"),
    # --- Chaitanya-caritamrita ---
    (r"\bChaitanya[-\s]?carita[nm][-\s]?rita\b", "Chaitanya-caritamrita"),
    (r"\bChaitanya[-\s]?char[a]?ta[-\s]?m[ae]rita\b", "Chaitanya-caritamrita"),
    (r"\bchitanya char[a]?ta marita\b", "Chaitanya-caritamrita"),
    (r"\bChaitanya Charitamrita\b", "Chaitanya-caritamrita"),
    # --- Chaitanya Mahaprabhu (Titania mis-hear) ---
    (r"\bSri Titania Mahaprabhu\b", "Sri Chaitanya Mahaprabhu"),
    (r"\bTitania Mahaprabhu\b", "Chaitanya Mahaprabhu"),
    # --- Founders/acharyas ---
    (r"\bBhakti\s?s[ai]dh?[ae]n[ta][ae]?\s?Saraswar?i\b", "Bhaktisiddhanta Saraswati"),
    (r"\bBhakti Suddhamadharata\b", "Bhaktisiddhanta Saraswati"),
    (r"\bBhakti Vinod[a]?ta? ?Kura\b", "Bhaktivinoda Thakura"),
    (r"\bBhakti Vanara Takura\b", "Bhaktivinoda Thakura"),
    (r"\bVishenav Chakravati Thakur\b", "Vishvanatha Chakravarti Thakura"),
    (r"\bVishnu Chakravati Thakur\b", "Vishvanatha Chakravarti Thakura"),
    (r"\bVishanad Chakamari Takura\b", "Vishvanatha Chakravarti Thakura"),
    (r"\bGrogavinda Maharaj\b", "Gour Govinda Maharaj"),
    (r"\bNaratam\b", "Narottam"),
    # --- Gaudiya Vaishnava ---
    (r"\bGho?di?[ae]?\s?Vaishnav(a|as|s)?\b", "Gaudiya Vaishnava"),
    (r"\bGhodiya[-\s]?vaishnavas\b", "Gaudiya Vaishnavas"),
    # --- Deities / pastime figures ---
    (r"\bnishringadev\b", "Nrisimhadev"),
    (r"\branikashifu\b", "Hiranyakashipu"),
    (r"\bRukmini Dworkadish\b", "Rukmini Dwarkadhish"),
    (r"\bKulushekhar\b", "Kulasekhara"),
    # --- Scriptures / terms ---
    (r"\bNectar Devotion\b", "Nectar of Devotion"),
    (r"\bIsh?apanesha\b", "Isopanisad"),
    (r"\bMan[au]samita\b", "Manu-samhita"),
    (r"\bGaijri mantra\b", "Gayatri mantra"),
    (r"\bSridharam Mayapur\b", "Sri Dham Mayapur"),
    (r"\b(Snakirtan|Snakirtana)\b", "Sankirtan"),
    (r"\bVyaskoja\b", "Vyasa-puja"),
    (r"\bVyasa Puj\b", "Vyasa-puja"),
    # --- mleccha (meat-eater) garbles ---
    (r"\b(Maletia|Malachas|Malecha|Maleccha|maletia|malachas)\b", "mleccha"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), r) for p, r in _RULES]

def apply_glossary(text):
    for pat, repl in _COMPILED:
        text = pat.sub(repl, text)
    return text

if __name__ == "__main__":
    import sys
    print(apply_glossary(open(sys.argv[1], encoding="utf-8").read()))
