##########################################################################################
# polymath/extensions/broadcaster.py: broadcast operations
##########################################################################################

import numpy as np
from polymath.qube import Qube


def broadcast_into_shape(self, shape, *, recursive=True, _protected=True):
    """This object broadcasted to the specified shape. DEPRECATED name; use broadcast_to.

    Parameters:
        shape (tuple): The shape into which the object is to be broadcast.
        recursive (bool, optional): True to broadcast the derivatives as well. Otherwise,
            they are removed.
        _protected (bool, optional): False to prevent the arrays being set to readonly.
            Note that this is a potentially dangerous option, because some elements of the
            returned array share memory with one another and with the original object.

    Returns:
        The broadcasted object; self if the shape already matches.

    Notes:
        Both the original object and the returned array are normally set to read-only,
        because they share memory with one another and because memory is shared among the
        elements of the returned array. The `_protected` option overrides this, leaving
        both arrays writable.
    """

    return self.broadcast_to(shape, recursive=recursive, _protected=_protected)


def broadcast_to(self, shape, *, recursive=True, _protected=True):
    """This object broadcasted to the specified shape.

    Parameters:
        shape (tuple): The shape into which the object is to be broadcast.
        recursive (bool, optional): True to broadcast the derivatives as well. Otherwise,
            they are removed.
        _protected (bool, optional): False to prevent the arrays being set to readonly.
            Note that this is a potentially dangerous option, because some elements of the
            returned array share memory with one another and with the original object.

    Returns:
        The broadcasted object; self if the shape already matches.

    Notes:
        Both the original object and the returned array are normally set to read-only,
        because they share memory with one another and because memory is shared among the
        elements of the returned array. The `_protected` option overrides this, leaving
        both arrays writable.
    """

    shape = tuple(shape)

    # If no broadcast is needed, return the object
    if shape == self._shape:
        return self if recursive else self.wod

    # Save the derivatives for later
    derivs = self._derivs

    # Special case: broadcast to ()
    if shape == ():
        if self._rank == 0:
            if isinstance(self._values, np.ndarray):
                new_values = self._values.ravel()[0]
            else:
                new_values = self._values
        else:
            new_values = self._values.reshape(self._item)

        if isinstance(self._mask, np.ndarray):
            new_mask = bool(self._mask.ravel()[0])
        else:
            new_mask = bool(self._mask)

        # Construct the new object
        obj = Qube.__new__(type(self))
        obj.__init__(new_values, new_mask, example=self)

    else:

        # Broadcast the values array
        if self._is_scalar:
            self_values = np.array([self._values])
        else:
            self_values = self._values

            # An array should be read-only upon broadcast
            if _protected:
                self.as_readonly(recursive=False)

        new_values = np.broadcast_to(self_values, shape + self._item)

        # Broadcast the mask if necessary
        if isinstance(self._mask, np.ndarray):
            new_mask = np.broadcast_to(self._mask, shape)

            # An array should be read-only upon broadcast
            if _protected:
                self.as_readonly(recursive=False)
        else:
            new_mask = self._mask

        # Construct the new object
        obj = Qube.__new__(type(self))
        obj.__init__(new_values, new_mask, example=self)
        obj.as_readonly(recursive=False)

    # Process the derivatives if necessary
    if recursive:
        for key, deriv in derivs.items():
            obj.insert_deriv(key, deriv.broadcast_to(shape, recursive=False,
                                                     _protected=_protected))

    return obj


def broadcasted_shape(*objects, item=()):
    """The shape defined by a broadcast across the objects.

    Parameters:
        *objects (Qube, array-like, int, float, None, or tuple): Zero or more array
            objects. Values of None are assigned shape (). A list or tuple is treated as
            the definition of an additional shape.
        item (list or tuple, optional): A list or tuple to be appended to the shape.
            This makes it possible to use the returned shape in the declaration of a NumPy
            array containing items that are not scalars.

    Returns:
        The broadcast shape, comprising the maximum value of each corresponding axis, with
        the `item` shape appended if any.

    Raises:
        ValueError: If an object dimension is incompatible with the broadcast.
    """

    # Create a list of all shapes
    shapes = []
    for obj in objects:
        if obj is None or Qube._is_one_value(obj):
            shape = ()
        elif isinstance(obj, (tuple, list)):
            shape = tuple(obj)
        else:
            shape = obj.shape

        shapes.append(shape)

    # Initialize the shape
    new_shape = []
    len_broadcast = 0

    # Loop through the arrays...
    for shape in shapes:
        shape = list(shape)

        # Expand the shapes to the same rank
        len_shape = len(shape)

        if len_shape > len_broadcast:
            new_shape = (len_shape - len_broadcast) * [1] + new_shape
            len_broadcast = len_shape

        if len_broadcast > len_shape:
            shape = (len_broadcast - len_shape) * [1] + shape
            len_shape = len_broadcast

        # Update the broadcast shape and check for compatibility
        for i in range(len_shape):
            if new_shape[i] == 1:
                new_shape[i] = shape[i]
            elif shape[i] == 1:
                pass
            elif shape[i] != new_shape[i]:
                raise ValueError(f'incompatible dimension on axis {i}: {new_shape}')

    return tuple(new_shape) + tuple(item)


def broadcast(*objects, recursive=True, _protected=True):
    """Broadcast one or objects to their common shape.

    Python scalars are returned unchanged because they already broadcast with anything.

    Parameters:
        *objects (Qube, array-like, int, float, None, or tuple):
            Zero or more array objects. Values of None are assigned shape (). A list or
            tuple is treated as the definition of an additional shape.
        recursive (bool, optional): True to broadcast the derivatives to the same shape;
            False to strip the derivatives from the returned objects.
        _protected (bool, optional): False to prevent the arrays being set to readonly.
            Note that this is a potentially dangerous option, because memory is shared
            among the elements within each of the returned objects.

    Returns:
        A tuple of objects, all broadcased to the common shape. Python scalars are
        returned unchanged because they already broadcast with anything.

    Raises:
        ValueError: If an object dimension is incompatible with the broadcast.

    Notes:
        Returned objects must be treated as read-only because of the mechanism NumPy uses
        to broadcast arrays. The returned objects are marked read-only but their internal
        arrays are not protected.
    """

    # Perform the broadcasts...
    shape = Qube.broadcasted_shape(*objects)
    results = []
    for obj in objects:
        if isinstance(obj, np.ndarray):
            new_obj = np.broadcast_to(obj, shape)
        elif isinstance(obj, Qube):
            new_obj = obj.broadcast_to(shape, recursive=recursive, _protected=_protected)
        else:
            new_obj = obj
        results.append(new_obj)

    return tuple(results)

##########################################################################################
