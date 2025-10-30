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
# 這裡的 EXPOSE 只是文件性質的，實際監聽的埠由 CMD 決定
EXPOSE 5001

# 定義啟動命令
# 修改 Gunicorn 的綁定埠，使其監聽由 Zeabur 提供的 $PORT 環境變數
# 如果 $PORT 不存在（例如在本地），則預設使用 5001
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT:-5001}", "InvestmentDashboard.api:app"]
