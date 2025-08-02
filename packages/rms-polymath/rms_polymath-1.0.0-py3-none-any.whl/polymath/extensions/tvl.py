################################################################################
# polymath/extensions/tvl.py: Three-valued logic operations
################################################################################

import numpy as np
from polymath.qube import Qube


def tvl_and(self, arg, builtins=None, masked=None):
    """Return the three-valued logic "and" operator result.

    Masked values are treated as indeterminate rather than being ignored. These are the
    rules:

        * False and anything = False
        * True and True = True
        * True and Masked = Masked

    Parameters:
        arg (Qube or bool): The right-hand operand for the AND operation.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked value instead of a builtin
            type.

    Returns:
        (Boolean or bool): The result of the three-valued logic "and" operation.
    """

    # Truth table...
    #           False       Masked      True
    # False     False       False       False
    # Masked    False       Masked      Masked
    # True      False       Masked      True

    self = Qube._BOOLEAN_CLASS.as_boolean(self)
    arg = Qube._BOOLEAN_CLASS.as_boolean(arg)

    if Qube.is_one_false(self._mask):
        self_is_true = self._values
        self_is_not_false = self._values
    else:
        self_is_true = self._values & self.antimask
        self_is_not_false = self._values | self._mask

    if Qube.is_one_false(arg._mask):
        arg_is_true = arg._values
        arg_is_not_false = arg._values
    else:
        arg_is_true = arg._values & arg.antimask
        arg_is_not_false = arg._values | arg._mask

    result_is_true = self_is_true & arg_is_true
    result_is_not_false = self_is_not_false & arg_is_not_false

    result_is_masked = Qube.and_(np.logical_not(result_is_true), result_is_not_false)

    result = Qube._BOOLEAN_CLASS(result_is_true, result_is_masked)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result


def tvl_or(self, arg, builtins=None, masked=None):
    """Return the three-valued logic "or" operator result.

    Masked values are treated as indeterminate rather than being ignored. These are the
    rules:

        * True or anything = True
        * False or False = False
        * False or Masked = Masked

    Parameters:
        arg (Qube or bool): The right-hand operand for the OR operation.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked value instead of a builtin
            type.
            value specified by Qube.PREFER_BUILTIN_TYPES.

    Returns:
        (Boolean or bool): The result of the three-valued logic "or" operation.
    """

    # Truth table...
    #           False       Masked      True
    # False     False       Masked      True
    # Masked    Masked      Masked      True
    # True      True        True        True

    self = Qube._BOOLEAN_CLASS.as_boolean(self)
    arg = Qube._BOOLEAN_CLASS.as_boolean(arg)

    if Qube.is_one_false(self._mask):
        self_is_true = self._values
        self_is_not_false = self._values
    else:
        self_is_true = self._values & self.antimask
        self_is_not_false = self._values | self._mask

    if Qube.is_one_false(arg._mask):
        arg_is_true = arg._values
        arg_is_not_false = arg._values
    else:
        arg_is_true = arg._values & arg.antimask
        arg_is_not_false = arg._values | arg._mask

    result_is_true = self_is_true | arg_is_true
    result_is_not_false = self_is_not_false | arg_is_not_false

    result_is_masked = Qube.and_(np.logical_not(result_is_true), result_is_not_false)

    result = Qube._BOOLEAN_CLASS(result_is_not_false, result_is_masked)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result


def tvl_any(self, axis=None, builtins=None, masked=None):
    """Return True if any unmasked value is True using three-valued logic.

    Masked values are treated as indeterminate rather than being ignored. These are the
    rules:

        * True if any unmasked value is True;
        * False if and only if all the items are False and unmasked;
        * otherwise, Masked.

    Parameters:
        axis (int or tuple, optional): An integer axis or a tuple of axes. The
            any operation is performed across these axes, leaving any remaining
            axes in the returned value. If None (the default), then the any
            operation is performed across all axes of the object.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked value instead of a builtin
            type.

    Returns:
        (Boolean or bool): The result of the three-valued logic "any" operation.
    """

    self = Qube._BOOLEAN_CLASS.as_boolean(self)

    # Construct the input args to Boolean()
    if self._is_scalar:
        args = (self,)
    elif isinstance(self._mask, (bool, np.bool_)):
        args = (np.any(self._values, axis=axis), self._mask)
    else:
        # True where any value is True AND its antimask is True
        new_values = np.any(self._values & self.antimask, axis=axis)

        # Masked if any value is masked unless new_values is True
        masked_found = np.any(self._mask, axis=axis)
        new_mask = np.logical_not(new_values) & masked_found

        args = (new_values, new_mask)

    result = Qube._BOOLEAN_CLASS(*args)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result


