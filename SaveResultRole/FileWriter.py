import os
import sys
import csv
import codecs
import logging
import datetime
import base64

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
            'users.get': self.__save_users_get,
            'newsfeed.search': self.__save_newsfeed_search,
        }

    def __save_values(self, filename, task, values):
        filename = os.path.join(self.__data_dir, filename)

        with codecs.open(filename, 'a', encoding="utf-8") as file:
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
            row['likes_count'], # add 's' at the end
            row['reposts_count'], # add 's' at the end
            row.get('copy_id', 0),
            row.get('copy_from_id', 0),
            row.get('copy_to_id', 0),
            row.get('copy_text', ''),
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

        filename = task['method'] + '_' + task['input']['owner_id'] + '.csv'
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

    def __save_users_get(self, task, results):
        values = [(
            row['id'],
            row['first_name'],
            row['last_name'],
            row['sex'],
            row.get('nickname', ''),
            row.get('screen_name', ''),
            row.get('bdate', ''),
            row['city']['id'] if 'city' in row else '',
            row['country']['id'] if 'country' in row else '',
            True if 'deactivated' in row else False,
            row.get('photo_50', ''),
            row.get('photo_100', ''),
            row.get('photo_200', ''),
            row.get('photo_max', ''),
            row.get('has_mobile', 0),
            row.get('mobile_phone', ''),
            row.get('home_phone', ''),
            row.get('university', ''),
            row.get('university_name', ''),
            row.get('faculity', ''),
            row.get('faculity_name', ''),
            row.get('graduation', ''),
        ) for row in results]

        if 'output_file' in task:
            filename = task['output_file']
        else:
            filename = task['method'] + '_' + str(len(task['input'])) + '.csv'

        self.__save_values(filename, task, values)


    def __save_newsfeed_search(self, task, results):
        values = [(
            task['query'],
            row['id'],
            row['from_id'],
            row['owner_id'], # to_id <- owner_id
            row.get('post_id', 0),
            row['post_type'],
            datetime.datetime.fromtimestamp(row['date']).strftime('%Y-%m-%d %H:%M:%S'),
            row['text'],
            row['comments_count'], # add 's' at the end (comment_count <- comments_count)
            row['likes_count'], # add 's' at the end
            row['reposts_count'], # add 's' at the end
            '|'.join(row['attachments'])
        ) for row in results]

        if 'output_file' in task:
            filename = task['output_file']
        else:
            filename = task['method'] + '_' + base64.urlsafe_b64encode(task['query'].encode()).decode() + '.csv'

        self.__save_values(filename, task, values)




    def save_results(self, task, data):
        if isinstance(data, dict) and 'error' in data:
            print("Save error!", file=sys.stderr)
            return

        if task['method'] in self.__methods:
            mthd = self.__methods[task['method']]
            mthd(task, data)





