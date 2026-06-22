# elon-musk-live-skill

![活的馬斯克技能包海報](assets/live-musk-skill-poster.jpg)

活的馬斯克技能包。這不是馬斯克本人，也不冒充本人發言；它是一個以公開資料為基礎、可每日更新、可追溯、可審核的 inspired-by 思維顧問技能包。

這個版本從 `alchaincyf/elon-musk-skill` 的靜態快照出發，加入每日資料更新流程：

- Google News RSS
- 公開新聞報導
- Elon Musk 公開 X 個人頁上看得到的內容
- 選配 X API；沒有 `X_BEARER_TOKEN` 時會正常 skipped

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

回答時應區分「馬斯克直接公開內容」「公司或官方材料」「媒體報導」「外界評論」，不要把媒體評論寫成馬斯克本人說法。

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
