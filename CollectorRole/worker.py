import os
import sys
import logging
from datetime import datetime
from time import sleep

from azure.storage import CloudStorageAccount

sys.path.insert(0, '../CommonLibs/')
from storage_helper import create_storage_account, create_queues
from message_helper import decode_task_message
from CloudQueueStorage import CloudQueueStorage

import api_vk
import settings



def message_handler(message):
    #queue_service.delete_message(settings.QUEUE_TASKS, message.message_id, message.pop_receipt)

    task = decode_task_message(message.message_text)
    logging.info(task)

    if task['method'] == 'wall.get':
        result = api_vk.vk_wall_get(task['input'])

        cloud_queue_storage.put_message(settings.QUEUE_RESULTS, result)

if __name__ == '__main__':

    #logging.basicConfig(filename='debug.log',level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    logging.info("starting...")

    cloud_queue_storage = CloudQueueStorage(
        settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY,
        settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB, settings.REDIS_PASSWORD)

    storage_account = create_storage_account(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
    
    blob_service = storage_account.create_blob_service()
    #table_service = storage_account.create_table_service()
    queue_service = storage_account.create_queue_service()


    while True:
        #
        # Write your worker process here.
        #
        # You will probably want to call a blocking function such as
        #    bus_service.receive_queue_message('queue name', timeout=seconds)
        # to avoid consuming 100% CPU time while your worker has no work.
        #


        # get 32 messages from the queue
        #messages = queue_service.get_messages(settings.QUEUE_TASKS, 32)
        messages = queue_service.peek_messages(settings.QUEUE_TASKS, 32)

        num_messages = len(messages)

        for m in messages:
            message_handler(m)

        logging.info("working - " + str(num_messages))
        sleep(3.0)
        sys.exit()


