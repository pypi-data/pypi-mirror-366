##########################################################################################
# polymath/extensions/shaper.py: re-shaping operations
##########################################################################################

import numpy as np
from polymath.qube import Qube


def reshape(self, shape, *, recursive=True):
    """Return a shallow copy of the object with a new leading shape.

    Parameters:
        shape (tuple or int): A tuple defining the new leading shape. A value of -1 can
            appear at one location in the new shape, and the size of that shape will be
            determined based on this object's size.
        recursive (bool, optional): True to apply the same shape to the derivatives.
            Otherwise, derivatives are deleted from the returned object.

    Returns:
        Qube: A shallow copy with the new shape. If the shape is unchanged, this object is
            returned without modification. The read-only status is preserved.

    Raises:
        ValueError: If the new shape is incompatible with the current shape.
    """

    if np.isscalar(shape):
        shape = (shape,)
    elif not isinstance(shape, tuple):
        shape = tuple(shape)

    new_values = np.reshape(self._values, shape + self._item)
    if isinstance(self._mask, np.ndarray):
        new_mask = self._mask.reshape(shape)
    else:
        new_mask = self._mask

    obj = Qube.__new__(type(self))
    obj.__init__(new_values, new_mask, example=self)
    obj._readonly = self._readonly

    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.reshape(shape, recursive=False))

    return obj


def flatten(self, *, recursive=True):
    """Return a shallow copy of the object flattened to one dimension.

    Parameters:
        recursive (bool, optional): True to apply the same flattening to the derivatives.
            Otherwise, derivatives are deleted from the returned object.

    Returns:
        Qube: A shallow copy flattened to one dimension.
    """

    if self._ndims <= 1:
        return self

    count = np.prod(self._shape)
    return self.reshape((count,), recursive=recursive)


def swap_axes(self, axis1, axis2, *, recursive=True):
    """Return a shallow copy of the object with two leading axes swapped.

    Parameters:
        axis1 (int): The first index of the swap. Negative indices are relative to the
            last index before the numerator items begin.
        axis2 (int): The second index of the swap.
        recursive (bool, optional): True to perform the same swap on the derivatives.
            Otherwise, derivatives are deleted from the returned object.

    Returns:
        Qube: A shallow copy with the specified axes swapped.

    Raises:
        ValueError: If either axis is out of range.
    """

    self._require_axis_in_range(axis1, self._ndims, 'swap_axes()', name='axis1')
    self._require_axis_in_range(axis2, self._ndims, 'swap_axes()', name='axis2')

    a1 = axis1 % self._ndims
    a2 = axis2 % self._ndims
    if a1 == a2:
        return self

    # Swap the axes of values and mask
    new_values = np.swapaxes(self._values, a1, a2)
    if isinstance(self._mask, np.ndarray):
        new_mask = self._mask.swapaxes(a1, a2)
    else:
        new_mask = self._mask

    obj = Qube.__new__(type(self))
    obj.__init__(new_values, new_mask, example=self)
    obj._readonly = self._readonly

    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.swap_axes(a1, a2, recursive=False))

    return obj


def roll_axis(self, axis, start=0, *, recursive=True, rank=None):
    """A shallow copy of the object with the specified axis rolled to a new position.

    Parameters:
        axis (int): The axis to roll.
        start (int, optional): The axis will be rolled to fall in front of this axis.
        recursive (bool, optional): True to perform the same axis roll on the derivatives.
            Otherwise, derivatives are deleted from the returned object.
        rank (int, optional): Rank to assume for the object, which could be larger than
            len(self.shape) because of broadcasting.

    Returns:
        Qube: A shallow copy with the axis rolled to the new position.

    Raises:
        ValueError: If the rank is too small for the object shape.
        ValueError: If the axis or start is out of range.
    """

    # Validate the rank
    rank = self._ndims if rank is None else rank
    if rank < self._ndims:
        opstr = self._opstr('roll_axis()')
        raise ValueError(f'{opstr} rank {rank} is too small for shape {self._shape}')

    # Identify the axis to roll, which could be negative
    self._require_axis_in_range(axis, rank, 'roll_axis()')
    a1 = axis % rank

    # Identify the start axis, which could be negative; note start == rank is valid
    if start != rank:
        self._require_axis_in_range(start, rank, 'roll_axis()', 'start')
    a2 = start + rank if start < 0 else start

    # Add missing axes if necessary
    if self._ndims < rank:
        self = self.reshape((rank - self._ndims) * (1,) + self._shape,
                            recursive=recursive)

    # Roll the values and mask of the object
    new_values = np.rollaxis(self._values, a1, a2)
    if isinstance(self._mask, np.ndarray):
        new_mask = np.rollaxis(self._mask, a1, a2)
    else:
        new_mask = self._mask

    obj = Qube.__new__(type(self))
    obj.__init__(new_values, new_mask, example=self)
    obj._readonly = self._readonly

    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.roll_axis(a1, a2, recursive=False, rank=rank))

    return obj


