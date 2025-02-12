# config.py

# Database configuration
DB_DRIVER = "{ODBC Driver 17 for SQL Server}"
DB_SERVER = "your_server_name"
DB_DATABASE = "your_database_name"
DB_USERNAME = "your_username"
DB_PASSWORD = "your_password"
DB_CONNECTION_STRING = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"

# Email configuration
SMTP_SERVER = "mail.bg"
SMTP_PORT = 465
SENDER_EMAIL = "your_sender_email@example.com"
SENDER_PASSWORD = "your_sender_password"

# File paths
BASE_OUTPUT_DIR = r""
INPUT_EXCEL_PATH = r""

# Buyer Emails table name in DB
BUYER_EMAIL_TABLE = "BuyerEmails"

# Search URLs
PRAKTIS_SEARCH_URL = "https://praktis.bg/catalogsearch/result/?q={}"
PRAKTIKER_SEARCH_URL = "https://praktiker.bg/search/{}"

# (Optionally, you can also export a list of user agents if desired)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]
