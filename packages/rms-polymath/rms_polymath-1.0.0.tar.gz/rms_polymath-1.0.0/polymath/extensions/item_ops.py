##########################################################################################
# polymath/extensions/item_ops.py: item restructuring operations
##########################################################################################

import numpy as np
from polymath.qube import Qube


def extract_numer(self, axis, index, classes=(), *, recursive=True):
    """Extract an object from one numerator axis.

    Parameters:
        axis (int): The item axis from which to extract a slice.
        index (int): The index value at which to extract the slice.
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
        recursive (bool, optional): True to include matching slices of the derivatives in
            the returned object; otherwise, the returned object will not contain
            derivatives.

    Returns:
        Qube: An object extracted from the specified numerator axis.

    Raises:
        ValueError: If the axis is out of range.
    """

    self._require_axis_in_range(axis, self._nrank, 'extract_numer()')

    # Position axis from left
    a1 = axis if axis >= 0 else axis + self._nrank
    k1 = self._ndims + a1

    # Roll this axis to the beginning and slice it out
    new_values = np.rollaxis(self._values, k1, 0)
    new_values = new_values[index]

    # Construct and cast
    obj = Qube(new_values, self._mask, nrank=self._nrank-1, example=self)
    obj = obj.cast(classes)
    obj._readonly = self._readonly

    # Slice the derivatives if necessary
    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.extract_numer(a1, index, classes=classes,
                                                      recursive=False))

    return obj


def extract_denom(self, axis, index, classes=()):
    """Extract an object from one denominator axis.

    Parameters:
        axis (int): The item axis from which to extract a slice.
        index (int): The index value at which to extract the slice.
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.

    Returns:
        Qube: An object extracted from the specified denominator axis.

    Raises:
        ValueError: If the axis is out of range.
    """

    self._require_axis_in_range(axis, self._drank, 'extract_denom()')

    # Position axis from left
    a1 = axis if axis >= 0 else axis + self._drank
    k1 = self._ndims + self._nrank + a1

    # Roll this axis to the beginning and slice it out
    new_values = np.rollaxis(self._values, k1, 0)
    new_values = new_values[index]

    # Construct and cast
    obj = Qube(new_values, self._mask, drank=self._drank - 1,
               example=self)
    obj = obj.cast((type(self),) + classes)
    obj._readonly = self._readonly

    return obj


def extract_denoms(self):
    """A tuple of objects extracted from one object with a 1-D denominator.

    Returns a list of objects with the same class as self, but drank = 0.

    Returns:
        list: A list of objects with drank = 0.

    Raises:
        ValueError: If the object does not have a 1-D denominator.
    """

    if self._drank == 0:
        return [self]

    if self._drank != 1:
        raise ValueError(f'{type(self).__name__}.extract_denoms() requires drank == 1')

    objects = []
    for k in range(self._denom[0]):
        obj = Qube.__new__(type(self))
        obj.__init__(self._values[..., k], self._mask, drank=0, example=self)
        obj._readonly = self._readonly
        objects.append(obj)

    return objects


def slice_numer(self, axis, index1, index2, classes=(), *, recursive=True):
    """Extract an object sliced from one numerator axis.

    Parameters:
        axis (int): The item axis from which to extract a slice.
        index1 (int): The starting index value at which to extract the slice.
        index2 (int): The ending index value at which to extract the slice.
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
        recursive (bool, optional): True to include matching slices of the derivatives in
            the returned object; otherwise, the returned object will not contain
            derivatives.

    Returns:
        Qube: An object sliced from the specified numerator axis.

    Raises:
        ValueError: If the axis is out of range.
    """

    self._require_axis_in_range(axis, self._nrank, 'slice_numer()')

    # Position axis from left
    a1 = axis if axis >= 0 else axis + self._nrank
    k1 = self._ndims + a1

    # Roll this axis to the beginning and slice it out
    new_values = np.rollaxis(self._values, k1, 0)
    new_values = new_values[index1:index2]
    new_values = np.rollaxis(new_values, 0, k1+1)

    # Construct and cast
    obj = Qube(new_values, self._mask, example=self)
    obj = obj.cast(classes)
    obj._readonly = self._readonly

    # Slice the derivatives if necessary
    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.slice_numer(a1, index1, index2, classes=classes,
                                                    recursive=False))

    return obj

