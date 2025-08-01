from wp21_train.utils.utility import get_short_type
from wp21_train.utils.version import __version__

class adapter:

    def write_data(self):
        pass

    def read_data(self):
        pass

    def _type(self, value):
        return get_short_type(value)

    def get_version(self):
        return f"adapter version: {__version__}"
