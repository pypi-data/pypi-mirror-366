"""
Minimal CQP-style matcher for single-token patterns
==================================================

Call ``match_cqp(tokens_df, expr, default_attr='word')`` to obtain a
*boolean* ``pd.Series`` (index = ``tokens_df.index``) that marks every
token which satisfies **expr**.  The supported subset of CQP is as follows:

* attribute/value pairs  –  `[pos = "JJ"]`
* implicit attribute      –  `"interesting"`  (equals `[word="interesting"]`)
* negation                –  `[pos != "N.*"]`
* wild-card               –  `[]`
* Boolean ops             –  `&`, `|`, `!` with parentheses
* flags                   –  `%c` (ignore case), `%d` (ignore diacritics),
                             any combination thereof.

PCRE syntax is used for the *right-hand side* patterns.
"""
from __future__ import annotations
import re, unicodedata, pandas as pd

# ────────────────────────────────────────────────────────────────────
# AST node types
# ────────────────────────────────────────────────────────────────────
class _Any:                    # []
    """Wildcard – matches every token."""
    pass


class _Not:
    def __init__(self, a): self.a = a


class _And:
    def __init__(self, a, b): self.a, self.b = a, b


class _Or:
    def __init__(self, a, b): self.a, self.b = a, b


class _Regex:
    def __init__(self, attr, pat, flags, neg=False):
        self.attr, self.pat, self.flags, self.neg = attr, pat, flags, neg


# ────────────────────────────────────────────────────────────────────
# Lexer
# ────────────────────────────────────────────────────────────────────
_TOK = re.compile(
    r"""\s*(?:
        (?P<LBR>\[)               |
        (?P<RBR>\])               |
        (?P<AMP>&)                |
        (?P<BAR>\|)               |
        (?P<NOT>!)                |
        (?P<LP>\()                |
        (?P<RP>\))                |
        (?P<ATTR>[A-Za-z][_0-9A-Za-z]*)\s*=\s* |
        (?P<NEQ>[A-Za-z][_0-9A-Za-z]*)\s*!=\s* |
        (?P<QUOT>"([^"\\]|\\.)*") |
        (?P<PERCENT>%[A-Za-z]+)   |
        (?P<DQ>"([^"\\]|\\.)*")   |
        (?P<SQ>'([^'\\]|\\.)*')   |
        (?P<STR>[^\s\[\]\(\)&|!]+)
    )""",
    re.VERBOSE,
)

def _unquote(s: str) -> str:
    if s and s[0] in "\"'":
        return bytes(s[1:-1], "utf-8").decode("unicode_escape")
    return s

def _tokenise(expr: str, default_attr: str):
    i = 0
    while i < len(expr):
        m = _TOK.match(expr, i)
        if not m:
            raise ValueError(f"Unexpected character at {expr[i:i+10]!r}")
        i = m.end()
        kind = m.lastgroup
        text = m.group(0).strip()
        if kind == "ATTR":
            yield ("ATTR", m.group(kind))
        elif kind == "NEQ":
            yield ("NEQ", m.group(kind))
        elif kind == "QUOT":
            yield ("QUOT", _unquote(text))
        elif kind == "PERCENT":
            yield ("FLAG", text[1:].lower())
        elif kind in ("DQ", "SQ"):
            yield ("LIT", _unquote(text))
        elif kind == "STR":
            yield ("LIT", text)
        else:
            yield (kind, text)
    yield ("EOF", "")

# ────────────────────────────────────────────────────────────────────
# Look-ahead iterator (peek without consuming)
# ────────────────────────────────────────────────────────────────────
class LookAhead:
    __slots__ = ("_it", "_buf")
    def __init__(self, iterable): self._it, self._buf = iter(iterable), None
    def __iter__(self): return self
    def __next__(self):
        if self._buf is not None:
            tok, self._buf = self._buf, None
            return tok
        return next(self._it)
    def peek(self):
        if self._buf is None:
            try: self._buf = next(self._it)
            except StopIteration: return None
        return self._buf

def _seen(s: LookAhead, kind): tok = s.peek(); return tok and tok[0] == kind

# ────────────────────────────────────────────────────────────────────
# Recursive-descent parser
# grammar:
#   expr  := or
#   or    := and ("|" and)*
#   and   := not ("&" not)*
#   not   := "!" not | atom
#   atom  := "[" ... "]" | "(" expr ")" | LITERAL
# ────────────────────────────────────────────────────────────────────
def _parse_expr(s): return _parse_or(s)

def _parse_or(s):
    lhs = _parse_and(s)
    while _seen(s, "BAR"):
        next(s)
        rhs = _parse_and(s)
        lhs = _Or(lhs, rhs)
    return lhs

def _parse_and(s):
    lhs = _parse_not(s)
    while _seen(s, "AMP"):
        next(s)
        rhs = _parse_not(s)
        lhs = _And(lhs, rhs)
    return lhs

