import os
import logging
import datetime

import pypyodbc


class DbHelper():
    """Helper for MS SQL Server"""

    def __init__(self, conn_str):
        self.__chunk_size = 50
        self.__conn_str = conn_str

        self.__conn = pypyodbc.connect(self.__conn_str)


    def __chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
        """
        for i in range(0, len(l), n):
            yield l[i:i+n]


    def __save_values(self, insert, values):
        if not self.__conn.connected:
            self.__conn = pypyodbc.connect(self.__conn_str)
        
        cur = self.__conn.cursor()

        chunks = self.__chunks(values, self.__chunk_size)
        for ch in chunks:

            try:
                cur.executemany(insert, ch)
                cur.commit()
            except pypyodbc.IntegrityError as e:
                logging.warning('insert by rows...')

                for row in ch: 
                    try:
                        cur.execute(insert, row)
                        cur.commit()
                    except pypyodbc.IntegrityError as e:
                        logging.warning('dublicate...')

        cur.close()


    def __save_wall_get(self, task, results):

        for p in results:
            if isinstance(p['date'], int):
                p['date'] = datetime.datetime.fromtimestamp(p['date'])

        insert = '''
INSERT INTO dbo.posts
(id, from_id, to_id, date, type, text, comment_count, like_count, repost_count, copy_id, copy_from_id, copy_to_id, copy_text) 
VALUES 
(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

        values = [(
            row['id'], 
            row['from_id'],
            row['owner_id'], # to_id <- owner_id
            row['date'].strftime('%Y-%m-%d %H:%M:%S'), 
            row['post_type'], # type <- post_type
            row['text'], 
            row['comments_count'], # add 's' at the end (comment_count <- comments_count)
            row['likes_count'],  # add 's' at the end
            row['reposts_count'],  # add 's' at the end
            row['copy_id'] if 'copy_id' in row else 0, 
            row['copy_from_id'] if 'copy_from_id' in row else 0,
            row['copy_to_id'] if 'copy_to_id' in row else 0,
            row['copy_text'] if 'copy_text' in row else '',
        ) for row in results]

        self.__save_values(insert, values)


    def __save_friends_get(self, task, results):

        insert = '''
INSERT INTO dbo.friends
(user_id, friend_id) 
VALUES 
(?, ?)
'''

        values = [(
               task['input'], 
               row,
        ) for row in results]

        self.__save_values(insert, values)


    def save(self, task, results):
        if task['method'] == 'wall.get':
            self.__save_wall_get(task, results)
        if task['method'] == 'friends.get':
            self.__save_friends_get(task, results)


