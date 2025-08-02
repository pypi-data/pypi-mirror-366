##########################################################################################
# polymath/extensions/math_ops.py: Math operations
##########################################################################################

import numpy as np
import numbers
from polymath.qube import Qube
from polymath.unit import Unit

##########################################################################################
# Unary operators
##########################################################################################

def __pos__(self, *, recursive=True):
    """+self, element by element.

    Parameters:
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The result.
    """

    return self.clone(recursive=recursive)


def __neg__(self, *, recursive=True):
    """-self, element-by-element negation.

    Parameters:
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The result.
    """

    # Construct a copy with negative values
    obj = self.clone(recursive=False)
    obj._set_values(-self._values)

    # Fill in the negative derivatives
    if recursive and self._derivs:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, -deriv)

    return obj


def __abs__(self, *, recursive=True):
    """abs(self), element-by-element absolute value.

    Parameters:
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The result.
    """

    _raise_unsupported_op('abs()', self)


def abs(self):
    """abs(self), element-by-element absolute value."""

    return self.__abs__()

def __len__(self):
    """Number of elements along first axis."""

    if self._ndims:
        return self._shape[0]
    else:
        raise TypeError(f'len of unsized {type(self).__name__} object')

def len(self):
    """Number of elements along first axis."""

    return self.__len__()

##########################################################################################
# Addition
##########################################################################################

def __add__(self, /, arg, *, recursive=True):
    """self + arg, element-by-element addition.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The sum.
    """

    # Handle a simple right-hand value...
    if self._rank == 0 and isinstance(arg, numbers.Real):
        obj = self.clone(recursive=recursive, retain_cache=True)
        obj._set_values(self._values + arg, retain_cache=True)
        return obj

    # Convert arg to another Qube if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = self.as_this_type(arg, coerce=False, op='+')
        except (ValueError, TypeError):
            _raise_unsupported_op('+', self, original_arg)

    # Verify compatibility
    self._require_compatible_units(arg, '+')

    if self._numer != arg._numer:
        if type(self) is not type(arg):
            _raise_unsupported_op('+', self, original_arg)

        _raise_incompatible_numers('+', self, arg)

    if self._denom != arg._denom:
        _raise_incompatible_denoms('+', self, arg)

    # Construct the result
    obj = Qube.__new__(type(self))
    obj.__init__(self._values + arg._values,
                 Qube.or_(self._mask, arg._mask),
                 unit=self._unit or arg._unit,
                 example=self)

    if recursive:
        obj.insert_derivs(obj._add_derivs(self, arg))

    return obj


def __radd__(self, /, arg, *, recursive=True):
    """arg + self, element-by-element addition.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The sum.
    """

    return self.__add__(arg, recursive=recursive)

def __iadd__(self, /, arg):
    """self += arg, element-by-element in-place addition.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: self after the addition.
    """

    self.require_writeable()

    # Handle a simple right-hand value...
    if self._rank == 0 and isinstance(arg, (numbers.Real, np.ndarray)):
        self._values += arg
        self._new_values()
        return self

    # Convert arg to another Qube if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = self.as_this_type(arg, coerce=False, op='+=')
        except (ValueError, TypeError):
            _raise_unsupported_op('+=', self, original_arg)

    # Verify compatibility
    self._require_compatible_units(arg, '+=')

    if self._numer != arg._numer:
        if type(self) is not type(arg):
            _raise_unsupported_op('+=', self, original_arg)

        _raise_incompatible_numers('+=', self, arg)

    if self._denom != arg._denom:
        _raise_incompatible_denoms('+=', self, arg)

    # Perform the operation
    if self.is_int() and not arg.is_int():
        raise TypeError(f'integer {type(self)} "+=" operation returns non-integer result')

    new_derivs = self._add_derivs(self, arg)    # if this raises exception, stop
    self._values += arg._values               # on exception, no harm done
    self._mask = Qube.or_(self._mask, arg._mask)
    self._unit = self._unit or arg._unit
    self.insert_derivs(new_derivs)

    self._cache.clear()
    return self


def _add_derivs(self, /, arg1, arg2):
    """Dictionary of added derivatives."""

    set1 = set(arg1._derivs.keys())
    set2 = set(arg2._derivs.keys())
    set12 = set1 & set2
    set1 -= set12
    set2 -= set12

    new_derivs = {}
    for key in set12:
        new_derivs[key] = arg1._derivs[key] + arg2._derivs[key]
    for key in set1:
        new_derivs[key] = arg1._derivs[key]
    for key in set2:
        new_derivs[key] = arg2._derivs[key]

    return new_derivs

##########################################################################################
# Subtraction
##########################################################################################

def __sub__(self, /, arg, *, recursive=True):
    """self - arg, element-by-element subtraction.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The difference.
    """

    # Handle a simple right-hand value...
    if self._rank == 0 and isinstance(arg, numbers.Real):
        obj = self.clone(recursive=recursive, retain_cache=True)
        obj._set_values(self._values - arg, retain_cache=True)
        return obj

    # Convert arg to the same subclass and try again
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = self.as_this_type(arg, coerce=False, op='-')
        except (ValueError, TypeError):
            _raise_unsupported_op('-', self, original_arg)

    # Verify compatibility
    self._require_compatible_units(arg, '-')

    if self._numer != arg._numer:
        if type(self) is not type(arg):
            _raise_unsupported_op('-', self, original_arg)

        _raise_incompatible_numers('-', self, arg)

    if self._denom != arg._denom:
        _raise_incompatible_denoms('-', self, arg)

    # Construct the result
    obj = Qube.__new__(type(self))
    obj.__init__(self._values - arg._values,
                 Qube.or_(self._mask, arg._mask),
                 unit=self._unit or arg._unit,
                 example=self)

    if recursive:
        obj.insert_derivs(obj._sub_derivs(self, arg))

    return obj


