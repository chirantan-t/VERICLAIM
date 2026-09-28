import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os
import re
import fitz  # pymupdf

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
pdf_path = os.path.join(DATA_DIR, "00963ecb-af16-4799-9522-e946b5e73286.pdf")

doc = fitz.open(pdf_path)

full_text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    blocks = page.get_text("blocks")
    for b in blocks:
        if b[6] == 0:
            text = b[4].strip()
            if text:
                full_text += text + "\n\n"

# Check citations
print("FIRST 30 CITATION-LIKE SENTENCES:")
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

sentences = sent_tokenize(full_text.replace("\n", " "))
count = 0
for s in sentences:
    # Check for author-year or numeric variants
    if re.search(r'\([A-Za-z]+ et al\., \d{4}\)', s) or re.search(r'\[\d+(?:,\s*\d+)*\]', s) or re.search(r'\([A-Za-z]+, \d{4}\)', s) or re.search(r'[A-Za-z]+ et al\. \(\d{4}\)', s):
        print("-", s)
        count += 1
        if count >= 30:
            break

print("\n==================\n")

print("FIRST 30 REFERENCE-LIKE LINES:")
ref_match = re.search(r"(?:References|REFERENCES|Bibliography|Literature Cited)\n", full_text)
if ref_match:
    ref_text = full_text[ref_match.end() :]
    lines = ref_text.split('\n')
    count = 0
    for line in lines:
        if line.strip():
            print(line.strip())
            count += 1
            if count >= 30:
                break
else:
    print("NO REFERENCES SECTION FOUND")
