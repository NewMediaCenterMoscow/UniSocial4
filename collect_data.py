import os
import sys
from datetime import datetime

sys.path.insert(1, './CollectorRole/')
sys.path.insert(1, './SaveResultRole/')

import click

from api_vk import VkApiRequest
from FileWriter import FileWriter


#########
# Helpers
#########
def readlines(file_handle):
    for l in file_handle:
        cl = l.strip()
        if len(cl) > 0:
            yield cl

def check_error(results):
    if isinstance(results, dict):
        if 'error' in results:
            return True
    return False

@click.group()
@click.pass_context
def main(ctx):
    ctx.get_help()


#########
# Methods
#########
@main.command('profiles')
@click.argument('input_file', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.argument('output_file')
def profiles(input_file, output_dir, output_file):
    ids = readlines(input_file)

    task = {'method': 'users.get', 'input': ids, 'output_file': output_file}

    api = VkApiRequest()
    results = api.users_get(ids)
    if not check_error(results):
        writer = FileWriter(output_dir)
        writer.save_results(task, results)

    click.echo('All done!')

@main.command('likes')
@click.argument('input_file', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def likes(input_file, output_dir):
    ids = readlines(input_file)

    task = {'method': 'likes.getList', 'input': {'type': '', 'owner_id': '', 'item_id':''}}

    api = VkApiRequest()
    writer = FileWriter(output_dir)

    for t in ids:
        dt = t.split('_')
        task['input']['type'] = dt[0]
        task['input']['owner_id'] = dt[1]
        task['input']['item_id'] = dt[2]

        results = api.likes_get_list(task['input']['type'], task['input']['owner_id'], task['input']['item_id'])
        if check_error(results):
            continue
        else:
            writer.save_results(task, results)

    click.echo('All done!')


@main.command('walls')
@click.argument('input_file', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def walls(input_file, output_dir):
    ids = readlines(input_file)

    task = {'method': 'wall.get', 'input': ''}

    api = VkApiRequest()
    writer = FileWriter(output_dir)

    for t in ids:
        task['input'] = t

        results = api.wall_get(task['input'])
        if check_error(results):
            print(results)
            continue
        else:
            writer.save_results(task, results)

    click.echo('All done!')


@main.command('search')
@click.argument('query')
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.option('--output_file', default=None, help='Filename to save the results')
def search(query, output_dir, output_file):

    task = {'method': 'newsfeed.search', 'query': query}
    if output_file is not None:
        task['output_file'] = output_file

    api = VkApiRequest()
    results = api.newsfeed_search(query)

    if not check_error(results):
        writer = FileWriter(output_dir)
        writer.save_results(task, results)

    click.echo('All done!')


@main.command('comments')
@click.argument('input_file', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def likes(input_file, output_dir):
    ids = readlines(input_file)

    task = {'method': 'wall.getComments', 'input': {'owner_id': '', 'post_id':''}}

    api = VkApiRequest()
    writer = FileWriter(output_dir)

    i = 0
    time_start = datetime.now()
    time_prev = time_start
    report_at = 64
    for t in ids:
        dt = t.split('_')
        task['input']['owner_id'] = dt[0]
        task['input']['post_id'] = dt[1]

        results = api.wall_get_comments(task['input']['owner_id'], task['input']['post_id'])
        if check_error(results):
            continue
        else:
            writer.save_results(task, results)

        i += 1
        if i % report_at == 0:
            time_now = datetime.now()
            time_elapsed = time_now - time_prev
            throuput = report_at / time_elapsed.seconds
            print('Processed: {0} ({1:.2f}/sec)'.format(i, throuput))

            time_prev = time_now

    time_end = datetime.now()
    click.echo('All done! Processed {0} items in {1}'.format(i, time_end - time_start))



@main.command('groups')
@click.argument('input_file', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.option('--output_file', default=None, help='Filename to save the results')
def groups(input_file, output_dir, output_file):
    ids = readlines(input_file)

    task = {'method': 'groups.get', 'input': '', }
    if output_file is not None:
        task['output_file'] = output_file

    access_token = os.getenv('VK_ACCESS_TOKEN', '')
    api = VkApiRequest(access_token=access_token)
    writer = FileWriter(output_dir)

    i = 0
    time_start = datetime.now()
    time_prev = time_start
    report_at = 64
    for id in ids:
        task['input'] = id

        results = api.groups_get(task['input'])
        if check_error(results):
            continue
        else:
            writer.save_results(task, results)

        i += 1
        if i % report_at == 0:
            time_now = datetime.now()
            time_elapsed = time_now - time_prev
            throuput = report_at / time_elapsed.seconds
            print('Processed: {0} ({1:.2f}/sec)'.format(i, throuput))

            time_prev = time_now

    time_end = datetime.now()
    click.echo('All done! Processed {0} items in {1}'.format(i, time_end - time_start))



@main.command('group_info')
@click.argument('input_file', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.argument('output_file')
def group_info(input_file, output_dir, output_file):
    ids = readlines(input_file)

    task = {'method': 'groups.getById', 'input': ids, 'output_file': output_file, }

    api = VkApiRequest()

    time_start = datetime.now()
    results = api.groups_get_by_id(task['input'])
    if not check_error(results):
        writer = FileWriter(output_dir)
        writer.save_results(task, results)

    time_end = datetime.now()
    click.echo('All done! {0}'.format(time_end - time_start))



if __name__ == '__main__':
    main()
