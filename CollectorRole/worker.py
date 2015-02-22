import os
import sys
import logging
from datetime import datetime
from time import sleep

sys.path.insert(0, '../CommonLibs/')
from CloudQueueStorage import CloudQueueStorage
from CloudStorageHelper import CloudStorageHelper
from MessageHelper import MessageHelper
from WorkerHelper import Worker

import api_vk
import settings


class CollectorWorker(Worker):

    def __init__(self):
        Worker.__init__(self)

        self.cloud_queue_storage = CloudQueueStorage(
            settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY,
            settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB, settings.REDIS_PASSWORD)
        self.cloud_storage_helper = CloudStorageHelper(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
        self.message_helper = MessageHelper()


    def message_handler(self, message):
        self.cloud_storage_helper.delete_message(settings.QUEUE_TASKS, message.message_id, message.pop_receipt)
    
        task = self.message_helper.parse_task_message(message.message_text)
        logging.info(task)

        if task['method'] == 'wall.get' or task['method'] == 'friends.get':
            if task['method'] == 'wall.get':
                result = api_vk.vk_wall_get(task['input'])
            elif task['method'] == 'friends.get':
                result = api_vk.vk_friends_get(task['input'])

            if 'error' in result:
                logging.error(result['error'])
            else:
                message = {
                    'task': task,
                    'result': result,
                }
                self.cloud_queue_storage.put_message(settings.QUEUE_RESULTS, message)


    def work(self):
        messages = self.cloud_storage_helper.get_messages(settings.QUEUE_TASKS, 32)

        num_messages = len(messages)

        for m in messages:
            self.message_handler(m)

        logging.info('working - ' + str(num_messages))

        if num_messages > 0:
            return True
        else:
            return False




if __name__ == '__main__':

    #logging.basicConfig(filename='debug.log',level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG, format="[C] %(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    logging.info("starting...")

    worker = CollectorWorker()
    worker.run()
