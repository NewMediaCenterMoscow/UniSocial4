import urllib3
import json
import time
import threading
import logging
import datetime
from time import sleep
from urllib3.util.retry import Retry


class ApiRequest():
    def __init__(self, base_address):
        self.__base_address = base_address

        self.__sleep_interval_base = 30
        self.__request_timeout = 10

        self.__request_result = None

        self.__http = urllib3.HTTPSConnectionPool(self.__base_address, maxsize=1, retries=Retry(False), timeout=self.__request_timeout)

        self.__request_interval = 0.1
        self.__request_interval_max = 1.0
        self.__request_interval_min = 0.0
        self.__request_prev_time = 0.0

        self.__stat_prev_time = 0.0
        self.__stat_period = 5.0
        self.__stat_number_of_requests = 0

        urllib3.disable_warnings()


    def __perform_request(self, method, method_params):
        self.__request_prev_time = time.time()
        try:
            r = self.__http.request('GET', method, fields=method_params)

            str_data = r.data.decode('utf-8') # str(r.data, 'utf-8', errors='replace')
            json_res = json.loads(str_data)

            self.__request_result = json_res

        except Exception as e:
            logging.error(e)
            self.__request_result = {'error': {'error_msg': str(e)}}

    def request(self, method, method_params, num_try=1):
        current_time = time.time()

        need_sleep_time = self.__request_interval - (current_time - self.__request_prev_time)
        if need_sleep_time > 0:
            logging.debug("sleep " + str(need_sleep_time))
            sleep(need_sleep_time)


        if num_try > 3:
            logging.error('max attempts')
            return {'error': {'error_msg': 'max attempts'}}

        try:
            thread = threading.Thread(target=self.__perform_request, kwargs={'method': method, 'method_params': method_params})
            thread.start()

            thread.join(self.__request_timeout)
            if thread.is_alive():
                logging.warning('timeout')
                thread.join()
                raise Exception(self.__request_result['error']['error_msg'])

            # success request - try to minmize request time
            current_time = time.time()

            self.__stat_number_of_requests += 1
            if self.__request_interval > self.__request_interval_min:
                self.__request_interval -= 0.1

            elapsed_time = current_time - self.__stat_prev_time
            if elapsed_time > self.__stat_period:
                message = '{0} requests in {1:.2f} sec. current request interval: {2}'.format(self.__stat_number_of_requests, elapsed_time, self.__request_interval)
                logging.info(message)
                self.__stat_number_of_requests = 0
                self.__stat_prev_time = current_time

            return self.__request_result

        except Exception as e:
            sleep_interval = self.__sleep_interval_base ** num_try

            # increase request time
            if self.__request_interval < self.__request_interval_max:
                self.__request_interval += 0.1

            logging.warning('repeat #' + str(num_try) + ' in ' + str(sleep_interval) + ' sec - ' + str(e))
            sleep(sleep_interval)

            return self.request(method, method_params, num_try + 1)


