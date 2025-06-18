# 使用官方 PostgreSQL 映像檔作為基礎
# 建議使用特定版本，例如 postgres:14-alpine 或 postgres:15-alpine
FROM postgres:17.5-alpine

# 將導出的 SQL 腳本複製到容器的 /docker-entrypoint-initdb.d/ 目錄
# 這個目錄下的所有 .sql 檔案會在資料庫首次啟動時自動執行
COPY globals.sql /docker-entrypoint-initdb.d/
#COPY zeabur.sql /docker-entrypoint-initdb.d/
# 如果有其他資料庫，也依此類推
# COPY another_db.sql /docker-entrypoint-initdb.d/

# 設定預設的 PostgreSQL 數據目錄 (這個是 postgres 官方映像檔的預設)
# ENV PGDATA=/var/lib/postgresql/data

# 這裡不需要額外的 CMD，因為基礎映像檔已經有預設的啟動命令
# 它的 entrypoint 會處理 /docker-entrypoint-initdb.d/ 中的 SQL 檔案
