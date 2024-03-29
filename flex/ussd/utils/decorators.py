from __future__ import annotations

import sys
import weakref
import typing as t
from warnings import warn
from threading import RLock
from functools import update_wrapper, wraps, lru_cache


try:
    from functools import cached_property as _native_cached_property
except ImportError:
    _native_cached_property = None


NOTHING = object()

T = t.TypeVar('T')


class class_only_method(classmethod):
    """Creates a classmethod available only to the class. Raises AttributeError
    when called from an instance of the class.
    """

    def __init__(self, func, name=None):
        super().__init__(func)
        self.__name__ = name or func.__name__

    def __get__(self, obj, cls):
        if obj is not None:
            raise AttributeError('Class method {}.{}() is available only to '
                                 'the class, and not it\'s instances.'
                                 .format(cls.__name__, self.__name__))
        return super().__get__(cls, cls)


class class_property(property, t.Generic[T]):
    """A decorator that converts a function into a lazy class property."""
    
    def __get__(self, obj, cls) -> T:
        return super().__get__(cls, cls)


class cached_class_property(class_property[T]):
    """A decorator that converts a function into a lazy class property."""

    def __init__(self, func: t.Callable[..., T]):
        super().__init__(func)
        self.lock = RLock()
        self.cache = weakref.WeakKeyDictionary()

    def __get__(self, obj, cls) -> T:

        # if self.has_cache_value(cls):
        #     return self.get_cache_value(cls)

        with self.lock:
            if self.has_cache_value(cls):
                return self.get_cache_value(cls)
            else:
                rv = super().__get__(obj, cls)
                self.set_cache_value(cls, rv)
                return rv
                
    def get_cache_value(self, cls, default=...) -> T:
        return self.cache[cls]

    def has_cache_value(self, cls) -> bool:
        return cls in self.cache

    def set_cache_value(self, cls, value: T):
        self.cache[cls] = value




if _native_cached_property is not None:
    native_cached_property = _native_cached_property
else:
    class native_cached_property: 
        def __init__(self, func):
            self.func = func
            self.attrname = None
            self.__doc__ = func.__doc__
            self.lock = RLock()

        def __set_name__(self, owner, name):
            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_property to two different names "
                    f"({self.attrname!r} and {name!r})."
                )

        def __get__(self, instance, owner=None):
            if instance is None:
                return self
            if self.attrname is None:
                raise TypeError(
                    "Cannot use cached_property instance without calling __set_name__ on it.")
            try:
                cache = instance.__dict__
            # not all objects have __dict__ (e.g. class defines slots)
            except AttributeError:
                msg = (
                    f"No '__dict__' attribute on {type(instance).__name__!r} "
                    f"instance to cache {self.attrname!r} property."
                )
                raise TypeError(msg) from None
            
            val = cache.get(self.attrname, NOTHING)
            if val is NOTHING:
                with self.lock:
                    # check if another thread filled cache while we awaited lock
                    val = cache.get(self.attrname, NOTHING)
                    if val is NOTHING:
                        val = self.func(instance)
                        try:
                            cache[self.attrname] = val
                        except TypeError:
                            msg = (
                                f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                                f"does not support item assignment for caching {self.attrname!r} property."
                            )
                            raise TypeError(msg) from None
            return val


