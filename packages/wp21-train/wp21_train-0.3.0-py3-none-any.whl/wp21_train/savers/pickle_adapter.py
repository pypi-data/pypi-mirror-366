import pickle

from wp21_train.savers.adapter import *
from wp21_train.utils.logging import log_message

class pickle_adapter(adapter):

    def __init__(self, file_name, dump_data = {}, dump_meta = {}):
        self._file = file_name + '.pkl'
        self._data = dump_data
        self._meta = dump_meta
        self._data['Title'] = 'data'
        self._meta['Title'] = 'meta-data'

    def write_data(self):
        with open(self._file, 'wb') as pickle_file:
            pickle.dump(self._meta, pickle_file)
            pickle.dump(self._data, pickle_file)
        log_message("info", f"Successful dump to {self._file}")

    def read_data(self):
        with open(self._file, 'rb') as pickle_file:
            temp_data = pickle.load(pickle_file)
        self._meta, self._data = temp_data
        log_message("info", f"Successful read from {self._file}")
        return [self._meta, self._data]
