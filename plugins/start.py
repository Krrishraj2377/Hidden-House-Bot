import traceback, asyncio, re, time
from datetime import datetime, timedelta
from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import (
    MessageNotModified,
    MessageIdInvalid,
    QueryIdInvalid,
    MessageDeleteForbidden,
    UserNotParticipant,
    PeerIdInvalid,
    HideRequesterMissing
)
from plugins.config import ADMINS, LOG_CHANNEL, MIX_CHANNEL
from plugins.database import db
from plugins.helper import *

USED_TXNS = set()
LAST_PAYMENT_CHECK = 0
PAYMENT_CACHE = {}

broadcast_cancel = False

START_TIME = time.time()

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        mention = message.from_user.mention
        username = message.from_user.username

        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, first_name)

        progress = await message.reply_text(
            "╭────────────────╮\n"
            "│ ░░░░░░░░░░ 0% │\n"
            "╰────────────────╯",
            quote=True
        )

        bars = [
            ("█░░░░░░░░░", 10),
            ("██░░░░░░░░", 20),
            ("███░░░░░░░", 30),
            ("████░░░░░░", 40),
            ("█████░░░░░", 50),
            ("██████░░░░", 60),
            ("███████░░░", 70),
            ("████████░░", 80),
            ("█████████░", 90),
            ("██████████", 100),
        ]

        for bar, percent in bars:
            await progress.edit_text(
                f"╭────────────────╮\n"
                f"│ {bar} {percent}% │\n"
                f"╰────────────────╯"
            )
            await asyncio.sleep(0.18)

        await asyncio.sleep(0.5)

        await progress.delete()

        buttons = [
            [
                InlineKeyboardButton("⚡ 500 ᴠɪᴅᴇᴏ • ₹249", callback_data="mixp1"),
                InlineKeyboardButton("🥈 1000 ᴠɪᴅᴇᴏ • ₹449", callback_data="mixp2")
            ],
            [
                InlineKeyboardButton("💳 2000 ᴠɪᴅᴇᴏ • ₹799", callback_data="mixp3"),
                InlineKeyboardButton("🔥 5000 ᴠɪᴅᴇᴏ • ₹1999", callback_data="mixp4")
            ],
            [InlineKeyboardButton("💎 10000 ᴠɪᴅᴇᴏ • ₹2999", callback_data="mixp5")],
            [
                InlineKeyboardButton("🎬 Fʀᴇᴇ ᴛʀɪᴀʟ", callback_data="trial"),
                InlineKeyboardButton("📞 Cᴏɴᴛᴀᴄᴛ ᴍᴇ", url="https://t.me/UnseenSuportProBot")
            ],
            [InlineKeyboardButton("🌗 USDT / BINANCE / CRYPTO", url="https://t.me/UnseenSuportProBot")]
        ]

        return await message.reply_photo(
            photo="https://files.catbox.moe/bj9mup.jpg",
            caption=(f"""<b>👋 ʜᴇʟʟᴏ {mention}!

✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴜɴsᴇᴇɴ sᴇʀᴠɪᴄᴇ ʙᴏᴛ

🔐 ᴘʀɪᴠᴀᴛᴇ • ᴠɪᴘ • 🔞 18+ ᴏɴʟʏ
🔥 ʀᴀᴡ • ʀᴇᴀʟ • ᴜɴᴄᴇɴsᴏʀᴇᴅ

🔥 ᴡʜᴀᴛ ʏᴏᴜ ɢᴇᴛ
🔞 18+ ᴠɪʀᴀʟ ᴠɪᴅᴇᴏs
👑 ᴘʀᴇᴍɪᴜᴍ ᴄᴏɴᴛᴇɴᴛs
📲 ᴅɪʀᴇᴄᴛ ᴠɪᴅᴇᴏs ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ
📦 ʜɪɢʜ ǫᴜᴀʟɪᴛʏ
🔄 ᴅᴏᴡɴʟᴏᴀᴅ ᴀᴠᴀɪʟᴀʙʟᴇ
🚫 ɴᴏ ᴀᴅs / ɴᴏ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ

⚡ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ
⏳ ɴᴏ ᴡᴀɪᴛɴɢ • ɴᴏ ᴀᴘᴘʀᴏᴠᴀʟ ᴅᴇʟᴀʏ

🪜 ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs
1️⃣ ᴄʜᴏᴏsᴇ ᴀ ᴍᴇᴍʙᴇʀsʜɪᴘ ᴘʟᴀɴ
2️⃣ ᴄᴏᴍᴘʟᴇᴛᴇ ᴘᴀʏᴍᴇɴᴛ ᴠɪᴀ ᴜᴘɪ
3️⃣ ɢᴇᴛ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ᴠɪᴘ ᴄʜᴀɴɴᴇʟ

🚀 ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴘʟᴀɴ & ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!</b>"""),
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Start Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Start Handler Error: {e}")
        print(traceback.format_exc())

"""@Client.on_message(filters.command("addpremium") & filters.private & filters.user(ADMINS))
async def add_premium(client, message):
    try:
        parts = message.text.split()

        if len(parts) < 4:
            return await message.reply_text(
                "⚙️ Usage:\n`/addpremium <user_id> <plan> <days>`\n\nExample:\n`/addpremium id mix 30`\n\nExample:\n`/addpremium id cp 30`\n\nExample:\n`/addpremium id mega 30`",
                parse_mode=enums.ParseMode.MARKDOWN
            )

        user_id = int(parts[1])
        category = parts[2]
        days = int(parts[3])

        if category not in CATEGORY_MAP:
            return await message.reply_text("❌ Invalid category")

        channel_id = CATEGORY_MAP[category]["channel"]
        category_name = CATEGORY_MAP[category]["name"]

        subs = await db.get_user_subscription(user_id)

        expiry_date = datetime.utcnow() + timedelta(days=days)

        for sub in subs:
            if sub["plan_key"] == category and sub.get("active", True):
                old_expiry = sub["expiry"]

                if isinstance(old_expiry, str):
                    old_expiry = datetime.fromisoformat(old_expiry)

                if old_expiry > datetime.utcnow():
                    expiry_date = old_expiry + timedelta(days=days)
                break

        invite = await client.create_chat_invite_link(
            chat_id=channel_id,
            name=f"Manual access {user_id}",
            creates_join_request=True
        )

        await db.create_pending_subscription(user_id, category, channel_id, days, invite.invite_link)

        try:
            user = await client.get_users(user_id)
        except Exception:
            user = None

        await client.send_message(
            user_id,
            f"🎉 <b>Premium Activated!</b>\n\n"
            f"👤 <b>User ID:</b> {user.mention} (<code>{user_id}</code>)\n"
            f"🎫 <b>Category:</b> {category_name}\n"
            f"⏳ Duration: {days} days\n"
            f"🔗 Join here:\n{invite.invite_link}\n\n"
            f"⚠️ Subscription time starts after joining the channel.",
            parse_mode=enums.ParseMode.HTML
        )

        await message.reply_text(
            f"✅ <b>Premium Added Successfully</b>\n\n"
            f"👤 <b>User ID:</b> {user.mention} (<code>{user_id}</code>)\n"
            f"💬 <b>Username:</b> @{user.username or 'None'}\n"
            f"🎫 <b>Category:</b> {category_name}\n"
            f"⏳ <b>Duration:</b> {days} days\n"
            f"⏰ <b>Expiry:</b> <code>{expiry_date.strftime('%d-%m-%Y %H:%M UTC')}</code>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Add Premium Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Add Premium Handler Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("removepremium") & filters.private & filters.user(ADMINS))
async def remove_premium(client, message):
    try:
        parts = message.text.split()

        if len(parts) != 3:
            return await message.reply_text(
                "⚙️ Usage:\n`/removepremium <user_id> <plan>`\n\nExample:\n`/removepremium id mix`\n\nExample:\n`/removepremium id cp`\n\nExample:\n`/removepremium id mega`",
                parse_mode=enums.ParseMode.MARKDOWN
            )

        user_id = int(parts[1])
        plan = parts[2].lower()

        if plan not in CATEGORY_MAP:
            return await message.reply_text("❌ Invalid plan.")

        subs = await db.get_user_subscription(user_id)

        found = False
        invite_link = None
        channel_id = None

        for sub in subs:
            if sub.get("plan_key") == plan and sub.get("active", True):
                invite_link = sub.get("invite_link")
                channel_id = sub.get("channel_id")
                found = True
                break

        if not found:
            return await message.reply_text(
                f"❌ User `{user_id}` doesn't have an active **{plan.upper()}** subscription.",
                parse_mode=enums.ParseMode.MARKDOWN
            )

        removed = await db.remove_subscription(user_id, plan)

        if not removed:
            return await message.reply_text(
                f"❌ User doesn't have an active **{CATEGORY_MAP[plan]['name']}** subscription.",
                parse_mode=enums.ParseMode.HTML
            )

        if invite_link:
            try:
                await client.revoke_chat_invite_link(
                    chat_id=channel_id,
                    invite_link=invite_link
                )
            except Exception as e:
                print(f"⚠️ Failed to revoke invite link: {e}")

        try:
            await client.ban_chat_member(channel_id, user_id)
            await client.unban_chat_member(channel_id, user_id)
        except (UserNotParticipant, PeerIdInvalid):
            pass
        except Exception as e:
            print(f"⚠️ Failed to kick user {user_id}: {e}")

        await message.reply_text(
            f"✅ {plan} subscription removed from `{user_id}`.",
            parse_mode=enums.ParseMode.MARKDOWN
        )

        try:
            await client.send_message(
                user_id,
                f"❌ Your **{plan.upper()}** premium subscription has been removed.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        except:
            pass
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Remove Premium Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Remove Premium Handler Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("resendlinks") & filters.private & filters.user(ADMINS))
async def resend_links(client, message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            return await message.reply_text(
                "⚙️ Usage:\n`/resendlinks <plan> <new_channel_id>`\n\nExample:\n`/resendlinks mix id`\n\nExample:\n`/resendlinks cp id`\n\nExample:\n`/resendlinks mega id`",
                parse_mode=enums.ParseMode.MARKDOWN
            )

        plan_prefix = parts[1].strip()
        new_channel_id = int(parts[2].strip())

        await message.reply_text(
            f"🔁 Starting resend process for **{plan_prefix}** plans...\n"
            f"📢 Updating to new channel ID: `{new_channel_id}`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

        for sub_plan in ["p1", "p2", "p3", "p4"]:
            plan_key = f"{plan_prefix}{sub_plan}"
            await db.update_plan_channel(plan_key, new_channel_id)

        active_users = await db.get_active_users_by_category(plan_prefix)
        now = datetime.utcnow()
        sent, skipped, failed = 0, 0, 0

        for user in active_users:
            try:
                sub = user["subscription"]
                expiry = sub["expiry"]

                if isinstance(expiry, str):
                    expiry = datetime.fromisoformat(expiry)

                if not expiry or expiry <= now:
                    skipped += 1
                    continue

                user_id = user["id"]

                old_link = sub.get("invite_link")
                if old_link:
                    try:
                        await client.revoke_chat_invite_link(
                            new_channel_id,
                            old_link
                        )
                    except:
                        pass

                invite = await client.create_chat_invite_link(
                    chat_id=new_channel_id,
                    name=f"Backup link for {user_id}",
                    creates_join_request=True
                )

                await db.col.update_one(
                    {
                        "id": user_id,
                        "subscriptions.plan_key": sub["plan_key"]
                    },
                    {
                        "$set": {
                            "subscriptions.$.channel_id": new_channel_id,
                            "subscriptions.$.invite_link": invite.invite_link,
                            "subscriptions.$.invite_link_created": datetime.utcnow()
                        }
                    }
                )

                remaining = (expiry - now).days

                await client.send_message(
                    user_id,
                    f"📢 <b>Channel Updated!</b>\n\n"
                    f"Your premium access has been moved to a new channel.\n"
                    f"🔗 <b>Join here:</b> {invite.invite_link}\n\n"
                    f"⏳ Your access remains valid for <b>{remaining}</b> more days.\n"
                    f"⚠️ Link expires in 1 hour, please join immediately.",
                    parse_mode=enums.ParseMode.HTML
                )

                sent += 1
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Failed for {user.get('id')}: {e}")
                failed += 1

        await message.reply_text(
            f"✅ <b>Resend Completed!</b>\n\n"
            f"📦 Plan Category: <code>{plan_prefix}</code>\n"
            f"📨 Sent: <b>{sent}</b>\n"
            f"⏸ Skipped Expired: <b>{skipped}</b>\n"
            f"⚠️ Failed: <b>{failed}</b>\n"
            f"💾 Future users will now get the new channel automatically.",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Resend Link Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Resend Link Handler Error: {e}")
        print(traceback.format_exc())"""

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(ADMINS))
async def broadcast(client, message):
    global broadcast_cancel
    broadcast_cancel = False
    try:
        if message.reply_to_message:
            b_msg = message.reply_to_message
        else:
            b_msg = await client.ask(
                message.chat.id,
                "📩 Send the message to broadcast\n\n/cancel to stop.",
            )

            if b_msg.text and b_msg.text.lower() == "/cancel":
                return await message.reply_text("🚫 Broadcast cancelled.")

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Cancel Broadcast", callback_data="cancel_broadcast")]]
        )

        sts = await message.reply_text(
            "⏳ Broadcast starting...",
            reply_markup=keyboard,
        )
        start_time = time.time()
        total_users = await db.total_users_count()

        done = blocked = deleted = failed = success = 0

        users = await db.get_all_users()
        async for user in users:
            if broadcast_cancel:
                await sts.edit_text("🚫 Broadcast cancelled by admin.")
                print("🛑 Broadcast cancelled mid-way.")
                return
            try:
                if "id" in user:
                    pti, sh = await broadcast_messages(int(user["id"]), b_msg)
                    if pti:
                        success += 1
                    else:
                        if sh == "Blocked":
                            blocked += 1
                        elif sh == "Deleted":
                            deleted += 1
                        else:
                            failed += 1
                    done += 1

                    if done % 10 == 0 or done == total_users:
                        progress = broadcast_progress_bar(done, total_users)
                        percent = (done / total_users) * 100
                        elapsed = time.time() - start_time
                        speed = done / elapsed if elapsed > 0 else 0
                        remaining = total_users - done
                        eta = timedelta(seconds=int(remaining / speed)) if speed > 0 else "∞"

                        try:
                            await sts.edit(f"""
📢 <b>Broadcast in Progress...</b>

{progress}

👥 Total Users: {total_users}
✅ Success: {success}
🚫 Blocked: {blocked}
❌ Deleted: {deleted}
⚠️ Failed: {failed}

⏳ ETA: {eta}
⚡ Speed: {speed:.2f} users/sec
""", reply_markup=keyboard)
                        except:
                            pass
                else:
                    done += 1
                    failed += 1
            except Exception:
                failed += 1
                done += 1
                continue

        time_taken = timedelta(seconds=int(time.time() - start_time))
        final_progress = broadcast_progress_bar(total_users, total_users)
        final_text = f"""
✅ <b>Broadcast Completed</b> ✅

⏱ Duration: {time_taken}
👥 Total Users: {total_users}

📊 Results:
✅ Success: {success} ({(success/total_users)*100:.1f}%)
🚫 Blocked: {blocked} ({(blocked/total_users)*100:.1f}%)
❌ Deleted: {deleted} ({(deleted/total_users)*100:.1f}%)
⚠️ Failed: {failed} ({(failed/total_users)*100:.1f}%)

━━━━━━━━━━━━━━━━━━━━━━
{final_progress} 100%
━━━━━━━━━━━━━━━━━━━━━━

⚡ Speed: {speed:.2f} users/sec
"""
        await sts.edit(final_text)
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Broadcast Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Broadcast Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("stats") & filters.private & filters.user(ADMINS))
async def stats(client, message):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        username = me.username
        users_count = await db.total_users_count()

        uptime = str(timedelta(seconds=int(time.time() - START_TIME)))

        await message.reply_text(
            f"📊 Status for @{username}\n\n"
            f"👤 Users: {users_count}\n"
            f"⏱ Uptime: {uptime}\n",
        )
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Stats Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Stats Error: {e}")
        print(traceback.format_exc())

