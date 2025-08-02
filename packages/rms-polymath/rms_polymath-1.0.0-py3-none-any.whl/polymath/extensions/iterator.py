################################################################################
# polymath/extensions/iterator.py: iterator over Qube objects
################################################################################

import itertools
import numpy as np


class QubeIterator(object):
    """Provide iteration across the first axis of a Qube object.

    This iterator allows iteration over elements along the first axis of a Qube object,
    similar to how NumPy arrays can be iterated.

    Attributes:
        obj (list or Qube): The object to iterate over.
        stop (int): The number of elements to iterate through.
        index (int): The current iteration position.
    """

    def __init__(self, obj):
        """Initialize the iterator with a Qube object.

        Parameters:
            obj (Qube): The Qube object to iterate over.
        """

        if not obj._shape:
            self.obj = [obj]
            self.stop = 1
        else:
            self.obj = obj
            self.stop = obj._shape[0]

        self.index = -1

    def __iter__(self):
        """Return the iterator object itself.

        Returns:
            QubeIterator: This iterator instance.
        """

        self.index = -1
        return self

    def __next__(self):
        """Return the next item in the iteration.

        Returns:
            Qube: The next element in the iteration.

        Raises:
            StopIteration: When iteration is complete.
        """

        self.index += 1
        if self.index >= self.stop:
            raise StopIteration

        return self.obj[self.index]


class QubeNDIterator(object):
    """Provide iteration across all axes of a Qube object.

    This iterator allows iteration over all elements in a multi-dimensional Qube object,
    returning both the index tuple and the value at that index.

    Attributes:
        obj (ndarray): The object to iterate over.
        shape (tuple): The shape of the object.
        iterator (iterator): The underlying iterator.
    """

    def __init__(self, obj):
        """Initialize the iterator with a Qube object.

        Parameters:
            obj (Qube): The Qube object to iterate over.
        """

        if not obj._shape:
            self.obj = np.array([obj], dtype='object')
            self.shape = (1,)
        else:
            self.obj = obj
            self.shape = obj._shape

        self.iterator = None

    def __iter__(self):
        """Return the iterator object itself.

        Returns:
            QubeNDIterator: This iterator instance.
        """

        self.iterator = itertools.product(*[range(s) for s in self.shape])
        return self

    def __next__(self):
        """Return the next item in the iteration.

        Returns:
            tuple: A tuple containing (index_tuple, item_at_index).

        Raises:
            StopIteration: When iteration is complete.
        """

        indx = self.iterator.__next__()
        return (indx, self.obj[indx])


def __iter__(self):
    """Return an iterator over the first axis of this object.

    Returns:
        QubeIterator: An iterator that iterates over the first axis of the object.
    """

    return QubeIterator(obj=self)


def ndenumerate(self):
    """Iterate across all axes of this object.

    This method provides an iterator that returns tuples containing the index
    and the corresponding item at that index.

    Returns:
        QubeNDIterator: An iterator yielding (index_tuple, item_at_index) pairs.
    """

    return QubeNDIterator(obj=self)

################################################################################
