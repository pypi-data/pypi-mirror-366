import yaml
from wp21_train.savers.adapter import adapter
from wp21_train.utils.logging import log_message

class yml_adapter(adapter):
    def __init__(self, file_name):
        self._file = file_name + '.yml'
        self._data = {}
        self._meta = {}

    def write_data(self):
        with open(self._file, 'w') as yml_file:
            yaml.dump({
                'data': self._data,
                'meta': self._meta
            }, yml_file, sort_keys=False)
        log_message("info", f"Successful dump to {self._file}")

    def read_data(self):
        with open(self._file, 'r') as yml_file:
            content = yaml.safe_load(yml_file)
            self._data = content.get('data', {})
            self._meta = content.get('meta', {})
        log_message("info", f"Successful read from {self._file}")
        return [self._data, self._meta]