def __rsub__(self, /, arg, *, recursive=True):
    """arg - self, element-by-element subtraction.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The difference.
    """

    # Convert arg to the same subclass and try again
    if not isinstance(arg, Qube):
        arg = self.as_this_type(arg, coerce=False, op='-')
        return arg.__sub__(self, recursive=recursive)


def __isub__(self, /, arg):
    """self -= arg, element-by-element in-place subtraction.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: self after the subtraction.
    """

    self.require_writeable()

    # Handle a simple right-hand value...
    if self._rank == 0 and isinstance(arg, (numbers.Real, np.ndarray)):
        self._values -= arg
        self._new_values()
        return self

    # Convert arg to another Qube if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = self.as_this_type(arg, coerce=False, op='-=')
        except (ValueError, TypeError):
            _raise_unsupported_op('-=', self, original_arg)

    # Verify compatibility
    self._require_compatible_units(arg, '-=')

    if self._numer != arg._numer:
        if type(self) is not type(arg):
            _raise_unsupported_op('-=', self, original_arg)

        _raise_incompatible_numers('-=', self, arg)

    if self._denom != arg._denom:
        _raise_incompatible_denoms('-=', self, arg)

    # Perform the operation
    if self.is_int() and not arg.is_int():
        raise TypeError(f'integer {type(self)} "-=" operation returns non-integer result')

    new_derivs = self._sub_derivs(self, arg)    # if this raises exception, stop
    self._values -= arg._values                 # on exception, no harm done
    self._mask = Qube.or_(self._mask, arg._mask)
    self._unit = self._unit or arg._unit
    self.insert_derivs(new_derivs)

    self._cache.clear()
    return self


def _sub_derivs(self, /, arg1, arg2):
    """Dictionary of subtracted derivatives."""

    set1 = set(arg1._derivs.keys())
    set2 = set(arg2._derivs.keys())
    set12 = set1 & set2
    set1 -= set12
    set2 -= set12

    new_derivs = {}
    for key in set12:
        new_derivs[key] = arg1._derivs[key] - arg2._derivs[key]
    for key in set1:
        new_derivs[key] = arg1._derivs[key]
    for key in set2:
        new_derivs[key] = -arg2._derivs[key]

    return new_derivs

##########################################################################################
# Multiplication
##########################################################################################

def __mul__(self, /, arg, *, recursive=True):
    """self * arg, element-by-element multiplication.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The product.
    """

    # Handle multiplication by a number
    if Qube._is_one_value(arg):
        return self._mul_by_number(arg, recursive=recursive)

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('*', self, original_arg)

    # Check denominators
    if self._drank and arg._drank:
        _raise_dual_denoms('*', self, original_arg)

    # Multiply by scalar...
    if arg._nrank == 0:
        try:
            return self._mul_by_scalar(arg, recursive=recursive)

        # Revise the exception if the arg was modified
        except (ValueError, TypeError):
            if arg is not original_arg:
                _raise_unsupported_op('*', self, original_arg)
            raise

    # Swap and try again
    if self._nrank == 0:
        return arg._mul_by_scalar(self, recursive=recursive)

    # Multiply by matrix...
    if self._nrank == 2 and arg._nrank in (1, 2):
        return Qube.dot(self, arg, -1, 0, classes=(type(arg), type(self)),
                        recursive=recursive)

    # Give up
    _raise_unsupported_op('*', self, original_arg)


def __rmul__(self, /, arg, *, recursive=True):
    """arg * self, element-by-element multiplication.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The product.
    """

    # Handle multiplication by a number
    if Qube._is_one_value(arg):
        return self._mul_by_number(arg, recursive=recursive)

    # Convert arg to a Scalar and try again
    original_arg = arg
    try:
        arg = Qube._SCALAR_CLASS.as_scalar(arg)
        return self._mul_by_scalar(arg, recursive=recursive)

    # Revise the exception if the arg was modified
    except (ValueError, TypeError):
        if arg is not original_arg:
            _raise_unsupported_op('*', original_arg, self)
        raise


def __imul__(self, /, arg):
    """Element-by-element in-place multiplication.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: self after the multiplication.
    """

    self.require_writeable()

    # If a number...
    if isinstance(arg, numbers.Real):
        self._values *= arg
        self._new_values()
        for key, deriv in self._derivs.items():
            deriv._values *= arg
            deriv._new_values()
        return self

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('*=', self, original_arg)

    # Scalar case
    if arg._rank == 0:

        # Align axes
        arg_values = arg._values
        if self._rank and np.shape(arg_values):
            arg_values = arg_values.reshape(np.shape(arg_values) +
                                            self._rank * (1,))

        # Multiply...
        if self.is_int() and not arg.is_int():
            raise TypeError(f'integer {type(self)} "*=" operation returns non-integer '
                            'result')

        new_derivs = self._mul_derivs(arg)  # if this raises exception, stop
        self._values *= arg_values         # on exception, object unchanged
        self._mask = Qube.or_(self._mask, arg._mask)
        self._unit = Unit.mul_units(self._unit, arg._unit)
        self.insert_derivs(new_derivs)

        self._cache.clear()
        return self

    # Matrix multiply case
    if self._nrank == 2 and arg._nrank == 2 and arg._drank == 0:
        result = Qube.dot(self, arg, -1, 0, classes=[type(self)], recursive=True)
        self._set_values(result._values, result._mask)
        self.insert_derivs(result._derivs)
        return self

    # Nothing else is implemented
    _raise_unsupported_op('*=', self, original_arg)


def _mul_by_number(self, /, arg, *, recursive=True):
    """Internal multiply op when the arg is a Python scalar."""

    obj = self.clone(recursive=False, retain_cache=True)
    obj._set_values(self._values * arg, retain_cache=True)

    if recursive and self._derivs:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv._mul_by_number(arg, recursive=False))

    return obj


