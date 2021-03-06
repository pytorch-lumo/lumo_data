from functools import wraps

from dbrecord import PDict
from torch.utils.data.dataloader import default_collate

from lumo_data import DBDataset, DataLoader
from torch.utils.data import DataLoader
import os

import torch.distributed

torch.distributed.init_process_group(backend="nccl")

class CollateBase:

    def __init__(self, collate_fn=default_collate, *args, **kwargs) -> None:
        super().__init__()
        self._collate_fn = collate_fn
        self.initial(*args, **kwargs)

    def initial(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.wraped_collate(*args, **kwargs)

    def before_collate(self, sample_list):
        return sample_list

    def collate(self, sample_list):
        return self._collate_fn(sample_list)

    def wraped_collate(self, sample_list):
        sample_list = self.before_collate(sample_list)
        batch = self.collate(sample_list)
        batch = self.after_collate(batch)
        return batch

    def after_collate(self, batch):
        return batch


class M(CollateBase):

    # def collate(self, sample_list):
    #     print(sample_list)
    #     return super().collate(sample_list)

    def after_collate(self, batch):
        if isinstance(batch, dict):
            assert isinstance(batch, dict) and 'b' not in batch
        return {'b': batch}


if os.path.exists('temp.sql'):
    os.remove('temp.sql')
dic = PDict('temp.sql')
for i in range(1000):
    dic[f'a{i}'] = i
dic.flush()
dataset = DBDataset('temp.sql')
for batch in DataLoader(dataset, num_workers=1, batch_size=16, collate_fn=M()):
    print(batch)