class cached_property(native_cached_property):
    """Transforms a method into property whose value is computed once. 
    The computed value is then cached as a normal attribute for the life of the 
    instance::

            class Foo(object):

                    @cached_property
                    def foo(self):
                            # calculate something important here
                            return 42

    To make the property mutable, set the `readonly` kwarg to `False` or provide
    setter function. If `readonly` is `False` and no setter is provided, it 
    behaves like a normal attribute when a value is set

    Therefore setting `readonly` to `False`:: 

            class Foo(object):

                    @cached_property(readonly=False).getter
                    def foo(self):
                            ...

    Is equivalent to:: 

            class Foo(object):

                    @cached_property
                    def foo(self):
                            ...

                    @foo.setter
                    def foo(self, value):
                            self.__dict__['foo'] = value

    By default: `del obj.attribute` deletes the cached value if present. Otherwise
    an AttributeError is raised. 
    The class has to have a `__dict__` in order for this property to work. 
    """

    def __init__(self, fget=None, /, fset=None, fdel=None, *, readonly=None):
        super().__init__(fget)
        self.fset = None
        self.fdel = None
        self.deleter(fdel)
        readonly or readonly is fset is None or self.setter(fset)

    def getter(self, func) -> cached_property:
        self.func = func
        self.__doc__ = func.__doc__
        return self

    def setter(self, func=None) -> cached_property:
        self.fset = self._get_fset(func)
        return self

    def deleter(self, func=None) -> cached_property:
        self.fdel = self._get_fdel(func)
        return self

    def __set__(self, instance, val):
        if not callable(self.fset):
            raise AttributeError(
                f'can\'t set readonly attribute {self.attrname!r}'
                f' on {type(instance).__name__!r}.'
            )
        with self.lock:
            self.fset(instance, val)

    def __delete__(self, instance):
        if not callable(self.fdel):
            raise AttributeError(
                f'can\'t delete attribute {self.attrname!r}'
                f' on {type(instance).__name__!r}.'
            )
        with self.lock:
            self.fdel(instance)

    def _get_fset(self, func=None):
        if func is not None:
            return func

        descriptor = self

        def fset(self, val):
            attrname = descriptor.attrname

            assert attrname is not None, (
                "Cannot use cached_property instance without calling __set_name__ on it."
            )

            try:
                self.__dict__[attrname] = val
            except TypeError:
                raise TypeError(
                    f"The '__dict__' attribute on {type(self).__name__!r} instance "
                    f"does not support item assignment for {attrname!r} property."
                ) from None

            except AttributeError:
                raise TypeError(
                    f"No '__dict__' attribute on {type(self).__name__!r} "
                    f"instance to cache {attrname!r} property."
                ) from None

        fset.descriptor = descriptor
        return fset

    def _get_fdel(self, func=None):
        if func is not None:
            return func

        descriptor = self

        def fdel(self):
            attrname = descriptor.attrname

            assert attrname is not None, (
                "Cannot use cached_property instance without calling __set_name__ on it."
            )

            try:
                del descriptor.__dict__[attrname]
            except TypeError:
                raise TypeError(
                    f"The '__dict__' attribute on {type(self).__name__!r} instance "
                    f"does not support item assignment for {attrname!r} property."
                ) from None

            except AttributeError:
                raise TypeError(
                    f"No '__dict__' attribute on {type(self).__name__!r} "
                    f"instance to cache {attrname!r} property."
                ) from None

            except KeyError:
                raise AttributeError(
                    f'can\'t delete attribute {attrname!r}'
                    f' on {type(self).__name__!r}.'
                ) from None

        fdel.descriptor = descriptor
        return fdel


