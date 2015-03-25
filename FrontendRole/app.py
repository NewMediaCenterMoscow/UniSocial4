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


sys.path.insert(0, '../CommonLibs/')
from CloudQueueStorage import CloudQueueStorage
from CloudStorageHelper import CloudStorageHelper
from MessageHelper import MessageHelper  

import settings



if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    bottle.debug(True)



@route('/', name='tasks')
@view('tasks.html')
def tasks():

    tasks = [{'name': 'Task 1'},{'name': 'Task 2'}]

    datasets = cloud_storage_helper.get_blobs_list(settings.BLOB_DATA_CONTAINER)

    return view_template(tasks=tasks, datasets = datasets)


@post('/tasks/add', name='tasks_add')
@view('tasks_add.html')
def tasks_add():

    method = request.forms.get('method')
    input = request.forms.get('input')

    queue_message = message_helper.create_task_description_message(method, input)
    cloud_storage_helper.put_message(settings.QUEUE_TASKS_DESCRIPTION, queue_message)

    results = {'text': 'Task added', 'message': queue_message}

    return view_template(results=results)


def wsgi_app():
    """Returns the application to make available through wfastcgi. This is used
    when the site is published to Microsoft Azure."""
    return default_app()

if __name__ == '__main__':

    cloud_storage_helper = CloudStorageHelper(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
    message_helper = MessageHelper()

    # Starts a local test server.
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    bottle.run(server='wsgiref', host=HOST, port=PORT, reloader=True)