def _mul_by_scalar(self, /, arg, *, recursive=True):
    """Internal multiply op when the arg is a Qube with nrank == 0 and no
    more than one object has a denominator."""

    # Align axes
    self_values = self._values
    self_shape = np.shape(self_values)
    if arg._drank > 0 and self_shape != ():
        self_values = self_values.reshape(self_shape + arg._drank * (1,))

    arg_values = arg._values
    arg_shape = (arg._shape + self._rank * (1,) + arg._denom)
    if np.shape(arg_values) not in ((), arg_shape):
        arg_values = arg_values.reshape(arg_shape)

    # Construct object
    obj = Qube.__new__(type(self))
    obj.__init__(self_values * arg_values,
                 Qube.or_(self._mask, arg._mask),
                 unit=Unit.mul_units(self._unit, arg._unit),
                 drank=max(self._drank, arg._drank),
                 example=self)

    obj.insert_derivs(self._mul_derivs(arg))
    return obj


def _mul_derivs(self, /, arg):
    """Dictionary of multiplied derivatives."""

    new_derivs = {}

    if self._derivs:
        arg_wod = arg.wod
        for key, self_deriv in self._derivs.items():
            new_derivs[key] = self_deriv * arg_wod

    if arg._derivs:
        self_wod = self.wod
        for key, arg_deriv in arg._derivs.items():
            if key in new_derivs:
                new_derivs[key] = new_derivs[key] + self_wod * arg_deriv
            else:
                new_derivs[key] = self_wod * arg_deriv

    return new_derivs

##########################################################################################
# Division
##########################################################################################

def __truediv__(self, /, arg, *, recursive=True):
    """self / arg, element-by-element division.

    Cases of divide-by-zero are masked.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The quotient.
    """

    # Handle division by a number
    if Qube._is_one_value(arg):
        return self._div_by_number(arg, recursive=recursive)

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('/', self, original_arg)

    # Check right denominator
    if arg._drank > 0:
        raise ValueError(f'right operand has denominator for {type(self)} "/": '
                         f'{arg._denom}')

    # Divide by scalar...
    if arg._nrank == 0:
        try:
            return self._div_by_scalar(arg, recursive=recursive)

        # Revise the exception if the arg was modified
        except (ValueError, TypeError):
            if arg is not original_arg:
                _raise_unsupported_op('/', self, original_arg)
            raise

    # Swap and multiply by reciprocal...
    if self._nrank == 0:
        return self.reciprocal(recursive=recursive)._mul_by_scalar(arg,
                                                                   recursive=recursive)

    # Matrix / matrix is multiply by inverse matrix
    if self._rank == 2 and arg._rank == 2:
        return self.__mul__(arg.reciprocal(recursive=recursive))

    # Give up
    _raise_unsupported_op('/', self, original_arg)


def __rtruediv__(self, /, arg, *, recursive=True):
    """arg / self, element-by-element division.

    Cases of divide-by-zero are masked.

    Parameters:
        arg (Qube, array-like, float, int, or bool): Argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The quotient.
    """

    # Handle right division by a number
    if Qube._is_one_value(arg):
        return self.reciprocal(recursive=recursive).__mul__(arg, recursive=recursive)

    # Convert arg to a Scalar and try again
    original_arg = arg
    try:
        arg = Qube._SCALAR_CLASS.as_scalar(arg)
        return arg.__truediv__(self, recursive=recursive)

    # Revise the exception if the arg was modified
    except (ValueError, TypeError):
        if arg is not original_arg:
            _raise_unsupported_op('/', original_arg, self)
        raise

# Generic in-place division
def __itruediv__(self, /, arg):
    """self /= arg, element-by-element in-place division.

    Cases of divide-by-zero are masked.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: self after the division.
    """

    if not self.is_float():
        raise TypeError(f'integer {type(self)} "/=" operation returns non-integer result')

    self.require_writeable()

    # If a number...
    if isinstance(arg, numbers.Real) and arg != 0:
        self._values /= arg
        self._new_values()
        for key, deriv in self._derivs.items():
            deriv._values /= arg
            deriv._new_values()
        return self

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('/=', self, original_arg)

    # In-place multiply by the reciprocal
    try:
        self.__imul__(arg.reciprocal())

    # Revise the exception if the arg was modified
    except (ValueError, TypeError):
        if arg is not original_arg:
            _raise_unsupported_op('/=', self, original_arg)
        raise

    return self


def _div_by_number(self, /, arg, *, recursive=True):
    """Internal division op when the arg is a Python scalar."""

    obj = self.clone(recursive=False, retain_cache=True)

    # Mask out zeros
    if arg == 0:
        obj._set_mask(True)
    else:
        obj._set_values(self._values / arg, retain_cache=True)

    if recursive and self._derivs:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv._div_by_number(arg, recursive=False))

    return obj


def _div_by_scalar(self, /, arg, *, recursive):
    """Internal division op when the arg is a Qube with rank == 0."""

    # Mask out zeros
    arg = arg.mask_where_eq(0., 1.)

    # Align axes
    arg_values = arg._values
    if np.shape(arg_values) and self._rank:
        arg_values = arg_values.reshape(arg.shape + self._rank * (1,))

    # Construct object
    obj = Qube.__new__(type(self))
    obj.__init__(self._values / arg_values,
                 Qube.or_(self._mask, arg._mask),
                 unit=Unit.div_units(self._unit, arg._unit),
                 example=self)

    if recursive:
        obj.insert_derivs(self._div_derivs(arg, nozeros=True))

    return obj


def _div_derivs(self, /, arg, *, nozeros=False):
    """Dictionary of divided derivatives.

    If nozeros is True, the arg is assumed not to contain any zeros, so divide-by-zero
    errors are not checked.
    """

    new_derivs = {}

    if not self._derivs and not arg._derivs:
        return new_derivs

    if not nozeros:
        arg = arg.mask_where_eq(0., 1.)

    arg_wod_inv = arg.wod.reciprocal(nozeros=True)

    for key, self_deriv in self._derivs.items():
        new_derivs[key] = self_deriv * arg_wod_inv

    if arg._derivs:
        self_wod = self.wod
        for key, arg_deriv in arg._derivs.items():
            term = self_wod * (arg_deriv * arg_wod_inv*arg_wod_inv)
            if key in new_derivs:
                new_derivs[key] -= term
            else:
                new_derivs[key] = -term

    return new_derivs

