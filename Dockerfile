# 使用官方的 Python 映像檔作為基礎
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
# 為了利用 Docker 的層快取，先複製 requirements.txt
# 這樣如果只有程式碼變動，而依賴不變，就不需要重新安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個應用程式程式碼
# 包括 InvestmentDashboard 目錄
COPY InvestmentDashboard/ InvestmentDashboard/
# 移除複製 service-account.json 的指令，因為它將透過環境變數提供

# 暴露應用程式運行的埠
EXPOSE 5001

# 定義啟動命令
# 使用 Gunicorn 啟動 Flask 應用程式
# InvestmentDashboard.api:app 指向 InvestmentDashboard/api.py 中的 Flask 應用實例 'app'
# -w 4 表示啟動 4 個 worker 進程，可以根據您的需求調整
# -b 0.0.0.0:5001 表示監聽所有網路介面的 5001 埠
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "InvestmentDashboard.api:app"]