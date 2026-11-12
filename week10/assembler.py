#!/usr/bin/env python3
"""Hack Assembler (nand2tetris Project 6)
用法: python3 assembler.py Prog.asm   ->  產生同資料夾下的 Prog.hack
"""
import sys
import os

# ---------- 對照表 ----------
COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', '!D': '0001101', '!A': '0110001',
    '-D': '0001111', '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111',
    'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
    'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
    'M': '1110000', '!M': '1110001', '-M': '1110011', 'M+1': '1110111',
    'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111',
    'D&M': '1000000', 'D|M': '1010101',
}
# 交換律的寫法也一併接受
COMP.update({'A+D': COMP['D+A'], 'M+D': COMP['D+M'],
             'A&D': COMP['D&A'], 'M&D': COMP['D&M'],
             'A|D': COMP['D|A'], 'M|D': COMP['D|M']})

JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
        'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}


def dest_bits(d):
    """用字母組合決定 d 位元,自動支援 DM/MD、ADM/AMD 等任意順序。"""
    return ('1' if 'A' in d else '0') + \
           ('1' if 'D' in d else '0') + \
           ('1' if 'M' in d else '0')


def clean(line):
    """移除註解與所有空白。"""
    return ''.join(line.split('//')[0].split())


def assemble(lines):
    symbols = {f'R{i}': i for i in range(16)}
    symbols.update({'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
                    'SCREEN': 16384, 'KBD': 24576})

    # 先清理,留下真正的指令與標籤
    code = [c for c in (clean(l) for l in lines) if c]

    # ---- 第一遍:登記標籤 (LABEL),不產生機器碼 ----
    instructions = []
    for c in code:
        if c.startswith('('):
            symbols[c[1:-1]] = len(instructions)
        else:
            instructions.append(c)

    # ---- 第二遍:逐行翻譯 ----
    out = []
    next_var = 16
    for ins in instructions:
        if ins.startswith('@'):                      # A 指令
            sym = ins[1:]
            if sym.isdigit():
                val = int(sym)
            else:
                if sym not in symbols:               # 新變數
                    symbols[sym] = next_var
                    next_var += 1
                val = symbols[sym]
            out.append(format(val, '016b'))
        else:                                        # C 指令: dest=comp;jump
            dest, jump = '', ''
            comp = ins
            if '=' in comp:
                dest, comp = comp.split('=', 1)
            if ';' in comp:
                comp, jump = comp.split(';', 1)
            out.append('111' + COMP[comp] + dest_bits(dest) + JUMP[jump])
    return out


def main():
    if len(sys.argv) != 2:
        print('用法: python3 assembler.py Prog.asm')
        sys.exit(1)
    src = sys.argv[1]
    with open(src) as f:
        result = assemble(f.readlines())
    dst = os.path.splitext(src)[0] + '.hack'
    with open(dst, 'w') as f:               # 'w' 會覆蓋已存在的檔案
        f.write('\n'.join(result) + '\n')
    print(f'完成: {dst} ({len(result)} 行)')


if __name__ == '__main__':
    main()