import os
import sys
import logging
from datetime import datetime
from time import sleep

sys.path.insert(0, '../CommonLibs/')
from CloudQueueStorage import CloudQueueStorage
from CloudStorageHelper import CloudStorageHelper
from MessageHelper import MessageHelper
#from DbHelper import DbHelper
from FileWriter import FileWriter
from WorkerHelper import Worker

import settings


class SaveResultWorker(Worker):

    def __init__(self):
        Worker.__init__(self)

        self.cloud_queue_storage = CloudQueueStorage(
            settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY,
            settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB, settings.REDIS_PASSWORD)
        self.cloud_storage_helper = CloudStorageHelper(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
        self.message_helper = MessageHelper()
        #self.db_helper = DbHelper(settings.SQL_SERVER_CONN_STR)
        self.results_writer = FileWriter(settings.DATA_DIR)

    def message_handler(self, message):
        self.cloud_storage_helper.delete_message(settings.QUEUE_RESULTS, message.message_id, message.pop_receipt)

        task = message.message_text['task']
        data = message.message_text['result']
        logging.info(task)

        #self.db_helper.save(task, data)
        self.results_writer.save_results(task, data)

    def work(self):
        messages = self.cloud_queue_storage.get_messages(settings.QUEUE_RESULTS, 32)

        num_messages = len(messages)

        for m in messages:
            if 'task' in m.message_text:
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

    worker = SaveResultWorker()
    worker.run()



