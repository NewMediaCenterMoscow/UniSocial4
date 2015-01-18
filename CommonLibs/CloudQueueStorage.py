import uuid
import pickle
import json
import zlib

import redis
from CloudStorageHelper import CloudStorageHelper

class CloudQueueStorage(object):
    """Queue service with saving a huge mesages in Redis"""

    __queue_message_limit = 40 * 1024 # Azure Queue Storage message size limit is 64Kb, but for base64 it is 48Kb (~75%)

    __MESSAGE_CODED = 'p'
    __MESSAGE_NO_CODED = 'n'
    __MESSAGE_IN_REDIS = 'redis'
    __MESSAGE_IN_QUEUE = 'queue'
    __MESSAGE_PART_DELIMETER = ':'

    def __init__(self, 
                 storage_account_name = None, storage_account_key = None, 
                 redis_host='localhost', redis_port=6379, redis_db=0, redis_password=None):
        
        self.__cloud_storage = CloudStorageHelper(storage_account_name, storage_account_key)
        self.__redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)


    def __process_messages(self, messages):
        for m in messages:
            msg = m.message_text

            msg_parts = m.message_text.split(self.__MESSAGE_PART_DELIMETER)

            # see put_message function for details
            if msg_parts[1] == self.__MESSAGE_IN_QUEUE:
                msg = msg_parts[2]
            elif msg_parts[1] == self.__MESSAGE_IN_REDIS:
                key = msg_parts[2]
                encoded_message = self.__redis.get(key)
                msg = zlib.decompress(encoded_message)

                # del redis record
                self.__redis.delete(key)

            if msg_parts[0] == self.__MESSAGE_CODED:
                msg = json.loads(msg.decode(), 0)

            m.message_text = msg

    def put_message(self, queue, message):
        # message format (default): 
        #  the frist symbol - "p" or "n: for pickle/ not pickle
        #  "p:queue:<message>" for queued message
        #  "p:redis:<redis-key>" for messages with body in redis

        if isinstance(message, bytes):
            message = message.decode()

        queue_msg = self.__MESSAGE_NO_CODED
        if not isinstance(message, str):
            message = json.dumps(message)
            queue_msg = self.__MESSAGE_CODED
        queue_msg += self.__MESSAGE_PART_DELIMETER


        # if the message is small - put it directly to queue
        if len(message) < self.__queue_message_limit:
            queue_msg += self.__MESSAGE_IN_QUEUE + self.__MESSAGE_PART_DELIMETER + message
            self.__cloud_storage.put_message(queue, queue_msg)
        else: # message is large so put it to redis and save link in queue

            # get random key for redis and check it not exists
            while True:
                key = str(uuid.uuid4())
                if not self.__redis.exists(key):
                    break

            # put data to redis
            encoded_message = zlib.compress(message.encode())
            self.__redis.set(key, encoded_message)

            # put message to queue
            queue_msg += self.__MESSAGE_IN_REDIS + self.__MESSAGE_PART_DELIMETER + key
            self.__cloud_storage.put_message(queue, queue_msg)

    def get_messages(self, queue, num_of_messages=None):
        messages = self.__cloud_storage.get_messages(queue, num_of_messages)

        self.__process_messages(messages)

        return messages

    def peek_messages(self, queue, num_of_messages=None):
        messages = self.__cloud_storage.peek_messages(queue, num_of_messages)

        self.__process_messages(messages)

        return messages


    def delete_message(queue, message_id, popreceipt):
        self.__cloud_storage.delete_message(queue, message_id, popreceipt)