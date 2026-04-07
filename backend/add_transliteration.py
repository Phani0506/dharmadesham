import json
import os
import sys
import subprocess

def install_and_import():
    try:
        from indic_transliteration import sanscript
    except ImportError:
        print("indic_transliteration not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "indic-transliteration"])
        from indic_transliteration import sanscript
    return sanscript

sanscript = install_and_import()

import glob

mahabharata_dir = r"c:\PHANI PERSONAL\PHANI PERSONAL 1\dharmadesham\mahabharata"
json_patterns = glob.glob(os.path.join(mahabharata_dir, "*.json"))

for file_path in json_patterns:
    print(f"Loading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Processing {len(data)} verses in {os.path.basename(file_path)}...")
    for item in data:
        if "text" in item:
            transliterated = sanscript.transliterate(item["text"], sanscript.DEVANAGARI, sanscript.IAST)
            item["transliteration"] = transliterated

    print(f"Saving modified file {os.path.basename(file_path)}...")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

print("Successfully added transliteration to all items in all files!")
