# Nand2Tetris Jack Compiler（Project 11）

以 Python 3 標準函式庫實作的 Jack 語言編譯器，把 `.jack` 原始碼編譯成 VM 碼（`.vm`），再由 Nand2Tetris 的 VM 模擬器執行。不需要安裝任何套件。

## 檔案結構

```
11/
├── JackCompiler.py   # 編譯器（單一檔案）
├── README.md
├── Seven/            # 測試程式（.jack 為原始碼，.vm 為編譯結果）
├── ConvertToBin/
├── Square/
├── Average/
├── Pong/
└── ComplexArrays/
```

## 使用方式

```
python JackCompiler.py <檔案.jack | 資料夾>
```

範例（在 `11` 資料夾執行）：

```
python JackCompiler.py Seven
python JackCompiler.py ConvertToBin
python JackCompiler.py Square
python JackCompiler.py Average
python JackCompiler.py Pong
python JackCompiler.py ComplexArrays
```

輸入資料夾時，會為裡面每個 `.jack` 檔在同一處產生同名的 `.vm` 檔。

一次編譯全部（PowerShell）：

```powershell
Get-ChildItem -Directory | ForEach-Object { python JackCompiler.py $_.FullName }
```

## 測試方式

1. 用編譯器產生測試資料夾的 `.vm`。
2. 開啟 `tools\VMEmulator.bat`。
3. File → Load Program，選擇**整個測試資料夾**。
4. 出現「No implementation was found for some functions」的提示時選 **Yes**，使用模擬器內建的 OS 函式。
5. Animate 選 `No animation`，按 Run，依下表檢查結果。

| 測試程式 | 測試內容 | 驗證方式 |
|----------|----------|----------|
| Seven | 算術運算式、`do`、`return` | 螢幕左上角顯示 7 |
| ConvertToBin | 函式、`if` / `while` / `let` / `do` / `return` | 在 RAM[8000] 輸入數值，檢查 RAM[8001]–RAM[8016] 為正確位元，且沒有 -1 |
| Square | constructor、method、field、方法呼叫 | 方向鍵移動方塊，`z` / `x` 縮放，`q` 離開 |
| Average | 陣列、字串 | 依畫面提示輸入數字，檢查平均值 |
| Pong | 物件、static 變數 | 玩遊戲並得分，確認分數顯示 |
| ComplexArrays | 複雜陣列運算式 | 預期值與實際值一致 |