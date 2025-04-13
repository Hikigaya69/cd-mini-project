import re
from collections import defaultdict

# === PARSE TREE PART === #
class Node:
    def __init__(self, label, terminal=False):
        self.label = label
        self.terminal = terminal
        self.children = []

    def add(self, child):
        self.children.append(child)

def print_tree(node, prefix="", is_last=True, output=[]):
    branch = "└── " if is_last else "├── "
    output.append(prefix + branch + node.label + (" (Terminal)" if node.terminal else ""))
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(child, new_prefix, is_last_child, output)
    return output

# === FIRST/FOLLOW PART === #
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

def compute_follow():
    follow["PROGRAM"].add("$")
    changed = True
    while changed:
        changed = False
        for head in grammar:
            for production in grammar[head]:
                for i, symbol in enumerate(production):
                    if symbol in non_terminals:
                        rest = production[i + 1:]
                        follow_before = follow[symbol].copy()
                        if rest:
                            rest_first = set()
                            for sym in rest:
                                sym_first = compute_first(sym)
                                rest_first |= (sym_first - {"ε"})
                                if "ε" in sym_first:
                                    continue
                                else:
                                    break
                            else:
                                rest_first.add("ε")
                            follow[symbol] |= (rest_first - {"ε"})
                            if "ε" in rest_first:
                                follow[symbol] |= follow[head]
                        else:
                            follow[symbol] |= follow[head]
                        if follow_before != follow[symbol]:
                            changed = True

# === PARSER LOGIC === #
def parser():
    try:
        with open("token_stream.txt") as f:
            tokens = [line.strip() for line in f.readlines() if line.strip()]

        pos = 0
        def match(expected):
            nonlocal pos
            if pos < len(tokens) and tokens[pos] == expected:
                pos += 1
            else:
                raise SyntaxError(f"Expected {expected} at position {pos}, got {tokens[pos] if pos < len(tokens) else 'EOF'}")

        root = Node("S")
        match("KEYWORD")   # int
        root.add(Node("TYPE", True))

        match("KEYWORD")   # main
        root.add(Node("MAIN", True))

        match("PUNCTUATION")  # (
        match("PUNCTUATION")  # )

        match("KEYWORD")   # begin
        code = Node("CODE")

        # DECLARE
        decl = Node("DECLARE")
        match("KEYWORD")   # int
        decl.add(Node("TYPE", True))

        idlist = Node("ID_LIST")
        match("IDENTIFIER")  # n1
        idlist.add(Node("ID", True))
        match("PUNCTUATION") # ,
        idlist.add(Node("CM", True))
        match("IDENTIFIER")  # n2
        idlist.add(Node("ID", True))
        match("PUNCTUATION") # ,
        idlist.add(Node("CM", True))
        match("IDENTIFIER")  # n3
        idlist.add(Node("ID", True))
        decl.add(idlist)

        match("PUNCTUATION")  # ;
        decl.add(Node("SC", True))
        code.add(decl)

        # 3 IF STATEMENTS
        stmts = Node("STATEMENTS")
        for _ in range(3):
            ifstmt = Node("IF_STMT")
            match("KEYWORD")       # if
            match("PUNCTUATION")   # (

            if tokens[pos] in ["EXPR", "IDENTIFIER", "LITERAL"]:
                match(tokens[pos])
            else:
                raise SyntaxError(f"Expected EXPR at position {pos}, got {tokens[pos]}")

            match("RELOP")  # relop

            if tokens[pos] in ["EXPR", "IDENTIFIER", "LITERAL"]:
                match(tokens[pos])
            else:
                raise SyntaxError(f"Expected EXPR at position {pos}, got {tokens[pos]}")

            match("PUNCTUATION")   # )
            match("KEYWORD")       # begin

            printf = Node("PRINTF")
            match("KEYWORD")       # printf
            match("PUNCTUATION")   # (
            if tokens[pos] in ["EXPR", "IDENTIFIER", "LITERAL"]:
                match(tokens[pos])
            else:
                raise SyntaxError(f"Expected ID/EXPR inside printf at position {pos}, got {tokens[pos]}")
            match("PUNCTUATION")   # )
            match("PUNCTUATION")   # ;
            ifstmt.add(printf)

            match("KEYWORD")       # end
            stmts.add(ifstmt)

        code.add(stmts)
        match("KEYWORD")  # end
        root.add(code)
        root.add(Node("END", True))

        # === OUTPUT === #
        # 1. Parse Tree
        tree_lines = print_tree(root)
        with open("parse_tree.txt", "w", encoding="utf-8") as tf:
            tf.writelines(line + "\n" for line in tree_lines)

        # 2. Grammar Rules Used
        with open("parser_table.txt", "w", encoding="utf-8") as pt:
            pt.write("Grammar Rules Used:\n")
            pt.write("1. S → TYPE MAIN CODE END\n")
            pt.write("2. CODE → DECLARE STATEMENTS\n")
            pt.write("3. DECLARE → TYPE ID_LIST SC\n")
            pt.write("4. ID_LIST → ID CM ID CM ID\n")
            pt.write("5. STATEMENTS → IF_STMT IF_STMT IF_STMT\n")
            pt.write("6. IF_STMT → IF ( EXPR RELOP EXPR ) BEGIN PRINTF END\n")
            pt.write("7. PRINTF → printf ( ID ) ;\n")

        # 3. FIRST/FOLLOW
        for non_term in grammar:
            compute_first(non_term)
        compute_follow()

        with open("first.txt", "w", encoding="utf-8") as ff:
            ff.write("FIRST Sets:\n" + "-" * 40 + "\n")
            for nt in grammar:
                ff.write(f"{nt}: {', '.join(first[nt])}\n")

        with open("follow.txt", "w", encoding="utf-8") as ffw:
            ffw.write("FOLLOW Sets:\n" + "-" * 40 + "\n")
            for nt in grammar:
                ffw.write(f"{nt}: {', '.join(follow[nt])}\n")

        print("Parse tree, parser table, FIRST and FOLLOW sets generated successfully.")

    except Exception as e:
        with open("error.txt", "w", encoding="utf-8") as ef:
            ef.write(f"Syntax Error:\n{str(e)}\n")
        print("Error written to error.txt")

if __name__ == "__main__":
    parser()
