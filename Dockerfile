# 使用官方的 Python 映像檔作為基礎
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個應用程式程式碼
COPY InvestmentDashboard/ InvestmentDashboard/

# 暴露應用程式運行的埠
EXPOSE 5001

# 定義啟動命令
# 將 CMD 改為 shell 形式，以正確處理環境變數的替換
CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-5001} InvestmentDashboard.api:app