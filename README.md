# Investment-Dashboard

## 專案簡介

本專案為「投資商品和策略儀表板」，以 Dash（Python）打造投資基金與資產展示平台，適用於投資顧問、基金公司或個人理財分析。可切換不同投資策略（如全天候、Smart 500）。

---

## 主要特色

- **多策略儀表板**：支援 All Weather、Smart 500 兩大投資策略，快速切換並檢視各自的介紹、資產配置、績效分析。
- **績效分析**：視覺化展現基金累積報酬、與指標比較、月度熱圖、關鍵指標（夏普值、MDD、年化報酬等）。
---

## 安裝與啟動

### 1. 環境需求

- Python 3.7+
- 建議虛擬環境（如 venv）

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 啟動本地伺服器

```bash
python -m InvestmentDashboard.app
```
或
```bash
gunicorn InvestmentDashboard.app:server
```

伺服器啟動後，瀏覽器前往 [http://localhost:8050](http://localhost:8050)

---

## 專案結構

```
Investment-Dashboard/
│
├── InvestmentDashboard/
│   ├── models/               # 模擬基金、股票、債券數據
│   ├── utils/                # 工具模組（如圖表產生、共用小工具等）
│
├── requirements.txt
└── README.md
```

- **models/**：基金、股票、債券數據的資料模型與讀取方法。
- **views/**：各頁面（基金介紹、績效、個股、債券）UI 與圖表元件。
- 其他檔案請參考註解說明。

---

## 主要頁面說明

- **策略主頁**  
  - 基金介紹：理念、流程、資產/產業配置圖
  - 績效分析：累積報酬比較圖、月度熱圖、各項績效指標
---