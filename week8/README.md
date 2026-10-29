# IC 設計的 EDA 是什麼？

以 veryl2chip、hack-computer 與康乃爾大學 ECE 5745 課程為例

## 摘要

EDA（Electronic Design Automation，電子設計自動化）是用軟體把「一份硬體描述」逐步變成「可以製造的晶片」的整套工具。現代晶片動輒數十億個電晶體，不可能靠人手畫線，必須由 EDA 完成模擬、合成、佈局、繞線與時序分析。本報告先說明 EDA 的定義與在 IC 設計流程中的角色，再以 veryl2chip 與 hack-computer 兩個網頁版 EDA 為例，說明每個階段實際在做什麼，最後對照康乃爾大學的 ASIC 課程，比較教學用、開源與商用 EDA 的差異。

## 1. EDA 是什麼

IC 設計的核心困難是「抽象層級落差」：設計者想的是「做一顆 CPU」，工廠需要的是「幾何圖形（光罩）」。EDA 就是填補這段落差的軟體，它大致做三件事：

1. **轉換**：把高階描述（Verilog、Veryl 等 HDL）自動轉成邏輯閘、標準單元，再轉成實體座標。
2. **最佳化**：在面積、速度（時序）、功耗之間找平衡。
3. **驗證**：在每一層檢查功能對不對、時序有沒有違規、功耗是否超標。

沒有 EDA，就沒有今天的 IC 產業；EDA 本身也是半導體產業的「守門員」，製程廠、IP 廠與設計公司都依賴它。

## 2. IC 設計流程與 EDA 的對應

| 階段 | 做什麼 | 對應的 EDA 功能 |
|---|---|---|
| ① 規格與 RTL 設計 | 用 HDL 描述電路行為 | HDL 編輯器、語法檢查 |
| ② 功能模擬 | 用測試程式（testbench）驗證行為 | 事件驅動模擬器、波形檢視 |
| ③ 邏輯合成 | 把 RTL 轉成邏輯閘網表（netlist），並化簡邏輯 | 邏輯合成器（RTL→Logic、Tech-independent 最佳化） |
| ④ 技術映射 | 把通用閘對應到實際元件：FPGA 的 LUT，或 ASIC 的標準單元 | Techmap、標準單元庫 |
| ⑤ 佈局（Placement） | 決定每個元件放在晶片的哪個位置 | 佈局器（常用模擬退火等演算法） |
| ⑥ 時脈樹與繞線 | 把時脈送到每個暫存器，並把元件之間連線 | CTS、全域／細部繞線 |
| ⑦ 靜態時序分析（STA） | 檢查所有路徑能否在目標頻率下運作 | STA 引擎 |
| ⑧ 功耗與 IR Drop | 估計功耗與電源網路壓降 | 功耗分析、電源完整性 |
| ⑨ 簽核與下線 | 設計規則檢查後輸出 GDSII 交給晶圓廠 | DRC/LVS、tape-out |

其中 ① 到 ④ 常合稱「前端」，⑤ 到 ⑨ 稱「後端」或「實體設計」。康乃爾 ECE 5745 課程的講義也是照這個脈絡編排，包含 Topic 5「自動化設計方法」、Topic 12「合成演算法」與 Topic 13「實體設計自動化演算法」。

## 3. EDA 背後的核心演算法

- **邏輯最佳化**：布林函數化簡、共用子電路，目標是用更少的閘做同樣的事。
- **技術映射**：把電路圖切成小塊，對應到庫裡成本最低的元件組合。
- **佈局**：本質是大規模組合最佳化問題，常用模擬退火（simulated annealing）或解析式佈局，目標是縮短線長、避免擁擠。
- **繞線**：在多層金屬上找不衝突的路徑，類似巨大的迷宮問題。
- **靜態時序分析**：把電路視為有向圖，沿最長路徑累加延遲，不必跑模擬就能檢查所有路徑。

這些問題大多是 NP-hard，所以 EDA 的價值不只是自動化，更在於「用啟發式演算法在合理時間內找到夠好的解」。

## 4. 工具實作與觀察

### 4.1 veryl2chip：AI 自製的 Veryl EDA

veryl2chip 是針對 Veryl HDL 的 EDA，全部以 Rust 撰寫，並編譯成 WebAssembly 在瀏覽器執行，不需安裝。依其 README，內容包含：

- **veryl-sim**：事件驅動模擬器，支援 testbench、`$assert` 與 VCD 波形。
- **veryl-eda**：合成成閘級網表、iCE40 FPGA 映射、自製佈局繞線與位元流（bitstream），以及 ASIC 後端（標準單元、佈局、繞線、時序）。
- **網頁介面**：合成流程分為共同階段 ① RTL→Logic、② Logic Netlist、③ Tech-indep Syn；FPGA 路線接 ④ LUT4 Techmap、⑤ Placement（有退火動畫）、⑥ 繞線、⑦ 時序；ASIC 路線則是 ④ 標準單元映射、⑤ Row Placement、⑥ CTS＋全域繞線、⑦ 細部繞線、⑧ 時序、⑨ 功耗與 IR Drop。
- **FPGA vs ASIC 比較**：把兩種實作的面積、線長、最高頻率、能耗並排比較。
- **可驗證性**：據 README 描述，FPGA 產出的 `.bin` 與官方 icepack 位元組一致，可用 iceprog 燒錄到真實 iCE40 開發板。