##########################################################################################
# Floor Division (with no support for derivatives)
##########################################################################################

def __floordiv__(self, /, arg):
    """self // arg, element-by-element floor division.

    Cases of divide-by-zero are masked. Derivatives are ignored.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: The result of the floor dividion.
    """

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('//', self, original_arg)

    # Check right denominator
    if arg._drank > 0:
        raise ValueError(f'right operand has denominator for {type(self)} "//": '
                         f'{arg._denom}')

    # Floor divide by scalar...
    if arg._nrank == 0:
        try:
            return self._floordiv_by_scalar(arg)

        # Revise the exception if the arg was modified
        except (ValueError, TypeError):
            if arg is not original_arg:
                _raise_unsupported_op('//', original_arg, self)
            raise

    # Give up
    _raise_unsupported_op('//', self, original_arg)


# Generic right floor division
def __rfloordiv__(self, /, arg):
    """arg // self, element-by-element floor division.

    Cases of divide-by-zero are masked. Derivatives are ignored.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: The result of the floor dividion.
    """

    # Convert arg to a Scalar and try again
    original_arg = arg
    try:
        arg = Qube._SCALAR_CLASS.as_scalar(arg)
        return arg.__floordiv__(self)

    # Revise the exception if the arg was modified
    except (ValueError, TypeError):
        if arg is not original_arg:
            _raise_unsupported_op('//', original_arg, self)
        raise


def __ifloordiv__(self, /, arg):
    """self //= arg, element-by-element in-place floor division.

    Cases of divide-by-zero are masked. Derivatives are ignored.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: self after the floor division.
    """

    self.require_writeable()

    # If a number...
    if isinstance(arg, numbers.Real) and arg != 0:
        self._values //= arg
        self._new_values()
        self.delete_derivs()
        return self

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('//=', self, original_arg)

    # Handle floor division by a scalar
    if arg._rank == 0:
        divisor = arg.mask_where_eq(0, 1)
        div_values = divisor._values

        # Align axes
        if self._rank:
            div_values = np.reshape(div_values, np.shape(div_values) + self._rank * (1,))
        self._values //= div_values
        self._mask = self._mask | divisor._mask
        self._unit = Unit.div_units(self._unit, arg._unit)
        self.delete_derivs()

        self._cache.clear()
        return self

    # Nothing else is implemented
    _raise_unsupported_op('//=', self, original_arg)


def _floordiv_by_number(self, /, arg):
    """Internal floor division op when the arg is a Python scalar."""

    obj = self.clone(recursive=False, retain_cache=True)

    if arg == 0:
        obj._set_mask(True)
    else:
        obj._set_values(self._values // arg, retain_cache=True)

    return obj


def _floordiv_by_scalar(self, /, arg):
    """Internal floor division op when the arg is a Qube with nrank == 0.

    The arg cannot have a denominator.
    """

    # Mask out zeros
    arg = arg.mask_where_eq(0, 1)

    # Align axes
    arg_values = arg._values
    if np.shape(arg_values) and self._rank:
        arg_values = arg_values.reshape(arg.shape + self._rank * (1,))

    # Construct object
    obj = Qube.__new__(type(self))
    obj.__init__(self._values // arg_values,
                 self._mask | arg._mask,
                 unit=Unit.div_units(self._unit, arg._unit),
                 example=self)
    return obj

##########################################################################################
# Modulus operators (with no support for derivatives)
##########################################################################################

def __mod__(self, /, arg, *, recursive=True):
    """self % arg, element-by-element modulus.

    Cases of divide-by-zero are masked. Derivatives in the numerator are supported, but
    not in the denominator.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The remainder.
    """

    # Handle modulus by a number
    if Qube._is_one_value(arg):
        return self._mod_by_number(arg, recursive=recursive)

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('%', self, original_arg)

    # Check right denominator
    if arg._drank > 0:
        raise ValueError(f'right operand has denominator for {type(self)} "%": '
                         f'{arg._denom}')

    # Modulus by scalar...
    if arg._nrank == 0:
        try:
            return self._mod_by_scalar(arg, recursive=recursive)

        # Revise the exception if the arg was modified
        except (ValueError, TypeError):
            if arg is not original_arg:
                _raise_unsupported_op('%', self, original_arg)
            raise

    # Give up
    _raise_unsupported_op('%', self, original_arg)


def __rmod__(self, /, arg, *, recursive=True):
    """arg % self, element-by-element modulus.

    Cases of divide-by-zero are masked. Derivatives in the numerator are supported, but
    not in the denominator.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.
        recursive (bool, optional): True to include derivatives in return.

    Returns:
        Qube: The remainder.
    """

    # Convert arg to a Scalar and try again
    original_arg = arg
    try:
        arg = Qube._SCALAR_CLASS.as_scalar(arg)
        return arg.__mod__(self, recursive=recursive)

    # Revise the exception if the arg was modified
    except (ValueError, TypeError):
        if arg is not original_arg:
            _raise_unsupported_op('%', original_arg, self)
        raise


def __imod__(self, /, arg):
    """self %= arg, element-by-element in-place modulus.

    Cases of divide-by-zero are masked. Derivatives in the numerator are supported, but
    not in the denominator.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Qube: self after the modulus operation.
    """

    self.require_writeable()

    # If a number...
    if isinstance(arg, numbers.Real) and arg != 0:
        self._values %= arg
        self._new_values()
        return self

    # Convert arg to a Scalar if necessary
    original_arg = arg
    if not isinstance(arg, Qube):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('%=', self, original_arg)

    # Handle modulus by a scalar
    if arg._rank == 0:
        divisor = arg.mask_where_eq(0, 1)
        div_values = divisor._values

        # Align axes
        if self._rank:
            div_values = np.reshape(div_values, np.shape(div_values) + self._rank * (1,))
        self._values %= div_values
        self._mask = self._mask | divisor._mask
        self._unit = Unit.div_units(self._unit, arg._unit)

        self._cache.clear()
        return self

    # Nothing else is implemented
    _raise_unsupported_op('%=', self, original_arg)


def _mod_by_number(self, /, arg, *, recursive=True):
    """Internal modulus op when the arg is a Python scalar."""

    obj = self.clone(recursive=False, retain_cache=True)

    # Mask out zeros
    if arg == 0:
        obj._set_mask(True)
    else:
        obj._set_values(self._values % arg, retain_cache=True)

    if recursive and self._derivs:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv)

    return obj


