from bottle import url

# set get_url function in templates
def view_template(**kargs):
    params = dict(**kargs)

    params['get_url'] = url

    return params