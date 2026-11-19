#!/usr/bin/env python3
"""
nand2tetris VM Translator (Project 7 + Project 8)

用法:
    python VMTranslator.py Xxx.vm       -> 產生 Xxx.asm（不含 bootstrap）
    python VMTranslator.py SomeDir      -> 產生 SomeDir/SomeDir.asm（含 bootstrap）
"""
import os
import sys

ARITH_BINARY = {"add": "+", "sub": "-", "and": "&", "or": "|"}
ARITH_UNARY = {"neg": "-", "not": "!"}
COMPARE = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}
SEGMENT_BASE = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}


class Parser:
    """讀取 .vm 檔並逐行解析指令。"""

    def __init__(self, path):
        self.commands = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("//")[0].strip()
                if line:
                    self.commands.append(line.split())

    def __iter__(self):
        return iter(self.commands)


class CodeWriter:
    def __init__(self, out_path, bootstrap):
        self.out = open(out_path, "w", encoding="utf-8")
        self.file_name = ""
        self.func = ""
        self.label_id = 0
        self.call_id = 0
        if bootstrap:
            self.write_bootstrap()

    # ---------- 基本工具 ----------
    def emit(self, *lines):
        for line in lines:
            self.out.write(line + "\n")

    def set_file_name(self, name):
        self.file_name = name

    def close(self):
        self.out.close()

    def _push_d(self):
        self.emit("@SP", "A=M", "M=D", "@SP", "M=M+1")

    def _scoped(self, label):
        return f"{self.func}${label}" if self.func else label

    # ---------- Bootstrap ----------
    def write_bootstrap(self):
        self.emit("// bootstrap", "@256", "D=A", "@SP", "M=D")
        self.write_call("Sys.init", 0)

    # ---------- 算術邏輯 ----------
    def write_arithmetic(self, cmd):
        self.emit(f"// {cmd}")
        if cmd in ARITH_BINARY:
            op = ARITH_BINARY[cmd]
            self.emit("@SP", "AM=M-1", "D=M", "A=A-1")
            if cmd == "sub":
                self.emit("M=M-D")
            else:
                self.emit(f"M=D{op}M" if cmd in ("and", "or") else f"M=M{op}D")
        elif cmd in ARITH_UNARY:
            self.emit("@SP", "A=M-1", f"M={ARITH_UNARY[cmd]}M")
        elif cmd in COMPARE:
            n = self.label_id
            self.label_id += 1
            self.emit(
                "@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D",
                f"@TRUE_{n}", f"D;{COMPARE[cmd]}",
                "@SP", "A=M-1", "M=0",
                f"@END_{n}", "0;JMP",
                f"(TRUE_{n})", "@SP", "A=M-1", "M=-1",
                f"(END_{n})",
            )

    # ---------- push / pop ----------
    def _direct_address(self, segment, i):
        if segment == "temp":
            return f"R{5 + i}"
        if segment == "pointer":
            return "THIS" if i == 0 else "THAT"
        if segment == "static":
            return f"{self.file_name}.{i}"
        return None

    def write_push_pop(self, cmd, segment, i):
        self.emit(f"// {cmd} {segment} {i}")
        i = int(i)
        if cmd == "push":
            if segment == "constant":
                self.emit(f"@{i}", "D=A")
            elif segment in SEGMENT_BASE:
                self.emit(f"@{i}", "D=A", f"@{SEGMENT_BASE[segment]}", "A=M+D", "D=M")
            else:
                self.emit(f"@{self._direct_address(segment, i)}", "D=M")
            self._push_d()
        else:  # pop
            if segment in SEGMENT_BASE:
                self.emit(
                    f"@{i}", "D=A", f"@{SEGMENT_BASE[segment]}", "D=M+D",
                    "@R13", "M=D",
                    "@SP", "AM=M-1", "D=M",
                    "@R13", "A=M", "M=D",
                )
            else:
                self.emit("@SP", "AM=M-1", "D=M",
                          f"@{self._direct_address(segment, i)}", "M=D")

    # ---------- 分支 ----------
    def write_label(self, label):
        self.emit(f"({self._scoped(label)})")

    def write_goto(self, label):
        self.emit(f"// goto {label}", f"@{self._scoped(label)}", "0;JMP")

    def write_if(self, label):
        self.emit(f"// if-goto {label}", "@SP", "AM=M-1", "D=M",
                  f"@{self._scoped(label)}", "D;JNE")

    # ---------- 函式 ----------
    def write_function(self, name, n_vars):
        self.func = name
        self.emit(f"// function {name} {n_vars}", f"({name})")
        for _ in range(int(n_vars)):
            self.emit("@SP", "A=M", "M=0", "@SP", "M=M+1")

    def write_call(self, name, n_args):
        n_args = int(n_args)
        ret = f"{self.func or 'Bootstrap'}$ret.{self.call_id}"
        self.call_id += 1
        self.emit(f"// call {name} {n_args}")
        self.emit(f"@{ret}", "D=A")
        self._push_d()
        for seg in ("LCL", "ARG", "THIS", "THAT"):
            self.emit(f"@{seg}", "D=M")
            self._push_d()
        self.emit(
            "@SP", "D=M", f"@{n_args + 5}", "D=D-A", "@ARG", "M=D",  # ARG = SP-n-5
            "@SP", "D=M", "@LCL", "M=D",                              # LCL = SP
            f"@{name}", "0;JMP",
            f"({ret})",
        )

    def write_return(self):
        self.emit(
            "// return",
            "@LCL", "D=M", "@R13", "M=D",             # FRAME = LCL
            "@5", "A=D-A", "D=M", "@R14", "M=D",      # RET = *(FRAME-5)
            "@SP", "AM=M-1", "D=M", "@ARG", "A=M", "M=D",  # *ARG = pop()
            "@ARG", "D=M+1", "@SP", "M=D",            # SP = ARG+1
        )
        for seg in ("THAT", "THIS", "ARG", "LCL"):
            self.emit("@R13", "AM=M-1", "D=M", f"@{seg}", "M=D")
        self.emit("@R14", "A=M", "0;JMP")