##########################################################################################
# Numerator shaping operations
##########################################################################################

def transpose_numer(self, axis1=0, axis2=1, *, recursive=True):
    """A copy of this object with two numerator axes transposed.

    Parameters:
        axis1 (int, optional): The first axis to transpose from among the numerator axes.
            Negative values count backward from the last numerator axis.
        axis2 (int, optional): The second axis to transpose.
        recursive (bool, optional): True to transpose the same axes of the derivatives;
            False to return an object without derivatives.

    Returns:
        Qube: A copy with the specified numerator axes transposed.

    Raises:
        ValueError: If either axis is out of range.
    """

    self._require_axis_in_range(axis1, self._nrank, 'slice_numer()', 'axis1')
    self._require_axis_in_range(axis2, self._nrank, 'slice_numer()', 'axis2')

    # Position axis1 from left
    a1 = axis1 if axis1 >= 0 else axis1 + self._nrank
    k1 = self._ndims + a1

    # Position axis2 from item left
    a2 = axis2 if axis2 >= 0 else axis2 + self._nrank
    k2 = self._ndims + a2

    # Swap the axes
    new_values = np.swapaxes(self._values, k1, k2)

    # Construct the result
    obj = Qube.__new__(type(self))
    obj.__init__(new_values, self._mask, example=self)
    obj._readonly = self._readonly

    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.transpose_numer(a1, a2, recursive=False))

    return obj


def reshape_numer(self, shape, classes=(), recursive=True):
    """This object with a new shape for numerator items.

    Parameters:
        shape (tuple): The new shape for numerator items.
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
        recursive (bool, optional): True to reshape the derivatives in the same way;
            otherwise, the returned object will not contain derivatives.

    Returns:
        Qube: The reshaped object.

    Raises:
        ValueError: If the item size would be changed by the reshape operation.
    """

    # Validate the shape
    shape = tuple(shape)
    if self.nsize != int(np.prod(shape)):
        opstr = self._opstr('reshape_numer()')
        raise ValueError(f'{opstr} item size must be unchanged: {self._numer}, {shape}')

    # Reshape
    full_shape = self._shape + shape + self._denom
    new_values = np.asarray(self._values).reshape(full_shape)

    # Construct and cast
    obj = Qube(new_values, self._mask, nrank=len(shape), example=self)
    obj = obj.cast(classes)
    obj._readonly = self._readonly

    # Reshape the derivatives if necessary
    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.reshape_numer(shape, classes, False))

    return obj


def flatten_numer(self, classes=(), *, recursive=True):
    """This object with a new numerator shape such that nrank == 1.

    Parameters:
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
        recursive (bool, optional): True to include matching slices of the derivatives in
            the returned object; otherwise, the returned object will not contain
            derivatives.

    Returns:
        Qube: The flattened object.
    """

    return self.reshape_numer((self.nsize,), classes, recursive=recursive)

##########################################################################################
# Denominator shaping operations
##########################################################################################

def transpose_denom(self, axis1=0, axis2=1):
    """A copy of this object with two denominator axes transposed.

    Parameters:
        axis1 (int, optional): The first axis to transpose from among the denominator
            axes. Negative values count backward from the last axis.
        axis2 (int, optional): The second axis to transpose.

    Returns:
        Qube: The transposed object.

    Raises:
        ValueError: If either axis is out of range.
    """

    self._require_axis_in_range(axis1, self._drank, 'transpose_denom()', 'axis1')
    self._require_axis_in_range(axis2, self._drank, 'transpose_denom()', 'axis2')

    # Position axis1 from left
    a1 = axis1 if axis1 >= 0 else axis1 + self._drank
    k1 = self._ndims + self._nrank + a1

    # Position axis2 from item left
    a2 = axis2 if axis2 >= 0 else axis2 + self._drank
    k2 = self._ndims + self._nrank + a2

    # Swap the axes
    new_values = np.swapaxes(self._values, k1, k2)

    # Construct the result
    obj = Qube.__new__(type(self))
    obj.__init__(new_values, self._mask, example=self)
    obj._readonly = self._readonly

    return obj


