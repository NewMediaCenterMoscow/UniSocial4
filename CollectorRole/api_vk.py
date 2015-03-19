import urllib3
import json
import time
import threading
import logging
import datetime
from time import sleep

class ApiRequest():
    def __init__(self, base_address):
        self.__base_address = base_address

        self.__sleep_interval_base = 30
        self.__request_timeout = 10

        self.__request_result = None

        self.__http = urllib3.HTTPSConnectionPool(self.__base_address, maxsize=1, retries=False, timeout=self.__request_timeout)

        self.__min_request_interval = 0.3
        self.__prev_request_time = 0.0

        urllib3.disable_warnings()


    def __perform_request(self, method, method_params):
        self.__prev_request_time = time.time()
        try:
            r = self.__http.request('GET', method, fields = method_params)

            str_data = r.data.decode('utf-8') #str(r.data, 'utf-8', errors='replace')
            json_res = json.loads(str_data)

            self.__request_result = json_res

        except Exception as e:
            logging.error(e)
            self.__request_result = {'error': {'error_msg': str(e)}}

    def request(self, method, method_params, num_try = 1):
        need_sleep_time = self.__min_request_interval - (time.time() - self.__prev_request_time)
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

            return self.__request_result

        except Exception as e:
            sleep_interval = self.__sleep_interval_base ** num_try
            logging.warning('repeat #' + str(num_try) + ' in ' + str(sleep_interval) + ' sec - ' + str(e))
            sleep(sleep_interval)
            return self.request(method, method_params, num_try + 1)


class VkApiRequest(ApiRequest):
    def __init__(self):
        ApiRequest.__init__(self, 'api.vk.com')

    def request(self, method, method_params, auth = None, num_try = 1):
        method = '/method/' + method

        method_params['v'] = '5.27'

        if auth is not None:
            method_params['access_token'] = auth

        return ApiRequest.request(self, method, method_params, num_try)

    def __get_list_offset(self, items_count, current_offset = 0, count = 100):
        current_offset += count

        if current_offset > items_count:
            return -1
        else:
            return current_offset

    def __get_list(self, method, method_params, offset = 0, count = 100, auth = None):

        method_params['offset'] = offset
        method_params['count'] = count

        result = []
        i = 0
        while True:
            tmp_res = self.request(method, method_params, auth)

            if 'error' in tmp_res:
                return tmp_res

            result.extend(tmp_res['response']['items'])

            items_count = tmp_res['response']['count']
            offset = self.__get_list_offset(items_count, offset, count)

            if offset == -1:
                break

            method_params['offset'] = offset
            i += 1

            if i % 25 == 0:
                sleep(0.3)
            if i % 99 == 0:
                sleep(1)

        return result


    # api methods

    def wall_get(self, id):
        method = 'wall.get'
        params = {
            'owner_id': id,
            'filter': 'all',
        }

        result = self.__get_list(method, params, offset = 0, count = 100)

        if 'error' in result:
            return {'error': result['error']['error_msg']}

        # delete extra data
        for p in result:
            # set likes/comments/reposts count
            p['comments_count'] = p['comments']['count']
            p['likes_count'] = p['likes']['count']
            p['reposts_count'] = p['reposts']['count']

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


    def friends_get(self, id):
        method = 'friends.get'
        params = {
            'user_id': id,
            'filter': 'all',
        }

        result = self.request(method, params)

        if 'error' in result:
            return {'error': result['error']['error_msg']}

        return result['response']['items']