這個專案最有教育價值的地方，是把原本黑盒子的 EDA 流程「畫出來」：每個階段都有報告與可縮放的圖，能直接看到佈局如何由亂變整齊、繞線如何展開。

### 4.2 hack-computer：Nand2Tetris 的 JavaScript 全工具鏈

hack-computer 以 JavaScript 實作 Nand2Tetris 的整條工具鏈（HDL、組譯器、VM、Jack 編譯器），並加上 RISC-V 後端與一顆用 HDL 寫成的單週期 RV32I 處理器。依其 README，`hdl.html` 除了 HDL 批次模擬與電路圖檢視（可逐層點入子元件，一路看到 Nand 與 DFF），還有「合成 LUT」功能，提供 FPGA／ASIC 雙後端的迷你 EDA 流程，階段同樣是 RTL→Logic、Logic Netlist、Tech-independent 合成、Techmap、Placement、Routing 與 STA。

README 提到一個很直觀的例子：以 Inc16 為例，合成前的化簡可把閘數從 384 降到 224。這正是邏輯最佳化的價值，同一個功能，EDA 可以用更少的硬體實現。

### 4.3 康乃爾大學 ECE 5745：業界流程的教學版

康乃爾的 Complex Digital ASIC Design 課程使用 Verilog RTL，並在 Tutorial 4 與 Section 1–3 教授 Synopsys／Cadence 的 ASIC 前端、後端與自動化流程；Section 7 另有開源的 OpenLANE 流程。課程實驗（如管線化整數乘法器、排序加速器）要求學生從 RTL 一路做到實體設計並分析面積、時序與功耗，是最接近業界實務的一條路。

### 4.4 三者比較

| 項目 | veryl2chip | hack-computer | 康乃爾 ECE 5745 |
|---|---|---|---|
| 輸入語言 | Veryl | Nand2Tetris HDL | Verilog |
| 執行環境 | 瀏覽器（WASM） | 瀏覽器／Node.js | 校內 Linux 伺服器＋商用／開源工具 |
| 重點 | 完整 FPGA/ASIC 流程視覺化 | 從 Nand 到 CPU 的整體理解 | 業界等級 ASIC 設計 |
| 製程資料 | 簡化標準單元 | 簡化模型 | 真實製程設計套件 |
| 適合用途 | 理解流程原理 | 入門、教學 | 進階實作、研究 |

教學用工具的標準單元庫與延遲模型都經過簡化，因此數字（頻率、功耗）只能用來比較趨勢，不能直接當成真實晶片的預測。

## 5. 商用 EDA 與開源 EDA

- **商用**：Synopsys、Cadence、Siemens EDA 三大廠合計主導市場，工具成熟、與晶圓廠製程深度整合，是先進製程下線的主流選擇，但授權費用高。
- **開源**：Yosys（合成）、OpenROAD／OpenLANE（實體設計）、nextpnr 搭配 icepack 與 iceprog（FPGA 流程）等，讓學生與小團隊也能完成從 RTL 到 GDSII 的流程。
- **教學／研究用**：像 veryl2chip 與 hack-computer 這類輕量工具，目標不是取代前兩者，而是讓人看懂流程。

## 6. AI 與 EDA 的關係

veryl2chip 的簡介標明是「AI 自製」的 EDA，這點本身就值得討論。AI 在 EDA 上有兩條路線：一是用 AI 協助撰寫工具與 RTL，降低開發門檻（veryl2chip 屬於此類）；二是把機器學習放進演算法內部，例如佈局最佳化與參數調校。不過晶片一旦下線就無法像軟體一樣修補，所以 AI 產出的設計仍需要完整的模擬、形式驗證與簽核流程把關。

## 7. 結論

EDA 是 IC 設計不可或缺的基礎建設：它把抽象的 HDL 描述，經由模擬、合成、技術映射、佈局、繞線與時序分析，一步步轉成可製造的晶片，並在每一步驗證結果。從 veryl2chip 與 hack-computer 可以看到，這條流程的原理其實可以被完整實作並視覺化，而康乃爾的課程則展示了業界等級的實務做法。對學習者而言，先用輕量工具理解流程，再用開源或商用工具接觸真實製程，是一條合理的學習路徑。

## 參考資料

1. veryl2chip：https://github.com/ccc-eda/veryl2chip/ ，線上版：https://ccc-eda.github.io/veryl2chip/web/dist/index.html
2. hack-computer：https://github.com/ccc-js/hack-computer ，線上版：https://ccc-js.github.io/hack-computer/dist/hdl.html
3. EDA 電子書：https://github.com/ccc-eda/eda-books/tree/main/book
4. Cornell ECE 5745 Handouts：https://www.csl.cornell.edu/courses/ece5745/handouts.html