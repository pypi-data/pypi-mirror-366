import copy
import multiprocessing.dummy as mt
import os

from pyarrow.parquet import ParquetFile


def get_inner_group_idx_from_row_idx(
    rows_accumulate, row_idx, curr_inner_group_idx, inner_group_num
):
    assert curr_inner_group_idx < inner_group_num
    if (
        rows_accumulate[curr_inner_group_idx]
        <= row_idx
        < rows_accumulate[curr_inner_group_idx + 1]
    ):
        return curr_inner_group_idx
    for i in range(inner_group_num):
        cur_gidx = (curr_inner_group_idx + i + 1) % inner_group_num
        if rows_accumulate[cur_gidx] <= row_idx < rows_accumulate[cur_gidx + 1]:
            return cur_gidx
    return -1


class ParquetDataset:
    r"""
    Given a path of parquet file, return target data by index
    Note: This class only implements an efficient way to return sample by index
        The index order is controlled by sampler, not here.

    Args:
        filepath (str or tuple of str): file from which to load the data. If is tuple of str, each
            each str represents a single parquet file, and corresponding rows across those files together
            form a sample
        columns (list of str, optional), columns to load (default: ``None`` means load all columns)
    """

    def __init__(self, filepath, columns=None):

        if isinstance(filepath, str):
            filepath = [filepath]
        assert isinstance(
            filepath, list
        ), f"filepath should be a list but got {type(filepath)}"
        self.parquet_files = []
        self.filepaths = []
        for path in filepath:
            if not os.path.exists(path):
                raise FileNotFoundError(f"file {path} does not exist")
            self.parquet_files.append(ParquetFile(path))
            self.filepaths.append(path)
        assert (
            len(self.parquet_files) > 0
        ), f"no valid parquet files found in {filepath}"

        self.columns = []
        if columns:
            assert isinstance(
                columns, list
            ), f"columns should be a list but got {type(columns)}"
            if isinstance(columns[0], str):
                # TODO: is it correct? ['col1', 'col2'] -> [['col1', 'col2']]?
                columns = [columns]
            assert len(columns) == len(self.parquet_files), (
                f"columns length {len(columns)} should be the same as the number of parquet files"
                " {len(self.parquet_files)}"
            )
            for idx, pf in enumerate(self.parquet_files):
                columns_from_file = set(pf.schema.names)
                columns_feed_in = columns[idx]
                # make sure the columns feed in is a subset of the columns in the file
                self.columns.append(
                    [col for col in columns_feed_in if col in columns_from_file]
                )
        else:
            self.columns = [None] * len(self.parquet_files)

        self.num_row_groups = self.parquet_files[0].num_row_groups
        self.row_groups = list(range(self.num_row_groups))
        self.row_group_rows = [
            self.parquet_files[0].metadata.row_group(i).num_rows
            for i in self.row_groups
        ]

        self.row_group_rows_accumulate = []
        rows = 0
        for i in self.row_groups:
            self.row_group_rows_accumulate.append(rows)
            rows += self.row_group_rows[i]
        self.row_group_rows_accumulate.append(rows)
        self.cur_row_group = 0
        self.cache = {}

        self.num_rows = self.parquet_files[0].metadata.num_rows
        # ensure that the metadata of the group files is same
        for idx, pf in enumerate(self.parquet_files):
            assert self.num_row_groups == pf.num_row_groups, (
                f"parquet file {self.filepaths[idx]} has {pf.num_row_groups} row groups but "
                "{self.filepaths[0]} has {self.num_row_groups}"
            )
            assert self.row_group_rows == [
                pf.metadata.row_group(rid).num_rows for rid in self.row_groups
            ], f"parquet file {self.filepaths[idx]} has different rows in row group than {self.filepaths[0]}"

    def _read_row_group(self, row_group):
        rows = []
        for idx, pf in enumerate(self.parquet_files):
            row_group_data = pf.read_row_group(row_group, columns=self.columns[idx])
            group_data = row_group_data.to_pandas()
            cur_rows = group_data.to_dict("records")
            if len(rows) == 0:
                rows = cur_rows
            else:
                assert len(rows) == len(
                    cur_rows
                ), "row group of each file should be the same"
                for i in range(len(rows)):
                    rows[i].update(cur_rows[i])
        return rows

    def __iter__(self):
        for row_group in self.row_groups:
            rows = self._read_row_group(row_group)
            yield from rows

    def _clean_cache(self):
        # TODO: maybe a better way to find out which row groups to delete
        gidx_to_delete = [i for i in self.cache]
        for i in gidx_to_delete:
            del self.cache[i]

    def __getitem__(self, idx):
        assert (
            0 <= idx < self.num_rows
        ), f"idx shoud be in [0, {self.num_rows}) but get {idx}"
        cur_row_group = get_inner_group_idx_from_row_idx(
            self.row_group_rows_accumulate, idx, self.cur_row_group, self.num_row_groups
        )
        assert cur_row_group >= 0, f"invalid row group {cur_row_group} for idx {idx}"
        self.cur_row_group = cur_row_group
        if cur_row_group not in self.cache:
            cur_rows = self._read_row_group(cur_row_group)
            self._clean_cache()
            self.cache[cur_row_group] = cur_rows
        else:
            cur_rows = self.cache[cur_row_group]
        sample = cur_rows[idx - self.row_group_rows_accumulate[cur_row_group]]
        if "row_idx" not in sample:
            sample["row_idx"] = idx
        return copy.deepcopy(sample)

    def __len__(self):
        return self.num_rows

    def close(self):
        del self.cache
        for pf in self.parquet_files:
            pf.close()

    def get_sub_lengths(self):
        return self.row_group_rows


