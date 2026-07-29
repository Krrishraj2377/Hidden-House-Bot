import motor.motor_asyncio
from plugins.config import DB_URI, DB_NAME
from datetime import datetime

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(id=id, name=name)

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})

    async def create_pending_subscription(self, user_id, plan_key, channel_id, days, invite_link):
        user = await self.col.find_one({"id": int(user_id)})

        if user and "subscriptions" not in user:
            subs = []

            if user.get("plan_key"):
                subs.append({
                    "plan_key": user.get("plan_key"),
                    "channel_id": user.get("channel_id"),
                    "expiry": user.get("expiry"),
                    "active": user.get("active", True)
                })

            await self.col.update_one(
                {"id": int(user_id)},
                {
                    "$set": {"subscriptions": subs},
                    "$unset": {
                        "plan_key": "",
                        "channel_id": "",
                        "expiry": "",
                        "active": ""
                    }
                }
            )

        await self.col.update_one(
            {
                "id": int(user_id),
                "subscriptions.plan_key": plan_key
            },
            {
                "$set": {
                    "subscriptions.$.channel_id": channel_id,
                    "subscriptions.$.days": days,
                    "subscriptions.$.invite_link": invite_link,
                    "subscriptions.$.joined": False,
                    "subscriptions.$.status": "pending",
                    "subscriptions.$.expiry": None,
                    "subscriptions.$.active": False
                }
            }
        )

        await self.col.update_one(
            {
                "id": int(user_id),
                "subscriptions.plan_key": {
                    "$ne": plan_key
                }
            },
            {
                "$push": {
                    "subscriptions": {
                        "plan_key": plan_key,
                        "channel_id": channel_id,
                        "days": days,
                        "invite_link": invite_link,
                        "joined": False,
                        "status": "pending",
                        "expiry": None,
                        "active": False
                    }
                }
            },
            upsert=True
        )

    async def get_active_subscriptions(self):
        now = datetime.utcnow().isoformat()
        return self.col.find({
            "active": True,
            "expiry": {"$gt": now}
        })

    async def get_user_subscription(self, user_id):
        user = await self.col.find_one({"id": int(user_id)})

        if not user:
            return []

        if "subscriptions" in user:
            return user.get("subscriptions", [])

        if user.get("plan_key"):
            return [{
                "plan_key": user.get("plan_key"),
                "channel_id": user.get("channel_id"),
                "expiry": user.get("expiry"),
                "active": user.get("active", True)
            }]

        return []

    async def get_active_users_by_category(self, category):
        users = []

        cursor = self.col.find({"subscriptions": {"$exists": True}})

        async for user in cursor:
            for sub in user.get("subscriptions", []):
                expiry = sub.get("expiry")

                if isinstance(expiry, str):
                    expiry = datetime.fromisoformat(expiry)

                if (
                    sub.get("plan_key") == category
                    and sub.get("active", True)
                    and expiry > datetime.utcnow()
                ):
                    users.append({
                        "id": user["id"],
                        "subscription": sub
                    })
                    break

        return users

    async def update_subscription(self, user_id, plan_key, channel_id, expiry):
        user = await self.col.find_one({"id": int(user_id)})

        if user and "subscriptions" not in user:
            subs = []
            if user.get("plan_key") and user.get("expiry"):
                subs.append({
                    "plan_key": user["plan_key"],
                    "channel_id": user["channel_id"],
                    "expiry": user["expiry"],
                    "active": user.get("active", True)
                })

            await self.col.update_one(
                {"id": int(user_id)},
                {
                    "$set": {"subscriptions": subs},
                    "$unset": {
                        "plan_key": "",
                        "channel_id": "",
                        "expiry": "",
                        "active": ""
                    }
                }
            )

        result = await self.col.update_one(
            {
                "id": int(user_id),
                "subscriptions.plan_key": plan_key
            },
            {
                "$set": {
                    "subscriptions.$.channel_id": channel_id,
                    "subscriptions.$.expiry": expiry,
                    "subscriptions.$.active": True
                }
            }
        )

        if result.modified_count == 0:
            await self.col.update_one(
                {"id": int(user_id)},
                {
                    "$push": {
                        "subscriptions": {
                            "plan_key": plan_key,
                            "channel_id": channel_id,
                            "expiry": expiry,
                            "active": True
                        }
                    }
                },
                upsert=True
            )

    async def deactivate_subscription(self, user_id, plan_key):
        await self.col.update_one(
            {
                "id": int(user_id),
                "subscriptions.plan_key": plan_key
            },
            {
                "$set": {
                    "subscriptions.$.active": False,
                    "subscriptions.$.expired_at": datetime.utcnow().isoformat()
                }
            }
        )

    async def remove_subscription(self, user_id, plan_key):
        user = await self.col.find_one({"id": int(user_id)})

        if not user:
            return None

        removed_sub = None

        for sub in user.get("subscriptions", []):
            if sub.get("plan_key") == plan_key:
                removed_sub = sub
                break

        if not removed_sub:
            return None

        await self.col.update_one(
            {"id": int(user_id)},
            {
                "$pull": {
                    "subscriptions": {
                        "plan_key": plan_key
                    }
                }
            }
        )

        return removed_sub

    async def update_plan_channel(self, plan_key, new_channel_id):
        await self.db.plan_channels.update_one(
            {"plan_key": plan_key},
            {"$set": {"channel_id": int(new_channel_id)}},
            upsert=True
        )

    async def get_plan_channel(self, plan_key):
        doc = await self.db.plan_channels.find_one({"plan_key": plan_key})
        return int(doc["channel_id"]) if doc and "channel_id" in doc else None

    async def save_used_txn(self, txn_id: str):
        await self.db.used_txns.update_one(
            {"txn_id": txn_id},
            {"$set": {"txn_id": txn_id}},
            upsert=True
        )

    async def is_txn_used(self, txn_id: str) -> bool:
        data = await self.db.used_txns.find_one({"txn_id": txn_id})
        return data is not None

    async def load_all_used_txns(self):
        cursor = self.db.used_txns.find({})
        return {doc["txn_id"] async for doc in cursor}

db = Database(DB_URI, DB_NAME)
