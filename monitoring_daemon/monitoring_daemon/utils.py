import os
import errno

__author__ = 'Pace Francesco'


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