def reshape_denom(self, shape):
    """This object with a new shape for denominator items.

    Parameters:
        shape (tuple): The new denominator shape.

    Returns:
        Qube: The reshaped object.

    Raises:
        ValueError: If the denominator size would be changed by the reshape operation.
    """

    # Validate the shape
    shape = tuple(shape)
    if self.dsize != int(np.prod(shape)):
        opstr = self._opstr('reshape_numer()')
        raise ValueError(f'{opstr} denominator size must be unchanged: {self._denom}, '
                         f'{shape}')

    # Reshape
    full_shape = self._shape + self._numer + shape
    new_values = np.asarray(self._values).reshape(full_shape)

    # Construct and cast
    obj = Qube.__new__(type(self))
    obj.__init__(new_values, self._mask, drank=len(shape), example=self)
    obj._readonly = self._readonly

    return obj


def flatten_denom(self):
    """This object with a new denominator shape such that drank == 1.
    """

    return self.reshape_denom((self.dsize,))

##########################################################################################
# Numerator/denominator operations
##########################################################################################

def join_items(self, classes):
    """The object with denominator axes joined to the numerator.

    Derivatives are removed.

    Parameters:
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.

    Returns:
        Qube: The object with joined items.
    """

    if not self._drank:
        return self.wod

    obj = Qube(self._values, self._mask, nrank=(self._nrank + self._drank), drank=0,
               example=self)
    obj = obj.cast(classes)
    obj._readonly = self._readonly

    return obj


def split_items(self, nrank, classes):
    """The object with numerator axes converted to denominator axes.

    Derivatives are removed.

    Parameters:
        nrank (int): Number of numerator axes to retain.
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.

    Returns:
        Qube: The object with split items.
    """

    obj = Qube(self._values, self._mask, nrank=nrank, drank=(self._rank - nrank),
               example=self)
    obj = obj.cast(classes)
    obj._readonly = self._readonly

    return obj


def swap_items(self, classes):
    """A new object with the numerator and denominator axes exchanged.

    Derivatives are removed.

    Parameters:
        classes (class, list, or tuple, optional): The class of the object returned. If
            a list is provided, the object will be an instance of the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.

    Returns:
        Qube: The object with swapped items.
    """

    new_values = self._values
    len_shape = new_values.ndim

    for r in range(self._nrank):
        new_values = np.rollaxis(new_values, -self._drank-1, len_shape)

    obj = Qube(new_values, self._mask, nrank=self._drank, drank=self._nrank, example=self)
    obj = obj.cast(classes)
    obj._readonly = self._readonly
    return obj


def chain(self, /, arg):
    """The chain multiplication of this derivative by another.

    Returns the denominator of the first object times the numerator of the second
    argument. The result will be an instance of the same class. This operation is never
    recursive.

    Parameters:
        arg (Qube): The right-hand term in the chain multiplication.

    Returns:
        Qube: The result of the chain multiplication.
    """

    left = self.flatten_denom().join_items(Qube)
    right = arg.flatten_numer(Qube)

    return Qube.dot(left, right, -1, 0, classes=[type(self)], recursive=False)

def __matmul__(self, /, arg):
    """The chain multiplication of this derivative by another.

    Returns the denominator of the first object times the numerator of the second
    argument. The result will be an instance of the same class. This operation is never
    recursive.

    Parameters:
        arg (Qube): The right-hand term in the chain multiplication.

    Returns:
        Qube: The result of the chain multiplication.
    """

    return self.chain(arg)

##########################################################################################
