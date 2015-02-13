import os
import sys
import time
import hashlib
from datetime import datetime
import logging
from time import sleep

sys.path.insert(0, '../CommonLibs/')
from CloudStorageHelper import CloudStorageHelper
from MessageHelper import MessageHelper
from WorkerHelper import Worker

import settings

class TaskGeneratorWorker(Worker):

    def __init__(self):
        Worker.__init__(self)

        self.cloud_storage_helper = CloudStorageHelper(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
        self.message_helper = MessageHelper()

        # create queues
        self.cloud_storage_helper.create_queues([settings.QUEUE_TASKS_DESCRIPTION, settings.QUEUE_TASKS, settings.QUEUE_RESULTS])

        # create dir for data
        if not os.path.isdir(settings.TEMP_BLOB_PATH):
             os.makedirs(settings.TEMP_BLOB_PATH)



    def message_handler(self, message):
        self.cloud_storage_helper.delete_message(settings.QUEUE_TASKS_DESCRIPTION, message.message_id, message.pop_receipt)

        # get task description
        task = self.message_helper.parse_task_description_message(message.message_text)
        logging.info(task)

        # check if file already exists
        filename = settings.TEMP_BLOB_PATH + task['input']
        if not os.path.exists(filename):
            self.cloud_storage_helper.get_blob_to_path(settings.BLOB_DATA_CONTAINER, task['input'], filename)

        # count tasks
        task_count = 0

        with open(filename, 'r') as file:
           for ids in file:

               queue_message = self.message_helper.create_task_message(task['method'], ids.strip())
               self.cloud_storage_helper.put_message(settings.QUEUE_TASKS, queue_message)

               # check task queue every 16th task
               if task_count % 16 == 0:
            
                   # sleep while there are to many messages in the queues
                   while True:
                        count_tasks = self.cloud_storage_helper.get_queue_len(settings.QUEUE_TASKS)
                        count_results = self.cloud_storage_helper.get_queue_len(settings.QUEUE_RESULTS)

                        if count_tasks < settings.MIN_QUEUE_LEN and count_results < settings.MIN_QUEUE_LEN:
                            break

                        logging.info('sleeping...')
                        sleep(10.0)

               task_count += 1


    def work(self):
        messages = self.cloud_storage_helper.get_messages(settings.QUEUE_TASKS_DESCRIPTION, 32)

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
    logging.basicConfig(level=logging.DEBUG)
    logging.info("starting...")

    worker = TaskGeneratorWorker()
    worker.run()