def move_axis(self, source, destination, *, recursive=True, rank=None):
    """A shallow copy of the object with the specified axis moved to a new position.

    Parameters:
        source (int or tuple): Axis to move or tuple of axes to move.
        destination (int or tuple): Destination of moved axis or axes.
        recursive (bool, optional): True to perform the same axis move on the derivatives.
            Otherwise, derivatives are deleted from the returned object.
        rank (int, optional): Rank to assume for the object, which could be larger than
            len(self.shape) because of broadcasting.

    Returns:
        Qube: A shallow copy with the specified axis moved to the new position.

    Raises:
        ValueError: If the rank is too small for the object shape.
        ValueError: If any axis is out of range.
    """

    # Validate the rank
    rank = self._ndims if rank is None else rank
    if rank < self._ndims:
        opstr = self._opstr('move_axis()')
        raise ValueError(f'{opstr} rank {rank} is too small for shape {self._shape}')

    # Identify the axes, which could be negative
    if np.isscalar(source):
        source = (source,)
    if np.isscalar(destination):
        destination = (destination,)

    for axis in source:
        self._require_axis_in_range(axis, rank, 'move_axis()', 'source')
    for axis in destination:
        self._require_axis_in_range(axis, rank, 'move_axis()', 'destination')

    source = tuple(x % rank for x in source)
    destination = tuple(x % rank for x in destination)

    # Add missing axes if necessary
    if self._ndims < rank:
        self = self.reshape((rank - self._ndims) * (1,) + self._shape,
                            recursive=recursive)

    # Move the values and mask of the object
    new_values = np.moveaxis(self._values, source, destination)
    if isinstance(self._mask, np.ndarray):
        new_mask = np.moveaxis(self._mask, source, destination)
    else:
        new_mask = self._mask

    obj = Qube.__new__(type(self))
    obj.__init__(new_values, new_mask, example=self)
    obj._readonly = self._readonly

    if recursive:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.move_axis(source, destination,
                                                  recursive=False, rank=rank))

    return obj


@staticmethod
def stack(*args, recursive=True):
    """Stack objects into one with a new leading axis.

    Parameters:
        *args: Any number of Scalars or arguments that can be casted to Scalars. They need
            not have the same shape, but it must be possible to cast them to the same
            shape. A value of None is converted to a zero-valued Scalar that matches the
            denominator shape of the other arguments.
        recursive (bool, optional): True to include all the derivatives. The returned
            object will have derivatives representing the union of all the derivatives
            found amongst the scalars.

    Returns:
        Qube: A stacked object with a new leading axis.

    Raises:
        TypeError: If an unexpected keyword argument is provided.
        ValueError: If the arguments have incompatible denominators.
    """

    args = list(args)

    # Get the type and unit if any
    # Only use class Qube if no suitable subclass was found
    floats_found = False
    ints_found = False

    float_arg = None
    int_arg = None
    bool_arg = None

    unit = None
    denom = None
    subclass_indx = None

    for i, arg in enumerate(args):
        if arg is None:
            continue

        qubed = False
        if not isinstance(arg, Qube):
            arg = Qube(arg)
            args[i] = arg
            qubed = True

        if denom is None:
            denom = arg._denom
        elif denom != arg._denom:
            raise ValueError('incompatible denominator shapes for stack(): '
                             f'{denom}, {arg._denom}')

        if arg.is_float():
            floats_found = True
            if float_arg is None or not qubed:
                float_arg = arg
                subclass_indx = i
        elif arg.is_int() and float_arg is None:
            ints_found = True
            if int_arg is None or not qubed:
                int_arg = arg
                subclass_indx = i
        elif arg.is_bool() and int_arg is None and float_arg is None:
            if bool_arg is None or not qubed:
                bool_arg = arg
                subclass_indx = i

        if arg._unit is not None:
            if unit is None:
                unit = arg._unit
            else:
                arg.confirm_unit(unit)

    drank = len(denom)

    # Convert to subclass and type
    for i, arg in enumerate(args):
        if arg is None:                 # Used as placehold for derivs
            continue

        args[i] = args[subclass_indx].as_this_type(arg, recursive=recursive,
                                                   coerce=False)

    # Broadcast all inputs into a common shape
    args = Qube.broadcast(*args, recursive=True)

    # Determine what type of mask is needed:
    mask_true_found = False
    mask_false_found = False
    mask_array_found = False
    for arg in args:
        if arg is None:
            continue
        elif Qube.is_one_true(arg._mask):
            mask_true_found = True
        elif Qube.is_one_false(arg._mask):
            mask_false_found = True
        else:
            mask_array_found = True

    # Construct the mask
    if mask_array_found or (mask_false_found and mask_true_found):
        mask = np.zeros((len(args),) + args[subclass_indx].shape, dtype=np.bool_)
        for i in range(len(args)):
            if args[i] is None:
                mask[i] = False
            else:
                mask[i] = args[i]._mask
    else:
        mask = mask_true_found

    # Construct the array
    if floats_found:
        dtype = np.float64
    elif ints_found:
        dtype = np.int_
    else:
        dtype = np.bool_

    values = np.empty((len(args),) + np.shape(args[subclass_indx]._values), dtype=dtype)
    for i in range(len(args)):
        if args[i] is None:
            values[i] = 0
        else:
            values[i] = args[i]._values

    # Construct the result
    result = Qube.__new__(type(args[subclass_indx]))
    result.__init__(values, mask, unit=unit, drank=drank)

    # Fill in derivatives if necessary
    if recursive:
        keys = []
        for arg in args:
            if arg is None:
                continue
            keys += arg._derivs.keys()

        keys = set(keys)        # remove duplicates

        derivs = {}
        for key in keys:
            deriv_list = []
            for arg in args:
                if arg is None:
                    deriv_list.append(None)
                else:
                    deriv_list.append(arg._derivs.get(key, None))

            derivs[key] = Qube.stack(*deriv_list, recursive=False)

        result.insert_derivs(derivs)

    return result

##########################################################################################
