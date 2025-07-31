import pandas as pd
import re
from pathlib import Path
import os

TOKEN_RE = re.compile(
    r"([A-Za-z0-9\-]+|[^\w\s\-])(\s*)"
)

class Corpus:
    def __init__(self, files):
        if isinstance(files, (str, Path)):
            files = [files]
        files = [Path(os.path.expanduser(str(f))) for f in files]
        self.files = files
        self._load()

    def _load(self):
        tokens = []
        documents = []
        cpos = 0
        all_paths = [file.resolve() for file in self.files]
        common_parent = os.path.commonpath([str(p) for p in all_paths])
        for file_id, file in enumerate(self.files):
            text = Path(file).read_text(encoding="utf8")
            start = cpos
            for match in TOKEN_RE.finditer(text):
                word, ws = match.groups()
                tokens.append({
                    "cpos": cpos,
                    "word": word,
                    "whitespace": bool(ws),
                    "file_id": file_id,
                })
                cpos += 1
            end = cpos - 1 if cpos > start else start
            rel_path = str(Path(file).resolve().relative_to(common_parent))
            documents.append({
                "file_id": file_id,
                "start": start,
                "end": end,
                "path": rel_path,
            })
        self.tokens = pd.DataFrame(tokens).set_index("cpos")
        self.documents = pd.DataFrame(documents).set_index("file_id")

    def __repr__(self):
        return f"<Corpus: {len(self.documents)} document(s), {len(self.tokens)} tokens>"

# Usage:
# from flexiconc import Corpus
# c = Corpus(["text1.txt", "text2.txt"])
# print(c.tokens.head())
# print(c.documents)