def translate_file(parser, writer):
    for cmd in parser:
        op = cmd[0]
        if op in ARITH_BINARY or op in ARITH_UNARY or op in COMPARE:
            writer.write_arithmetic(op)
        elif op in ("push", "pop"):
            writer.write_push_pop(op, cmd[1], cmd[2])
        elif op == "label":
            writer.write_label(cmd[1])
        elif op == "goto":
            writer.write_goto(cmd[1])
        elif op == "if-goto":
            writer.write_if(cmd[1])
        elif op == "function":
            writer.write_function(cmd[1], cmd[2])
        elif op == "call":
            writer.write_call(cmd[1], cmd[2])
        elif op == "return":
            writer.write_return()
        else:
            raise ValueError(f"Unknown VM command: {' '.join(cmd)}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <file.vm | directory>")
        sys.exit(1)

    target = os.path.abspath(sys.argv[1])
    if os.path.isdir(target):
        files = sorted(
            os.path.join(target, f) for f in os.listdir(target) if f.endswith(".vm")
        )
        out_path = os.path.join(target, os.path.basename(target) + ".asm")
        bootstrap = len(files) > 1  # 作業規定：多個 .vm 檔才寫 bootstrap
    else:
        files = [target]
        out_path = os.path.splitext(target)[0] + ".asm"
        bootstrap = False

    if not files:
        print("No .vm files found.")
        sys.exit(1)

    writer = CodeWriter(out_path, bootstrap)
    for path in files:
        writer.set_file_name(os.path.splitext(os.path.basename(path))[0])
        translate_file(Parser(path), writer)
    writer.close()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()