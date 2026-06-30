# SVD Image Compression Platform

SVD Image Compression Platform 是一個以線性代數為核心的圖像壓縮平台。系統將使用者上傳的圖片轉換為灰階像素矩陣，透過奇異值分解（Singular Value Decomposition, SVD）取得主要影像成分，並以不同 rank 重建壓縮後的圖片。使用者可以比較原圖與不同壓縮程度的結果，觀察保留奇異值數量、壓縮率與重建誤差之間的關係。

本專案的目的不是建立大型影像辨識模型，而是以可視化方式呈現線性代數如何應用於真實圖像資料。相較於分類任務，圖像壓縮的輸出較穩定，且能直接對應到矩陣分解、低秩近似與誤差分析等課程概念。

## 題目調整與取捨

在本專案定題過程中，曾考慮延續圖像辨識方向，包含以 PCA 或 Eigenface 概念進行手寫數字辨識。然而，實際的圖像分類任務通常需要足夠規模的標記資料集、模型訓練、前處理策略、驗證集與準確率評估。若僅以少量模板或簡化的 PCA 距離進行分類，系統容易受到拍攝角度、光線、紙張陰影、筆畫粗細與字形差異影響，辨識結果不穩定。

因此，手寫數字辨識題目最後未作為主題。此調整並非否定機器學習方向，而是基於專案目標與展示重點的取捨：本專案希望將焦點放在線性代數本身，而非資料集訓練與模型調參。SVD 圖像壓縮能更直接地展示矩陣分解與低秩近似，且成果可由原圖與壓縮圖的視覺差異清楚呈現。

此專案也延續前一個主題所強調的完整應用流程：包含可操作的使用介面、資料紀錄、結果查詢與明確的 README 說明，使作品不只停留在單一程式片段，而是形成一個可展示、可測試、可說明的完整平台。

## 專案目標

本專案欲展示以下問題：一張圖片是否可以用較少的矩陣資訊近似重建，並在壓縮率與影像品質之間取得平衡。

系統將圖片視為矩陣 A，進行 SVD 分解：

    A = U Sigma V^T

接著只保留前 k 個最大的奇異值，重建低秩近似矩陣：

    A_k = U_k Sigma_k V_k^T

當 k 較小時，資料量較少，圖片會較模糊；當 k 較大時，圖片較接近原圖，但壓縮率較低。

## 功能

- Flask 網頁平台，內建 operator 與 admin 兩種登入角色
- 上傳 PNG、JPG、PPM 圖片
- 將圖片轉為灰階像素矩陣
- 使用 SVD 進行矩陣分解
- 產生多個 rank 的壓縮圖片版本
- 顯示原圖、壓縮圖、壓縮率、品質分數、RMSE 與保留能量比例
- 儲存每次壓縮紀錄到 JSON
- 查詢歷史壓縮紀錄
- 後台統計總紀錄數、平均品質、平均壓縮比例與平均誤差
- 提供「查看線性代數邏輯」頁面，說明 SVD 分解與低秩重建公式
- 保留 terminal menu，可用 main.py 執行 CLI 版

## 使用技術

- Python
- Flask
- HTML / CSS
- Pillow
- NumPy
- JSON
- dataclass
- unittest
- Linear Algebra
- Singular Value Decomposition
- Low-rank Approximation
- Git / GitHub

## 專案結構

    svd-image-compression-platform/
      app.py
      main.py
      demo_all_features.py
      pyproject.toml
      requirements.txt
      README.md
      sample_images/
        sample-gradient.png
      static/
        sample-preview.png
        styles.css
      templates/
        admin.html
        analyze.html
        base.html
        dashboard.html
        login.html
        math_detail.html
        record_detail.html
        records.html
      src/
        compression_platform/
          __init__.py
          cli.py
          compression.py
          platform.py
          records.py
          users.py
          web.py
      tests/
        test_compression.py
        test_platform.py
        test_records.py
        test_web.py
      data/
        records.json
      uploads/
        .gitkeep

