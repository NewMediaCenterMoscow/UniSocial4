STORAGE_ACCOUNT_NAME = '__paste_your_storage_account_name_here__'
STORAGE_ACCOUNT_KEY = '__paste_your_storage_key_here__'

QUEUE_TASKS_DESCRIPTION = 'tasks-description'
QUEUE_TASKS = 'tasks'
QUEUE_RESULTS = 'results'

BLOB_DATA_CONTAINER = 'data'
TEMP_BLOB_PATH = './data/'

MAX_QUEUE_LEN = 512
MIN_QUEUE_LEN = 50

# import local settings
try:
    from settings_local import *
except ImportError:
    pass