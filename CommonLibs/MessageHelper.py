class MessageHelper(object):
    """Helper for message formatting"""

    def create_task_description_message(self, method, input):
        message = method + ':' + input
        return message

    def parse_task_description_message(self, message):
        msg = message.split(':')
        return {'method': msg[0], 'input': msg[1]}

    def create_task_message(self, method, input):
        message = method + ':' + input
        return message

    def parse_task_message(self, message):
        msg = message.split(':')
        return {'method': msg[0], 'input': msg[1]}
