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

每日任務更新公開 repo `Jiang-Yude/elon-musk-live-skill` 的 live-data。

1. 由 Codex App 自動化使用 repo 的本機絕對路徑執行每日更新腳本。公開 repo 文件不寫入本機絕對路徑，避免把個人環境路徑推上 GitHub。

   ```bash
   bash scripts/run_daily_update.sh
   ```

2. 讀取 `references/source-config.json`。
3. 抓取 RSS 新聞與評論，標記為 `news_report` 或 `news_commentary`。
4. 嘗試讀取 `@elonmusk` 公開 X 個人頁 7 天內可見貼文，標記為 `musk_direct_public_web`。
5. 若環境變數 `X_BEARER_TOKEN` 存在，額外抓取 `@elonmusk` X API，標記為 `musk_direct`。
6. 用 `references/live-data/state/seen-ids.json` 去重。
7. 寫入當日 JSONL 原始資料：`references/live-data/raw/YYYY-MM-DD.jsonl`。
8. 產出每日 Markdown 摘要：`references/live-data/daily/YYYY-MM-DD daily-digest.md`。
9. 確認 digest 開頭有「來源說明」免責句，提醒讀者新聞與評論只是參考，不代表 Elon Musk 本人立場，也不代表本技能包作者立場。
10. 記錄錯誤到 `references/live-data/logs/`。
11. 若 `raw/` 或 `daily/` 有新變更，push 前先做敏感掃描，確認沒有 token、API key、密碼、email、本機絕對路徑或任何像個資／登入憑證的字串，再 commit 並 push 到 `origin main`。

## 每日更新不做什麼

- 不自動改 `SKILL.md`
- 不自動宣稱人格改變
- 不在每日任務內做 promotion
- 不發文
- 不留言
- 不抓登入牆或付費牆內容
- 不把 API token 寫進檔案
- 不把新聞報導或評論寫成 Elon Musk 本人立場
- 不對新聞做價值判斷；新聞只作為提醒與參考，重要性需人工審核

## 排程

Codex App 內建自動化：

- 名稱：`AI 每日馬斯克技能包更新`
- id：`ai-4`
- 位置：Codex App 左側「自動化」清單

預設每天台灣時間早上執行一次。實際時間以 Codex App 自動化設定為準。

自動化指令要求回報：

- 新增項目數
- 來源類型分布：`musk_direct` / `company_primary` / `news_report` / `news_commentary`
- digest 熱門候選前三則
- 若 `musk_direct` 為 0，明寫「今日無本人直接內容，全為媒體」
- 錯誤或略過來源
- 本次是否有 push

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

每日任務若覺得某筆資料重要，也只能寫一則更新候選到 `references/live-data/review-queue/`；promotion 等人工跨模型補審，不在每日任務做。
