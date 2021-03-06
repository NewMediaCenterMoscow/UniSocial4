import base64
import logging

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


    def decode_messages(self, messages):
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
        try:
            queue_metadata = self.__queue_service.get_queue_metadata(name)
            count = queue_metadata['x-ms-approximate-messages-count']    
            return int(count)
        except Exception as e:
            logging.error("getting queue metadata: {0}".format(e))
            return -1

    def put_message(self, queue, message, encode = True):
        if encode:
            message = self.encode_message(message)

        try:
            self.__queue_service.put_message(queue, message)
        except Exception as e:
            logging.error("put messages: {0}".format(e))

    def get_messages(self, queue, num_of_messages=None, decode = True):
        try:
            messages = self.__queue_service.get_messages(queue, num_of_messages)
        except Exception as e:
            logging.error("get messages: {0}".format(e))
            messages = []

        if decode:
            self.decode_messages(messages)

        return messages


    def peek_messages(self, queue, num_of_messages=None, decode = True):
        try:
            messages = self.__queue_service.peek_messages(queue, num_of_messages)
        except Exception as e:
            logging.error("peek messages: {0}".format(e))
            messages = []

        if decode:
            self.decode_messages(messages)

        return messages

    def delete_message(self, queue, message_id, popreceipt):
        try:
            self.__queue_service.delete_message(queue, message_id, popreceipt)
        except Exception as e:
            logging.error("delete messages: {0}".format(e))
            

    # Blobs

    def get_blobs_list(self, container):
        blobs = self.__blob_service.list_blobs(container)
        return blobs

    def get_blob_to_path(self, container, blob_name, file_name):
        self.__blob_service.get_blob_to_path(container, blob_name, file_name)
