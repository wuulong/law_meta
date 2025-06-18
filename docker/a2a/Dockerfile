# Dockerfile (uv version)

# 1. 使用官方 Python slim 映像作為基礎
# 這是我們的工作環境，擁有穩定的 glibc 和 Python
FROM python:3.12-slim-bookworm

# 2. 設定工作目錄
WORKDIR /app

# 3. 複製依賴性檔案
COPY requirements.txt .
COPY nvm_install.sh . 
COPY a2k.sh . 

# 4. 安裝 uv 並使用它來安裝 Python 依賴
# 我們將所有步驟合併在一個 RUN 指令中，以減少映像層數
RUN apt-get update && \
    # 安裝 curl，以便下載 uv 安裝腳本
    apt-get install -y curl && \
    # 使用官方安裝腳本安裝 uv
    curl -LsSf https://astral.sh/uv/install.sh | bash && \
    # 使用 uv 安裝 requirements.txt 中的套件。
    # - /root/.cargo/bin/uv 是 uv 的預設安裝路徑 (在 root 使用者下)
    # - "pip install" 是 uv 的子命令，用來模擬 pip 的行為
    # - "--system" 指示 uv 將套件安裝到全域的 site-packages，這在 Docker 中是常見做法
    # - "--no-cache" 避免留下快取，以減小映像大小
    /root/.local/bin/uv pip install --no-cache --system -r requirements.txt && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && \
    # 清理工作：移除 curl 和 apt 快取，保持映像乾淨
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 5. 複製應用程式程式碼
COPY ./app/adk_agents .

RUN /root/.local/bin/uv venv &&\
/root/.local/bin/uv pip install google-adk && \
chmod +x ./nvm_install.sh && \
chmod +x ./a2k.sh && \ 
./nvm_install.sh

# 6. 設定容器啟動時執行的命令
CMD ["/bin/bash", "./a2k.sh"]
