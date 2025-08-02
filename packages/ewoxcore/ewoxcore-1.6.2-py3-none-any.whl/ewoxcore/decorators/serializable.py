from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type


def Serializable(cls):
    class_name = cls.__name__

    # Set the __type attribute
    setattr(cls, '__type', class_name)

    return cls