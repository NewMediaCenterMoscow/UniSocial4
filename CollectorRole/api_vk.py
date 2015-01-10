import requests
import logging
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
        return vk_request(method, methodParams, needAuth, num_try + 1, session)


def vk_get_list(method, method_params, offset = 0, count = 100, auth = None):

    session = requests.Session()

    method_params['offset'] = offset
    method_params['count'] = count

    result = []

    while True:
        tmp_res = vk_request(method, method_params, auth, session = session)

        result.extend(tmp_res['response']['items'])

        items_count = tmp_res['response']['count']
        offset = get_list_offset(items_count, offset, count)

        if offset == -1:
            break

        method_params['offset'] = offset

    return result


def vk_wall_get(id):
    method = 'wall.get'
    params = {
        'owner_id': id,
        'filter': 'all',
    }

    result = vk_get_list(method, params, offset = 0, count = 100)

    ## delete extra data
    #for p in result:
    #    # set likes/comments/reposts count
    #    p['comments_count'] = p['comments']['count']
    #    p['likes_count'] = p['likes']['count']
    #    p['reposts_count'] = p['reposts']['count']

    #    p.pop('comments_count', None)
    #    p.pop('likes_count', None)
    #    p.pop('reposts_count', None)

    #    # delete attachments
    #    p.pop('attachments', None)

    #    # set copy-related parameters
    #    if 'copy_history' in p:
    #        p['copy_id'] = p['copy_history'][0]['id']
    #        p['copy_owner_id'] = p['copy_history'][0]['owner_id']
    #        p['copy_from_id'] = p['copy_history'][0]['from_id']
    #        p['copy_text'] = p['copy_history'][0]['text']

    #        p.pop('copy_history', None)


    return result