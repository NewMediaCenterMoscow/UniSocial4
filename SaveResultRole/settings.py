STORAGE_ACCOUNT_NAME = '__paste_your_storage_account_name_here__'
STORAGE_ACCOUNT_KEY = '__paste_your_storage_key_here__'

QUEUE_TASKS_DESCRIPTION = 'tasks-description'
QUEUE_TASKS = 'tasks'
QUEUE_RESULTS = 'results'

BLOB_DATA_CONTAINER = 'data'
TEMP_BLOB_PATH = './data/'

MAX_QUEUE_LEN = 512
MIN_QUEUE_LEN = 50

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = '__paste_your_password_here__'

SQL_SERVER_CONN_STR = 'DSN=MSSQL'
DATA_DIR = '.'

# import local settings
try:
    from settings_local import *
except ImportError:
    pass