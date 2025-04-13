import re
from collections import defaultdict, deque

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

# === GRAMMAR & FIRST/FOLLOW PART === #

# Grammar definition based on the sample input
grammar = {
    "PROGRAM":      [["main_block"]],
    "main_block":   [["KEYWORD", "KEYWORD", "DECLS", "STMTS", "KEYWORD"]],
    "DECLS":        [["KEYWORD", "ID_LIST", "PUNCTUATION"]],
    "ID_LIST":      [["IDENTIFIER", "ID_TAIL"]],
    "ID_TAIL":      [["PUNCTUATION", "ID_LIST"], []],
    "STMTS":        [["STMT", "STMTS"], []],
    "STMT":         [["KEYWORD", "PUNCTUATION", "EXPR", "RELOP", "EXPR", "PUNCTUATION", "KEYWORD", "ACTION", "KEYWORD"]],
    "ACTION":       [["KEYWORD", "PUNCTUATION", "IDENTIFIER", "PUNCTUATION"]],
}

non_terminals = set(grammar.keys())
first = defaultdict(set)
follow = defaultdict(set)

# Compute FIRST sets
def compute_first(symbol):
    if symbol not in non_terminals:
        return {symbol}

    if first[symbol]:
        return first[symbol]

    for prod in grammar[symbol]:
        if not prod:
            first[symbol].add("ε")
        else:
            for sym in prod:
                sym_first = compute_first(sym)
                first[symbol] |= (sym_first - {"ε"})
                if "ε" not in sym_first:
                    break
            else:
                first[symbol].add("ε")
    return first[symbol]

# Compute FOLLOW sets
def compute_follow():
    follow["PROGRAM"].add("$")
    changed = True
    while changed:
        changed = False
        for nt in grammar:
            for prod in grammar[nt]:
                trailer = follow[nt].copy()
                for symbol in reversed(prod):
                    if symbol in non_terminals:
                        if follow[symbol] != follow[symbol] | trailer:
                            follow[symbol] |= trailer
                            changed = True
                        if "ε" in first[symbol]:
                            trailer |= (first[symbol] - {"ε"})
                        else:
                            trailer = first[symbol]
                    else:
                        trailer = compute_first(symbol)

# Run FIRST/FOLLOW computations
for non_term in grammar:
    compute_first(non_term)
compute_follow()

# Write FIRST sets to file
with open("first.txt", "w", encoding="utf-8") as ff:
    ff.write("FIRST Sets:\n" + "-" * 40 + "\n")
    for nt in grammar:
        ff.write(f"{nt}: {', '.join(first[nt])}\n")

# Write FOLLOW sets to file
with open("follow.txt", "w", encoding="utf-8") as ffw:
    ffw.write("FOLLOW Sets:\n" + "-" * 40 + "\n")
    for nt in grammar:
        ffw.write(f"{nt}: {', '.join(follow[nt])}\n")
