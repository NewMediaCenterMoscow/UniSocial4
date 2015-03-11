import requests
import logging
import datetime
from time import sleep


def get_list_offset(items_count, current_offset = 0, count = 100):
    current_offset += count

    if current_offset > items_count:
        return -1
    else:
        return current_offset

def vk_request(method, method_params, auth = None, num_try = 1, session = None):

    base_sleep_interval = 30
    
    if num_try >= 3:
        #sys.stdout.write('\nmax attempts...\n')
        logging.error('max_attempts')
        return {'error': true}

    req = requests
    if session is not None:
        req = session

    method_params['v'] = '5.27'
    
    if auth is not None:
        method_params['access_token'] = auth
    
    try:
        r = req.get('https://api.vk.com/method/' + method, params=method_params)
        result = r.json()

        return result
    except Exception as e:
        #sys.stdout.write('\nsleeping: ' + str(baseSleepInterval ** numTry) + '\n')

        logging.warning(e)
        sleep(base_sleep_interval ** num_try)
        return vk_request(method, method_params, auth, num_try + 1, session)


def vk_get_list(method, method_params, offset = 0, count = 100, auth = None):

    session = requests.Session()

    method_params['offset'] = offset
    method_params['count'] = count

    result = []
    i = 0
    while True:
        tmp_res = vk_request(method, method_params, auth, session = session)

        if 'error' in tmp_res:
            return tmp_res

        result.extend(tmp_res['response']['items'])

        items_count = tmp_res['response']['count']
        offset = get_list_offset(items_count, offset, count)

        if offset == -1:
            break

        method_params['offset'] = offset
        i += 1

        if i % 25 == 0:
            sleep(0.3)
        if i % 99 == 0:
            sleep(1)

    return result


def vk_wall_get(id):
    method = 'wall.get'
    params = {
        'owner_id': id,
        'filter': 'all',
    }

    result = vk_get_list(method, params, offset = 0, count = 100)

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

        # delete attachments
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


def vk_friends_get(id):
    method = 'friends.get'
    params = {
        'user_id': id,
        'filter': 'all',
    }

    result = vk_request(method, params)

    if 'error' in result:
        return {'error': result['error']['error_msg']}

    return result['response']['items']


