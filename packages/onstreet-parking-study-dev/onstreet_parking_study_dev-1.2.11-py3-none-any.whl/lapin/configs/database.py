import os

STAGING_DATABASE = {
    "engine_type": "postgresql",
    "engine_conf": {
        "host": os.getenv("POSTGRES_HOST", ""),
        "user": os.getenv("POSTGRES_USER", ""),
        "pwd": os.getenv("POSTGRES_PASSWORD", ""),
        "database": os.getenv("POSTGRES_DB", "Staging"),
        "port": os.getenv("POSTGRES_PORT", 5432),
    },
}
