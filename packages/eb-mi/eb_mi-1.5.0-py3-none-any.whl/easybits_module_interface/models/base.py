from copy import deepcopy
from dataclasses import dataclass, field, fields, make_dataclass
from typing import Dict, List, Optional, Union


class BaseDataClass:
    """
    Base class for dataclasses with a from_dict method.
    """
    @classmethod
    def get_model_kwargs(cls, kwargs: Dict) -> Dict:
        """
        Getter for kwargs based on the fields of the class.

        :param kwargs: kwargs to filter
        :return: filtered kwargs
        """
        field_names = [field.name for field in fields(cls)]
        kwargs_out = deepcopy(kwargs)
        for f in kwargs.keys():
            if f not in field_names:
                kwargs_out.pop(f, None)
        return kwargs_out

    @classmethod
    def from_dict(cls, **kwargs):
        """
        Safe method to create an instance from given kwargs.

        :param kwargs: object as kwargs
        :return: instance of the class
        """
        return cls(**cls.get_model_kwargs(kwargs))


class DynamicFieldsDataClass(BaseDataClass):
    """
    Base class for dataclasses with dynamic fields.

    Example:
        >>> @dataclass
        ... class MyFoo(DynamicFieldsDataClass):
        ...     foo: str
        ...
        >>> obj = MyFoo.from_dict(foo='string', bar=1)
        >>> obj.foo
        'string'
        >>> obj.bar
        1
        >>> asdict(obj)
        {'foo': 'string', 'bar': 1}
        >>> MyFoo(foo='string', bar=1)
        AttributeError: 'MyFoo' object has no attribute 'bar'
    """
    @classmethod
    def from_dict(cls, **kwargs):
        """
        Creates a new dataclass with the fields provided in the kwargs.

        New fields are added to the class definition as Optional[str].

        :param kwargs: object as kwargs
        :return: new dataclass instance
        """
        field_names = [field.name for field in fields(cls)]
        new_fields = [(k, Optional[str], None) for k, v in kwargs.items() if k not in field_names]
        dynamic_cls = make_dataclass(cls.__name__, new_fields, bases=(cls,))
        return dynamic_cls(**kwargs)


