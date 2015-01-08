from storage_helper import encode_message, decode_message

def encode_task_description_message(method, input):
    message = encode_message(method + ':' + input)
    return message

def decode_task_description_message(message):
    msg = decode_message(message).split(':')
    return {'method': msg[0], 'input': msg[1]}

def encode_task_message(method, input):
    message = encode_message(method + ':' + input)
    return message

def decode_task_message(message):
    msg = decode_message(message).split(':')
    return {'method': msg[0], 'input': msg[1]}