@Client.on_message(filters.command("premiumstats") & filters.private & filters.user(ADMINS))
async def premium_stats(client, message):
    try:
        now = datetime.utcnow()

        cursor = db.col.find({})

        active_counts = {}
        expired_counts = {}
        total_active = 0
        total_expired = 0

        async for user in cursor:
            if "subscriptions" not in user:
                if user.get("plan_key"):
                    user["subscriptions"] = [{
                        "plan_key": user.get("plan_key"),
                        "channel_id": user.get("channel_id"),
                        "expiry": user.get("expiry"),
                        "active": user.get("active", True)
                    }]
                else:
                    continue

            for sub in user.get("subscriptions", []):
                plan_key = sub.get("plan_key")
                expiry = sub.get("expiry")
                active = sub.get("active", True)

                if not plan_key:
                    continue

                category = resolve_category(plan_key)
                if not category:
                    continue

                if isinstance(expiry, str):
                    expiry = datetime.fromisoformat(expiry)

                if category not in active_counts:
                    active_counts[category] = 0
                    expired_counts[category] = 0

                if expiry and expiry > now and active:
                    active_counts[category] += 1
                    total_active += 1
                else:
                    expired_counts[category] += 1
                    total_expired += 1

        text = "📊 <b>Premium Stats</b>\n\n"
        text += f"👥 <b>Total Active:</b> {total_active}\n"
        text += f"💤 <b>Total Expired:</b> {total_expired}\n\n"

        all_plans = sorted(set(active_counts.keys()) | set(expired_counts.keys()))

        for plan in all_plans:
            act = active_counts.get(plan, 0)
            exp = expired_counts.get(plan, 0)
            cat_name = CATEGORY_MAP[plan]["name"]

            text += (
                f"• <b>{cat_name}</b>\n"
                f"   ✅ Active: <code>{act}</code>\n"
                f"   ❌ Expired: <code>{exp}</code>\n\n"
            )

        await message.reply_text(
            text,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Premium Stats Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>"
        )
        print(f"⚠️ Premium Stats Error: {e}")
        print(traceback.format_exc())

