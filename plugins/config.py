import traceback, re, os

try:
    id_pattern = re.compile(r"^.\d+$")

    # Bot Information
    API_ID = int(os.environ.get("API_ID", "35384565"))
    API_HASH = os.environ.get("API_HASH", "dbba8a136120df358bd3b6e1fbc18792")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8994248340:AAHqVfhnMcObZxoBJWsj5gMLESIpTVWW1-A")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "UnseenServiceRobot") # without @

    # Database Information
    DB_URI = os.environ.get("DB_URI", "mongodb+srv://Test:Test123@test.ysxzrpt.mongodb.net/?appName=Test")
    DB_NAME = os.environ.get("DB_NAME", "hiddenhouse")

    # Moderator Information
    ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get("ADMINS", "8477930865").split()]

    # Channel Information
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003407592547"))
    MIX_CHANNEL = int(os.environ.get("MIX_CHANNEL", "-1003749230010"))
except Exception as e:
    print("⚠️ Error loading config.py:", e)
    traceback.print_exc()