## 核心流程

    uploaded image
      -> convert to grayscale matrix A
      -> resize for stable processing
      -> compute SVD: A = U Sigma V^T
      -> keep top-k singular values
      -> reconstruct A_k = U_k Sigma_k V_k^T
      -> save compressed image variants
      -> compute compression ratio, RMSE, quality score
      -> store compression record

## 線性代數說明

SVD 可以將任意矩陣拆成三個部分：U、Sigma 與 V^T。其中 Sigma 的對角線元素稱為奇異值，代表不同方向所保留的資料能量。奇異值通常由大到小排列，因此前幾個奇異值通常能保留圖片中最主要的結構。

若只保留前 k 個奇異值，就得到 rank-k approximation。這種低秩近似可以用較少的資料重建原始圖片，是圖像壓縮與資料降維中常見的線性代數應用。

本平台會同時顯示：

- Rank k：保留的奇異值數量
- Compression ratio：相對於原矩陣節省的資料比例
- RMSE：原圖與重建圖之間的均方根誤差
- Retained energy：前 k 個奇異值保留的能量比例

## 環境需求

本專案以 Python 建置，主要套件如下：

- Flask：建立網頁平台與路由
- Pillow：讀取與轉換圖片
- NumPy：執行矩陣運算與 SVD 分解
- unittest：驗證核心功能與網頁流程

建議使用 Python 3.10 以上版本執行。

## 執行方式

建立虛擬環境：

    python -m venv .venv

安裝專案套件：

    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

啟動 Flask 網頁平台：

    .\.venv\Scripts\python.exe app.py

啟動後開啟瀏覽器：

    http://127.0.0.1:5000

測試帳號：

    operator / operator123
    admin / admin123

## 使用流程

1. 登入平台。
2. 進入 Compress 頁面。
3. 上傳 PNG、JPG 或 PPM 圖片，或直接使用內建範例圖片。
4. 系統將圖片轉為灰階矩陣並執行 SVD。
5. 結果頁顯示不同 rank 的壓縮版本。
6. 使用者可比較壓縮率、品質分數、RMSE 與保留能量比例。
7. 點選「查看線性代數邏輯」可檢視 SVD 公式、奇異值與 rank-k 重建說明。

## Terminal 版本

除了網頁版之外，專案也保留 terminal menu 操作方式：

    .\.venv\Scripts\python.exe main.py

此版本可在終端機中執行圖片壓縮、查詢紀錄與查看 SVD 細節，作為網頁版之外的輔助展示。

## 測試方式

執行全部測試：

    .\.venv\Scripts\python.exe -m unittest discover -s tests

測試項目包含：

- SVD 壓縮是否能產生多個 rank 版本
- 壓縮結果是否包含壓縮率、品質分數、RMSE 與保留能量比例
- 平台是否能建立並儲存壓縮紀錄
- JSON 紀錄與後台統計是否正確
- Flask 登入頁與 operator 登入流程是否正常

也可以執行完整功能 demo：

    .\.venv\Scripts\python.exe demo_all_features.py

若流程正常，終端機會輸出：

    ALL FEATURES PASSED

## 專案成果

本專案完成了一個可操作的線性代數應用平台，而非單純的公式展示。使用者能透過上傳圖片直接觀察 SVD 壓縮效果，並從不同 rank 的重建圖片理解低秩近似的意義。

本專案展示了以下重點：

- 如何將圖片轉換為矩陣資料
- 如何使用 SVD 分解矩陣
- 如何透過保留前 k 個奇異值進行低秩近似
- 如何比較壓縮率與影像品質
- 如何將線性代數方法包裝成可操作的網頁平台
- 如何保存分析紀錄並提供後台統計

## 未來改進方向

- 加入彩色圖片 RGB 三通道 SVD 壓縮
- 新增可調整 rank 的互動式 slider
- 提供壓縮圖片下載功能
- 顯示奇異值能量曲線圖
- 比較原始圖片檔案大小與 SVD 儲存估計
- 將 JSON 紀錄改為 SQLite 資料庫
- 加入更多測試圖片以比較不同影像類型的壓縮效果
