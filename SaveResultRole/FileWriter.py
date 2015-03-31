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

        self.__methods = {
            'wall.get': self.__save_wall_get,
            'wall.getComments': self.__save_wall_get_comments,
            'friends.get': self.__save_friends_get,
            'likes.getList': self.__save_likes_get_list,
        }

    def __save_values(self, filename, task, values):
        filename = os.path.join(self.__data_dir, filename)

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
        
        filename = task['method'] + '_' + task['input'] + '.csv'
        self.__save_values(filename, task, values)


    def __save_friends_get(self, task, results):
        values = [(
               task['input'], 
               row,
        ) for row in results]

        filename = task['method'] + '_' + task['input'] + '.csv'
        self.__save_values(filename, task, values)


    def __save_wall_get_comments(self, task, results):
        values = [(
            task['input']['owner_id'],
            task['input']['post_id'],
            row['id'], 
            row['from_id'],
            datetime.datetime.fromtimestamp(row['date']).strftime('%Y-%m-%d %H:%M:%S'), 
            row['text'], 
            row['likes_count'],
            '|'.join(row['attachments'])
        ) for row in results]

        filename = task['method'] + '_' + task['input']['owner_id'] + '_' + task['input']['post_id'] + '.csv'
        self.__save_values(filename, task, values)

    def __save_likes_get_list(self, task, results):
        values = [(
                task['input']['type'],
                task['input']['owner_id'],
                task['input']['item_id'],
               row,
        ) for row in results]

        filename = task['method'] + '_' + task['input']['type'] + '_' + task['input']['owner_id'] + '_' + task['input']['item_id'] + '.csv'
        self.__save_values(filename, task, values)


    def save_results(self, task, data):
        if task['method'] in self.__methods:
            mthd = self.__methods[task['method']]
            mthd(task, data)
           
            
            
            
   


