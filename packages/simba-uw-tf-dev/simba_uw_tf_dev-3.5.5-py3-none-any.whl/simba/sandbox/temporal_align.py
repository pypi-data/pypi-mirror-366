import os
from typing import Union, List, Optional
import numpy as np
from simba.utils.read_write import recursive_file_search, find_core_cnt
from simba.utils.checks import check_file_exist_and_readable
import multiprocessing, functools


def _read_npz_helper(path: str,
                     keys: Optional[List[str]] = None):

    data = np.load(path[0])
    data = {k: data[k] for k in data.files}
    data = {key: data[key] for key in keys if key in data} if keys is not None else data
    data['frame_times'] = np.array([int(str(x)[:13]) for x in data['frame_times']])
    return {path[0]: data['frame_times'], 'start_time': np.min(data['frame_times']), 'end_time': np.max(data['frame_times']), 'count': len(data['frame_times'])}




def read_npz(data_paths: List[Union[str, os.PathLike]], keys: Optional[List[str]] = None, core_cnt: int = -1):
    _ = [check_file_exist_and_readable(x) for x in data_paths]
    data_paths = [[x] for x in data_paths]
    core_cnt = find_core_cnt()[0] if core_cnt == -1 else core_cnt
    results = {}
    with multiprocessing.Pool(core_cnt, maxtasksperchild=50) as pool:
        constants = functools.partial(_read_npz_helper, keys=keys)
        for batch_cnt, batch_result in enumerate(pool.imap(constants, data_paths, chunksize=1)):
            results.update(batch_result)
    pool.terminate()
    pool.join()
    return results

def temporal_align(data_dir: Union[str, os.PathLike], keys: Optional[List[str]] = None):
    meta_paths = recursive_file_search(directory=data_dir, extensions=['npz'])
    meta_data = read_npz(data_paths=meta_paths, keys=keys)
    print(meta_data)






#
#
#
# data = np.load(r"D:\netholabs\spatial_stitching\npz\npz_sample\2025-07-16_06-01-02_metadata.npz")
# print(data.files)
#
# data['frame_times'].shape[0]

if __name__ == "__main__":
    temporal_align(data_dir=r"D:\netholabs\tempotal_stitching", keys=['frame_times'])