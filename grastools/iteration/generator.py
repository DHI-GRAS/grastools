import collections
import functools


class InconsistentLengthError(Exception):
    pass


class IteratorWithLength(collections.abc.Sized, collections.abc.Iterator):
    """Iterable with __len__ method"""

    def __init__(self, iterable, length=None):
        self._count = 0
        self._iterable = iterable.__iter__()
        self._length = length
        super(IteratorWithLength, self).__init__()

    @property
    def length(self):
        return self.__len__()

    def __len__(self):
        if self._length is None:
            self.__iter__()
        return self._length

    def __iter__(self):
        self._iterable.__iter__()

        if self._length is not None:
            return self

        try:
            first = self._iterable.__next__()
            isempty = False
        except StopIteration:
            isempty = True

        if isempty:
            raise InconsistentLengthError('Empty iterator')

        try:
            self._length = int(first)
            isint = True
        except TypeError:
            isint = False

        if not isint:
            raise TypeError('First yielded element must be an integer if length is not given')

        return self

    def __next__(self):
        try:
            item = self._iterable.__next__()
        except StopIteration:
            if self._count < self._length:
                raise InconsistentLengthError('Iterator shorter than given length')
            raise

        self._count += 1
        if self._count > self._length:
            raise InconsistentLengthError('Iterator longer than given length')

        return item

    def __repr__(self):
        return '<IteratorWithLength(iterable=%r, length=%d)>' % (self._iterable, self._length)


class GeneratorWithLength(IteratorWithLength, collections.abc.Generator):
    def send(self, *args, **kwargs):
        return self._iterable.send(*args, **kwargs)

    def throw(self, *args, **kwargs):
        return self._iterable.throw(*args, **kwargs)

    def __repr__(self):
        return '<GeneratorWithLength(iterable=%r, length=%d)>' % (self._iterable, self._length)


def sequence(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        return GeneratorWithLength(function(*args, **kwargs))
    return wrapped


def generator_with_length(iterable, length):
    if isinstance(iterable, collections.abc.Generator):
        return GeneratorWithLength(iterable, length=length)

    iter(iterable)
    return IteratorWithLength(iterable, length=length)