def method_decorator(decorator, name=''):
    """
    Convert a function decorator into a method decorator
    """
    # 'obj' can be a class or a function. If 'obj' is a function at the time it
    # is passed to _dec,  it will eventually be a method of the class it is
    # defined on. If 'obj' is a class, the 'name' is required to be the name
    # of the method that will be decorated.
    def _dec(obj):
        is_class = isinstance(obj, type)
        if is_class:
            if name and hasattr(obj, name):
                func = getattr(obj, name)
                if not callable(func):
                    raise TypeError(
                        "Cannot decorate '{0}' as it isn't a callable "
                        "attribute of {1} ({2})".format(name, obj, func)
                    )
            else:
                raise ValueError(
                    "The keyword argument `name` must be the name of a method "
                    "of the decorated class: {0}. Got '{1}' instead".format(
                        obj, name,
                    )
                )
        else:
            func = obj

        def decorate(function):
            """
            Apply a list/tuple of decorators if decorator is one. Decorator
            functions are applied so that the call order is the same as the
            order in which they appear in the iterable.
            """
            if hasattr(decorator, '__iter__'):
                for dec in decorator[::-1]:
                    function = dec(function)
                return function
            return decorator(function)

        def _wrapper(self, *args, **kwargs):
            @decorate
            def bound_func(*args2, **kwargs2):
                return func.__get__(self, type(self))(*args2, **kwargs2)
            # bound_func has the signature that 'decorator' expects i.e.  no
            # 'self' argument, but it is a closure over self so it can call
            # 'func' correctly.
            return bound_func(*args, **kwargs)
        # In case 'decorator' adds attributes to the function it decorates, we
        # want to copy those. We don't have access to bound_func in this scope,
        # but we can cheat by using it on a dummy function.

        @decorate
        def dummy(*args, **kwargs):
            pass
        update_wrapper(_wrapper, dummy)
        # Need to preserve any existing attributes of 'func', including the name.
        update_wrapper(_wrapper, func)

        if is_class:
            setattr(obj, name, _wrapper)
            return obj

        return _wrapper
    # Don't worry about making _dec look similar to a list/tuple as it's rather
    # meaningless.
    if not hasattr(decorator, '__iter__'):
        update_wrapper(_dec, decorator)
    # Change the name to aid debugging.
    if hasattr(decorator, '__name__'):
        _dec.__name__ = 'method_decorator(%s)' % decorator.__name__
    else:
        _dec.__name__ = 'method_decorator(%s)' % decorator.__class__.__name__
    return _dec


_T_Look = t.TypeVar('_T_Look')
class lookup_property(property, t.Generic[_T_Look]):
    """Baseclass for `environ_property` and `header_property`."""
    read_only = True

    def __init__(self, name=None, lookup='self', default=..., load_func=None, dump_func=None,
                 read_only=None, doc=None):
        self.name = name
        self.default = default
        self.load_func = load_func
        self.dump_func = dump_func
        if lookup == 'self':
            self.lookup_func = None
            self.read_only = True
        elif isinstance(lookup, str):
            def attr_lookup(obj):
                for a in attr_lookup.attr.split('.'):
                    obj = getattr(obj, a)
                return obj
            attr_lookup.attr = lookup
            self.lookup_func = attr_lookup
        elif callable(lookup):
            self.lookup_func = lookup
        else:
            raise ValueError(
                    f'lookup must be a callable or string. Got {type(lookup)}')
        
        if read_only is not None:
            self.read_only = read_only
        self.__doc__ = doc

    def lookup(self, obj):
        return obj if self.lookup_func is None else self.lookup_func(obj)

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name

    def __get__(self, obj, type=None) -> _T_Look:
        if obj is None:
            return self

        src = self.lookup(obj)
        rv = getattr(src, self.name, self.default)
        if rv is ...:
            raise AttributeError(self.name)
        else:
            return rv if self.load_func is None else self.load_func(obj, rv)

    def __set__(self, obj, value):
        if self.read_only:
            raise AttributeError('read only property')
        if self.dump_func is not None:
            value = self.dump_func(obj, value)

        setattr(self.lookup(obj), self.name, value)

    def __delete__(self, obj):
        if self.read_only:
            raise AttributeError('read only property')
        else:
            delattr(self.lookup(obj), self.name)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.name
        )


class dict_lookup_property(object):

    """Baseclass for `environ_property` and `header_property`."""
    read_only = False

    def __init__(self, name, default=None, lookup=None, load_func=None, dump_func=None,
                 read_only=None, doc=None):
        self.name = name
        self.default = default
        self.load_func = load_func
        self.dump_func = dump_func
        if lookup and isinstance(lookup, str):
            def attr_lookup(obj):
                return getattr(obj, attr_lookup.attr)
            attr_lookup.attr = lookup
            self.lookup_func = attr_lookup
        else:
            self.lookup_func = lookup

        if read_only is not None:
            self.read_only = read_only
        self.__doc__ = doc

    def lookup(self, obj):
        return self.lookup_func(obj)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        storage = self.lookup(obj)
        if self.name not in storage:
            return self.default
        rv = storage[self.name]
        if self.load_func is not None:
            try:
                rv = self.load_func(rv)
            except (ValueError, TypeError):
                rv = self.default
        return rv

    def __set__(self, obj, value):
        if self.read_only:
            raise AttributeError('read only property')
        if self.dump_func is not None:
            value = self.dump_func(value)
        self.lookup(obj)[self.name] = value

    def __delete__(self, obj):
        if self.read_only:
            raise AttributeError('read only property')
        self.lookup(obj).pop(self.name, None)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.name
        )