def _mod_by_scalar(self, /, arg, *, recursive=True):
    """Internal modulus op when the arg is a Qube with rank == 0."""

    # Mask out zeros
    arg = arg.wod.mask_where_eq(0, 1)

    # Align axes
    arg_values = arg._values
    if np.shape(arg_values) and self._rank:
        arg_values = arg_values.reshape(arg.shape + self._rank * (1,))

    # Construct the object
    obj = Qube.__new__(type(self))
    obj.__init__(self._values % arg_values,
                 self._mask | arg._mask,
                 unit=Unit.div_units(self._unit, arg._unit),
                 example=self)

    if recursive and self._derivs:
        for key, deriv in self._derivs.items():
            obj.insert_deriv(key, deriv.broadcast_to(obj._shape))

    return obj

##########################################################################################
# Exponentiation operator
##########################################################################################

def __pow__(self, /, arg):
    """arg ** self, element-by-element exponentiation.

    Derivatives are not supported.

    This general method supports single integer exponents between -15 and 15 are handled
    using repeated multiplications. It will handle any class that supports __mul__() (and
    reciprocal() if the exponent is negative), such as Matrix objects and Quaternions.

    It is overridden by Scalar to obtain the normal behavior of the "**" operator.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The exponent.

    Returns:
        Qube: The result of the exponentiation.
    """

    if not isinstance(arg, numbers.Real):
        try:
            arg = Qube._SCALAR_CLASS.as_scalar(arg)
        except (ValueError, TypeError):
            _raise_unsupported_op('**', self, arg)

        if arg._shape:
            _raise_unsupported_op('**', self, arg)

        if arg._mask:
            return self.as_fully_masked(recursive=True)

        arg = arg._values

    expo = int(arg)
    if expo != arg:
        _raise_unsupported_op('**', self, arg)

    # At this point, expo is an int

    # Check range
    if expo < -15 or expo > 15:
        raise ValueError('exponent is limited to range (-15,15)')

    # Handle zero
    if expo == 0:
        item = self.identity()
        result = self.filled(self._shape, item, numer=self._numer, mask=self._mask)
        for key, deriv in self._derivs.items():
            new_deriv = deriv.zeros(deriv._shape, numer=deriv._numer,
                                    denom=deriv._denom, mask=deriv._mask)
            result.insert_deriv(key, new_deriv)

        return result

    # Handle negative exponent
    if expo < 0:
        x = self.reciprocal(recursive=True)
        expo = -expo
    else:
        x = self

    # Handle one
    if expo == 1:
        return x

    # Handle 2 through 15
    # Note powers[0] is not a copy!
    # Note derivatives and units are included in multiplies
    powers = [x, x * x]
    if expo >= 4:
        powers.append(powers[-1] * powers[-1])
    if expo >= 8:
        powers.append(powers[-1] * powers[-1])

    # Select the powers needed for this exponent
    x_powers = []
    for k, e in enumerate((1, 2, 4, 8)):
        if (expo & e):
            x_powers.append(powers[k])

    # Multiply the items together
    # x_powers[0] might not be a copy, but x_powers[-1] must be, because we have
    # already already handled expo == 1.
    result = x_powers[-1]
    for x_power in x_powers[:-1]:
        result *= x_power

    return result


def __ipow__(self, /, arg):
    """self **= arg, element-by-element in-place power.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The exponent.

    Returns:
        Qube: self after the modulus operation.
    """

    self.require_writeable()

    result = self ** arg
    self._set_values(result._values, result._mask)
    self.set_unit(self, result._unit)
    return self

##########################################################################################
# Comparison operators, returning boolean scalars or Booleans
#   Masked values are treated as equal to one another. Masked and unmasked values are
#   always unequal.
##########################################################################################

def _compatible_arg(self, /, arg):
    """None if it is impossible for self and arg to be equal; otherwise, the argument made
    compatible with self.
    """

    # If the subclasses cannot be unified, raise a ValueError
    if not isinstance(arg, type(self)):
        try:
            obj = Qube.__new__(type(self))
            obj.__init__(arg, example=self)
            arg = obj
        except (ValueError, TypeError):
            return None

    else:
        # Compare unit for compatibility
        if not Unit.can_match(self._unit, arg._unit):
            return None

        # Compare item shapes
        if self._item != arg._item:
            return None

    # Check for compatible shapes
    try:
        (self, arg) = Qube.broadcast(self, arg)
    except ValueError:
        return None

    return arg


def __eq__(self, /, arg):
    """self == arg, element by element.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The exponent.

    Returns:
        Boolean: True where the elements are equal.
    """

    # Try to make argument compatible
    arg = self._compatible_arg(arg)
    if arg is None:
        return False        # an incompatible argument is not equal

    # Compare...
    compare = (self._values == arg._values)
    if self._rank:
        compare = np.all(compare, axis=tuple(range(-self._rank, 0)))

    both_masked = (self._mask & arg._mask)
    one_masked  = (self._mask != arg._mask)

    # Return a Python bool if the shape is ()
    if not isinstance(compare, np.ndarray):
        if one_masked:
            return False
        if both_masked:
            return True
        return bool(compare)

    # Apply the mask
    if not isinstance(one_masked, np.ndarray):
        if one_masked:
            compare.fill(False)
        if both_masked:
            compare.fill(True)
    else:
        compare[one_masked] = False
        compare[both_masked] = True

    result = Qube._BOOLEAN_CLASS(compare)
    result._truth_if_all = True
    return result


