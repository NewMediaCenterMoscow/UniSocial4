import os
import csv
import logging
import datetime

from AbstractWriter import AbstractWriter

class FileWriter(AbstractWriter):
    """Save results to a flat file"""

    def __init__(self, data_dir):
        AbstractWriter.__init__(self)

        self.__data_dir = data_dir

    def __save_values(self, task, values):
        filename = os.path.join(self.__data_dir, task['method'] + '_' + task['input'] + '.csv')

        with open(filename, 'a') as file:
            writer = csv.writer(file)
            writer.writerows(values)

    def __save_wall_get(self, task, results):
        values = [(
            row['id'], 
            row['from_id'],
            row['owner_id'], # to_id <- owner_id
            datetime.datetime.fromtimestamp(row['date']).strftime('%Y-%m-%d %H:%M:%S'), 
            row['post_type'], # type <- post_type
            row['text'], 
            row['comments_count'], # add 's' at the end (comment_count <- comments_count)
            row['likes_count'],  # add 's' at the end
            row['reposts_count'],  # add 's' at the end
            row['copy_id'] if 'copy_id' in row else 0, 
            row['copy_from_id'] if 'copy_from_id' in row else 0,
            row['copy_to_id'] if 'copy_to_id' in row else 0,
            row['copy_text'] if 'copy_text' in row else '',
            '|'.join(row['attachments'])
        ) for row in results]

        self.__save_values(task, values)


    def __save_friends_get(self, task, results):
        values = [(
               task['input'], 
               row,
        ) for row in results]

        self.__save_values(task, values)



    def save_results(self, task, data):
        if task['method'] == 'wall.get':
            self.__save_wall_get(task, data)
        if task['method'] == 'friends.get':
            self.__save_friends_get(task, data)       


