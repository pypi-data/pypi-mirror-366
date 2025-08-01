from array import array
from ROOT import TTree, TROOT, TFile, TBranch, TLeaf, std

from wp21_train.savers.adapter import *
from wp21_train.utils.logging import log_message


class root_adapter(adapter):

    def __init__(self, file_name, dump_data = {}, dump_meta = {}):
        self._file = file_name + ".root"
        self._data = self._process_data(dump_data)
        self._meta = self._process_data(dump_meta)

    def write_data(self):
        file_in = TFile(self._file, 'RECREATE')
        for i_data in self._data:            
            i_data.Write()
        for i_meta in self._meta:
            i_meta.Write()
        file_in.Close()
        log_message("info", f'Successful dump to {self._file}')

    def read_data(self):
        file_in = TFile(self._file, 'READ')
        self._data = file_in.GetTree('data')
        self._meta = file_in.GetTree('meta-data')
        log_message("info", f'Successful read from {self._file}')
        return [self._meta, self._data]

    def _process_data(self, din):
        cnt   = 0
        trees = []
        for i_word in din:
            title     = din[i_word]['Title']
            data_tree = TTree(title+f'{cnt}', title+f' {cnt} TTree')            
            var_list  = []
            for i_entry in din[i_word]:
                var_type = self._type(din[i_word][i_entry])
                if var_type != 's':
                    var_list.append(array(var_type, [0.]))
                    data_tree.Branch(i_entry,var_list[len(var_list)-1],i_entry+'/'+var_type.upper())                    
                else:
                    var_list.append(std.string(''))
                    data_tree.Branch(i_entry,var_list[len(var_list)-1])

            val = 0
            for i_entry in din[i_word]:
                var_type = self._type(din[i_word][i_entry])
                if var_type != 's':
                    var_list[val][0] = din[i_word][i_entry]
                else:
                    var_list[val] = std.string(din[i_word][i_entry])
                val += 1

            data_tree.Fill()
            cnt += 1
            trees.append(data_tree)
        return trees
