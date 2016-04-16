import sys
import click

sys.path.insert(1, './CollectorRole/')
sys.path.insert(1, './SaveResultRole/')

from api_vk import VkApiRequest
from FileWriter import FileWriter


#########
# Helpers
#########
def readlines(filename):
    with open(filename, 'r') as f:
        return readlines_handler(f)

def readlines_handler(f):
    return (cl for cl in (l.strip() for l in f.readlines()) if len(cl) > 0)


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
    ids = readlines_handler(input_file)

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
    ids = readlines_handler(input_file)

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
    ids = readlines_handler(input_file)

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
@click.option('--output_file', default=None, help='Filename to sve the results')
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




if __name__ == '__main__':
    main()
