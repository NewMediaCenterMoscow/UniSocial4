import os
import datetime

import pypyodbc


class DbHelper():
    """Helper for MS SQL Server"""

    def __init__(self, address, username, password, database):
        self.__chunk_size = 50

        self.__address = address
        self.__username = username
        self.__password = password
        self.__database = database

        self.__conn_str = 'Driver={{SQL Server Native Client 11.0}};Server=tcp:{0};Database={1};Uid={2};Pwd={3};Encrypt=yes;Connection Timeout=30;'.format(address, database, username, password)

        self.__conn = pypyodbc.connect(self.__conn_str)


    def __chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
        """
        for i in range(0, len(l), n):
            yield l[i:i+n]


    def __save_wall_get(self, task, results):
        if not self.__conn.connected:
            self.__conn = pypyodbc.connect(self.__conn_str)

        cur = self.__conn.cursor()

        insert = '''INSERT INTO dbo.posts
        (id, from_id, to_id, date, type, text, comment_count, like_count, repost_count, copy_id, copy_from_id, copy_to_id, copy_text) 
        VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        chunks = self.__chunks(results, self.__chunk_size)

        for ch in chunks:

            # check date
            for row in ch:
                if isinstance(row['date'], int):
                    row['date'] = datetime.datetime.fromtimestamp(row['date'])

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
            ) for row in ch]

            cur.executemany(insert, values)
            cur.commit()

        cur.close()

    def save(self, task, results):
        if task['method'] == 'wall.get':
            self.__save_wall_get(task, results)



