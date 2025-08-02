import numpy as np
import pandas as pd
from tqdm.std import tqdm


class AbstractMultiModalDataset:
    def __init__(self, long_sits: pd.DataFrame, original_gdf_lenght: int):
        grouped = long_sits.groupby("indexnum")

        max_seq_len = grouped.size().max()
        num_bands = len(long_sits.columns) - 2

        self.X = np.zeros((original_gdf_lenght, max_seq_len, num_bands), dtype=np.float16)
        self.T = np.zeros((original_gdf_lenght, max_seq_len), dtype="datetime64[D]")

        for idx, group in tqdm(grouped):
            group_sorted = group.sort_values("timestamp")
            seq_len = len(group_sorted)

            self.X[idx, :seq_len, :] = group_sorted.drop(columns=["timestamp", "indexnum"]).to_numpy(dtype=np.float16)
            self.T[idx, :seq_len] = group_sorted["timestamp"].to_numpy().astype("datetime64[D]")

    def __len__(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def __getitem__(self, idx):
        raise NotImplementedError("Subclasses should implement this method.")
