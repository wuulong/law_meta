# law_meta
law metadata framework

# 架構
- 請參考 [法律語法形式化.md](https://github.com/wuulong/law_meta/blob/main/%E6%B3%95%E5%BE%8B%E8%AA%9E%E6%B3%95%E5%BD%A2%E5%BC%8F%E5%8C%96.md)

# 一般
- 版本： 20250313
- Code 版權: MIT
- 資料版權： CC-BY-SA 4.0，作者：哈爸
- 內容：99% 都是 AI （Gemini Flash 2.0 think）的回答
- 緣起： [AIQA-法律語法形式化.pdf](https://drive.google.com/open?id=1v_5KyygdGDIiQRRuC5RpMcKzbdaKPYUQ&usp=drive_copy)
- 構思的過程：
	- 第二次
		- [[AIQA-法律語法形式化-採購法]]
		- 採購法的成果：[[採購法語法形式化 1]]
		- 法規：[政府採購法](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030057) 
	- 第三次
		- [[AIQA-法律語法形式化4]]
		- 採購法的成果：[[採購法語法形式化]]
        - 與上一版差異
	        - 20250310: 根據方法 3.1, 法規時間軸、程序流程圖、法規語意向量、法條規則。法規內關聯性內含
- Code history
    - 20250312: 讀寫 json, 基本支援 LLM 建構 json
    - 20250313: 用 code 產生小架構的法規，增加管理功能
    - 20250314: 加入 query 的一些功能，順便測試一下資料
	- 20250319: 改善 prompt, 生成更正確，加幾個法
- 實作檢視心得
	- 法條規則太多，建議分離成另外一個檔案
	- 法條時間軸，用另外檔案，因為資料來源也不同。留著只是多個空欄位
	- 產生的 json, 還是有固定型態的語法錯誤。如該是陣列的卻只有一筆，格式不對。可能可以寫一些檢查的 code
# 法規 md 製作技巧
- 到法規資料庫，以下都是手動複製到文字 md 檔，建議順序
	- 概要
	- 條文
	- 沿革
# 手動使用技巧
- 使用 AI studio 選用 Gemini 2.0 Flash Think 01-21 模型
- 開新 chat
	- system prompt: 請以台灣人的立場，用繁體中文回答

## 使用
- 放入需要的 法規與相關的 json 檔案
	- 可先下載預先產製好的
		- 民法
		- 中華民國憲法(合併增修條文)
		- 政府採購法施行細則
		- 憲法增修條文(合併憲法)
		- 中華民國刑法
		- 政府採購法
		- 行政程序法
		- 預算法
- 開始問

## 製作法規 json 技巧
- 放入
	- 法律語法形式化.md
	- 放入要製作那個法規的 md

- prompt template:
	- 根據[法規名稱]的整體資訊，按照法律語法形式化的設計，依照裡面範例格式，產生法規 Meta Data
		- 法律概念 Meta Data
		- 法規階層關係 Meta Data
		- 法規關聯性 Meta Data
	- 根據[法規名稱]的整體資訊，請給我裡面章節的資訊，需含條號範圍
	- 根據[法規名稱]的整體資訊，按照法律語法形式化的設計，依照裡面範例格式，產生逐條建立[法條 Meta Data]
- 紀錄產出文字，手動複製出 json 內容
- 遇中斷時可使用以下 prompt
	- 前面產生時發生中斷，請重新產生第九十六條到第114條的 Meta Data
	- 前面產生時發生中斷，請產生第一百十二條
- 編輯時刪除上一次的最後一個不完整法條

# 自動產製 json 

- 使用 law_meta_loader.ipynb
- 放入要製作那個法規的 md
- 一點手動開關與執行，產製出 json

# 使用 meta data做自動化分析
- law_meta_loader.ipynb 內開始提供一些範例，請參考