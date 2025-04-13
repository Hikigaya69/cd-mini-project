import re
from collections import defaultdict

# === LEXER PART === #

# Token patterns
patterns = {
    "KEYWORD":     r"\b(int|main|if|begin|end|printf)\b",
    "RELOP":       r"\brelop\b",
    "EXPR":        r"\bexpr\b",
    "IDENTIFIER":  r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
    "OPERATOR":    r"(==|!=|<=|>=|<|>|=)",
    "LITERAL":     r"\b\d+\b",
    "PUNCTUATION": r"[\(\);,]"
}

token_spec = "|".join(f"(?P<{k}>{v})" for k, v in patterns.items())
token_regex = re.compile(token_spec)

summary = defaultdict(list)
tokens = []

# Lexical Analysis
with open("input.txt") as file, open("tokens.txt", "w", encoding="utf-8") as tf:
    tf.write("{:<20} {:<20} {:<20}\n".format("Token", "Lexeme", "Type"))
    tf.write("-" * 60 + "\n")
    for line in file:
        for mo in re.finditer(token_regex, line):
            kind = mo.lastgroup
            value = mo.group()
            tokens.append((kind, value))
            summary[kind].append(value)
            tf.write("{:<20} {:<20} {:<20}\n".format(
                kind, value,
                "Keyword" if kind == "KEYWORD" else
                "Identifier" if kind == "IDENTIFIER" else
                "Number" if kind == "LITERAL" else
                "Operator" if kind == "OPERATOR" else
                "Punctuation" if kind == "PUNCTUATION" else
                "Expression" if kind == "EXPR" else
                "Relational Operator"
            ))

# Token summary
with open("token_summary.txt", "w", encoding="utf-8") as sf:
    sf.write("Summary of Analysis:\n")
    sf.write("-" * 60 + "\n")
    sf.write("{:<22} {:<12} {}\n".format("Category", "Count", "Elements"))
    sf.write("-" * 60 + "\n")
    for k, v in summary.items():
        sf.write("{:<22} {:<12} {}\n".format(k.capitalize(), len(v), "\t".join(set(v))))

# Token stream
with open("token_stream.txt", "w", encoding="utf-8") as f:
    for kind, val in tokens:
        if kind in ["KEYWORD", "EXPR", "RELOP", "IDENTIFIER", "PUNCTUATION"]:
            f.write(f"{kind}\n")