T = t.TypeVar('T')

@t.overload
def export(obj: T, /, *, name: t.Optional[str] = None, exports: t.Optional[t.List[str]] = None, module: t.Optional[str] = None) -> T: 
	...
@t.overload
def export(*, name: t.Optional[str] = None, exports: t.Optional[t.List[str]] = None, module: t.Optional[str] = None) -> t.Callable[[T], T]: 
	...
def export(obj: T =..., /, *, name=None, exports=None, module=None) -> t.Union[T, t.Callable[[T], T]]:
    def add_to_all(_obj: T) -> T:
        _module = sys.modules[module or _obj.__module__]
        _exports = exports or getattr(_module, '__all__', None)
        if _exports is None:
            _exports = []
            setattr(_module, '__all__', _exports)
        _exports.append(name or _obj.__name__)
        return _obj
    return add_to_all if obj is ... else add_to_all(obj)



def deprecated(alt=None, version=None, *, message=None, onload=False) -> t.Callable[[t.Callable[..., T]], t.Callable[..., T]]:
    """Issues a deprecated warning on module load or when the decorated function is invoked.
    """
    def decorator(func: t.Callable[..., T]) -> t.Callable[..., T]:
        name = f'{func.__module__}.{func.__qualname__}()'
        altname = alt if alt is None or isinstance(alt, str)\
                    else f'{alt.__module__}.{alt.__qualname__}()'
        
        message = (message or ''.join((
                '{name} is deprecated and will be removed in ',
                'version "{version}".' if version else 'upcoming versions.',
                ' Use {altname} instead.' if altname else '',
            ))).format(name=name, altname=altname, version=version)

        if onload:
            warn(message, DeprecationWarning, 2)
        
        @wraps(func)
        def wrapper(*a, **kw) -> T:
            warn(f'{message}', DeprecationWarning, 2)
            return func(*a, **kw)

        return wrapper

    return decorator




# def _attr_is_sloted(cls, attr):
#     """Check if given attribute is in the given class's __slots__.

#     Checks recursively from the class to it's bases."""
#     if not hasattr(cls, '__slots__'):
#         return False

#     if attr in cls.__slots__:
#         return True

#     for base in cls.__bases__:
#         if base is not object and _attr_is_sloted(base, attr):
#             return True

#     return False



# def with_metaclass(meta, *bases):
# 	"""Create a base class with a metaclass."""
# 	# This requires a bit of explanation: the basic idea is to make a dummy
# 	# metaclass for one level of class instantiation that replaces itself with
# 	# the actual metaclass.

# 	class metaclass(meta, *(type(b) for b in bases)):

# 		def __new__(cls, name, this_bases, d):
# 			return meta(name, bases, d)

# 		@classmethod
# 		def __prepare__(cls, name, this_bases):
# 			return meta.__prepare__(name, bases)

# 	return type.__new__(metaclass, 'temporary_class', bases, {})


# _last_creation_index = 0


# def _next_creation_index():
# 	global _last_creation_index
# 	return _last_creation_index += 1


# class CreationOrderMixin:

# 	def __init_subclass__(cls, attribute=None, **kwargs):
# 		super().__init_subclass__(**kwargs)
# 			cls.default_name = default_name

# 	def __init__(self, *a, *kw):
# 		super().__init__(*a, **kw)


# def set_creation_order(func=None, attr='_creation_order'):
# 	def decorator(func):
# 		@wraps(func)
# 		def wrapper(self, *args, **kw):
# 			setattr(self, name, )
# 			rv = func(self, *args, **kw)