def __ne__(self, /, arg):
    """self != arg, element by element.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The exponent.

    Returns:
        Boolean: True where the elements are not equal.
    """

    # Try to make argument compatible
    arg = self._compatible_arg(arg)
    if arg is None:
        return True         # an incompatible argument is not equal

    # Compare...
    compare = (self._values != arg._values)
    if self._rank:
        compare = np.any(compare, axis=tuple(range(-self._rank, 0)))

    both_masked = (self._mask & arg._mask)
    one_masked  = (self._mask != arg._mask)

    # Compare units for compatibility
    if not Unit.can_match(self._unit, arg._unit):
        compare = True
        one_masked = True

    # Return a Python bool if the shape is ()
    if not isinstance(compare, np.ndarray):
        if one_masked:
            return True
        if both_masked:
            return False
        return bool(compare)

    # Apply the mask
    if np.shape(one_masked):
        compare[one_masked] = True
        compare[both_masked] = False
    else:
        if one_masked:
            compare.fill(True)
        if both_masked:
            compare.fill(False)

    result = Qube._BOOLEAN_CLASS(compare)
    result._truth_if_any = True
    return result


def __le__(self, /, arg):
    """self <= arg, element by element.

    This general method always raises ValueError. It is overriden by :meth:`Scalar.__le__`
    and :meth:`Boolean.__le__`.


    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Boolean: True where the elements of self are less or equal.

    Raises:
        ValueError: If the comparison is undefined.
    """

    _raise_unsupported_op("<=", self)


def __lt__(self, /, arg):
    """self < arg, element by element.

    This general method always raises ValueError. It is overriden by :meth:`Scalar.__lt__`
    and :meth:`Boolean.__lt__`.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Boolean: True where the elements of self are less.

    Raises:
        ValueError: If the comparison is undefined.
    """

    _raise_unsupported_op("<", self)


def __ge__(self, /, arg):
    """self >= arg, element by element.

    This general method always raises ValueError. It is overriden by :meth:`Scalar.__ge__`
    and :meth:`Boolean.__ge__`.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Boolean: True where the elements of self are greater or equal.

    Raises:
        ValueError: If the comparison is undefined.
    """

    _raise_unsupported_op(">=", self)


def __gt__(self, /, arg):
    """self > arg, element by element.

    This general method always raises ValueError. It is overriden by :meth:`Scalar.__gt__`
    and :meth:`Boolean.__gt__`.

    Parameters:
        arg (Qube, array-like, float, int, or bool): The argument.

    Returns:
        Boolean: True where the elements of self are greater.

    Raises:
        ValueError: If the comparison is undefined.
    """

    _raise_unsupported_op(">", self)


def __bool__(self):
    """True if nonzero, otherwise False, element by element.

    This method also supports "if a == b: ..." and "if a != b: ..." statements using the
    internal attributes _truth_if_all and _truth_if_any. In this case, equality requires
    that every unmasked element of a and b be equal and both objects be masked at the same
    locations.

    Comparison of objects of shape () is also supported.

    Any other if-test involving PolyMath objects requires an explict call to all() or
    any().

    Returns:
        Boolean: True where the elements of self are nonzero or True.
    """

    if self._truth_if_all:          # this is the result of __eq__()
        return bool(np.all(self.as_mask_where_nonzero()))

    if self._truth_if_any:          # this is the result of __ne__()
        return bool(np.any(self.as_mask_where_nonzero()))

    if self._is_array:
        raise ValueError(f'{type(self).__name__} truth value requires any() or all()')

    if self._mask:
        raise ValueError(f'the truth value of an entirely masked {type(self).__name__} '
                         'object is undefined')

    return bool(self._values)


def __float__(self):
    """This object as a single float."""

    if not self._is_scalar:
        raise ValueError(f'{type(self).__name__} array value cannot be converted to '
                         'float')
    if self._mask:
        raise ValueError(f'{type(self).__name__} masked value cannot be converted to '
                         'float')

    return float(self._values)


