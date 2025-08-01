import json

from wp21_train.savers.adapter import adapter
from wp21_train.utils.logging import log_message


class json_adapter(adapter):

    def __init__(self, file_name, dump_data = {}, dump_meta = {}):
        self._file = file_name + '.json'
        self._data = dump_data
        self._meta = dump_meta
        #self._data['Title'] = 'data'
        #self._meta['Title'] = 'meta-data'

    def write_data(self):
        with open(self._file, 'w') as json_file:
            json.dump(self._meta, json_file, indent=4)            
            json.dump(self._data, json_file, indent=4)
        log_message("info", f'Successful dump to {self._file}')

    def read_data(self):
        with open(self._file, 'r') as json_file:
            temp_dict = json.load(json_file)
        self._meta, self._data = temp_dict
        log_message("info", f"Successful read from {self._file}")
        return [self._meta, self._data]
