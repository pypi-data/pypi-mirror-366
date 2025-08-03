# Standard library
import abc
from pathlib import Path

# Third-party
import requests
from torch.utils.data import DataLoader, random_split, Dataset


class BaseDataset(abc.ABC):
    def __init__(self, config, batch_size=32, split_ratio=0.8, num_workers=0, *, shuffle=True):
        self.config = config
        self.batch_size = batch_size
        self.split_ratio = split_ratio
        self.num_workers = num_workers
        self.shuffle = shuffle

    def get_dataloaders(self) -> tuple[DataLoader, DataLoader]:
        dataset = self.load_dataset()
        train_size = int(self.split_ratio * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
        return (
            DataLoader(
                train_dataset,
                batch_size=self.batch_size,
                shuffle=self.shuffle,
                num_workers=self.num_workers,
            ),
            DataLoader(
                val_dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=self.num_workers,
            ),
        )

    @abc.abstractmethod
    def load_dataset(self):
        """Must be implemented in the subclass."""
        msg = "Subclasses must implement load_dataset()"
        raise NotImplementedError(msg)
