from abc import ABC, abstractmethod
from typing import Dict, Any


class CloudStorageInterface(ABC):
    @abstractmethod
    def upload(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def download(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        raise NotImplementedError
