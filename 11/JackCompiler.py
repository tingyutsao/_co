#!/usr/bin/env python3
"""
nand2tetris Jack Compiler (Project 10 + Project 11)

用法:
    python JackCompiler.py Xxx.jack     -> 產生 Xxx.vm
    python JackCompiler.py SomeDir      -> 為資料夾內每個 .jack 產生同名 .vm
"""
import os
import re
import sys

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static", "var",
    "int", "char", "boolean", "void", "true", "false", "null", "this",
    "let", "do", "if", "else", "while", "return",
}
TOKEN_RE = re.compile(
    r'//[^\n]*|/\*.*?\*/|"[^"\n]*"|[{}()\[\].,;+\-*/&|<>=~]|\d+|[A-Za-z_]\w*',
    re.DOTALL,
)
BINARY_OPS = {
    "+": "add", "-": "sub", "&": "and", "|": "or",
    "<": "lt", ">": "gt", "=": "eq",
    "*": "call Math.multiply 2", "/": "call Math.divide 2",
}
UNARY_OPS = {"-": "neg", "~": "not"}
KIND_SEGMENT = {"static": "static", "field": "this", "arg": "argument", "var": "local"}


# --------------------------------------------------------------------------
# Tokenizer
# --------------------------------------------------------------------------
class Tokenizer:
    def __init__(self, text):
        self.tokens = []
        for tok in TOKEN_RE.findall(text):
            if tok.startswith("//") or tok.startswith("/*"):
                continue
            if tok.startswith('"'):
                self.tokens.append(("string", tok[1:-1]))
            elif tok.isdigit():
                self.tokens.append(("int", tok))
            elif tok in KEYWORDS:
                self.tokens.append(("keyword", tok))
            elif re.match(r"[A-Za-z_]", tok):
                self.tokens.append(("identifier", tok))
            else:
                self.tokens.append(("symbol", tok))
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else (None, None)

    def next(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok


# --------------------------------------------------------------------------
# Symbol table
# --------------------------------------------------------------------------
class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.sub_scope = {}
        self.counts = {"static": 0, "field": 0, "arg": 0, "var": 0}

    def start_subroutine(self):
        self.sub_scope = {}
        self.counts["arg"] = 0
        self.counts["var"] = 0

    def define(self, name, type_, kind):
        scope = self.class_scope if kind in ("static", "field") else self.sub_scope
        scope[name] = (type_, kind, self.counts[kind])
        self.counts[kind] += 1

    def var_count(self, kind):
        return self.counts[kind]

    def lookup(self, name):
        return self.sub_scope.get(name) or self.class_scope.get(name)


# --------------------------------------------------------------------------
# VM writer
# --------------------------------------------------------------------------
class VMWriter:
    def __init__(self):
        self.lines = []

    def push(self, seg, i):
        self.lines.append(f"push {seg} {i}")

    def pop(self, seg, i):
        self.lines.append(f"pop {seg} {i}")

    def arithmetic(self, cmd):
        self.lines.append(cmd)

    def label(self, name):
        self.lines.append(f"label {name}")

    def goto(self, name):
        self.lines.append(f"goto {name}")

    def if_goto(self, name):
        self.lines.append(f"if-goto {name}")

    def call(self, name, n):
        self.lines.append(f"call {name} {n}")

    def function(self, name, n):
        self.lines.append(f"function {name} {n}")

    def ret(self):
        self.lines.append("return")

    def text(self):
        return "\n".join(self.lines) + "\n"


# --------------------------------------------------------------------------
# Compilation engine
# --------------------------------------------------------------------------
class CompilationEngine:
    def __init__(self, tokenizer):
        self.t = tokenizer
        self.vm = VMWriter()
        self.st = SymbolTable()
        self.class_name = ""
        self.label_id = 0

    # ---- helpers ----
    def expect(self, value=None):
        tok = self.t.next()
        return tok[1]

    def new_label(self, prefix):
        label = f"{prefix}{self.label_id}"
        self.label_id += 1
        return label

    def push_var(self, name):
        _, kind, idx = self.st.lookup(name)
        self.vm.push(KIND_SEGMENT[kind], idx)

    def pop_var(self, name):
        _, kind, idx = self.st.lookup(name)
        self.vm.pop(KIND_SEGMENT[kind], idx)

    # ---- program structure ----
    def compile_class(self):
        self.expect()                      # 'class'
        self.class_name = self.expect()    # className
        self.expect()                      # '{'
        while self.t.peek()[1] in ("static", "field"):
            self.compile_class_var_dec()
        while self.t.peek()[1] in ("constructor", "function", "method"):
            self.compile_subroutine()
        self.expect()                      # '}'

    def compile_class_var_dec(self):
        kind = self.expect()               # static | field
        type_ = self.expect()
        self.st.define(self.expect(), type_, kind)
        while self.t.peek()[1] == ",":
            self.expect()
            self.st.define(self.expect(), type_, kind)
        self.expect()                      # ';'

    def compile_subroutine(self):
        sub_kind = self.expect()           # constructor | function | method
        self.expect()                      # return type
        name = self.expect()
        self.st.start_subroutine()
        if sub_kind == "method":
            self.st.define("this", self.class_name, "arg")
        self.expect()                      # '('
        self.compile_parameter_list()
        self.expect()                      # ')'
        self.expect()                      # '{'
        while self.t.peek()[1] == "var":
            self.compile_var_dec()
        self.vm.function(f"{self.class_name}.{name}", self.st.var_count("var"))
        if sub_kind == "constructor":
            self.vm.push("constant", self.st.var_count("field"))
            self.vm.call("Memory.alloc", 1)
            self.vm.pop("pointer", 0)
        elif sub_kind == "method":
            self.vm.push("argument", 0)
            self.vm.pop("pointer", 0)
        self.compile_statements()
        self.expect()                      # '}'

    def compile_parameter_list(self):
        if self.t.peek()[1] == ")":
            return
        type_ = self.expect()
        self.st.define(self.expect(), type_, "arg")
        while self.t.peek()[1] == ",":
            self.expect()
            type_ = self.expect()
            self.st.define(self.expect(), type_, "arg")

    def compile_var_dec(self):
        self.expect()                      # 'var'
        type_ = self.expect()
        self.st.define(self.expect(), type_, "var")
        while self.t.peek()[1] == ",":
            self.expect()
            self.st.define(self.expect(), type_, "var")
        self.expect()                      # ';'

    # ---- statements ----
    def compile_statements(self):
        while self.t.peek()[1] in ("let", "if", "while", "do", "return"):
            getattr(self, "compile_" + self.t.peek()[1])()

    def compile_let(self):
        self.expect()                      # 'let'
        name = self.expect()
        if self.t.peek()[1] == "[":
            self.expect()
            self.push_var(name)
            self.compile_expression()
            self.expect()                  # ']'
            self.vm.arithmetic("add")
            self.expect()                  # '='
            self.compile_expression()
            self.expect()                  # ';'
            self.vm.pop("temp", 0)
            self.vm.pop("pointer", 1)
            self.vm.push("temp", 0)
            self.vm.pop("that", 0)
        else:
            self.expect()                  # '='
            self.compile_expression()
            self.expect()                  # ';'
            self.pop_var(name)

    def compile_if(self):
        else_label = self.new_label("IF_ELSE")
        end_label = self.new_label("IF_END")
        self.expect()                      # 'if'
        self.expect()                      # '('
        self.compile_expression()
        self.expect()                      # ')'
        self.vm.arithmetic("not")
        self.vm.if_goto(else_label)
        self.expect()                      # '{'
        self.compile_statements()
        self.expect()                      # '}'
        self.vm.goto(end_label)
        self.vm.label(else_label)
        if self.t.peek()[1] == "else":
            self.expect()
            self.expect()                  # '{'
            self.compile_statements()
            self.expect()                  # '}'
        self.vm.label(end_label)

    def compile_while(self):
        start_label = self.new_label("WHILE_START")
        end_label = self.new_label("WHILE_END")
        self.expect()                      # 'while'
        self.vm.label(start_label)
        self.expect()                      # '('
        self.compile_expression()
        self.expect()                      # ')'
        self.vm.arithmetic("not")
        self.vm.if_goto(end_label)
        self.expect()                      # '{'
        self.compile_statements()
        self.expect()                      # '}'
        self.vm.goto(start_label)
        self.vm.label(end_label)

    def compile_do(self):
        self.expect()                      # 'do'
        name = self.expect()
        self.compile_call(name)
        self.expect()                      # ';'
        self.vm.pop("temp", 0)

    def compile_return(self):
        self.expect()                      # 'return'
        if self.t.peek()[1] != ";":
            self.compile_expression()
        else:
            self.vm.push("constant", 0)
        self.expect()                      # ';'
        self.vm.ret()

    # ---- expressions ----
    def compile_expression(self):
        self.compile_term()
        while self.t.peek()[0] == "symbol" and self.t.peek()[1] in BINARY_OPS:
            op = self.expect()
            self.compile_term()
            self.vm.arithmetic(BINARY_OPS[op])

    def compile_expression_list(self):
        count = 0
        if self.t.peek()[1] != ")":
            self.compile_expression()
            count = 1
            while self.t.peek()[1] == ",":
                self.expect()
                self.compile_expression()
                count += 1
        return count

    def compile_call(self, first_name):
        """first_name 已被讀取；接下來是 '(' 或 '.'。"""
        n_args = 0
        if self.t.peek()[1] == ".":
            self.expect()                  # '.'
            sub_name = self.expect()
            entry = self.st.lookup(first_name)
            if entry:                      # first_name 是物件變數 -> method
                self.push_var(first_name)
                full_name = f"{entry[0]}.{sub_name}"
                n_args = 1
            else:                          # first_name 是類別名稱 -> function / constructor
                full_name = f"{first_name}.{sub_name}"
        else:                              # 同類別內的 method
            self.vm.push("pointer", 0)
            full_name = f"{self.class_name}.{first_name}"
            n_args = 1
        self.expect()                      # '('
        n_args += self.compile_expression_list()
        self.expect()                      # ')'
        self.vm.call(full_name, n_args)

    def compile_term(self):
        kind, value = self.t.next()
        if kind == "int":
            self.vm.push("constant", value)
        elif kind == "string":
            self.vm.push("constant", len(value))
            self.vm.call("String.new", 1)
            for ch in value:
                self.vm.push("constant", ord(ch))
                self.vm.call("String.appendChar", 2)
        elif kind == "keyword":
            if value == "true":
                self.vm.push("constant", 0)
                self.vm.arithmetic("not")
            elif value in ("false", "null"):
                self.vm.push("constant", 0)
            elif value == "this":
                self.vm.push("pointer", 0)
        elif kind == "identifier":
            nxt = self.t.peek()[1]
            if nxt == "[":
                self.expect()
                self.push_var(value)
                self.compile_expression()
                self.expect()              # ']'
                self.vm.arithmetic("add")
                self.vm.pop("pointer", 1)
                self.vm.push("that", 0)
            elif nxt in ("(", "."):
                self.compile_call(value)
            else:
                self.push_var(value)
        elif value == "(":
            self.compile_expression()
            self.expect()                  # ')'
        elif value in UNARY_OPS:
            self.compile_term()
            self.vm.arithmetic(UNARY_OPS[value])


# --------------------------------------------------------------------------
def compile_file(path):
    with open(path, encoding="utf-8") as f:
        engine = CompilationEngine(Tokenizer(f.read()))
    engine.compile_class()
    out_path = os.path.splitext(path)[0] + ".vm"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(engine.vm.text())
    print(f"Wrote {out_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python JackCompiler.py <file.jack | directory>")
        sys.exit(1)
    target = os.path.abspath(sys.argv[1])
    if os.path.isdir(target):
        files = sorted(
            os.path.join(target, f) for f in os.listdir(target) if f.endswith(".jack")
        )
    else:
        files = [target]
    if not files:
        print("No .jack files found.")
        sys.exit(1)
    for path in files:
        compile_file(path)


if __name__ == "__main__":
    main()