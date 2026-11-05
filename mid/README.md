111410555 曹庭瑜

# 每週檢驗表格

| 第幾週 | 習題內容 | 有上課且準時繳交 | 補交且附上請假證明 | 作業連結 |
|--------|----------|------------------|--------------------|----------|
| 3      | 第 1, 2 章 | 是 |  | [01](https://github.com/tingyutsao/_co/tree/main/01), [02](https://github.com/tingyutsao/_co/tree/main/02) |
| 4      | 第3 章除 PC | 是 |  | [03](https://github.com/tingyutsao/_co/tree/main/03) |
| 5      | 第 4 章 | 是 |  | [04](https://github.com/tingyutsao/_co/tree/main/04) |
| 6      | HackCPU 電路圖 | 是 |  | [電路圖](https://github.com/tingyutsao/_co/tree/main/week6) |
| 7      | 第 5 章 | 是 |  | [05](https://github.com/tingyutsao/_co/tree/main/05) |
| 8      | EDA 軟體報告 | 是 |  | [EDA](https://github.com/tingyutsao/_co/tree/main/week8) |

# 期中前作業內容摘要

本專案依照 Nand2Tetris 課程（《The Elements of Computing Systems》，Nisan 與 Schocken），從單一 Nand 閘逐步組裝出完整的 Hack 電腦。期中前完成第 1、2、3（除 PC）、4、5 章的習題，外加 HackCPU 電路圖與一份 EDA 軟體報告。

## 第 3 週：第 1, 2 章（資料夾 01、02）

### 01 — 布林邏輯

全部由 Nand 閘出發，逐一建立：

- 基本閘：`Not`、`And`、`Or`、`Xor`
- 選擇／解多路：`Mux`、`DMux`
- 16 位元版本：`Not16`、`And16`、`Or16`、`Mux16`
- 多通道版本：`Or8Way`、`Mux4Way16`、`Mux8Way16`、`DMux4Way`、`DMux8Way`

每顆晶片各有一個 `.hdl`（實作）、`.tst`（測試腳本），部分附有 `.cmp` / `.out`（預期與實際輸出比對）。

### 02 — 布林算術

- `HalfAdder`、`FullAdder`：1 位元加法器（FullAdder 由兩個 HalfAdder 加一個 Or 組成）
- `Add16`：以 ripple-carry 架構連出的 16 位元加法器
- `Inc16`：16 位元 +1 增量器
- `ALU`：Hack 算術邏輯單元，具控制位元 `zx, nx, zy, ny, f, no` 與輸出旗標 `zr, ng`

## 第 4 週：第 3 章除 PC（資料夾 03）

分為 `a/`（小型記憶）與 `b/`（大型記憶）兩部分：

- `a/`：`Bit`、`Register`、`RAM8`、`RAM64`（依題意 **PC 不做**，目前僅保留骨架）
- `b/`：`RAM512`、`RAM4K`、`RAM16K`

RAM 是分層疊出來的：較大的 RAM 由八（或四）顆較小的 RAM 組成，用 `DMux` 選擇寫入哪一顆、`Mux` 輸出讀取結果。1 位元的保存用 `Mux` + `DFF` 做成 `Bit`，再擴充成 `Register`。

## 第 5 週：第 4 章 機器語言（資料夾 04）

撰寫兩個 Hack 組合語言程式， Hammer 上機前在組譯器中測試：

- `mult/mult.asm`：用重複加法計算 `R2 = R0 × R1`（迴圈累加 `R2 += R0`，共做 `R1` 次），寫成 `mult.hack`
- `fill/Fill.asm`：無限迴圈偵測鍵盤輸入（`@KBD`），有按鍵時把整個螢幕塗黑，否則清成白色

附有 `Mult.tst`、`Fill.tst`、`FillAutomatic.tst` 等測試腳本與比對檔。

## 第 6 週：HackCPU 電路圖（資料夾 week6）

- [`week6.png`](https://github.com/tingyutsao/_co/tree/main/week6/week6.png)：手繪（軟體繪製）的 Hack CPU 電路圖，包含 A/C 指令解碼、A 與 D 暫存器、ALU 與跳躍邏輯、程式計數器 PC 的架構與連線。

## 第 7 週：第 5 章 電腦架構（資料夾 05）

組出整台 Hack 電腦：

- `Memory.hdl`：完整位址空間 — RAM16K（`0x0000–0x3FFF`）、Screen（`0x4000–0x5FFF`）、Keyboard（`0x6000`）
- `CPU.hdl`：Hack CPU — A/C 指令解碼、A 與 D 暫存器、ALU、跳躍邏輯與程式計數器
- `Computer.hdl`：`ROM32K` + `CPU` + `Memory` 組成的完整電腦

測試程式有 `Add.hack`、`Max.hack`、`Rect.hack`，搭配 `CPU.tst`、`Memory.tst`、`ComputerAdd/Max/Rect.tst`（含 external 版本）等驗證檔，用 CPU 模擬器跑通過。

## 第 8 週：EDA 軟體報告（資料夾 week8）

[`week8/README.md`](https://github.com/tingyutsao/_co/blob/main/week8/README.md) —〈IC 設計的 EDA 是什麼？〉，內容包括：

- EDA 的定義與在 IC 設計流程中的角色（模擬 → 合成 → 技術映射 → 佈局 → 繞線 → STA → 簽核）
- EDA 背後的核心演算法：邏輯最佳化、技術映射、佈局（模擬退火）、繞線、靜態時序分析
- 以 **veryl2chip**（AI 自製的 Veryl EDA，Rust + WebAssembly，FPGA/ASIC 雙後端）與 **hack-computer**（Nand2Tetris 的 JavaScript 全工具鏈）兩個網頁版工具作實例
- 對照康乃爾大學 ECE 5745 ASIC 課程，比較教學用、開源（Yosys、OpenROAD/OpenLANE、nextpnr）與商用（Synopsys、Cadence、Siemens EDA）工具的差異

# 儲存庫結構

```
.
├── README.md
├── mid/    README.md（本檔，期中檢驗清單）
├── 01/     布林邏輯：Not, And, Or, Xor, Mux, DMux 及 16 位元、多通道版本
├── 02/     布林算術：HalfAdder, FullAdder, Add16, Inc16, ALU
├── 03/     記憶：a/ (Bit, Register, RAM8, RAM64)、b/ (RAM512, RAM4K, RAM16K)
├── 04/     機器語言：mult/ 與 fill/ 組合語言程式
├── 05/     電腦架構：CPU, Memory, Computer + Add/Max/Rect.hack
├── week6/  HackCPU 電路圖 (week6.png)
├── week8/  EDA 軟體報告 (README.md)
```

# 如何執行

晶片（`.hdl`）用 Nand2Tetris 硬體模擬器測試，組合語言（`.asm`）用組譯器轉成 `.hack` 後以 CPU 模擬器測試。在模擬器中載入對應的 `.tst` 腳本執行，輸出會與 `.cmp` 檔自動比對。
