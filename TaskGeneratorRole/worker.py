import os
import sys
import time
import hashlib
from datetime import datetime
import logging
from time import sleep
from azure.storage import CloudStorageAccount

sys.path.insert(0, '../CommonLibs/')
from storage_helper import create_storage_account, create_queues, get_queue_len
from message_helper import decode_task_description_message, encode_task_message


import settings


def message_handler(message):
    queue_service.delete_message(settings.QUEUE_TASKS_DESCRIPTION, message.message_id, message.pop_receipt)

    # get task description
    task = decode_task_description_message(message.message_text)
    logging.info(task)

    ## get blob etag
    #blob_prop = blob_service.get_blob_properties(settings.BLOB_DATA_CONTAINER, task['input'])
    #blol_etag = datetime.strptime(blob_prop['last-modified'], '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=pytz.UTC)

    #print(blob_prop['last-modified'])
    #print(blol_modified_time)

    ## check if file already exists
    #filename = settings.TEMP_BLOB_PATH + task['input']
    #if os.path.exists(filename):
    #    # get last modified date
    #    file_modified_time = datetime.fromtimestamp(os.path.getmtime(filename))

    #    # if blob newer - update file
    #    if blol_modified_time > file_modified_time:
    #        blob_service.get_blob_to_path(settings.BLOB_DATA_CONTAINER, task['input'], filename)
    #        logging.info(task['input'] + ': updating...')
    #    else:
    #         logging.info(task['input'] + ': up-to-date')
    #else:
    #    blob_service.get_blob_to_path(settings.BLOB_DATA_CONTAINER, task['input'], filename)
    #    logging.info(task['input'] + ': downloading...')


    # check if file already exists
    filename = settings.TEMP_BLOB_PATH + task['input']
    if not os.path.exists(filename):
        blob_service.get_blob_to_path(settings.BLOB_DATA_CONTAINER, task['input'], filename)

    # count tasks
    task_count = 0

    with open(filename, 'r') as file:
       for ids in file:

           queue_message = encode_task_message( task['method'], ids.strip() )
           queue_service.put_message(settings.QUEUE_TASKS, queue_message)

           # check task queue every 16th task
           if task_count % 16 == 0:
            
               # sleep while there are to many messages in the queues
               while True:
                    count_tasks = get_queue_len(queue_service, settings.QUEUE_TASKS)
                    count_results = get_queue_len(queue_service, settings.QUEUE_RESULTS)

                    if count_tasks < settings.MIN_QUEUE_LEN and count_results < settings.MIN_QUEUE_LEN:
                        break

                    logging.info('sleeping...')
                    sleep(10.0)

           task_count += 1




if __name__ == '__main__':

    #logging.basicConfig(filename='debug.log',level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    logging.info("starting...")

    storage_account = create_storage_account(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
    
    blob_service = storage_account.create_blob_service()
    #table_service = storage_account.create_table_service()
    queue_service = storage_account.create_queue_service()

    # create queues
    create_queues(queue_service, [settings.QUEUE_TASKS_DESCRIPTION, settings.QUEUE_TASKS, settings.QUEUE_RESULTS])

    # create dir for data
    if not os.path.isdir(settings.TEMP_BLOB_PATH):
         os.makedirs(settings.TEMP_BLOB_PATH)

    while True:
        #
        # Write your worker process here.
        #
        # You will probably want to call a blocking function such as
        #    bus_service.receive_queue_message('queue name', timeout=seconds)
        # to avoid consuming 100% CPU time while your worker has no work.
        #

        # get 32 messages from the queue
        messages = queue_service.get_messages(settings.QUEUE_TASKS_DESCRIPTION, 32)
        #messages = queue_service.peek_messages(settings.QUEUE_TASKS_DESCRIPTION, 32)

        num_messages = len(messages)

        for m in messages:
            message_handler(m)


        logging.info("working - " + str(num_messages))
        sleep(3.0)

