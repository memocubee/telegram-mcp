# telegram-mcp

讓 Claude (Claude Code / Claude Desktop) 能主動發送 Telegram 通知訊息的 MCP Server。

透過 Telegram Bot API，Claude 可以傳訊息給你的 Telegram 帳號或群組，適合用於任務完成通知、排程提醒、自動化告警等場景。

---

## 功能

| 指令說法 | 效果 |
|---|---|
| 「傳 Telegram 通知給我說任務完成了」 | 發送通知訊息 |
| 「用 Telegram 告訴我現在的天氣」 | 發送查詢結果 |
| 「排程結束後用 Telegram 通知我」 | 搭配排程自動通知 |
| 「幫我確認 Telegram Bot 有沒有連線成功」 | 驗證連線狀態 |

---

## 前置需求

| 項目 | 說明 |
|---|---|
| Python 3.10 以上 | 需安裝在電腦上 |
| Telegram Bot Token | 透過 @BotFather 建立，免費 |
| Chat ID | 你的 Telegram 帳號或群組的數字 ID |

---

## 安裝步驟

### 第一步：安裝 Python 套件

```bash
pip install "mcp[cli]" httpx pydantic
```

### 第二步：建立 Telegram Bot 並取得 Token

1. 打開 Telegram，搜尋 **@BotFather** 並開啟
2. 傳送 `/newbot`
3. 輸入 Bot 名稱（例如：`我的Claude通知`）
4. 輸入 Bot 用戶名，**必須以 `bot` 結尾**（例如：`my_claude_notify_bot`）
5. BotFather 會回傳 Token，格式類似：
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567
   ```
6. 複製這串 Token 存好備用

> 已有 Bot？在 BotFather 傳 `/mybots` → 選你的 Bot → **API Token** 即可找回。

### 第三步：取得 Chat ID

**方法一：getUpdates（推薦）**
1. 在 Telegram 開啟你的 Bot，傳任意一則訊息
2. 瀏覽器開啟：
   ```
   https://api.telegram.org/bot你的Token/getUpdates
   ```
3. 找到 `"chat":{"id":` 後面的數字即是 Chat ID

**方法二：@userinfobot**
1. Telegram 搜尋 **@userinfobot**
2. 傳送 `/start`，Bot 會直接回傳你的 Chat ID

> 群組的 Chat ID 是**負數**，這是正常的。

### 第四步：填入憑證

下載 `telegram_mcp_server.py`，用文字編輯器打開，修改頂端：

```python
TELEGRAM_BOT_TOKEN = "貼上你的 Bot Token"
TELEGRAM_CHAT_ID   = "貼上你的 Chat ID"
```

填好後存檔。

### 第五步：設定 Claude Desktop

找到設定檔（Windows）：
```
%APPDATA%\Claude\claude_desktop_config.json
```

加入以下設定：

```json
{
  "mcpServers": {
    "telegram": {
      "command": "python",
      "args": ["D:\\你的路徑\\telegram_mcp_server.py"]
    }
  }
}
```

> 路徑換成你存放 `telegram_mcp_server.py` 的實際位置，反斜線寫成 `\\`。

**完全關閉 Claude Desktop 再重新開啟**。

---

## 確認安裝成功

重啟後跟 Claude 說：

> 「幫我確認 Telegram Bot 有沒有連線成功」

Claude 回傳 Bot 名稱就代表成功。

---

## 在 Claude Code (CLI) 中使用

在 `~/.claude.json` 或專案 `.claude/settings.json` 加入：

```json
{
  "mcpServers": {
    "telegram": {
      "command": "python",
      "args": ["/path/to/telegram_mcp_server.py"]
    }
  }
}
```

---

## 換電腦時

1. 複製 `telegram_mcp_server.py` 到新電腦（Token 和 Chat ID 已在裡面）
2. 新電腦執行 `pip install "mcp[cli]" httpx pydantic`
3. 更新設定檔裡的檔案路徑
4. 重啟 Claude Desktop

---

## 常見問題

**Q：401 錯誤？**
Bot Token 填錯了，回去 `telegram_mcp_server.py` 確認 Token 是否正確。

**Q：Chat ID 是負數？**
群組的 Chat ID 是負數，正常現象，直接填入即可。

**Q：getUpdates 頁面是空的？**
先去 Telegram 傳一則訊息給你的 Bot，再重新整理頁面。

**Q：`python` 找不到？**
命令提示字元執行 `where python`。如果找不到，重新安裝 Python 時勾選「**Add Python to PATH**」。  
或在設定檔中改用完整路徑：`"command": "C:\\Python311\\python.exe"`

---

## License

MIT