def tvl_all(self, axis=None, builtins=None, masked=None):
    """Return True if all unmasked values are True using three-valued logic.

    Masked values are treated as indeterminate rather than being ignored. These are the
    rules:

        * True if and only if all the items are True and unmasked.
        * False if any unmasked value is False.
        * otherwise, Masked.

    Parameters:
        axis (int or tuple, optional): An integer axis or a tuple of axes. The
            all operation is performed across these axes, leaving any remaining
            axes in the returned value. If None (the default), then the all
            operation is performed across all axes of the object.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked value instead of a builtin
            type.

    Returns:
        (Boolean or bool): The result of the three-valued logic "all" operation.
    """

    self = Qube._BOOLEAN_CLASS.as_boolean(self)

    # Construct the input args to Boolean()
    if self._is_scalar:
        args = (self,)
    elif isinstance(self._mask, (bool, np.bool_)):
        args = (np.all(self._values, axis=axis), self._mask)
    else:
        # False where any value is False AND its antimask is True
        # Therefore, True where every value is True OR its mask is True
        new_values = np.all(self._values | self._mask, axis=axis)

        # Masked where any value is masked unless new_values is False
        mask_found = np.any(self._mask, axis=axis)
        new_mask = new_values & mask_found

        args = (new_values, new_mask)

    result = Qube._BOOLEAN_CLASS(*args)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result


def tvl_eq(self, arg, builtins=None):
    """Return the three-valued logic "equals" operator result.

    Masked values are treated as indeterminate, so if either value is masked, the returned
    value is masked.

    Parameters:
        arg (Qube or bool): The right-hand operand for the equality comparison.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().

    Returns:
        (Boolean or bool): The result of the three-valued logic equality comparison.
    """

    return self._tvl_op(arg, (self == arg), builtins=builtins)


def tvl_ne(self, arg, builtins=None):
    """Return the three-valued logic "not equal" operator result.

    Masked values are treated as indeterminate, so if either value is masked, the returned
    value is masked.

    Parameters:
        arg (Qube or bool): The right-hand operand for the inequality comparison.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().

    Returns:
        (Boolean or bool): The result of the three-valued logic inequality comparison.
    """

    return self._tvl_op(arg, (self != arg), builtins=builtins)


def tvl_lt(self, arg, builtins=None):
    """Return the three-valued logic "less than" operator result.

    Masked values are treated as indeterminate, so if either value is masked, the returned
    value is masked.

    Parameters:
        arg (Qube or number): The right-hand operand for the comparison.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().

    Returns:
        (Boolean or bool): The result of the three-valued logic "less than" comparison.
    """

    return self._tvl_op(arg, (self < arg), builtins=builtins)


def tvl_gt(self, arg, builtins=None):
    """Return the three-valued logic "greater than" operator result.

    Masked values are treated as indeterminate, so if either value is masked, the returned
    value is masked.

    Parameters:
        arg (Qube or number): The right-hand operand for the comparison.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().

    Returns:
        (Boolean or bool): The result of the three-valued logic "greater than" comparison.
    """

    return self._tvl_op(arg, (self > arg), builtins=builtins)


def tvl_le(self, arg, builtins=None):
    """Return the three-valued logic "less than or equal to" operator result.

    Masked values are treated as indeterminate, so if either value is masked, the returned
    value is masked.

    Parameters:
        arg (Qube or number): The right-hand operand for the comparison.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().

    Returns:
        (Boolean or bool): The result of the three-valued logic "less than or equal to"
        comparison.
    """

    return self._tvl_op(arg, (self <= arg), builtins=builtins)


def tvl_ge(self, arg, builtins=None):
    """Return the three-valued logic "greater than or equal to" operator result.

    Masked values are treated as indeterminate, so if either value is masked, the returned
    value is masked.

    Parameters:
        arg (Qube or number): The right-hand operand for the comparison.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().

    Returns:
        (Boolean or bool): The result of the three-valued logic "greater than or equal to"
        comparison.
    """

    return self._tvl_op(arg, (self >= arg), builtins=builtins)


def _tvl_op(self, arg, comparison, builtins=None):
    """Return the three-valued logic version of any boolean operator.

    Masked values are treated as indeterminate, so if either value is masked, the returned
    value is masked.

    Parameters:
        arg (Qube or number): The right-hand operand for the operation.
        comparison (Qube or bool): The result of the boolean comparison.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().

    Returns:
        (Boolean or bool): The result of the three-valued logic operation.
    """

    # Return a Python bool if appropriate
    if isinstance(comparison, bool):
        if builtins is None:
            builtins = Qube.prefer_builtins()
        if builtins:
            return comparison

        comparison = Qube._BOOLEAN_CLASS(comparison)

    # Determine arg_mask, if any
    if isinstance(arg, Qube):
        arg_mask = arg._mask
    elif isinstance(arg, np.ma.MaskedArray):
        arg_mask = arg.mask
    else:
        arg_mask = False

    comparison._set_mask(Qube.or_(self._mask, arg_mask))
    return comparison

################################################################################
