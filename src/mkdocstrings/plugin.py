import importlib
import inspect
import re

from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type


class MkdocstringsPlugin(BasePlugin):
    config_scheme = (
        ("global_classes_filters",  Type(tuple, default=("!^_[^_]", "!^__weakref__$"))),
        ("global_modules_filters",  Type(tuple, default=())),
    )

    def import_object(self, path):
        """
        Transform a path into an actual Python object.

        The path can be arbitrary long. You can pass the path to a package,
        a module, a class, a function or a global variable, as deep as you
        want, as long as the deepest module is importable through
        ``importlib.import_module`` and each object is obtainable through
        the ``getattr`` method. Local objects will not work.

        Args:
            path (str): the dot-separated path of the object.

        Returns:
            tuple: the imported module and obtained object.
        """
        if path is None or not path:
            return None

        obj_parent_modules = path.split(".")
        objects = []

        while True:
            try:
                parent_module_path = ".".join(obj_parent_modules)
                parent_module = importlib.import_module(parent_module_path)
                break
            except ImportError:
                if len(obj_parent_modules) == 1:
                    raise ImportError("No module named '%s'" % obj_parent_modules[0])
                objects.insert(0, obj_parent_modules.pop(-1))

        module = parent_module
        current_object = parent_module
        for obj in objects:
            current_object = getattr(current_object, obj)
        return module, current_object


    def on_page_markdown(self, markdown, page, **kwargs):
        lines = markdown.split("\n")
        for line in lines:
            if line.startswith("::: "):
                import_string = line.replace("::: ", "")
                module, obj = self.import_object(import_string)
                module_path = module.__file__
                if inspect.ismodule(obj):
                    attributes = []
                    functions = []
                    classes = []

                elif inspect.isclass(obj):
                    attributes = []
                    methods = []
                    for key, value in sorted(obj.__dict__.items()):
                        types = []
                        if re.match(r"^__\w+__$", key):
                            types.append("special")
                        if type(value) == classmethod:
                            types.append("class")
                            methods.append((key, value, types))
                        elif type(value) == staticmethod:
                            types.append("static")
                            methods.append((key, value, types))
                        elif type(value) == type(lambda: None):
                            methods.append((key, value, types))
                        elif type(value) == property:
                            types.append("property")
                            if value.fset is None:
                                types.append("readonly")
                            attributes.append((key, value, types))
                        elif type(value) == type:
                            classes.append((key, value, types))

                    print("attributes")
                    for attribute in attributes:
                        print(attribute)
                    print()
                    print("methods")
                    for method in methods:
                        print(method)
                    print()
                    print("classes")
                    for class_ in classes:
                        print(class_)
                    print()

                elif callable(obj):
                    pass
        return markdown

    class InnerClass:
        pass

    @classmethod
    def im_a_class_method(cls):
        pass

    @staticmethod
    def im_a_static_method():
        pass

    @property
    def im_a_property(self):
        return None

    @im_a_property.setter
    def im_a_property(self):
        pass

    @property
    def im_a_readonly_property(self):
        return None
