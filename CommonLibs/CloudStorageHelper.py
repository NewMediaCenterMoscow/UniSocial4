import base64
from azure.storage import CloudStorageAccount

class CloudStorageHelper(object):
    """Helper for Azure Storage (Queue, Blob)"""

    def __init__(self, account_name = None, account_key = None):
        self.__account_name = account_name
        self.__account_key = account_key

        self.__storage_account = CloudStorageAccount(account_name, account_key)

        self.__queue_service = self.__storage_account.create_queue_service()
        self.__blob_service = self.__storage_account.create_blob_service()
        self.__table_service = None


    def _decode_messages(self, messages):
        for m in messages:
            m.message_text = self.decode_message(m.message_text)


    def encode_message(self, message):
        """Convert message to base64-string"""
        if isinstance(message, str):
            message = message.encode()

        result = base64.b64encode(message).decode()
        return result

    def decode_message(self, message):
        """Convert base64-string to a string message"""
        return base64.b64decode( message.encode() ).decode()


    # Queues

    def create_queue(self, name):
        self.__queue_service.create_queue(name)

    def create_queues(self, names):
        for name in names:
            self.__queue_service.create_queue(name)

    def get_queue_len(self, name):
        queue_metadata = self.__queue_service.get_queue_metadata(name)
        count = queue_metadata['x-ms-approximate-messages-count']    
        return int(count)

    def put_message(self, queue, message, encode = True):
        if encode:
            message = self.encode_message(message)

        self.__queue_service.put_message(queue, message)

    def get_messages(self, queue, num_of_messages=None, decode = True):
        messages = self.__queue_service.get_messages(queue, num_of_messages)

        if decode:
            _decode_messages(messages)

        return messages

    def peek_messages(self, queue, num_of_messages=None, decode = True):
        messages = self.__queue_service.peek_messages(queue, num_of_messages)

        if decode:
            _decode_messages(messages)

        return messages

    def delete_message(self, queue, message_id, popreceipt):
        self.__queue_service.delete_message(queue, message_id, popreceipt)

    # Blobs

    def get_blobs_list(self, container):
        if self.__blob_service is None:
            self.__blob_service = self.__storage_account.create_blob_service()

        blobs = self.__blob_service.list_blobs(container)
        return blobs