class ParquetConcateDataset:
    r"""
    Given multiple parquet files as a whole dataset, return target data by index
    Note: This class only implements an efficient way to return sample by index.
        The index order is controlled by sampler, not here.

    Args:
        filepaths (list of str): files from which to load the data.
        columns (list of str, optional), columns to load (default: ``None`` means load all columns)
    """

    def __init__(self, filepaths, columns=None):
        self.filepaths = filepaths
        self.num_files = len(filepaths)
        self.columns = columns
        rows = []
        rows_per_group = []
        with mt.Pool(16) as p:
            sub_ds_info = p.map(self._get_sub_ds_length, self.filepaths)
        rows = [i[0] for i in sub_ds_info]
        rows_per_group = [i[1] for i in sub_ds_info]
        self.rows_per_file = rows
        self.rows_per_group = rows_per_group
        self.num_rows = sum(self.rows_per_file)
        self.num_rows_accumulate = []
        cur_rows = 0
        for i in range(self.num_files):
            self.num_rows_accumulate.append(cur_rows)
            cur_rows += rows[i]
        self.num_rows_accumulate.append(cur_rows)
        self.cur_ds_idx = 0
        self.cache = {}

    def _get_sub_ds_length(self, path):
        ds = ParquetDataset(path)
        row = len(ds)
        row_groups = ds.get_sub_lengths()
        ds.close()
        return row, row_groups

    def __len__(self):
        return self.num_rows

    def _clean_cache(self):
        ds_idx_to_delete = [i for i in self.cache]
        for i in ds_idx_to_delete:
            self.cache[i].close()
            del self.cache[i]

    def __getitem__(self, idx):
        if idx < 0:
            idx += len(self)
        assert 0 <= idx < len(self), f"idx should be in [0, {len(self)}) but get {idx}"
        cur_ds_idx = get_inner_group_idx_from_row_idx(
            self.num_rows_accumulate, idx, self.cur_ds_idx, self.num_files
        )
        assert cur_ds_idx >= 0, f"invalid file idx {cur_ds_idx} for row idx {idx}"
        self.cur_ds_idx = cur_ds_idx
        if cur_ds_idx not in self.cache:
            cur_ds = ParquetDataset(self.filepaths[cur_ds_idx], self.columns)
            self._clean_cache()
            self.cache[cur_ds_idx] = cur_ds
        else:
            cur_ds = self.cache[cur_ds_idx]
        data = cur_ds[idx - self.num_rows_accumulate[cur_ds_idx]]
        if "filepath" not in data:
            data["filepath"] = self.filepaths[cur_ds_idx]
        return data

    def get_sub_lengths(self, level="row_group"):
        assert level in {"row_group", "file"}
        if level == "row_group":
            return self.rows_per_group
        else:
            return self.rows_per_file


if __name__ == "__main__":
    folder = "/mnt/personal/parquet_demo_data"
    fnames = [
        "01_0001.parquet",
        "02_0001.parquet",
        "03_0001.parquet",
        "04_0001.parquet",
        "05_0001.parquet",
        "06_0001.parquet",
        "07_0001.parquet",
    ]
    files = [f"{folder}/{fname}" for fname in fnames]
    ds = ParquetConcateDataset(files)
    assert [sum(i) for i in ds.rows_per_group] == ds.rows_per_file
    assert sum(ds.rows_per_file) == len(ds)
    for i in range(10):
        data = ds[i * 500]
        print(data["filepath"])
