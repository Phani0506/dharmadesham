import json
import re
import os

# Normalize Sanskrit string for robust matching
def normalize_sanskrit(text):
    # Remove all punctuation, dandas, newlines, and spaces
    text = text.replace('\n', '')
    text = text.replace('।', '')
    text = text.replace('॥', '')
    text = text.replace(' ', '')
    # Convert different encodings of 'o' (e.g., रॊ to रो)
    text = text.replace('ॊ', 'ो')
    text = text.replace('म', 'म्') # Just a quick normalizer for end-of-word m if needed, maybe not safe generally. Let's just remove halants.
    text = text.replace('्', '') # Remove all halants to match base chars
    return text

print("Loading Itihasa dataset...")
itihasa_en = []
itihasa_sn = []
itihasa_sn_norm = []

for split in ['train_full', 'dev', 'test']:
    sn_path = f'itihasa/{split}.sn.csv'
    en_path = f'itihasa/{split}.en.csv'
    with open(sn_path, 'r', encoding='utf-8') as f_sn, open(en_path, 'r', encoding='utf-8') as f_en:
        for sn_line, en_line in zip(f_sn, f_en):
            sn_line = sn_line.strip()
            en_line = en_line.strip()
            if not sn_line or not en_line: continue
            
            itihasa_sn.append(sn_line)
            itihasa_en.append(en_line)
            itihasa_sn_norm.append(normalize_sanskrit(sn_line))

print(f"Loaded {len(itihasa_sn)} matches from Itihasa.")

with open('mahabharata/chapter 1.json', 'r', encoding='utf-8') as f:
    chapter1 = json.load(f)

# Try matching
matches = 0
for idx, item in enumerate(chapter1[:20]):
    text = item['text']
    norm_text = normalize_sanskrit(text)
    
    # Try finding in itihasa
    # To handle substrings (since shlokas might be grouped or partial), check if norm contained
    found = False
    for i, sn_norm in enumerate(itihasa_sn_norm):
        if not sn_norm:
            continue
        # Also let's require a minimum match length or more robust matching
        # But for now let's just make sure sn_norm is reasonably long
        if len(sn_norm) < 5:
            continue
        if norm_text in sn_norm or sn_norm in norm_text:
            found = True
            print(f"Match found for shloka {item['shloka']}!")
            print(f"JSON: {text}")
            print(f"ITI:  {itihasa_sn[i]}")
            print(f"ENG:  {itihasa_en[i]}")
            print("-" * 50)
            break
    
    if not found:
        print(f"NO MATCH for shloka {item['shloka']} (normalized: {norm_text})")
        print(f"Original: {text}")
        print("=" * 50)