class VkApiRequest(ApiRequest):
    def __init__(self):
        ApiRequest.__init__(self, 'api.vk.com')

        self.__next_from_methods = ['newsfeed.search']
        self.__version = '5.27'



    def request(self, method, method_params, num_try=1, auth=None):
        if not method.startswith('/method/'):
            method = '/method/' + method

        method_params['v'] = self.__version

        if auth is not None:
            method_params['access_token'] = auth

        return ApiRequest.request(self, method, method_params, num_try)

    def __get_list_offset(self, items_count, current_offset=0, count=100, limit=0):
        current_offset += count

        if current_offset > items_count or (limit != 0 and items_count >= limit):
            return -1
        else:
            return current_offset

    def __get_list(self, method, method_params, offset=0, count=100, limit=0, auth=None):

        if method in self.__next_from_methods:
            next_from_method = True
        else:
            next_from_method = False

        if not next_from_method:
            method_params['offset'] = offset
            method_params['count'] = count
        else:
            method_params['count'] = count

        result = []
        i = 0
        while True:
            tmp_res = self.request(method, method_params, auth=auth)

            if 'error' in tmp_res:
                return tmp_res

            result.extend(tmp_res['response']['items'])

            if not next_from_method:
                items_count = tmp_res['response']['count']
                offset = self.__get_list_offset(items_count, offset, count, limit)

                if offset == -1:
                    break

                method_params['offset'] = offset
            else:
                if 'next_from' in tmp_res['response']:
                    method_params['start_from'] = tmp_res['response']['next_from']
                else:
                    break

            i += 1

            if i % 25 == 0:
                sleep(0.3)
            if i % 99 == 0:
                sleep(1)

        return result

    def __chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]


    # api methods

    def wall_get(self, id, custom_perameters=None, limit=0):
        method = 'wall.get'
        params = {
            'owner_id': id,
            'filter': 'all',
        }
        if custom_perameters is not None:
            params.update(custom_perameters)

        count = 100
        if 'count' in params:
            count = params['count']


        result = self.__get_list(method, params, offset=0, count=count, limit=limit)

        if 'error' in result:
            return {'error': result['error']['error_msg']}

        # delete extra data
        for p in result:

            # set likes/comments/reposts count
            p['comments_count'] = p['comments']['count'] if 'comments' in p else 0
            p['likes_count'] = p['likes']['count'] if 'likes' in p else 0
            p['reposts_count'] = p['reposts']['count'] if 'reposts' in p else 0

            p.pop('comments', None)
            p.pop('likes', None)
            p.pop('reposts', None)

            # delete attachments but save links
            if 'attachments' in p:
                p['attachments'] = [a['link']['url'] for a in p['attachments'] if a['type'] == 'link']
            else:
                p['attachments'] = []

            # set copy-related parameters
            if 'copy_history' in p:
                p['copy_id'] = p['copy_history'][0]['id']
                p['copy_owner_id'] = p['copy_history'][0]['owner_id']
                p['copy_from_id'] = p['copy_history'][0]['from_id']
                p['copy_text'] = p['copy_history'][0]['text']

                p.pop('copy_history', None)


        return result


    def friends_get(self, id, custom_perameters=None):
        method = 'friends.get'
        params = {
            'user_id': id,
            'filter': 'all',
        }
        if custom_perameters is not None:
            params.update(custom_perameters)

        result = self.request(method, params)

        if 'error' in result:
            return {'error': result['error']['error_msg']}

        return result['response']['items']

    def wall_get_comments(self, owner_id, post_id, custom_perameters=None, limit=0):
        method = 'wall.getComments'
        params = {
            'owner_id': owner_id,
            'post_id': post_id,
            'need_likes': 1,
        }
        if custom_perameters is not None:
            params.update(custom_perameters)

        count = 100
        if 'count' in params:
            count = params['count']

        result = self.__get_list(method, params, offset=0, count=count, limit=limit)

        if 'error' in result:
            return {'error': result['error']['error_msg']}

        # delete extra data
        for p in result:
            # set likes/comments/reposts count
            if 'likes' in p:
                p['likes_count'] = p['likes']['count']
                p.pop('likes', None)
            else:
                p['likes_count'] = 0

            # delete attachments but save links
            if 'attachments' in p:
                p['attachments'] = [a['link']['url'] for a in p['attachments'] if a['type'] == 'link']
            else:
                p['attachments'] = []


        return result


    def likes_get_list(self, type, owner_id, item_id, custom_perameters=None, limit=0):
        method = 'likes.getList'
        params = {
            'type': type,
            'owner_id': owner_id,
            'item_id': item_id,

        }
        if custom_perameters is not None:
            params.update(custom_perameters)

        count = 1000
        if 'count' in params:
            count = params['count']

        result = self.__get_list(method, params, offset=0, count=count, limit=limit)

        if 'error' in result:
            return {'error': result['error']['error_msg']}


        return result

    def users_get(self, ids, custom_perameters=None):
        method = 'users.get'
        params = {
            'fields': 'education,contacts,nickname, screen_name, sex, bdate, city, country, timezone, photo_50, photo_100, photo_200, photo_max, has_mobile',
        }
        if custom_perameters is not None:
            params.update(custom_perameters)

        batch_size = 1000
        result = []

        if not isinstance(ids, list):
            ids = list(ids)

        for ids_batch in self.__chunks(ids, batch_size):
            params['user_ids'] = ','.join(ids_batch)
            partial_result = self.request(method, params)

            if 'error' in partial_result:
                return {'error': result['error']['error_msg']}

            result.extend(partial_result['response'])

        return result

    def newsfeed_search(self, q, custom_parameters=None, limit=0):
        method = 'newsfeed.search'
        params = {
            'q': q,
        }
        if custom_parameters is not None:
            params.update(custom_parameters)

        count = 200
        if 'count' in params:
            count = params['count']

        result = self.__get_list(method, params, offset=0, count=count, limit=limit)

        if 'error' in result:
            return {'error': result['error']['error_msg']}

        # delete extra data
        for p in result:
            # set likes/comments/reposts count
            p['comments_count'] = p['comments']['count'] if 'comments' in p else 0
            p['likes_count'] = p['likes']['count'] if 'likes' in p else 0
            p['reposts_count'] = p['reposts']['count'] if 'reposts' in p else 0

            p.pop('comments', None)
            p.pop('likes', None)
            p.pop('reposts', None)

            # delete attachments but save links
            if 'attachments' in p:
                p['attachments'] = [a['link']['url'] for a in p['attachments'] if a['type'] == 'link']
            else:
                p['attachments'] = []

        return result

