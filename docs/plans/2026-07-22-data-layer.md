# TwInsight 資料層接通計畫

目標：把資料面從 0 接到「盤後批次能真的灌進資料、API 能真的吐出資料」。

## 設計決定（CEO 已拍板）

1. **不做會員系統** → 不建 `users` 表，`watchlist` / `alert_settings` 不掛 `user_id`。
   之後真要多人再用一支 migration 加回。`auth` 模組暫不實作。
2. **技術指標預先算好存表**，不在查詢時即算 —— P3 選股要對全市場 ~1800 檔跑技術面
   條件，即算會撞到規格書「頁面 <2 秒」的要求。

## 資料表（10 張）

| 表 | 來源 | 用途 |
|---|---|---|
| `stocks` | 證交所 OpenAPI | 股票主檔：代號/名稱/產業/市場別 |
| `daily_prices` | yfinance | 日線 OHLCV → K 線、均線、指標輸入 |
| `technical_indicators` | 自算 (pandas-ta) | MA/RSI/KD/MACD/布林，盤後算好 |
| `institutional_trades` | FinMind | 三大法人買賣超（P2） |
| `margin_trading` | FinMind | 融資融券餘額（P2） |
| `major_holders` | FinMind | 千張大戶持股比率（P2） |
| `valuations` | FinMind | 每日本益比/股價淨值比/殖利率（P1 資訊卡、P3 基本面篩選） |
| `financial_statements` | FinMind | 季度 EPS/營收（P1 資訊卡、P3 EPS 成長率） |
| `screener_results` | 自算 | 每日選股結果（P3） |
| `watchlist` / `alert_settings` | 使用者操作 | 自選股與警示（P4） |
| `job_runs` | 批次自身 | 批次執行紀錄，用於觀測成功/失敗 |

## 外部 client 放哪

新增 `app/providers/` 套件放 4 支外部 client（twse / yfinance / finmind / fugle）。
原本 `app/modules/stocks/provider.py` 移過去 —— 因為 FinMind 同時服務 chips 與
stocks 兩個模組，放在單一模組底下會造成重複。全部用已有的 `httpx`，不新增依賴
（不裝 FinMind/Fugle SDK）。

## 執行順序（每步都可獨立驗證）

1. **models + 首支 migration**：定義 `app/core/models.py`，接上 `alembic/env.py` 的
   `target_metadata`，跑 `upgrade head` 確認 10 張表真的建出來。
2. **證交所 OpenAPI** → 灌 `stocks` 主檔（免金鑰，先打通「抓→寫 DB」路徑）。
3. **yfinance** → 灌 `daily_prices`（免金鑰）。
4. **技術指標** → 從 `daily_prices` 算，寫 `technical_indicators`（純計算）。
5. **FinMind** → 籌碼 3 表 + 估值/財報 2 表。**必須用整批 dataset 端點**，
   不可逐檔迴圈，否則會爆免費額度。
6. **Fugle** → 即時報價，接上 `GET /api/v1/stocks/{symbol}/quote` 與 Redis
   `quote:{symbol}` TTL 30s。
7. **批次串起來**：`app/jobs/run_batch.py` 依序執行 2→5 並寫 `job_runs`。

## 驗收條件

- `alembic upgrade head` 後，DB 裡確實有 10 張表（用 `\dt` 或 information_schema 驗證）
- `stocks` 表有真實的上市櫃股票數量（>1500 筆）
- `daily_prices` 對至少一檔（2330）有真實歷史資料
- `technical_indicators` 對該檔算出非空的 MA/RSI/KD/MACD
- `GET /api/v1/stocks/2330/quote` 回真實報價，且第二次呼叫走 Redis 快取
- `uv run pytest` 全綠、`ruff check` 全綠
- 每一步都在真的跑起來的 docker compose 上驗證，不是只看單元測試

## 禁區

- 不寫會員/JWT 邏輯
- 不碰前端（本計畫只做後端資料層；前端串接是下一個計畫）
- 不新增雲端依賴
