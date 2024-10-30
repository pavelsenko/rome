import os

DATABASE_PGSQL = {
    'engine': 'postgresql',
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'name': os.getenv('DB_NAME', 'rome'),
}