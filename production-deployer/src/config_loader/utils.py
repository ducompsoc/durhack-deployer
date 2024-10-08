from typing import Iterable

type Record = dict[str, Record | object]

def deep_merge_into(source: Record, destination: Record) -> None:
    """
    Deep-merge some dictionaries by adding all items from the first object to the second, without deleting
    existing items (except to overwrite them).
    No special handling is implemented for lists, they will be 'merged' by replacement.
    
    Source: `source`_

    .. _source: https://stackoverflow.com/a/20666342
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge_into(value, node)
        else:
            destination[key] = value

def deep_merge(sources: Iterable[Record]) -> Record:
    """
    Deep-merge a variable number of objects by adding all items from each object to a new object, without
    deleting previously added items (except to overwrite them).
    No special handling is implemented for lists, they will be 'merged' by replacement.
    """
    destination: Record = {}
    for source in sources:
        deep_merge_into(source, destination)
    
    return destination
