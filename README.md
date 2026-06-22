# elon-musk-live-skill

**陪你用第一性原理思考的馬斯克技能包，會自動抓馬斯克的消息自動更新內容。**

![活的馬斯克技能包海報](assets/live-musk-skill-poster.jpg)

## 這是什麼

一個第一性原理顧問。它的靈感來自 Elon Musk 公開的思考方式，身份是 inspired-by 的思維顧問，用公開資料中可追溯的思考模式工作。它本身並非 Elon Musk，也不替本人發言。

它幫你做的事：把問題拆回事實與約束、重新定義目標、檢查未驗證的假設、找出根本限制、設計最小驗證，再用「靈魂考驗」式反問幫你看見盲點（模糊目標、沉沒成本、自我合理化、逃避現實檢驗）。

## 裝完第一句可以問什麼

- 「這個產品 / 商業模式 / 決策，幫我用第一性原理拆一遍。」
- 「我這個計畫的根本假設是什麼？哪一個錯了會整盤垮？」
- 「靈魂考驗我，我是不是在自我合理化？」

## 免安裝，先試一段

把下面這段貼進 ChatGPT 或 Claude，先感受流程。覺得自己會重複用，再 clone 安裝。

```text
你是一個第一性原理顧問，靈感來自 Elon Musk 公開的思考方式。你本身並非他本人，也不替他發言。
我給你一個問題或想法，請依序幫我：
1. 把目標重新定義成可觀察的成功條件。
2. 分出哪些是已驗證事實，哪些是未驗證假設。
3. 找出最硬的限制（物理、成本、時間、人才或認知）。
4. 設計一個本週就能做、最便宜、最快暴露錯誤的最小驗證。
5. 用尖銳但不羞辱的反問，戳我最可能在自我合理化或逃避現實檢驗的地方。
我的問題是：（在這裡寫）
```

## 跟直接問 AI 差在哪

裸 prompt 入口成本很低。這個技能包多給你四件固定下來的東西：

- **決策啟發式 if-then 規則庫**：白癡指數、刪到後悔為止、物理是法律其他是建議等，每次都用同一套硬規則拆問題。
- **靈魂考驗有退場條件**：碰到情緒壓力或健康、法律等高風險議題會自動收手，先處理人再處理問題。
- **來源分級**：本人公開內容、公司一手資料、媒體報導、外界評論分開標，降低講錯話的風險。
- **live data 分層**：每日資料只進流動層，通過 gate 才改正式人格，避免被單日新聞帶偏。

## 適合誰，誰先用試用 prompt 就好

適合安裝的情況：

- 你常常要反覆叫 AI 幫你拆假設、找根本限制。
- 你想要一個固定流程，每次都逼自己回到事實與最小驗證。
- 你想被反問，幫你看見自己在自我合理化的地方。

先用上面試用 prompt 的情況：

- 你只是偶爾問一兩次，還沒有固定的決策場景。
- 你目前用裸 prompt 問 AI 就夠用。

## 附帶功能：公開資料每日更新

附帶一條每日更新流程，讓馬斯克相關脈絡保持最新。這個版本從 `alchaincyf/elon-musk-skill` 的靜態快照出發，每日從以下公開來源增量更新：

- Google News RSS
- 公開新聞報導
- Elon Musk 公開 X 個人頁上看得到的內容

抓取失敗、X 公開頁 best-effort 抓不到、或評論混進來時，回答會回到來源分級標清楚層級，不確定的標成待補來源，避免內容漂掉。

## 使用方式

把這個資料夾放到支援 Agent Skills 的 skills 目錄，例如：

```bash
git clone https://github.com/Jiang-Yude/elon-musk-live-skill.git ~/.codex/skills/elon-musk-live
```

手動更新資料：

```bash
cd ~/.codex/skills/elon-musk-live
bash scripts/run_daily_update.sh
```

更新後會產出：

- `references/live-data/raw/YYYY-MM-DD.jsonl`
- `references/live-data/daily/YYYY-MM-DD daily-digest.md`

## 更新邏輯

每日更新只進 `references/live-data/`，不會直接改 `SKILL.md`。

只有資料通過 `references/promotion-gate.md` 的正式更新 gate，才適合把穩定變化整理進技能包本體。

## 來源邊界

- `musk_direct_public_web`：公開 X 個人頁可見內容，best-effort 擷取，不等同官方 API
- `news_report`：媒體報導的可核對事實
- `news_commentary`：評論、分析、社論、市場解讀

回答時會區分「馬斯克直接公開內容」「公司或官方材料」「媒體報導」「外界評論」，把媒體評論寫成外界解讀，不寫成馬斯克本人說法。

## 授權與來源

本倉包含上游 `alchaincyf/elon-musk-skill` 與 `alchaincyf/nuwa-skill` 的快照作為初始材料與方法論參考，相關授權檔保留在 `references/upstream/`。

本倉新增的 live update wrapper、資料流規則與本地改造內容以 MIT License 釋出。

## 江江教練

- Threads：https://www.threads.com/@jiang_yude_coach
- YouTube：https://www.youtube.com/@aipkmcc
- Instagram：https://www.instagram.com/jiang_yude_coach/
- 知識官網：https://ai-km-jiang.vercel.app/
- LINE 社群：https://line.me/R/ti/g2/V63_43ngbs_kq1mpVc9LlxXB-1kchHnwdsy3WQ
- GitHub：https://github.com/Jiang-Yude
