import os
from pathlib import Path
from dotenv import load_dotenv

# Get the config directory (where this file lives)
config_dir = Path(__file__).parent
env_path = config_dir / '.env'

# Load environment variables from .env file
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded configuration from {env_path}")
else:
    print(f"⚠️ Warning: {env_path} not found!")

# Verify critical variables are loaded
critical_vars = ['GOOGLE_API_KEY_1', 'ORACLE_CLOUD_PASSWORD', 'ORACLE_CLOUD_DSN']
missing = [var for var in critical_vars if not os.getenv(var)]

if missing:
    print(f"⚠️ Missing configuration: {', '.join(missing)}")
else:
    print("✅ All critical configuration loaded successfully")
