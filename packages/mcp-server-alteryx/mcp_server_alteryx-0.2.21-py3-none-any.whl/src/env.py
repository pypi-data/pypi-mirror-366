import os

ALTERYX_CLIENT_ID = os.getenv("ALTERYX_CLIENT_ID")
ALTERYX_CLIENT_SECRET = os.getenv("ALTERYX_CLIENT_SECRET")

ALTERYX_API_HOST = os.getenv("ALTERYX_API_HOST", "http://localhost/webapi/")

ALTERYX_VERIFY_SSL = os.getenv("ALTERYX_VERIFY_SSL", "1").lower() not in ("0", "false", "no")

ALTERYX_USERNAME = os.getenv("ALTERYX_USERNAME")
ALTERYX_PASSWORD = os.getenv("ALTERYX_PASSWORD")
