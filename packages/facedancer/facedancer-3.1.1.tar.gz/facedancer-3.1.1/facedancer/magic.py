#
# This file is part of Facedancer.
#
""" Functionally for automatic instantiations / tracking via decorators. """

import inspect

from abc         import ABCMeta, abstractmethod
from dataclasses import dataclass, is_dataclass, field, fields


class DescribableMeta(ABCMeta):
    """ Metaclass for USBDescribable subclasses. """
    def __new__(cls, name, bases, classdict):
        annotations = classdict.setdefault('__annotations__', {})
        for base in bases:
            if is_dataclass(base):
                for field in fields(base):
                    if field.name in classdict:
                        if field.name not in annotations:
                            annotations[field.name] = str(field.type)
        new_cls = ABCMeta.__new__(cls, name, bases, classdict)
        return dataclass(new_cls, kw_only=True)


def adjust_defaults(cls, **kwargs):
    """ Adjusts the defaults of an existing dataclass. """
    assert is_dataclass(cls)
    for name, value in kwargs.items():
        cls.__dataclass_fields__[name] = field(default = value)
        cls.__init__.__kwdefaults__[name] = value
    return cls


class AutoInstantiable(metaclass=DescribableMeta):
    """ Base class for methods that can be decorated with use_automatically. """

    @abstractmethod
    def get_identifier(self) -> int:
        """ Returns a unique integer identifier for this object.

        This is usually the index or address of the relevant USB object.
        """

    def matches_identifier(self, other: int) -> bool:
        return (other == self.get_identifier())


class AutoInstantiator:
    """ Simple wrapper class annotated on objects that can be instantiated automatically.

    Used for the @use_automatically decorator; which removes a lot of the Facedancer boilerplate
    at the cost of being somewhat cryptic.
    """

    def __init__(self, target_type):
        self._target_type = target_type

    def creates_instance_of(self, expected_type):
        return issubclass(self._target_type, expected_type)

    def __call__(self, parent):
        return self._target_type(parent=parent)


def use_automatically(cls):
    """ Class decorator used to annotate Facedancer inner classes. Implies @dataclass.

    This decorator can be placed on inner classes that describe "subordinate"
    objects on USB devices. For example, a USBDevice can have several subordinate
    USBConfigurations; which select the various configurations for that class.

    When placed on a subordinate class, this allows the parent class to automatically
    instantiate the relevant given class during its creation; automatically populating
    the subordinate properties of the relevant device.

    For example, assume we have a Facedancer class representing a custom USB device::

        class ExampleDevice(USBDevice):
            product_string : str = "My Example Device"

            @use_automatically
            class DefaultConfiguration(USBConfiguration):
                number : int = 1

    In this case, when an ExampleDevice is instantiated, the USBDevice code knows how
    to instantiate DefaultConfiguration, and will do so automatically.

    Note that this decorator should _only_ be used for subordinate types; and expects that
    the decorated class has no explicitly-declared __init__ method. The __post_init__ mechanism
    of python dataclasses can be overridden to perform any needed initialization.
    """
    return AutoInstantiator(cls)


def _use_inner_classes_automatically(cls):
    # Iterate over the relevant class...
    for name, member in cls.__dict__.items():

        # ... and tag each inner class with both use_automatically
        # -and- use_inner_classes_automatically. The former
        if inspect.isclass(member) and issubclass(member, AutoInstantiable):

            wrapped_class = _use_inner_classes_automatically(member)
            wrapped_class = use_automatically(member)

            setattr(cls, name, wrapped_class)

    return cls


def use_inner_classes_automatically(cls):
    """ Decorator that acts as if all inner classes were defined with `use_automatically`. """
    return _use_inner_classes_automatically(cls)


def instantiate_subordinates(obj, expected_type):
    """ Automatically instantiates any inner classes with a matching type.

    This is used by objects that represent USB hardware behaviors (e.g. USBDevice,
    USBConfiguration, USBInterface, USBEndpoint) in order to automatically create
    objects of any inner class decorated with ``@use_automatically``.
    """

    # Search our class for anything decorated with an AutoInstantiator of the relevant type.
    for member in type(obj).__dict__.values():
        if isinstance(member, AutoInstantiator) and member.creates_instance_of(expected_type):
            yield member(object)
