from typing import Any, List, Union, Iterable


def as_list(value: Union[Iterable[Any], Any]) -> List[Any]:
    """
    将输入值转换为列表

    参数:
        value: 可以是单个值或可迭代对象

    返回:
        列表形式的数据

    示例:
        >>> as_list(1)
        [1]
        >>> as_list((1, 2))
        [1, 2]
        >>> as_list(None)
        []
    """
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [value]
    if hasattr(value, '__iter__'):
        return list(value)
    return [value]