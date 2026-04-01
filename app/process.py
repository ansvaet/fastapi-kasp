import re
from collections import defaultdict
from typing import Tuple, Dict
from pathlib import Path
import logging
from app.lemmas import lemmatizer
from app.writer import write_excel


def count_lines(file_path: Path) -> int:
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

def process_file(file_path: Path, output_path: Path) -> None:

    total_lines = count_lines(file_path)
    
    total_counts = defaultdict(int)
    line_counts = defaultdict(lambda: defaultdict(int))
    
    # оставляем буквы, дефис, апостроф
    word_pattern = re.compile(r'[^\w\-’\']+', re.UNICODE)
    

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            tokens = line.split()
            local_counts = defaultdict(int)
            
            for token in tokens:

                word = word_pattern.sub('', token)
                if not word or word.isdigit():
                    continue

                try:
                    lemma = lemmatizer.normalize(word.lower())
                    local_counts[lemma] += 1
                except Exception as e:
                    continue
            

            for lemma, cnt in local_counts.items():
                total_counts[lemma] += cnt
                line_counts[lemma][line_idx] += cnt
            

    write_excel(output_path, total_counts, line_counts, total_lines)
