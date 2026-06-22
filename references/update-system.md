# 自動更新系統

## 目標

建立每日增量更新流程，讓馬斯克技能包維持最新公開脈絡，同時避免短期新聞噪音污染正式 `SKILL.md`。

## 資料流

```text
公開來源
  -> scripts/update_live_data.py
  -> references/live-data/raw/YYYY-MM-DD.jsonl
  -> references/live-data/daily/YYYY-MM-DD daily-digest.md
  -> references/live-data/review-queue/
  -> weekly review
  -> 通過 gate 才更新 SKILL.md
```

## 每日更新做什麼

1. 讀取 `references/source-config.json`
2. 抓取 RSS 新聞與評論
3. 嘗試讀取 `@elonmusk` 公開 X 個人頁 7 天內可見貼文，標記為 `musk_direct_public_web`
4. 若環境變數 `X_BEARER_TOKEN` 存在，額外抓取 `@elonmusk` X API
5. 用 `state/seen-ids.json` 去重
6. 寫入當日 JSONL 原始資料
7. 產出每日 Markdown 摘要
8. 記錄錯誤到 `logs/`

## 每日更新不做什麼

- 不自動改 `SKILL.md`
- 不自動宣稱人格改變
- 不發文
- 不留言
- 不抓登入牆或付費牆內容
- 不把 API token 寫進檔案

## 排程

Codex App 內建自動化：

- 名稱：`AI 每日馬斯克技能包更新`
- id：`ai-4`
- 位置：Codex App 左側「自動化」清單

預設每天台灣時間 08:30 執行一次。

## 失敗處理

- RSS 抓取失敗：記錄錯誤，其他來源繼續
- 公開 X 頁面抓不到：記錄為 skipped，不視為失敗
- X token 不存在：官方 API 記錄為 skipped，不視為失敗
- X API 失敗：記錄 HTTP 狀態，不重試暴衝
- 寫檔失敗：整體退出非 0，讓 Codex App 自動化執行紀錄留痕

## Secret 處理

`X_BEARER_TOKEN` 是選配，不進對話、不進檔案。

目前不要求 token。若之後要提高 X 貼文抓取穩定度，再用 Keychain 或 hidden input 設定，讓 wrapper script 讀取。

## 人工審查節奏

每週讀最近 7 份 daily digest，依 `promotion-gate.md` 判斷是否產出更新候選。

候選先進 `references/live-data/review-queue/`，等 Claude 或另一模型補審後再改正式 `SKILL.md`。
