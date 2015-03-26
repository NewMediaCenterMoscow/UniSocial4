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
        self.vk_api = api_vk.VkApiRequest()

        self.__methods = {
            'wall.get': self.__wall_get,
            'wall.getComments': self.__wall_get_comments,
            'friends.get': self.__friends_get,
        }


    def __wall_get(self, task):
        result = self.vk_api.wall_get(task['input'])
        return result
    def __friends_get(self, task):
        result = self.vk_api.friends_get(task['input'])
        return result
    def __wall_get_comments(self, task):
        input_data = task['input'].split('_')
        task['input'] = {'owner_id': input_data[0], 'post_id': input_data[1]} 
        result = self.vk_api.wall_get_comments(task['input']['owner_id'], task['input']['post_id'])
        return result

    def message_handler(self, message):
    
        task = self.message_helper.parse_task_message(message.message_text)
        logging.info(task)

        if task['method'] in self.__methods:
            api_func = self.__methods[task['method']]
            result = api_func(task)

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
        for m in messages:
            self.cloud_storage_helper.delete_message(settings.QUEUE_TASKS, m.message_id, m.pop_receipt)

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
    logging.basicConfig(level=logging.INFO, format="[C] %(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    logging.info("starting...")

    worker = CollectorWorker()
    worker.run()