def __int__(self):
    """This object as a single int; floats always round down."""

    if not self._is_scalar:
        raise ValueError(f'{type(self).__name__} array value cannot be converted to int')
    if self._mask:
        raise ValueError(f'{type(self).__name__} masked value cannot be converted to int')

    return int(self._values // 1)

##########################################################################################
# Boolean operators
##########################################################################################

def __invert__(self):
    """~self, unary inversion, element by element.

    This is boolean "not", not bit inversion.
    """

    return Qube._BOOLEAN_CLASS(self._values == 0, self._mask)


def __and__(self, /, arg):
    """self & arg, element-by-element logical "and"."""

    if isinstance(arg, np.ma.MaskedArray):
        arg = Qube._BOOLEAN_CLASS(arg != 0)

    if isinstance(arg, Qube):
        return Qube._BOOLEAN_CLASS((self._values != 0) & (arg._values != 0),
                                   Qube.or_(self._mask, arg._mask))

    return Qube._BOOLEAN_CLASS((self._values != 0) & (arg != 0), self._mask)


def __rand__(self, /, arg):
    """arg & self, element-by-element logical "and"."""

    return self.__and__(arg)


def __or__(self, /, arg):
    """self | arg, element-by-element logical "or"."""

    if isinstance(arg, np.ma.MaskedArray):
        arg = Qube._BOOLEAN_CLASS(arg != 0)

    if isinstance(arg, Qube):
        return Qube._BOOLEAN_CLASS((self._values != 0) | (arg._values != 0),
                                   Qube.or_(self._mask, arg._mask))

    return Qube._BOOLEAN_CLASS((self._values != 0) | (arg != 0), self._mask)

def __ror__(self, /, arg):
    """arg | self, element-by-element logical "or"."""

    return self.__or__(arg)


def __xor__(self, /, arg):
    """self | arg, element-by-element logical exclusive "or"."""

    if isinstance(arg, np.ma.MaskedArray):
        arg = Qube._BOOLEAN_CLASS(arg != 0)

    if isinstance(arg, Qube):
        return Qube._BOOLEAN_CLASS((self._values != 0) != (arg._values != 0),
                                   Qube.or_(self._mask, arg._mask))

    return Qube._BOOLEAN_CLASS((self._values != 0) != (arg != 0), self._mask)

def __rxor__(self, /, arg):
    """arg | self, element-by-element logical exclusive "or"."""

    return self.__xor__(arg)


def __iand__(self, /, arg):
    """self &= arg, element-by-element in-place logical "and"."""

    self.require_writeable()

    if isinstance(arg, np.ma.MaskedArray):
        arg = Qube._BOOLEAN_CLASS(arg != 0)

    if isinstance(arg, Qube):
        self._values &= (arg._values != 0)
        self._mask = Qube.or_(self._mask, arg._mask)
    else:
        self._values &= (arg != 0)

    return self


def __ior__(self, /, arg):
    """self &= arg, element-by-element in-place logical "or"."""

    self.require_writeable()

    if isinstance(arg, np.ma.MaskedArray):
        arg = Qube._BOOLEAN_CLASS(arg != 0)

    if isinstance(arg, Qube):
        self._values |= (arg._values != 0)
        self._mask = Qube.or_(self._mask, arg._mask)
    else:
        self._values |= (arg != 0)

    return self


def __ixor__(self, /, arg):
    """self ^= arg, element-by-element in-place logical exclusive "or"."""

    self.require_writeable()

    if isinstance(arg, np.ma.MaskedArray):
        arg = Qube._BOOLEAN_CLASS(arg != 0)

    if isinstance(arg, Qube):
        self._values ^= (arg._values != 0)
        self._mask = Qube.or_(self._mask, arg._mask)
    else:
        self._values ^= (arg != 0)

    return self


def logical_not(self):
    """The negation of this object, True where it is zero or False."""

    if self._rank:
        values = np.any(self._values, axis=tuple(range(-self._rank, 0)))
    else:
        values = self._values

    return Qube._BOOLEAN_CLASS(np.logical_not(values), self._mask)

##########################################################################################
# Any and all
##########################################################################################

def any(self, axis=None, *, builtins=None, masked=None, out=None):
    """True if any of the unmasked items are nonzero.

    Parameters:
        axis (int or tuple, optional): Axis or a tuple of axes. The `any` operation is
            performed across these axes, leaving any remaining axes in the returned value.
            If None (the default), then the any operation is performed across all axes of
            the object.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked Boolean instead of a builtin
            type in this case.
        out (any, optional): Ignored. This enables "np.any(Qube)" to work.

    Returns:
        (Boolean or bool): Result of operation.
    """

    self = Qube._BOOLEAN_CLASS.as_boolean(self)

    if not self._shape:
        args = (self,)                  # make a copy

    elif not isinstance(self._mask, np.ndarray):
        args = (np.any(self._values, axis=axis), self._mask)

    else:
        # True where a value is True AND its antimask is True
        bools = self._values & self.antimask
        args = (np.any(bools, axis=axis), np.all(self._mask, axis=axis))

    result = Qube._BOOLEAN_CLASS(*args)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result


def all(self, axis=None, *, builtins=None, masked=None, out=None):
    """True if all the unmasked items are nonzero.

    Parameters:
        axis (int or tuple, optional): Axis or a tuple of axes. The any operation is
            performed across these axes, leaving any remaining axes in the returned value.
            If None (the default), then the any operation is performed across all axes of
            the object.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked Boolean instead of a builtin
            type in this case.
        out (any, optional): Ignored. This enables "np.any(Qube)" to work.
    """

    self = Qube._BOOLEAN_CLASS.as_boolean(self)

    if not self._shape:
        args = (self,)                  # make a copy

    elif not isinstance(self._mask, np.ndarray):
        args = (np.all(self._values, axis=axis), self._mask)

    else:
        # True where a value is True OR its mask is True
        bools = Qube.or_(self._values, self._mask)
        args = (np.all(bools, axis=axis), np.all(self._mask, axis=axis))

    result = Qube._BOOLEAN_CLASS(*args)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result


def any_true_or_masked(self, axis=None, *, builtins=None):
    """True if any of the items are nonzero or masked.

    This differs from the any() method in how it handles the case of every value being
    masked. This method returns True, whereas any() returns a masked Boolean value.

    Parameters:
        axis (int or tuple, optional): Axis or a tuple of axes. The any operation is
            performed across these axes, leaving any remaining axes in the returned value.
            If None (the default), then the any operation is performed across all axes of
            the object.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
    """

    self = Qube._BOOLEAN_CLASS.as_boolean(self)

    if not self._shape:
        args = (self,)                  # make a copy

    else:
        # True where a value is True OR its mask is True
        bools = Qube.or_(self._values, self._mask)
        args = (np.any(bools, axis=axis), False)

    result = Qube._BOOLEAN_CLASS(*args)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin()

    return result


def all_true_or_masked(self, axis=None, *, builtins=None):
    """True if all of the items are nonzero or masked.

    This differs from the all() method in how it handles the case of every value being
    masked. This method returns True, whereas all() returns a masked Boolean value.

    Parameters:
        axis (int or tuple, optional): Axis or a tuple of axes. The any operation is
            performed across these axes, leaving any remaining axes in the returned value.
            If None (the default), then the any operation is performed across all axes of
            the object.

        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
    """

    self = Qube._BOOLEAN_CLASS.as_boolean(self)

    if not self._shape:
        args = (self,)                  # make a copy

    else:
        # True where a value is True OR its mask is True
        bools = Qube.or_(self._values, self._mask)
        args = (np.all(bools, axis=axis), False)

    result = Qube._BOOLEAN_CLASS(*args)

    # Convert result to a Python bool if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin()

    return result

##########################################################################################
# Special operators
##########################################################################################

def reciprocal(self, *, recursive=True, nozeros=False):
    """An object equivalent to the reciprocal of this object.

    This method is not implemented for the base class. It is overridden by
    :meth:`Scalar.reciprocal`, :meth:`Vector.reciprocal`, :meth:`Matrix.reciprocal`, and
    :meth:`Quaternion.reciprocal`.

    Input:
        recursive (bool, optional): True to return the derivatives of the reciprocal too;
            otherwise, derivatives are removed.
        nozeros (bool, optional): False (the default) to mask out any zero-valued items in
            this object prior to the divide. Set to True only if you know in advance that
            this object has no zero-valued items.
    """

    _raise_unsupported_op('reciprocal()', self)


def zero(self):
    """An object of this subclass containing all zeros.

    The returned object has the same denominator shape as this object.

    This is default behavior and may need to be overridden by some subclasses.
    """

    # Scalar case
    if not self._rank:
        if self.is_float():
            new_value = 0.
        else:
            new_value = 0

    # Array case
    else:
        if self.is_float():
            new_value = np.zeros(self._item, dtype=np.float64)
        else:
            new_value = np.zeros(self._item, dtype=np.int_)

    # Construct the object
    obj = Qube.__new__(type(self))
    obj.__init__(new_value, False, derivs={}, example=self)

    # Return it as readonly
    return obj.as_readonly()


def identity(self):
    """An object of this subclass equivalent to the identity.

    This method is overridden by :meth:`Scalar.identity`, :meth:`Matrix.identity` and
    :meth:`Boolean.identity`
    """

    _raise_unsupported_op('identity()', self)


def sum(self, axis=None, *, recursive=True, builtins=None, masked=None, out=None):
    """The sum of the unmasked values along the specified axis or axes.

    This method is overridden by :meth:`Boolean.sum`.

    Parameters:
        axis (int or tuple, optional): An integer axis or a tuple of axes. The sum is
            determined across these axes, leaving any remaining axes in the returned
            value. If None (the default), then the sum is performed across all axes if the
            object.
        recursive (bool, optional): True to include the sums of the derivatives inside the
            returned Scalar.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked value instead of a builtin
            type.
        out (optional): Ignored. This enables "np.sum(Qube)" to work.
    """

    result = self._mean_or_sum(axis, recursive=recursive, _combine_as_mean=False)

    # Convert result to a Python type if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result


def mean(self, axis=None, *, recursive=True, builtins=None, masked=None, dtype=None,
         out=None):
    """The mean of the unmasked values along the specified axis or axes.

    Parameters:
        axis (int or tuple, optional): An integer axis or a tuple of axes. The sum is
            determined across these axes, leaving any remaining axes in the returned
            value. If None (the default), then the sum is performed across all axes if the
            object.
        recursive (bool, optional): True to include the sums of the derivatives inside the
            returned Scalar.
        builtins (bool, optional): If True and the result is a single unmasked scalar, the
            result is returned as a Python boolean instead of as an instance of Boolean.
            Default is to use the global setting defined by Qube.prefer_builtins().
        masked (bool, optional): The value to return if builtins is True but the returned
            value is masked. Default is to return a masked value instead of a builtin
            type.
        dtype (optional): Ignored. This enables "np.sum(Qube)" to work.
        out (optional): Ignored. This enables "np.sum(Qube)" to work.
    """

    result = self._mean_or_sum(axis, recursive=recursive, _combine_as_mean=True)

    # Convert result to a Python type if necessary
    if builtins is None:
        builtins = Qube.prefer_builtins()

    if builtins:
        return result.as_builtin(masked=masked)

    return result

##########################################################################################
# Error messages
##########################################################################################

def _raise_unsupported_op(op, /, obj1, obj2=None):
    """Raise a TypeError or ValueError for unsupported operations."""

    opstr = obj1._opstr(op)

    if obj2 is None:
        raise TypeError(f'{opstr} operation is not supported')

    if (isinstance(obj1, (list, tuple, np.ndarray)) or
        isinstance(obj2, (list, tuple, np.ndarray))):                           # noqa

        if isinstance(obj1, Qube):
            shape1 = obj1._numer
        else:
            shape1 = np.shape(obj1)

        if isinstance(obj2, Qube):
            shape2 = obj2._numer
        else:
            shape2 = np.shape(obj2)

        raise ValueError(f'unsupported operand item for {opstr}: {shape1}, {shape2}')

    raise TypeError(f'unsupported operand type for {opstr}: {type(obj2)}')


def _raise_incompatible_shape(op, /, obj1, obj2):
    """Raise a ValueError for incompatible object shapes."""

    opstr = obj1._opstr(op)
    raise ValueError(f'incompatible object shapes for {opstr}: '
                     f'{obj1._shape}, {obj2._shape}')


def _raise_incompatible_numers(op, /, obj1, obj2):
    """Raise a ValueError for incompatible numerators in operation."""

    opstr = obj1._opstr(op)
    raise ValueError(f'incompatible numerator shapes for {opstr}: '
                     f'{obj1._numer}, {obj2._numer}')


def _raise_incompatible_denoms(op, /, obj1, obj2):
    """Raise a ValueError for incompatible denominators in operation."""

    opstr = obj1._opstr(op)
    raise ValueError(f'incompatible denominator shapes for {opstr}: '
                     f'{obj1._denom}, {obj2._denom}')


def _raise_dual_denoms(op, /, obj1, obj2):
    """Raise a ValueError for denominators on both operands."""

    opstr = obj1._opstr(op)
    raise ValueError(f'only one operand of {opstr} can have a denominator')

##########################################################################################
