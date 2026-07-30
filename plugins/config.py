import traceback, re, os

try:
    id_pattern = re.compile(r"^.\d+$")

    # Bot Information
    API_ID = int(os.environ.get("API_ID", "35384565"))
    API_HASH = os.environ.get("API_HASH", "dbba8a136120df358bd3b6e1fbc18792")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8977435339:AAEAcVwzsujTRToqLGX1dl3RVvPPAz5xn3Q")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "UnseenServiceRobot") # without @

    # Database Information
    DB_URI = os.environ.get("DB_URI", "mongodb+srv://nikl85743_db_user:4ztyZ1IVyVID6z3y@cluster0.6tgpbcj.mongodb.net/?appName=Cluster0")
    DB_NAME = os.environ.get("DB_NAME", "unseenservice")

    # Moderator Information
    ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get("ADMINS", "8477930865 8531722224").split()]

    # Channel Information
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003407592547"))
    MIX_CHANNEL = int(os.environ.get("MIX_CHANNEL", "-1004435665031"))
    CP_CHANNEL = int(os.environ.get("CP_CHANNEL", "-1003264225931"))
    MEGA_CHANNEL = int(os.environ.get("MEGA_CHANNEL", "-1003212677737"))
except Exception as e:
    print("⚠️ Error loading config.py:", e)
    traceback.print_exc()