"""@Client.on_message(filters.command("kickexpired") & filters.private & filters.user(ADMINS))
async def kickexpired(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "Usage:\n/kickexpired mix | cp | mega",
                parse_mode=enums.ParseMode.HTML
            )

        cat_key = resolve_category(message.command[1])
        if not cat_key:
            return await message.reply_text("❌ Invalid category")

        channel_id = CATEGORY_MAP[cat_key]["channel"]
        cat_name = CATEGORY_MAP[cat_key]["name"]

        now = datetime.utcnow()
        kicked = 0
        found_expired = False

        cursor = db.col.find({})

        async for user in cursor:
            user_id = user.get("id")

            if "subscriptions" not in user:
                if user.get("plan_key"):
                    user["subscriptions"] = [{
                        "plan_key": user.get("plan_key"),
                        "channel_id": user.get("channel_id"),
                        "expiry": user.get("expiry"),
                        "active": user.get("active", True)
                    }]
                else:
                    continue

            for sub in user.get("subscriptions", []):
                if sub.get("plan_key") != cat_key:
                    continue

                if not sub.get("active", True):
                    continue

                expiry = sub.get("expiry")

                if isinstance(expiry, str):
                    expiry = datetime.fromisoformat(expiry)

                if expiry <= now:
                    found_expired = True
                    try:
                        await client.ban_chat_member(channel_id, user_id)
                        await client.unban_chat_member(channel_id, user_id)
                    except (UserNotParticipant, PeerIdInvalid):
                        pass
                    except Exception as e:
                        print(f"⚠️ Kick failed {user_id}: {e}")

                    await db.deactivate_subscription(user_id, cat_key)
                    kicked += 1

        if not found_expired:
            return await message.reply_text(
                f"ℹ️ <b>{cat_name}</b>\nNo expired users found.",
                parse_mode=enums.ParseMode.HTML
            )

        await message.reply_text(
            f"✅ <b>{cat_name}</b>\nExpired users kicked: <b>{kicked}</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Kick Expired Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>"
        )
        print(f"⚠️ Kick Expired Error: {e}")
        print(traceback.format_exc())"""

