#!/usr/bin/env python3
"""
Telegram MCP Server

讓 Claude 能夠發送 Telegram 通知訊息。

== 設定區（只需要改這裡）==================================================
"""

# ▼▼▼ 填入你的資料 ▼▼▼
TELEGRAM_BOT_TOKEN = "在這裡貼上你的 Bot Token"
TELEGRAM_CHAT_ID   = "在這裡貼上你的 Chat ID"
# ▲▲▲ 填完存檔即可 ▲▲▲

"""
===========================================================================

取得 Bot Token：
  1. 打開 Telegram，搜尋 @BotFather
  2. 傳送 /newbot，依指示建立 Bot
  3. BotFather 會給你一串 Token，格式：1234567890:ABCdef...

取得 Chat ID：
  1. 傳任意訊息給你的 Bot
  2. 瀏覽器開啟：https://api.telegram.org/bot你的Token/getUpdates
  3. 找到 "chat":{"id": 後面的數字就是 Chat ID
"""

import httpx
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("telegram_mcp")

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        try:
            msg = e.response.json().get("description", e.response.text)
        except Exception:
            msg = e.response.text
        if status == 401:
            return "錯誤：Bot Token 無效，請確認 TELEGRAM_BOT_TOKEN 是否正確。"
        if status == 400:
            return f"錯誤：請求格式不正確 — {msg}"
        if status == 429:
            return "錯誤：傳送太頻繁，請稍後再試。"
        return f"錯誤：Telegram API 回傳 {status} — {msg}"
    if isinstance(e, httpx.TimeoutException):
        return "錯誤：請求逾時，請稍後再試。"
    return f"錯誤：{type(e).__name__} — {e}"


class SendMessageInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(
        ...,
        description="要發送的通知訊息內容。",
        min_length=1,
        max_length=4096,
    )
    chat_id: str = Field(
        default="",
        description="（選填）指定接收對象的 Chat ID，留空使用預設收件人。",
    )


@mcp.tool(
    name="telegram_send_message",
    annotations={
        "title": "發送 Telegram 通知訊息",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def telegram_send_message(params: SendMessageInput) -> str:
    """發送文字通知訊息到 Telegram。

    Args:
        params (SendMessageInput):
            - message (str): 訊息內容（最多 4096 字）
            - chat_id (str, 選填): 指定 Chat ID，留空使用預設收件人

    Returns:
        str: 成功訊息或錯誤描述。
    """
    try:
        target_chat_id = params.chat_id if params.chat_id else TELEGRAM_CHAT_ID
        if not target_chat_id:
            return "錯誤：未設定 Chat ID，請在檔案頂端填入 TELEGRAM_CHAT_ID。"

        payload = {
            "chat_id": target_chat_id,
            "text": params.message,
            "parse_mode": "HTML",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{TELEGRAM_API_BASE}/sendMessage",
                json=payload,
                timeout=30.0,
            )
            resp.raise_for_status()
        return "✅ Telegram 通知已成功發送！"
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="telegram_get_bot_info",
    annotations={
        "title": "取得 Telegram Bot 資訊",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def telegram_get_bot_info() -> str:
    """取得 Bot 基本資訊，用來驗證 Token 是否正確。"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{TELEGRAM_API_BASE}/getMe", timeout=30.0)
            resp.raise_for_status()
        data = resp.json().get("result", {})
        return (
            f"✅ Bot 連線成功！\n"
            f"名稱：{data.get('first_name', '')}\n"
            f"用戶名：@{data.get('username', '')}\n"
            f"Bot ID：{data.get('id', '')}"
        )
    except Exception as e:
        return _handle_error(e)


if __name__ == "__main__":
    mcp.run()
