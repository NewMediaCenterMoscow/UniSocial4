import os
import base64
from azure.storage import CloudStorageAccount

def create_storage_account(account_name, account_key):
    if os.environ.get('EMULATED', '').lower() == 'true':
        # Running in the emulator, so use the development storage account
        storage_account = CloudStorageAccount(None, None)
    else:
        storage_account = CloudStorageAccount(account_name, account_key)


    return storage_account


def create_queues(queue_service, names):
    for name in names:
        queue_service.create_queue(name)


def get_queue_len(queue_service, name):
    queue_metadata = queue_service.get_queue_metadata(name)
    count = queue_metadata['x-ms-approximate-messages-count']    
    return int(count)

def encode_message(text):
    return base64.b64encode( text.encode() ).decode()
def decode_message(message):
    return base64.b64decode( message.encode() ).decode()