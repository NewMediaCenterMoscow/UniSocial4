"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

import os
import sys
import json
import pickle
import base64
import bottle
from bottle import default_app, redirect, route, post, request, view, template, url

from bottle_helpers import view_template
import settings


#sys.path.insert(0, '../CommonLibs/')
from storage_helper import create_storage_account, create_queues, encode_message, decode_message
from message_helper import encode_task_description_message

if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    bottle.debug(True)


# get data blobs
storage_account = create_storage_account(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
blob_service = storage_account.create_blob_service()
queue_service = storage_account.create_queue_service()


@route('/', name='tasks')
@view('tasks.html')
def tasks():

    tasks = [{'name': 'Task 1'},{'name': 'Task 2'}]

    datasets = blob_service.list_blobs(settings.BLOB_DATA_CONTAINER)


    return view_template(tasks=tasks, datasets = datasets)


@post('/tasks/add', name='tasks_add')
@view('tasks_add.html')
def tasks_add():

    method = request.forms.get('method')
    input = request.forms.get('input')

    queue_message = encode_task_description_message(method, input)
    queue_service.put_message(settings.QUEUE_TASKS_DESCRIPTION, queue_message)

    results = {'text': 'Task added', 'message': queue_message}

    return view_template(results=results)


def wsgi_app():
    """Returns the application to make available through wfastcgi. This is used
    when the site is published to Microsoft Azure."""
    return default_app()

if __name__ == '__main__':
    # Starts a local test server.
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    bottle.run(server='wsgiref', host=HOST, port=PORT, reloader=True)
