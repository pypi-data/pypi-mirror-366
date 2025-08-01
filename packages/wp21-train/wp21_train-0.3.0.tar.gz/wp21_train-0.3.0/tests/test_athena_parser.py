import os

from wp21_train.savers.yml_adapter import yml_adapter
from wp21_train.parser.athena_parser import athena_parser

def test_athena_parser():
    test_dir = os.path.dirname(__file__)
    file_name = os.path.join(test_dir, 'info_test_file')

    tmp_dir = os.path.join(test_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    adapter_1 = yml_adapter(file_name)
    data, meta = adapter_1.read_data()

    assert data    , "Parsed data are empty"
    assert meta    , "Parsed meta-data are empty"

    parser_1 = athena_parser(data, meta, nevents=1000)
    
    os.rename('config.yaml', os.path.join(tmp_dir, 'config.yaml'))
    os.rename('environment.yaml', os.path.join(tmp_dir, 'environment.yaml'))

    assert os.path.isfile(os.path.join(tmp_dir, 'config.yaml')), "config file not created"
    assert os.path.isfile(os.path.join(tmp_dir, 'environment.yaml')), "environment file not created"
    
    file_name_2 = os.path.join(tmp_dir, 'info_test_file')
    adapter_2 = yml_adapter(file_name_2)
    adapter_2._data = data
    adapter_2._meta = meta
    adapter_2.write_data()

    assert os.path.isfile(os.path.join(tmp_dir, 'info_test_file.yml')), "info file not created"


    os.remove(os.path.join(tmp_dir, 'config.yaml'))
    os.remove(os.path.join(tmp_dir, 'environment.yaml'))
    os.remove(os.path.join(tmp_dir, 'info_test_file.yml'))
    os.rmdir(tmp_dir)