@Client.on_callback_query()
async def callback(client, query):
    try:
        me = await get_me_safe(client)
        if not me:
            return

        user_id = query.from_user.id
        data = query.data

        global LAST_PAYMENT_CHECK, PAYMENT_CACHE

        # Start
        if data == "start":
            buttons = [
                [
                    InlineKeyboardButton("⚡ 500 ᴠɪᴅᴇᴏ • ₹249", callback_data="mixp1"),
                    InlineKeyboardButton("🥈 1000 ᴠɪᴅᴇᴏ • ₹449", callback_data="mixp2")
                ],
                [
                    InlineKeyboardButton("💳 2000 ᴠɪᴅᴇᴏ • ₹799", callback_data="mixp3"),
                    InlineKeyboardButton("🔥 5000 ᴠɪᴅᴇᴏ • ₹1999", callback_data="mixp4")
                ],
                [InlineKeyboardButton("💎 10000 ᴠɪᴅᴇᴏ • ₹2999", callback_data="mixp5")],
                [
                    InlineKeyboardButton("🎬 Fʀᴇᴇ ᴛʀɪᴀʟ", callback_data="trial"),
                    InlineKeyboardButton("📞 Cᴏɴᴛᴀᴄᴛ ᴍᴇ", url="https://t.me/UnseenSuportProBot")
                ],
                [InlineKeyboardButton("🌗 USDT / BINANCE / CRYPTO", url="https://t.me/UnseenSuportProBot")]
            ]
            await query.message.edit_text(
                text=(f"""<b>👋 ʜᴇʟʟᴏ {query.from_user.mention}!

✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴜɴsᴇᴇɴ sᴇʀᴠɪᴄᴇ ʙᴏᴛ

🔐 ᴘʀɪᴠᴀᴛᴇ • ᴠɪᴘ • 🔞 18+ ᴏɴʟʏ
🔥 ʀᴀᴡ • ʀᴇᴀʟ • ᴜɴᴄᴇɴsᴏʀᴇᴅ

🔥 ᴡʜᴀᴛ ʏᴏᴜ ɢᴇᴛ
🔞 18+ ᴠɪʀᴀʟ ᴠɪᴅᴇᴏs
👑 ᴘʀᴇᴍɪᴜᴍ ᴄᴏɴᴛᴇɴᴛs
📲 ᴅɪʀᴇᴄᴛ ᴠɪᴅᴇᴏs ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ
📦 ʜɪɢʜ ǫᴜᴀʟɪᴛʏ
🔄 ᴅᴏᴡɴʟᴏᴀᴅ ᴀᴠᴀɪʟᴀʙʟᴇ
🚫 ɴᴏ ᴀᴅs / ɴᴏ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ

⚡ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ
⏳ ɴᴏ ᴡᴀɪᴛɴɢ • ɴᴏ ᴀᴘᴘʀᴏᴠᴀʟ ᴅᴇʟᴀʏ

🪜 ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs
1️⃣ ᴄʜᴏᴏsᴇ ᴀ ᴍᴇᴍʙᴇʀsʜɪᴘ ᴘʟᴀɴ
2️⃣ ᴄᴏᴍᴘʟᴇᴛᴇ ᴘᴀʏᴍᴇɴᴛ ᴠɪᴀ ᴜᴘɪ
3️⃣ ɢᴇᴛ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ᴠɪᴘ ᴄʜᴀɴɴᴇʟ

🚀 ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴘʟᴀɴ & ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!</b>"""),
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await query.answer()

        # Confirmation menu when a price is selected
        elif data.startswith("mixp"):
            price_map = {
                "mixp1": ("₹249", "500 ᴠɪᴅᴇᴏ"),
                "mixp2": ("₹449", "1000 ᴠɪᴅᴇᴏ"),
                "mixp3": ("₹799", "2000 ᴠɪᴅᴇᴏ"),
                "mixp4": ("₹1999", "5000 ᴠɪᴅᴇᴏ"),
                "mixp5": ("₹2999", "10000 ᴠɪᴅᴇᴏ")
            }

            price, duration = price_map[data]

            buttons = [
                [InlineKeyboardButton("✅ ᴘᴜʀᴄʜᴀsᴇ", callback_data=f"confirm_{data}")],
                [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="start")]
            ]

            await query.message.edit_text(
                text=(f"""<b>🛒 ᴘᴜʀᴄʜᴀsᴇ ᴄᴏɴꜰɪʀᴍᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ

🎬 ᴜɴsᴇᴇɴ ᴄᴏʟʟᴇᴄᴛɪᴏɴ</b>

📢 <b>ᴄʜᴀɴɴᴇʟ:</b> ᴜɴsᴇᴇɴ sᴇʀᴠɪᴄᴇ
💰 <b>ᴀᴍᴏᴜɴᴛ:</b> {price}
⏰ <b>ᴠᴀʟɪᴅɪᴛʏ:</b> {duration}

👨🏻‍💻 <b>ᴜsᴇʀ: {query.from_user.mention}</b>

<b>📋 ᴄᴏɴꜰɪʀᴍᴀᴛɪᴏɴ ʀᴇǫᴜᴇsᴛ:</b>
1️⃣ ᴘʟᴇᴀsᴇ ʀᴇᴠɪᴇᴡ ᴛʜᴇ ᴏʀᴅᴇʀ ᴅᴇᴛᴀɪʟs
2️⃣ ᴄᴏɴꜰɪʀᴍ ᴛʜᴀᴛ ʏᴏᴜ ᴡɪsʜ ᴛᴏ ᴘᴜʀᴄʜᴀsᴇ
3️⃣ ᴄʟɪᴄᴋ ✅ ᴄᴏɴꜰɪʀᴍ ᴘᴜʀᴄʜᴀsᴇ ʙᴇʟᴏᴡ

<b>⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ:</b>
• ᴘʟᴇᴀsᴇ ᴠᴇʀɪꜰʏ ᴀʟʟ ᴅᴇᴛᴀɪʟs ʙᴇꜰᴏʀᴇ ᴄᴏɴꜰɪʀᴍɪɴɢ
• ᴏɴᴄᴇ ᴄᴏɴꜰɪʀᴍᴇᴅ, ᴘᴀʏᴍᴇɴᴛ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ ᴡɪʟʟ ʙᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ
━━━━━━━━━━━━━━━━━━
<b>✶ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ 50% ᴏꜰꜰ ᴡʜᴇɴ ʏᴏᴜ ʀᴇɴᴇᴡ ᴛʜɪꜱ ᴘʟᴀɴ</b>"""),
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await query.answer()

        # Payment menu when a confirm
        elif data.startswith("confirm_mixp"):
            price_map = {
                "confirm_mixp1": ("₹249", "500 ᴠɪᴅᴇᴏ"),
                "confirm_mixp2": ("₹449", "1000 ᴠɪᴅᴇᴏ"),
                "confirm_mixp3": ("₹799", "2000 ᴠɪᴅᴇᴏ"),
                "confirm_mixp4": ("₹1999", "5000 ᴠɪᴅᴇᴏ"),
                "confirm_mixp5": ("₹2999", "10000 ᴠɪᴅᴇᴏ")
            }

            price, duration = price_map[data]

            buttons = [
                [InlineKeyboardButton("✅ ᴘᴀʏᴍᴇɴᴛ ᴅᴏɴᴇ", callback_data=f"paid1_{data.replace('confirm_', '')}")],
                [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=data.replace("confirm_", ""))]
            ]

            upi_id = "goldensuplier@fam"
            upi_name = "KM Membership Bot"
            qr_image = generate_upi_qr(upi_id, upi_name, price)

            caption = (f"""<b>✅ ᴏʀᴅᴇʀ ᴄʀᴇᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ

🎬 ᴜɴsᴇᴇɴ ᴄᴏʟʟᴇᴄᴛɪᴏɴ</b>

📢 <b>ᴄʜᴀɴɴᴇʟ:</b> ᴜɴsᴇᴇɴ sᴇʀᴠɪᴄᴇ
💰 <b>ᴀᴍᴏᴜɴᴛ:</b> {price}
⏰ <b>ᴠᴀʟɪᴅɪᴛʏ:</b> {duration}
💳 <b>ᴜᴘɪ ɪᴅ:</b> <code>{upi_id}</code>

<b>📱 ᴘᴀʏᴍᴇɴᴛ ɪɴsᴛʀᴜᴄᴛɪᴏɴs:</b>  
1️⃣ sᴄᴀɴ ᴛʜᴇ ǫʀ ᴄᴏᴅᴇ ᴀʙᴏᴠᴇ  
2️⃣ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ ᴘᴀʏᴍᴇɴᴛ  
3️⃣ ᴏɴᴄᴇ ʏᴏᴜ ᴘᴀʏ, ᴄʟɪᴄᴋ ✅ ᴘᴀʏᴍᴇɴᴛ ᴅᴏɴᴇ.""")

            await query.message.delete()

            await client.send_photo(
                chat_id=query.message.chat.id,
                photo=qr_image,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
            await query.answer()

        # User clicked Payment Done
        elif data.startswith("paid1_"):
            plan_key = data.replace("paid1_", "")
            plan_map = {
                "mixp1": ("₹249", "500 ᴠɪᴅᴇᴏ"),
                "mixp2": ("₹449", "1000 ᴠɪᴅᴇᴏ"),
                "mixp3": ("₹799", "2000 ᴠɪᴅᴇᴏ"),
                "mixp4": ("₹1999", "5000 ᴠɪᴅᴇᴏ"),
                "mixp5": ("₹2999", "10000 ᴠɪᴅᴇᴏ")
            }

            if plan_key not in plan_map:
                return await query.message.edit_text("⚠️ ɪɴᴠᴀʟɪᴅ ᴘʟᴀɴ ᴋᴇʏ.")

            price, duration = plan_map[plan_key]
            amount_expected = int(price.replace("₹", ""))

            await query.message.edit_text(
                text=(
                    f"🔍 <b>ᴄʜᴇᴄᴋɪɴɢ ᴘᴀʏᴍᴇɴᴛ sᴛᴀᴛᴜs...</b>\n\n"
                    f"🎫 <b>ᴘʟᴀɴ:</b> 🎬 ᴜɴsᴇᴇɴ ᴄᴏʟʟᴇᴄᴛɪᴏɴ\n"
                    f"📢 <b>ᴄʜᴀɴɴᴇʟ:</b> ᴜɴsᴇᴇɴ sᴇʀᴠɪᴄᴇ\n"
                    f"💰 <b>ᴀᴍᴏᴜɴᴛ:</b> ₹{amount_expected}\n"
                    f"🕒 <b>ᴠᴀʟɪᴅɪᴛʏ:</b> {duration}\n\n"
                    f"⚡ <b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴡʜɪʟᴇ ᴠᴇʀɪғʏ ʏᴏᴜʀ ᴛʀᴀɴsᴀᴄᴛɪᴏɴ.</b>"
                ),
                parse_mode=enums.ParseMode.HTML
            )

            now = datetime.now(pytz.UTC)

            if (now.timestamp() - LAST_PAYMENT_CHECK) > 30:
                new_txns = await fetch_fampay_payments()
                for txn in new_txns:
                    if txn.get("time") and txn["time"].tzinfo is None:
                        txn["time"] = pytz.UTC.localize(txn["time"])
                    PAYMENT_CACHE[txn["txn_id"]] = txn
                LAST_PAYMENT_CHECK = now.timestamp()

            matched_txn = None
            for txn in sorted(PAYMENT_CACHE.values(), key=lambda x: x["time"], reverse=True):
                txn_id = txn["txn_id"]

                if txn_id in USED_TXNS:
                    continue

                txn_time = txn["time"].astimezone(pytz.UTC)
                txn_age = now - txn_time

                if txn["amount"] == amount_expected and txn_age < timedelta(minutes=10):
                    matched_txn = txn
                    break

            if not matched_txn:
                return await query.message.edit_text(
                    f"❌ ɴᴏ ʀᴇᴄᴇɴᴛ ᴘᴀʏᴍᴇɴᴛ ғᴏᴜɴᴅ ғᴏʀ ₹{amount_expected}.\n\n"
                    "ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ 1 ᴍɪɴᴜᴛᴇ ᴀɴᴅ ᴘʀᴇss **ᴘᴀʏᴍᴇɴᴛ ᴅᴏɴᴇ** ᴀɢᴀɪɴ.",
                    parse_mode=enums.ParseMode.MARKDOWN
                )

            txn_id = matched_txn["txn_id"]

            USED_TXNS.add(txn_id)
            await db.save_used_txn(txn_id)

            channel_id = await db.get_plan_channel(plan_key)
            if not channel_id:
                channel_id = MIX_CHANNEL
                if not channel_id:
                    return await query.message.edit_text(
                        "⚠️ ɴᴏ ᴄʜᴀɴɴᴇʟ ᴀssɪɢᴍᴇᴅ ғᴏʀ ᴛʜɪs ᴘʟᴀɴ. ᴄᴏɴᴀᴛᴄᴛ ᴀᴅᴍɪɴ."
                    )

            user = query.from_user

            invite = await client.create_chat_invite_link(
                chat_id=channel_id,
                name=f"Access for {user.first_name}",
                creates_join_request=True
            )

            for admin_id in ADMINS:
                await client.send_message(
                    admin_id,
                    f"📢 <b>ɴᴇᴡ ᴘᴀʏᴍᴇɴᴛ ᴠᴇʀɪғɪᴇᴅ</b>\n\n"
                    f"👤 <b>ᴜsᴇʀ:</b> {user.mention} (<code>{user.id}</code>)\n"
                    f"💬 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{user.username or 'None'}\n"
                    f"🎫 <b>ᴘʟᴀɴ:</b> 🎬 ᴜɴsᴇᴇɴ ᴄᴏʟʟᴇᴄᴛɪᴏɴ\n"
                    f"🕒 <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}\n"
                    f"💰 <b>ᴀᴍᴏᴜɴᴛ:</b> ₹{amount_expected}\n"
                    f"🧾 <b>ᴛxɴ ɪᴅ:</b> <code>{txn_id}</code>\n"
                    f"⏰ <b>ᴛɪᴍᴇ:</b> {matched_txn['time']}\n"
                    f"🔗 <b>ɪɴᴠɪᴛᴇ ʟɪɴᴋ:</b> {invite.invite_link}",
                    parse_mode=enums.ParseMode.HTML
                )

            await query.message.edit_text(
                f"✅ <b>ᴘᴀʏᴍᴇɴᴛ ᴠᴇʀɪғɪᴇᴅ!</b>\n\n"
                f"👤 ᴜsᴇʀ: {user.mention} (<code>{user.id}</code>)\n"
                f"🎫 ᴘʟᴀɴ: 🎬 ᴜɴsᴇᴇɴ ᴄᴏʟʟᴇᴄᴛɪᴏɴ\n"
                f"🕒 ᴅᴜʀᴀᴛɪᴏɴ: {duration}\n"
                f"💰 ᴀᴍᴏᴜɴᴛ: ₹{amount_expected}\n"
                f"🧾 ᴛxɴ ɪᴅ: <code>{txn_id}</code>\n"
                f"⏰ ᴛɪᴍᴇ: {matched_txn['time']}\n\n"
                f"🎟️ ʏᴏᴜʀ ᴀᴄᴄᴇss ʟɪɴᴋ:\n{invite.invite_link}\n\n"
                f"⚠️ ʟɪɴᴋ ᴇxᴘɪʀᴇs ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ.",
                parse_mode=enums.ParseMode.HTML
            )

            days_map = {
                "500 ᴠɪᴅᴇᴏ": 7,
                "1000 ᴠɪᴅᴇᴏ": 30,
                "2000 ᴠɪᴅᴇᴏ": 90,
                "5000 ᴠɪᴅᴇᴏ": 180,
                "10000 ᴠɪᴅᴇᴏ": 3650
            }

            days = days_map.get(duration, 7)

            subs = await db.get_user_subscription(user.id)

            expiry_date = datetime.utcnow() + timedelta(days=days)

            for sub in subs:
                if sub["plan_key"] == plan_key and sub.get("active", True):
                    old_expiry = sub["expiry"]

                    if isinstance(old_expiry, str):
                        old_expiry = datetime.fromisoformat(old_expiry)

                    if old_expiry > datetime.utcnow():
                        expiry_date = old_expiry + timedelta(days=days)
                        break

            if expiry_date:
                await db.create_pending_subscription(user.id, plan_key, channel_id, days, invite.invite_link)

            await query.answer()

        elif data == "subscription":
            buttons = [[InlineKeyboardButton("⬅️ Back", callback_data="start")]]

            subs = await db.get_user_subscription(user_id)

            if not subs:
                return await query.message.edit_text(
                    "🔍 <b>Your Premium Subscriptions</b>\n\n"
                    "❌ You don't have any active subscription.",
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            plan_names = {
                "mix": "🎬 Mixed Collection",
                "cp": "🕵️‍♂️ CP/RP Collection",
                "mega": "🚀 Mega Collection"
            }

            now = datetime.utcnow()
            text = "📊 <b>Your Premium Subscriptions</b>\n\n"

            active_found = False

            for sub in subs:
                plan_key = sub.get("plan_key")
                channel_id = sub.get("channel_id")
                expiry = sub.get("expiry")
                active = sub.get("active", True)
                invite_link = sub.get("invite_link")
                status = sub.get("status", "active").title()

                if not expiry:
                    category = resolve_category(plan_key)
                    plan_name = plan_names.get(category, plan_key)

                    text += (
                        f"🎫 <b>{plan_name}</b>\n"
                        f"📊 <b>Status:</b> <code>Pending Join</code>\n"
                        f"📢 <b>Channel ID:</b> <code>{channel_id}</code>\n"
                    )

                    if invite_link:
                        text += f"🔗 <b>Join Link:</b>\n<code>{invite_link}</code>\n"

                    text += (
                        "\n⚠️ <i>Your subscription time will start after you join the channel.</i>\n\n"
                    )

                    active_found = True
                    continue

                if isinstance(expiry, str):
                    expiry = datetime.fromisoformat(expiry)

                if expiry <= now:
                    if active:
                        await db.deactivate_subscription(user_id, plan_key)
                    continue

                active_found = True

                remaining = expiry - now
                category = resolve_category(plan_key)
                plan_name = plan_names.get(category, plan_key)

                text += (
                    f"🎫 <b>{plan_name}</b>\n"
                    f"📊 <b>Status:</b> <code>{status}</code>\n"
                    f"📢 <b>Channel ID:</b> <code>{channel_id}</code>\n"
                    f"⏰ <b>Expires:</b> <code>{expiry.strftime('%d-%m-%Y %H:%M UTC')}</code>\n"
                    f"⌛ <b>Remaining:</b> <code>{remaining.days} days</code>\n"
                )

                if invite_link:
                    text += f"🔗 <b>Join Link:</b>\n<code>{invite_link}</code>\n"

                text += "\n"

            if not active_found:
                text = (
                    "🔍 <b>Your Premium Subscriptions</b>\n\n"
                    "❌ You don't have any active subscriptions."
                )

            await query.message.edit_text(
                text,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

            await query.answer()

        # Free Trial
        elif data == "trial":
            buttons = [
                [InlineKeyboardButton("✅ ᴄʟɪᴄᴋ ʜᴇʀᴇ", url=f"https://t.me/unseenprobot?start=Z2V0LTUwMjIyMzcwMTA4NTAtMjYxMTU2MzI0NTY0MjA")],
                [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="start")]
            ]

            await query.message.edit_text(
                text=(f"""<b>🎁 ꜰʀᴇᴇ ᴛʀɪᴀʟ ᴀᴄᴛɪᴠᴀᴛᴇᴅ</b>

⏳ <b>ᴛʀɪᴀʟ ᴅᴜʀᴀᴛɪᴏɴ:</b> sᴏᴍᴇ ᴛɪᴍᴇs
🕒 <b>ᴇxᴘɪʀᴇs ᴀᴛ:</b> sᴏᴍᴇ ᴛɪᴍᴇs

━━━━━━━━━━━━━━━━━━
📌 <b>sᴛᴀᴛᴜs:</b> ᴛʀɪᴀʟ ᴀᴄᴛɪᴠᴇ 🎉
━━━━━━━━━━━━━━━━━━

<b>🚀 ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴀᴄᴄᴇss ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴄᴏɴᴛᴇɴᴛ.

⚠️ ᴛʜɪs ᴛʀɪᴀʟ ɪs ᴠᴀʟɪᴅ ꜰᴏʀ ᴏɴʟʏ sᴏᴍᴇ ᴛɪᴍᴇs.  
⏰ ᴀꜰᴛᴇʀ ᴇxᴘɪʀʏ, ᴀᴄᴄᴇss ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇᴍᴏᴠᴇᴅ.

💳 ᴘᴜʀᴄʜᴀsᴇ ᴀ ᴍᴇᴍʙᴇʀsʜɪᴘ ᴛᴏ ɢᴇᴛ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss.</b>"""),
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await query.answer()
            

        # Cancel Broadcast
        elif data == "cancel_broadcast":
            global broadcast_cancel
            broadcast_cancel = True
            await query.answer("🚫 Broadcast cancelled!", show_alert=True)
            await query.message.edit_text("🛑 Broadcast cancelled by admin.")
            await query.answer()

        else:
            await client.send_message(
                LOG_CHANNEL,
                f"⚠️ Unknown Callback Data Received:\n\n{data}\n\nUser: {query.from_user.id}\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
            )
            await query.answer("⚠️ Unknown action.", show_alert=True)
    except (MessageNotModified, MessageIdInvalid, QueryIdInvalid, MessageDeleteForbidden):
        return
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ Callback Handler Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ Callback Handler Error: {e}")
        print(traceback.format_exc())
        await query.answer("❌ An error occurred. The admin has been notified.", show_alert=True)

"""@Client.on_chat_join_request()
async def handle_join_request(client, request):
    try:
        user_id = request.from_user.id
        chat_id = request.chat.id

        user = await db.col.find_one({"id": user_id})

        if not user or "subscriptions" not in user:
            try:
                await client.decline_chat_join_request(chat_id, user_id)
            except HideRequesterMissing:
                return
            return

        matched = None

        for sub in user.get("subscriptions", []):
            if (
                sub.get("channel_id") == chat_id
                and sub.get("status") == "pending"
            ):
                matched = sub
                break

            if (
                sub.get("channel_id") == chat_id
                and sub.get("active")
            ):
                matched = sub
                break


        if not matched:
            try:
                await client.decline_chat_join_request(chat_id, user_id)
            except HideRequesterMissing:
                return
            return

        expiry = matched.get("expiry")

        if expiry:
            if isinstance(expiry, str):
                expiry = datetime.fromisoformat(expiry)

            if expiry <= datetime.utcnow():
                try:
                    await client.decline_chat_join_request(chat_id, user_id)
                except HideRequesterMissing:
                    return
                return

        try:
            await client.approve_chat_join_request(chat_id, user_id)
        except HideRequesterMissing:
            return

        if not matched.get("joined"):
            days = matched.get("days", 30)

            expiry_date = datetime.utcnow() + timedelta(days=days)

            await db.col.update_one(
                {
                    "id": user_id,
                    "subscriptions.plan_key": matched["plan_key"]
                },
                {
                    "$set": {
                        "subscriptions.$.joined": True,
                        "subscriptions.$.status": "active",
                        "subscriptions.$.active": True,
                        "subscriptions.$.expiry": expiry_date
                    }
                }
            )

        await client.send_message(
            user_id,
            "✅ Your premium access has been activated."
        )
    except Exception as e:
        await client.send_message(
            LOG_CHANNEL,
            f"⚠️ handle_join_request Error:\n\n<code>{e}</code>\n\nTraceback:\n<code>{traceback.format_exc()}</code>."
        )
        print(f"⚠️ handle_join_request Error: {e}")
        print(traceback.format_exc())"""