def _parse_not(s):
    if _seen(s, "NOT"):
        next(s)
        return _Not(_parse_not(s))
    return _parse_atom(s)

# ────────────────────────────────────────────────────────────────────
#  lowest-level grammar rule:  atom
# ────────────────────────────────────────────────────────────────────
def _parse_atom(s):
    """
    atom := "[" expr? "]"        # empty ⇒ wildcard
          | "(" expr ")"         # parenthesised group
          | ATTR_OP              # attr (=|!=) pattern [flags]
          | LITERAL              # implicit default attribute

    ATTR_OP is either
        <attr> "="  <pattern>   |   <attr> "!=" <pattern>
    A pattern may optionally be followed by flag-tokens
        %c  (ignore case),  %d  (ignore diacritics),  %cd / %dc  (both).
    """
    tok = s.peek()
    if tok is None:
        raise ValueError("Unexpected end of input")

    # ── 1) square-bracketed expression / wildcard ──────────────────
    if tok[0] == "LBR":
        next(s)                                  # consume '['
        if _seen(s, "RBR"):                      # bare []  → wildcard
            next(s)
            return _Any()

        inner = _parse_or(s)                     # full sub-expression
        if not _seen(s, "RBR"):
            raise ValueError("Missing ']'")
        next(s)                                  # consume ']'
        return inner

    # ── 2) parenthesised sub-expression ─────────────────────────────
    if tok[0] == "LP":
        next(s)                                  # consume '('
        inner = _parse_or(s)
        if not _seen(s, "RP"):
            raise ValueError("Missing ')'")
        next(s)                                  # consume ')'
        return inner

    # ── 3) attribute comparison   attr (=|!=) pattern [flags] ───────
    if tok[0] in ("ATTR", "NEQ"):
        neg  = tok[0] == "NEQ"
        attr = next(s)[1]                        # consume ATTR / NEQ

        val_tok = next(s)
        if val_tok[0] not in ("LIT", "QUOT"):
            raise ValueError("Missing pattern after attribute comparison")
        pat   = val_tok[1]

        flags = next(s)[1] if _seen(s, "FLAG") else ""
        return _Regex(attr, pat, flags, neg)

    # ── 4) bare literal → implicit default attribute ────────────────
    if tok[0] in ("LIT", "QUOT"):
        pat   = next(s)[1]
        flags = next(s)[1] if _seen(s, "FLAG") else ""
        return _Regex(None, pat, flags, False)

    raise ValueError(f"Unexpected token {tok}")

# ────────────────────────────────────────────────────────────────────
# Evaluator
# ────────────────────────────────────────────────────────────────────
_strip_diacr = lambda s: unicodedata.normalize("NFD", s).translate(
    {ord(c): None for c in unicodedata.combining(chr(c))}
)

def _eval_ast(node, df: pd.DataFrame, default_attr: str) -> pd.Series:
    if isinstance(node, _Any):
        return pd.Series(True, index=df.index)

    if isinstance(node, _Regex):
        attr = node.attr or default_attr
        series = df[attr].astype(str)

        ignore_c = "c" in node.flags
        ignore_d = "d" in node.flags

        pat = node.pat
        if ignore_d:
            series = series.map(_strip_diacr)
            pat    = _strip_diacr(pat)
        flags = re.IGNORECASE if ignore_c else 0

        pat = r"\A" + pat + r"\Z"

        matches = series.str.contains(pat, regex=True, na=False, flags=flags)
        return ~matches if node.neg else matches

    if isinstance(node, _Not):
        return ~_eval_ast(node.a, df, default_attr)

    if isinstance(node, _And):
        return _eval_ast(node.a, df, default_attr) & _eval_ast(node.b, df, default_attr)

    if isinstance(node, _Or):
        return _eval_ast(node.a, df, default_attr) | _eval_ast(node.b, df, default_attr)

    raise TypeError(f"Unknown AST node {node!r}")

# ────────────────────────────────────────────────────────────────────
# Public helper
# ────────────────────────────────────────────────────────────────────
def match_cqp(tokens_df: pd.DataFrame,
              expr: str,
              default_attr: str = "word") -> pd.Series:
    """
    Parameters
    ----------
    tokens_df : pandas.DataFrame
        Must contain *at least* the column named by `default_attr`
        plus any additional columns referenced in the expression.
    expr : str
        Single-token CQP expression (no positional operators).
    default_attr : str, default ``"word"``
        Attribute that is used when the expression omits one.

    Returns
    -------
    pandas.Series[bool]
        Index aligned with *tokens_df* where *True* marks the matching
        rows (tokens).
    """
    stream = LookAhead(_tokenise(expr, default_attr))
    ast    = _parse_expr(stream)
    if stream.peek() and stream.peek()[0] != "EOF":
        raise ValueError("Trailing junk after valid expression")
    return _eval_ast(ast, tokens_df, default_attr)
