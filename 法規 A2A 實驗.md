# 主歷程
- 法規 MCP 實驗
- 升級到 A2A 並包成 docker compose
- 進行中：整合法規小工具與摘要、關鍵字

# 目前成果
- A2A 實驗版1 - docker compose
	- 連線： http://211.73.81.235:30304/
		- 目前資料有本 repo 內的範例資料
	- [docker compose setting](https://github.com/wuulong/law_meta/tree/main/docker)
		- 可以自己安裝、內含 DB schema, 範例資料與相關運作程式
	- 在 .env 中指定 POSTGRES_PORT(30199),POSTGRES_PASSWORD(LN3F5E8iGs67HDRlZWOehT0yJ2a4m19k)
		- [agent.py](http://agent.py) 也是取用環境變數(+ POSTGRES_HOST 用 hostname 指向db)
	- 測試 prompt: 政府採購法第三條條文是什麼
		- 可以看到回覆： 政府採購法第三條條文是「政府機關、公立學校、公營事業（以下簡稱機關）辦理採購，依本法之規定；本法未規定者，適用其他法律之規定。」
	- 提問時，請限定範圍在目前 repo 內有提供的法規


# 簡單說明

## 緣起
- 評估法律 MCP 是否該以一般性 DB MCP 做為基礎。
- 用 postgresql mcp 測試是否能夠真實解決目前法律資料分析的難點。

## 相關連結
- [sqlite MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres)
- 找合適的 [postgresql mcp](http://github.com/modelcontextprotocol/servers/tree/main/src/postgres)
	- Tool Name: query, Description: Run a read-only SQL query
- 用 [zeabur 安裝 postgresql](https://zeabur.com/templates/B20CX0) 供測試。


## DB 相關文件
- 由 data spec 生出 db schema: [law_db_law.sql](https://github.com/wuulong/law_meta/blob/main/law_db_law.sql)
- 修改既有程式，升級成 db enable，順便灌入資料: [law_meta](https://github.com/wuulong/law_meta/tree/feat/postgres-metadata-integration)
	- {補充當時穩定版 tag}
- 目前 db_dump: [law_meta_backup.sql](https://github.com/wuulong/law_meta/blob/main/law_meta_backup.sql)

## 測試效果
 - 請參考 [AIQA-法規 A2A 實驗](./AIQA-法規%20A2A%20實驗.md)
