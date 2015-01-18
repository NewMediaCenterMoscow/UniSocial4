import os
import sys
import logging
from datetime import datetime
from time import sleep

sys.path.insert(0, '../CommonLibs/')
from CloudQueueStorage import CloudQueueStorage
from CloudStorageHelper import CloudStorageHelper
from MessageHelper import MessageHelper

import settings
from DbHelper import DbHelper

def message_handler(message):
    cloud_storage_helper.delete_message(settings.QUEUE_RESULTS, message.message_id, message.pop_receipt)

    task = m.message_text['task']
    data = m.message_text['result']
    logging.info(task)

    db_helper.save(task, data)



if __name__ == '__main__':

    #logging.basicConfig(filename='debug.log',level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    logging.info("starting...")

    cloud_queue_storage = CloudQueueStorage(
        settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY,
        settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB, settings.REDIS_PASSWORD)
    cloud_storage_helper = CloudStorageHelper(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
    message_helper = MessageHelper()
    db_helper = DbHelper(settings.SQL_SERVER_ADDRESS, settings.SQL_SERVER_USER, settings.SQL_SERVER_PASSWORD, settings.SQL_SERVER_DATABASE)

    while True:
        #
        # Write your worker process here.
        #
        # You will probably want to call a blocking function such as
        #    bus_service.receive_queue_message('queue name', timeout=seconds)
        # to avoid consuming 100% CPU time while your worker has no work.
        #


        # get 32 messages from the queue
        #messages = cloud_queue_storage.peek_messages(settings.QUEUE_RESULTS, 32)
        messages = cloud_queue_storage.get_messages(settings.QUEUE_RESULTS, 32)

        num_messages = len(messages)

        for m in messages:
            message_handler(m)

        logging.info("working - " + str(num_messages))
        sleep(3.0)
        sys.exit()
