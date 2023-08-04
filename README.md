# chatgpt-retrieval-plugin-gui
chatgpt-retrieval-plugin GUI

透過上傳 PDF 檔作為資料庫，回答用戶問題

# Step

1. Clone chatgpt-retrieval-plugin repo

    ```bash
    git clone https://github.com/TingChenChang/chatgpt-retrieval-plugin.git
    ```

2. 在 Docker 啟動 redis-stack-server

    ```bash
    docker run -d --name redis-stack -p 6379:6379 redis/redis-stack-server:latest
    ```

3. Run chatgpt-retrieval-plugin repo

    ```bash
    poetry env use python3.10
    poetry shell
    poetry install

    export DATASTORE=redis
    export BEARER_TOKEN=<your_bearer_token>
    export OPENAI_API_KEY=<your_openai_api_key>
    ```

4. Run chatgpt-retrieval-plugin-gui repo

    ```bash
    pip install -r requirement.txt
    python app.py
    ```

5. GUI

    - Upload - 上傳 pdf 檔作為資料庫

    - Chatbot - 根據資料庫內容，回答用戶問題

    - File System - 管理資料庫檔案
