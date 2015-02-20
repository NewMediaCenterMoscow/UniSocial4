class AbstractWriter(object):
    """Abstract writer"""

    def __init__(self):
        pass

    def save_results(self, task, data):
        raise NotImplementedError( "Should have implemented this" )