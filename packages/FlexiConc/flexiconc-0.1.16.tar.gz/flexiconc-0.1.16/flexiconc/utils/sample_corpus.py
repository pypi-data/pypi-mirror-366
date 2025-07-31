import sqlite3

DB_PATH = "../sample_corpus.sqlite3"  # Change this path as needed

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Drop old tables if they exist for a clean run
cur.execute("DROP TABLE IF EXISTS tokens")
cur.execute("DROP TABLE IF EXISTS spans_text")
cur.execute("DROP TABLE IF EXISTS spans_s")

# Create tokens table: cpos, word, lemma, pos
cur.execute("""
CREATE TABLE tokens (
    cpos INTEGER PRIMARY KEY,
    word TEXT,
    lemma TEXT,
    pos TEXT
)
""")

# Text 1 (Alice): 1 sentence
# Text 2 (Bob): 2 sentences
tokens_data = [
    # Text 1 by Alice
    (0,  "The",   "the",   "DT"),
    (1,  "quick", "quick", "JJ"),
    (2,  "brown", "brown", "JJ"),
    (3,  "fox",   "fox",   "NN"),
    (4,  "jumps", "jump",  "VBZ"),
    (5,  "!",     "!",     "."),

    # Text 2 by Bob, sentence 1
    (6,  "Wizards",  "wizard",  "NNS"),
    (7,  "quickly",  "quickly", "RB"),
    (8,  "mix",      "mix",     "VBP"),
    (9,  "potions",  "potion",  "NNS"),
    (10, "at",       "at",      "IN"),
    (11, "midnight", "midnight","NN"),
    (12, ".",        ".",       "."),

    # Text 2 by Bob, sentence 2
    (13, "Magic",     "magic",     "NN"),
    (14, "is",        "be",        "VBZ"),
    (15, "hard",      "hard",      "JJ"),
    (16, "work",      "work",      "NN"),
    (17, ".",         ".",         "."),
]
cur.executemany("INSERT INTO tokens VALUES (?, ?, ?, ?)", tokens_data)

# Create spans_text: id, start, end, author
cur.execute("""
CREATE TABLE spans_text (
    id INTEGER PRIMARY KEY,
    start INTEGER,
    end INTEGER,
    author TEXT
)
""")
cur.executemany("INSERT INTO spans_text VALUES (?, ?, ?, ?)", [
    (0, 0, 6,   "Alice"),
    (1, 6, 18,  "Bob")
])

# Create spans_s: id, start, end
cur.execute("""
CREATE TABLE spans_s (
    id INTEGER PRIMARY KEY,
    start INTEGER,
    end INTEGER
)
""")
cur.executemany("INSERT INTO spans_s VALUES (?, ?, ?)", [
    (0, 0, 6),     # The quick brown fox jumps !
    (1, 6, 13),    # Wizards quickly mix potions at midnight .
    (2, 13, 18)    # Magic is hard work .
])

conn.commit()
conn.close()
print(f"Created a sample corpus at {DB_PATH}.")
