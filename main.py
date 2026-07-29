import traceback, asyncio, pytz
from datetime import datetime, date
from pyrogram import Client
from pyrogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault
)
from plugins.config import API_ID, API_HASH, BOT_TOKEN, ADMINS, LOG_CHANNEL
from plugins.database import db
from plugins.start import *

RESTART_TXT = """<b><u>BOT RESTARTED !</u></b>

📅 Date : <code>{}</code>
⏰ Time : <code>{}</code>
🌐 Timezone : <code>Asia/Kolkata</code>
🤖 Bot : @HiddenHouseXdBot

✅ Bot is now online and ready to process requests."""

async def set_auto_menu(client):
    try:
        owner_cmds = [
            BotCommand("start", "Check I am alive"),
            BotCommand("addpremium", "Add premium users"),
            BotCommand("removepremium", "Remove premium users"),
            BotCommand("resendlinks", "Resend link to users"),
            BotCommand("kickexpired", "Kick expired user"),
            BotCommand("broadcast", "Broadcast a message to users"),
            BotCommand("stats", "View bot statistics"),
            BotCommand("premiumstats", "View bot premium user statistics")
        ]
        for admin_id in ADMINS:
            await client.set_bot_commands(owner_cmds, scope=BotCommandScopeChat(chat_id=admin_id))

        default_cmds = [
            BotCommand("start", "Check I am alive")
        ]
        await client.set_bot_commands(default_cmds, scope=BotCommandScopeDefault())
    except Exception as e:
        print(f"⚠️ Set Menu Error: {e}")
        print(traceback.format_exc())

async def expiry_runtime_watcher(client):
    while True:
        try:
            now = datetime.utcnow()

            cursor = db.col.find({})

            async for user in cursor:
                user_id = user.get("id")

                if not user_id:
                    continue

                subscriptions = user.get("subscriptions", [])

                for sub in subscriptions:
                    if not sub.get("active", False):
                        continue

                    expiry = sub.get("expiry")
                    channel_id = sub.get("channel_id")
                    plan_key = sub.get("plan_key")

                    if not expiry or not channel_id:
                        continue

                    if isinstance(expiry, str):
                        expiry = datetime.fromisoformat(expiry)

                    if expiry <= now:
                        try:
                            await client.ban_chat_member(channel_id, user_id)
                            await client.unban_chat_member(channel_id, user_id)
                        except Exception as e:
                            print(f"⚠️ Kick error {user_id}: {e}")

                        await db.col.update_one(
                            {
                                "id": user_id,
                                "subscriptions.plan_key": plan_key
                            },
                            {
                                "$set": {
                                    "subscriptions.$.active": False,
                                    "subscriptions.$.status": "expired"
                                }
                            }
                        )

                        try:
                            await client.send_message(
                                user_id,
                                f"⏰ Your {plan_key} premium has expired.\n"
                                "You have been removed from the channel."
                            )
                        except:
                            pass

                        print(
                            f"⚡ Expired removed: {user_id} ({plan_key})"
                        )

            await asyncio.sleep(60)
        except Exception as e:
            print(f"⚠️ Expiry watcher error: {e}")
            await asyncio.sleep(10)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "Hidden House Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins")
        )

    async def start(self):
        await super().start()
        await set_auto_menu(self)
        asyncio.create_task(expiry_runtime_watcher(self))
        today = date.today()
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        await self.send_message(LOG_CHANNEL, RESTART_TXT.format(today, now))
        print('Bot Started.')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

Bot().run()
