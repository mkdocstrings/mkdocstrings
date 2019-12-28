import inspect

try:
    from typing import GenericMeta  # python 3.6
except ImportError:
    # in 3.7, GenericMeta doesn't exist but we don't need it
    class GenericMeta(type):
        pass


def annotation_to_string(annotation):
    if inspect.isclass(annotation) and not isinstance(annotation, GenericMeta):
        return annotation.__name__
    return str(annotation).replace("typing.", "")
