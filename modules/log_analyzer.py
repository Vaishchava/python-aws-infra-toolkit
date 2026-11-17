import re
from collections import Counter

def analyze_log_file(filepath):
    patterns = re.compile(r"(ERROR|CRITICAL|502 Bad Gateway|504 Gateway|Failed password)", re.IGNORECASE)
    counts = Counter()
    sample_lines = []

    with open(filepath, "r", errors="ignore") as f:
        for line in f:
            match = patterns.search(line)
            if match:
                keyword = match.group(1).upper()
                counts[keyword] += 1
                if len(sample_lines) < 5:
                    sample_lines.append(line.strip())

    return {"file": filepath, "summary": dict(counts), "recent_samples": sample_lines}
