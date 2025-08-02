from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod

T = TypeVar("T")


class ICacheProvider(ABC):
    @abstractmethod
    def activate_expiration(self, timer_interval:int) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def change_use_local(self, use_local:bool) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def set_cache_size(self, size:int) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def get(self, cacheKey:str) -> Any:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def insert(self, cacheKey:str, cacheValue:Any) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def remove(self, cacheKey:str) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def get_all_values(self) -> List[Any]:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def add(self, key:str, value:str, absolute_expiration:timedelta) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def add_expire_at(self, key:str, value:str, expire_at:datetime) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def add_ext(self, key:str, value:T, absolute_expiration:timedelta) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def add_expire_at_ext(self, key:str, value:T, expire_at:datetime) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def insert_ext(self, key:str, value:T) -> None:
        raise NotImplementedError("Implement inhereted method")


    @abstractmethod
    def get_ext(self, class_type:T, key:str) -> T:
        raise NotImplementedError("Implement inhereted method")
