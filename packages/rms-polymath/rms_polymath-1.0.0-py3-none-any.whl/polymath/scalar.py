##########################################################################################
# polymath/scalar.py: Scalar subclass of PolyMath base class
##########################################################################################

import functools
import numpy as np
import numbers
import sys
import warnings

from polymath.qube import Qube
from polymath.unit import Unit

# Maximum argument to exp()
_EXP_CUTOFF = np.log(sys.float_info.max)
_TWOPI = np.pi * 2.


class Scalar(Qube):
    """Represent dimensionless scalar values in the PolyMath framework.

    This class provides functionality for working with scalar values including
    mathematical operations, trigonometric functions, and statistical methods. Scalars can
    have units, derivatives, and support masking for undefined values.
    """

    _NRANK = 0          # The number of numerator axes.
    _NUMER = ()         # Shape of the numerator.
    _FLOATS_OK = True   # True to allow floating-point numbers.
    _INTS_OK = True     # True to allow integers.
    _BOOLS_OK = False   # True to allow booleans.
    _UNITS_OK = True    # True to allow units; False to disallow them.
    _DERIVS_OK = True   # True to allow derivatives and denominators; False to disallow.
    _DEFAULT_VALUE = 1

    @staticmethod
    @functools.lru_cache(maxsize=20)
    def _minval(dtype):
        """The minimum value associated with this dtype.

        Returns:
            float or int: The minimum value for the current data type.
        """

        if dtype.kind == 'f':
            return -np.inf
        elif dtype.kind == 'u':
            return 0
        elif dtype.kind == 'i':
            return -256 ** dtype.itemsize // 2
        elif dtype.kind == 'b':
            return 0
        else:
            raise ValueError(f'invalid dtype {dtype}')

    @staticmethod
    @functools.lru_cache(maxsize=20)
    def _maxval(dtype):
        """The maximum value associated with this dtype.

        Returns:
            float or int: The maximum value for the current data type.
        """

        if dtype.kind == 'f':
            return np.inf
        elif dtype.kind == 'u':
            return 256 ** dtype.itemsize - 1
        elif dtype.kind == 'i':
            return 256 ** dtype.itemsize // 2 - 1
        elif dtype.kind == 'b':
            return 1
        else:
            raise ValueError(f'invalid dtype {dtype}')

    @staticmethod
    def as_scalar(arg, *, recursive=True):
        """Convert the argument to Scalar if possible.

        Parameters:
            arg: The object to convert to Scalar.
            recursive (bool, optional): True to include derivatives in the conversion.

        Returns:
            Scalar: The converted Scalar object.
        """

        if isinstance(arg, Scalar):
            if arg.is_bool():
                return arg.as_int()
            return arg if recursive else arg.wod

        if isinstance(arg, Qube):
            if type(arg) is Qube._BOOLEAN_CLASS:
                return Qube._BOOLEAN_CLASS(arg).as_int()

            arg = Scalar(arg)
            return arg if recursive else arg.wod

        if isinstance(arg, Unit):
            return Scalar(arg.from_unit_factor, unit=arg)

        return Scalar(arg)

    def to_scalar(self, indx, *, recursive=True):
        """This scalar (duplicates Vector.to_scalar behavior).

        Parameters:
            indx (int): Index of the vector component; must be zero.
            recursive (bool, optional): True to include the derivatives.

        Returns:
            Scalar: This scalar object.

        Raises:
            ValueError: If indx is not zero.
        """

        if indx != 0:
            raise ValueError('Scalar.to_scalar() index out of range')

        if recursive:
            return self

        return self.wod

    def as_index(self, *, masked=None):
        """Make this object suitable for indexing an N-dimensional NumPy array.

        Parameters:
            masked: The value to insert in the place of a masked item. If None and the
                object contains masked elements, the array will be flattened and masked
                elements will be skipped.

        Returns:
            ndarray: An array suitable for indexing.
        """

        (index, mask) = self.as_index_and_mask(purge=(masked is None), masked=masked)
        return index

    def as_index_and_mask(self, *, purge=False, masked=None):
        """Make this object suitable for indexing and masking an N-dimensional array.

        Parameters:
            purge (bool, optional): True to eliminate masked elements from the index;
                False to retain them but leave them masked.
            masked: The index value to insert in place of any masked item. This may be
                needed because each value in the returned index array must be an integer
                and in range. If None (the default), then masked values in the index will
                retain their unmasked values when the index is applied.

        Returns:
            tuple: A tuple containing (index_array, mask_array).

        Raises:
            IndexError: If this object contains floating-point values.
            ValueError: If this object has a denominator.
        """

        if self.is_float():
            raise IndexError('Scalar.as_index_and_mask() does not allow floating-point '
                             'indexing')

        self._disallow_denom('as_index_and_mask()')
        self._require_unitless('as_index_and_mask()')

        # If nothing is masked, this is easy
        if not np.any(self._mask):
            if np.shape(self._values):
                return (self._values.astype(np.intp), False)
            else:
                return (int(self._values), False)

        # If purging...
        if purge:

            # If all masked...
            if Qube.is_one_true(self._mask):
                return ((), False)

            # If partially masked...
            return (self._values[self.antimask].astype(np.intp), False)

        # Without a replacement...
        if masked is None:
            new_values = self._values.astype(np.intp)

        # If all masked...
        elif Qube.is_one_true(self._mask):
            new_values = np.empty(self._values.shape, dtype=np.intp)
            new_values[...] = masked

        # If partially masked...
        else:
            new_values = self._values.copy().astype(np.intp)
            new_values[self._mask] = masked

        return (new_values, self._mask)

    def int(self, top=None, *, remask=False, clip=False, inclusive=True, shift=None,
            builtins=None, masked=None):
        """An integer (floor) version of this Scalar.

        If this object already contains integers, it is returned as is. Otherwise, a copy
        is returned. Derivatives are always removed. Units are disallowed.

        Class Vector has a similar method :meth:`Vector.int`.

        Parameters:
            top (int, optional): Optional nominal maximum integer value.
            remask (bool, optional): If True, values less than zero or greater than the
                specified top value (if provided) are masked.
            clip (bool, optional): If True, values less than zero or greater than the
                specified top value are clipped.
            inclusive (bool, optional): True to leave the top value unmasked; False to
                mask it.
            shift (bool, optional): True to shift any occurrences of the top value down by
                one; False to leave them unchanged. Default None lets shift match the
                input value of inclusive.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                the result is returned as a Python int instead of an instance of Scalar.
                Default is the value specified by Qube.prefer_builtins().
            masked: Value to return if builtins is True but the returned value is masked.
                Default is to return a masked value instead of a builtin type.

        Returns:
            Scalar or int: The integer version of this scalar.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.int() does not support denominators')

        self._require_unitless('int()')

        # For compatibility with Vector.int, where the first arg is the shape
        if isinstance(top, (list, tuple)):
            top = top[0]

        if top is not None:

            # Convert to int; be sure it's a copy before modifying
            if self.is_int():
                copied = self.copy()
                values = copied._values
                mask = copied._mask
            else:
                values = self.wod.as_int()._values
                mask = self._mask
                if isinstance(mask, np.ndarray):
                    mask = mask.copy()

            if shift is None:
                shift = inclusive

            if shift and not clip:      # shift is unneeded if clip is True
                if self._is_array:
                    values[self._values == top] -= 1
                elif self._values == top:
                    values = top - 1

            if remask:
                is_outside = Scalar.is_outside(self._values, 0, top, inclusive)

            if clip:
                values = np.clip(values, 0, top-1)

            if remask and np.any(is_outside):
                mask = Qube.or_(mask, is_outside)

            result = Scalar(values, mask, example=self)

        else:
            result = self.wod.as_int()
            if clip:
                result = result.mask_where_lt(0, replace=0, remask=remask)

            elif remask:
                result = result.mask_where_lt(0, remask=remask)

        # Convert result to a Python int if necessary
        if builtins is None:
            builtins = Qube.prefer_builtins()

        if builtins:
            return result.as_builtin(masked=masked)

        return result

    def frac(self, *, recursive=True):
        """An object containing the fractional components of all values.

        The returned object is an instance of the same subclass as this object.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the returned
                object. frac() leaves the derivatives unchanged.

        Returns:
            Scalar: An object with fractional components.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.frac() does not support denominators')

        self._require_unitless('frac()')

        # Convert to fractional values
        if self._is_array:
            new_values = (self._values % 1.)
        else:
            new_values = self._values % 1.

        # Construct a new copy
        obj = Qube.__new__(type(self))
        obj.__init__(new_values, mask=self._mask, derivs=self._derivs)

        return obj

    def sin(self, *, recursive=True):
        """The sine of each value.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the sine inside
                the returned object. Defaults to True.

        Returns:
            Scalar: The sine values.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.sin() does not support denominators')

        self._require_angle('sin()')

        obj = Scalar(np.sin(self._values), mask=self._mask)

        if recursive and self._derivs:
            factor = self.wod.cos()
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

    def cos(self, *, recursive=True):
        """The cosine of each value.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the cosine
                inside the returned object. Defaults to True.

        Returns:
            Scalar: The cosine values.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.cos() does not support denominators')

        self._require_angle('cos()')

        obj = Scalar(np.cos(self._values), mask=self._mask)

        if recursive and self._derivs:
            factor = -self.wod.sin()
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

    def tan(self, *, recursive=True):
        """The tangent of each value.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the tangent
                inside the returned object. Defaults to True.

        Returns:
            Scalar: The tangent values.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.tan() does not support denominators')

        self._require_angle('tan()')

        obj = Scalar(np.tan(self._values), mask=self._mask)

        if recursive and self._derivs:
            inv_sec_sq = self.wod.cos()**(-2)
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, inv_sec_sq * deriv)

        return obj

    def arcsin(self, *, recursive=True, check=True):
        """The arcsine of each value.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the arcsine
                inside the returned object. Defaults to True.
            check (bool, optional): True to mask out the locations of any values outside
                the domain [-1,1]. If False, a ValueError will be raised if any value is
                encountered where the arcsine is undefined. Check=True is slightly faster
                if we already know at the time of the call that all input values are
                valid.

        Returns:
            Scalar: The arcsine values.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If check is False and any value is outside domain (-1,1).
        """

        if self._drank:
            raise ValueError('Scalar.arcsin() does not support denominators')

        # Limit domain to [-1,1] if necessary
        if check:
            self._require_unitless('arcsin()')

            temp_mask = (self._values < -1) | (self._values > 1)
            if np.any(temp_mask):
                if Qube.is_one_true(temp_mask):
                    temp_values = 0.
                else:
                    temp_values = self._values.copy()
                    temp_values[temp_mask] = 0.
                    temp_mask = Qube.or_(self._mask, temp_mask)
            else:
                temp_values = self._values
                temp_mask = self._mask

            obj = Scalar(np.arcsin(temp_values), temp_mask)

        else:
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    func_values = np.arcsin(self._values)
                except RuntimeWarning:
                    raise ValueError('Scalar.arcsin() of value outside domain (-1,1)')

            obj = Scalar(func_values, mask=self._mask)

        if recursive and self._derivs:
            factor = (1. - self.wod**2)**(-0.5)
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

    def arccos(self, *, recursive=True, check=True):
        """The arccosine of each value.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the arccosine
                inside the returned object. Defaults to True.
            check (bool, optional): True to mask out the locations of any values outside
                the domain [-1,1]. If False, a ValueError will be raised if any value is
                encountered where the arccosine is undefined. Check=True is slightly
                faster if we already know at the time of the call that all input values
                are valid.

        Returns:
            Scalar: The arccosine values.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If check is False and any value is outside domain (-1,1).
        """

        if self._drank:
            raise ValueError('Scalar.arccos() does not support denominators')

        # Limit domain to [-1,1] if necessary
        if check:
            self._require_unitless('arccos()')

            temp_mask = (self._values < -1) | (self._values > 1)
            if np.any(temp_mask):
                if Qube.is_one_true(temp_mask):
                    temp_values = 0.
                else:
                    temp_values = self._values.copy()
                    temp_values[temp_mask] = 0.
                    temp_mask = Qube.or_(self._mask, temp_mask)
            else:
                temp_values = self._values
                temp_mask = self._mask

            obj = Scalar(np.arccos(temp_values), temp_mask)

        else:
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    func_values = np.arccos(self._values)
                except RuntimeWarning:
                    raise ValueError('Scalar.arccos() of value outside domain (-1,1)')

            obj = Scalar(func_values, mask=self._mask)

        if recursive and self._derivs:
            factor = -(1. - self.wod**2)**(-0.5)
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

    def arctan(self, *, recursive=True):
        """The arctangent of each value.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the arctangent
                inside the returned object.

        Returns:
            Scalar: The arctangent values.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.arctan() does not support denominators')

        self._require_unitless('arctan()')

        obj = Scalar(np.arctan(self._values), mask=self._mask)

        if recursive and self._derivs:
            factor = 1. / (1. + self.wod**2)
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

    def arctan2(self, arg, *, recursive=True):
        """The four-quadrant value of arctan2(y,x).

        If this object is read-only, the returned object will also be read-only.

        Parameters:
            arg: The second argument to arctan2().
            recursive (bool, optional): True to include the derivatives of the arctangent
                inside the returned object. This is the result of merging the derivatives
                in both this object and the argument object.

        Returns:
            Scalar: The four-quadrant arctangent values.

        Raises:
            ValueError: If either object has denominators.
        """

        y = self
        x = Scalar.as_scalar(arg)
        y._require_compatible_units(x)

        if x._drank or y._drank:
            raise ValueError('Scalar.arctan2() does not support denominators')

        obj = Scalar(np.arctan2(y._values, x._values),
                     Qube.or_(x._mask, y._mask))

        if recursive and (x._derivs or y._derivs):
            denom_inv = (x.wod**2 + y.wod**2).reciprocal()

            new_derivs = {}
            for key, y_deriv in y._derivs.items():
                new_derivs[key] = x.wod * denom_inv * y_deriv

            for key, x_deriv in x._derivs.items():
                term = y.wod * denom_inv * x_deriv
                if key in new_derivs:
                    new_derivs[key] -= term
                else:
                    new_derivs[key] = -term

            obj.insert_derivs(new_derivs)

        return obj

    def sqrt(self, *, recursive=True, check=True):
        """The square root, masking imaginary values.

        If this object is read-only, the returned object will also be read-only.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the square root
                inside the returned object.
            check (bool, optional): True to mask out the locations of any values < 0
                before taking the square root. If False, a ValueError will be raised any
                negative value encountered. Check=True is slightly faster if we already
                know at the time of the call that all input values are valid.

        Returns:
            Scalar: The square root values.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If check is False and any value is negative.
        """

        if self._drank:
            raise ValueError('Scalar.sqrt() does not support denominators')

        if check:
            no_negs = self.mask_where_lt(0., replace=1.)
            sqrt_vals = np.sqrt(no_negs._values)

        else:
            no_negs = self
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    sqrt_vals = np.sqrt(no_negs._values)
                except RuntimeWarning:
                    raise ValueError('Scalar.sqrt() of negative value')

        obj = Scalar(sqrt_vals, mask=no_negs._mask,
                     unit=Unit.sqrt_unit(no_negs._unit))

        if recursive and no_negs._derivs:
            factor = 0.5 / obj
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

    def log(self, *, recursive=True, check=True):
        """The natural log, masking undefined values.

        If this object is read-only, the returned object will also be read-only.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the log inside
                the returned object. Defaults to True.
            check (bool, optional): True to mask out the locations of any values <= 0
                before taking the log. If False, a ValueError will be raised any value <=
                0 is encountered. Check=True is slightly faster if we already know at the
                time of the call that all input values are valid. Defaults to True.

        Returns:
            Scalar: The natural logarithm values.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If check is False and any value is non-positive.
        """

        if self._drank:
            raise ValueError('Scalar.log() does not support denominators')

        if check:
            no_negs = self.mask_where_le(0., replace=1.)
            log_values = np.log(no_negs._values)
        else:
            no_negs = self
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    log_values = np.log(no_negs._values)
                except RuntimeWarning:
                    raise ValueError('Scalar.log() of non-positive value')

        obj = Scalar(log_values, mask=no_negs._mask)

        if recursive and no_negs._derivs:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv / no_negs)

        return obj

    def exp(self, *, recursive=True, check=False):
        """This Scalar raised to the given power or powers.

        If this object is read-only, the returned object will also be read-only.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the function
                inside the returned object.
            check (bool, optional): True to mask out the locations of any values that will
                overflow to infinity. If False, a ValueError will be raised any value
                overflows. Check=True is slightly faster if we already know at the time of
                the call that all input values are valid.

        Returns:
            Scalar: The exponential values.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If check is False and any value overflows.
        """

        if self._drank:
            raise ValueError('Scalar.exp() does not support denominators')

        self._require_unitless('exp()')

        if check:
            no_oflow = self.mask_where_gt(_EXP_CUTOFF, replace=_EXP_CUTOFF)
            exp_values = np.exp(no_oflow._values)

        else:
            no_oflow = self
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    exp_values = np.exp(no_oflow._values)
                except (ValueError, TypeError):
                    raise ValueError('Scalar.exp() overflow encountered')

        obj = Scalar(exp_values, mask=no_oflow._mask)

        if recursive and self._derivs:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv * exp_values)

        return obj

    def sign(self, *, zeros=True, builtins=None, masked=None):
        """The sign of each value as +1, -1 or 0.

        Parameters:
            zeros (bool, optional): If zeros is False, then only values of +1 and -1 are
                returned; sign(0) = +1 instead of 0.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                the result is returned as a Python int instead of an instance of Scalar.
                Default is the value specified by Qube.prefer_builtins().
            masked: Value to return if builtins is True but the returned value is masked.
                Default is to return a masked value instead of a builtin type.

        Returns:
            Scalar or int: The sign values.
        """

        result = Scalar(np.sign(self._values), mask=self._mask)

        if not zeros:
            result[result == 0] = 1

        # Convert result to a Python int if necessary
        if builtins is None:
            builtins = Qube.prefer_builtins()

        if builtins:
            return result.as_builtin(masked=masked)

        return result

    @staticmethod
    def solve_quadratic(a, b, c, *, recursive=True, include_antimask=False):
        """A tuple containing the two results of a quadratic equation as Scalars.

        Duplicates and complex values are masked. The formula solved is:
            a * x**2 + b * x + c = 0

        The solution is implemented to provide maximal precision.

        Parameters:
            a: The coefficient of x**2.
            b: The coefficient of x.
            c: The constant term.
            recursive (bool, optional): True to include derivatives in the solution.
            include_antimask (bool, optional): If True, a Boolean is also
                returned containing True where the solution exists (because the
                discriminant is nonnegative).

        Returns:
            tuple: A tuple containing (x0, x1) or (x0, x1, antimask) if include_antimask
            is True.
        """

        a = Scalar.as_scalar(a, recursive=recursive)
        b = Scalar.as_scalar(b, recursive=recursive)
        c = Scalar.as_scalar(c, recursive=recursive)
        (a, b, c) = Scalar.broadcast(a, b, c)

        neg_half_b = -0.5 * b
        discr = neg_half_b**2 - a*c

        term = neg_half_b + neg_half_b.sign(zeros=False) * discr.sqrt()
        x0 = c / term
        x1 = term / a

        # If x0 is masked, use x1
        mask = x0.mask
        x0[mask] = x1[mask]
        x1 = x1.remask_or(mask | (x1 == x0))    # also mask duplicates inside x1

        if include_antimask:
            return (x0, x1, discr >= 0)
        else:
            return (x0, x1)

    def eval_quadratic(self, a, b, c, *, recursive=True):
        """Evaluate a quadratic function for this Scalar.

        The value returned is:
            a * self**2 + b * self + c

        Parameters:
            a: The coefficient of x**2.
            b: The coefficient of x.
            c: The constant term.
            recursive (bool, optional): True to include derivatives in the evaluation.

        Returns:
            Scalar: The result of the quadratic evaluation.
        """

        if not recursive:
            self = self.wod
            a = Scalar.as_scalar(a, recursive=False)
            b = Scalar.as_scalar(b, recursive=False)
            c = Scalar.as_scalar(c, recursive=False)

        return self * (self * a + b) + c

    def max(self, axis=None, *, builtins=None, masked=None, out=None):
        """The maximum of the unmasked values.

        Parameters:
            axis (int or tuple, optional): An integer axis or a tuple of axes. The maximum
                is determined across these axes, leaving any remaining axes in the
                returned value. If None (the default), then the maximum is performed
                across all axes if the object.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                the result is returned as a Python int or float instead of an instance of
                Scalar. Default is the value specified by Qube.prefer_builtins().
            masked: Value to return if builtins is True but the returned value is masked.
                Default is to return a masked value instead of a builtin type.
            out: Ignored. Enables "np.max(Scalar)" to work.

        Returns:
            Scalar or float or int: The maximum values.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.max() does not support denominators')

        self._check_axis(axis, 'max()')         # make sure axis input is valid

        if self._size == 0:
            return self.wod._zero_sized_result(axis)

        if self._shape == ():
            result = self.wod

        elif not np.any(self._mask):
            result = Scalar(np.max(self._values, axis=axis), mask=False, example=self)

        # If all masked, use the unmasked values but leave the result masked
        elif np.all(self._mask):
            result = Scalar(np.max(self._values, axis=axis), mask=True, example=self)

        else:
            # In this case, the values and mask are both arrays
            min_possible = Scalar._minval(self._values.dtype)   # smallest possible value
            new_values = self._values.copy()
            new_values[self._mask] = min_possible
            max_values = np.max(new_values, axis=axis)

            # Deal with completely masked items. Here, use the max of the
            # unmasked values.
            mask = np.all(self._mask, axis=axis)
            if np.any(mask):
                alt_values = np.max(self._values, axis=axis)
                if np.shape(mask):
                    max_values[mask] = alt_values[mask]
                else:
                    max_values = alt_values
            else:
                mask = False

            result = Scalar(max_values, mask, example=self)

        # Convert result to a Python type if necessary
        if builtins is None:
            builtins = Qube.prefer_builtins()

        if builtins:
            return result.as_builtin(masked=masked)

        return result

    def min(self, axis=None, *, builtins=None, masked=None, out=None):
        """The minimum of the unmasked values.

        Parameters:
            axis (int or tuple, optional): An integer axis or a tuple of axes. The minimum
                is determined across these axes, leaving any remaining axes in the
                returned value. If None (the default), then the minimum is performed
                across all axes if the object.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                the result is returned as a Python int or float instead of an instance of
                Scalar. Default is the value specified by Qube.prefer_builtins().
            masked: Value to return if builtins is True but the returned value is masked.
                Default is to return a masked value instead of a builtin type.
            out: Ignored. Enables "np.min(Scalar)" to work.

        Returns:
            Scalar or float or int: The minimum values.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.min() does not support denominators')

        self._check_axis(axis, 'min()')         # make sure axis input is valid

        if self._size == 0:
            return self.wod._zero_sized_result(axis)

        if self._shape == ():
            result = self.wod

        elif not np.any(self._mask):
            result = Scalar(np.min(self._values, axis=axis), mask=False,
                            example=self)

        # If all masked, use the unmasked values but leave the result masked
        elif np.all(self._mask):
            result = Scalar(np.min(self._values, axis=axis), mask=True,
                            example=self)

        else:
            # In this case, the values and mask are both arrays
            max_possible = Scalar._maxval(self._values.dtype)   # largest possible value
            new_values = self._values.copy()
            new_values[self._mask] = max_possible
            min_values = np.min(new_values, axis=axis)

            # Deal with completely masked items. Here, use the min of the
            # unmasked values.
            mask = np.all(self._mask, axis=axis)
            if np.any(mask):
                alt_values = np.min(self._values, axis=axis)
                if np.shape(mask):
                    min_values[mask] = alt_values[mask]
                else:
                    min_values = alt_values
                    mask = True
            else:
                mask = False

            result = Scalar(min_values, mask, example=self)

        # Convert result to a Python type if necessary
        if builtins is None:
            builtins = Qube.prefer_builtins()

        if builtins:
            return result.as_builtin(masked=masked)

        return result

    def argmax(self, axis=None, *, builtins=None, masked=None):
        """The index of the maximum of the unmasked values along the specified axis.

        This returns an integer Scalar array of the same shape as self, except that the
        specified axis has been removed. Each value indicates the index of the maximum
        along that axis. The index is masked where the values along the axis are all
        masked.

        If axis is None, then it returns the index of the maximum argument after
        flattening the array.

        Parameters:
            axis (int, optional): An optional integer axis. If None, it returns the index
                of the maximum argument in the flattened array.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                the result is returned as a Python int instead of an instance of Scalar.
                Default is the value specified by Qube.prefer_builtins().
            masked: Value to return if builtins is True but the returned value is masked.
                Default is to return a masked value instead of a builtin type.

        Returns:
            Scalar or int: The index of the maximum value.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If this object has shape ().
        """

        if self._drank:
            raise ValueError('Scalar.argmax() does not support denominators')

        self._check_axis(axis, 'argmax()')      # make sure axis input is valid

        if self._shape == ():
            raise ValueError('no Scalar.argmax() for object with shape ()')

        if self._size == 0:
            ints = self.zeros(self.shape, dtype='int')
            return ints._zero_sized_result(axis)

        if not np.any(self._mask):
            result = Scalar(np.argmax(self._values, axis=axis), mask=False)

        # If all masked, use the argmax values but leave the result masked
        elif np.all(self._mask):
            result = Scalar(np.argmax(self._values, axis=axis), mask=True)

        # In this case, the values and mask are both arrays
        else:
            min_possible = Scalar._minval(self._values.dtype)   # smallest possible value
            new_values = self._values.copy()
            new_values[self._mask] = min_possible
            argmax = np.argmax(new_values, axis=axis)

            # Deal with completely masked items. Here, use the argmax of the unmasked
            # values.
            mask = np.all(self._mask, axis=axis)
            if np.any(mask):
                alt_argmax = np.argmax(self._values, axis=axis)
                if np.shape(mask):
                    argmax[mask] = alt_argmax[mask]
                else:
                    argmax = alt_argmax
                    mask = True
            else:
                mask = False

            result = Scalar(argmax, mask)

        # Convert result to a Python type if necessary
        if builtins is None:
            builtins = Qube.prefer_builtins()

        if builtins:
            return result.as_builtin(masked=masked)

        return result

    def argmin(self, axis=None, *, builtins=None, masked=None):
        """The index of the minimum of the unmasked values along the specified axis.

        This returns an integer Scalar array of the same shape as self, except that the
        specified axis has been removed. Each value indicates the index of the minimum
        along that axis. The index is masked where the values along the axis are all
        masked.

        Parameters:
            axis (int, optional): An optional integer axis. If None, it returns the index
                of the minimum argument in the flattened array.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                the result is returned as a Python int instead of an instance of Scalar.
                Default is the value specified by Qube.prefer_builtins().
            masked: Value to return if builtins is True but the returned value is masked.
                Default is to return a masked value instead of a builtin type.

        Returns:
            Scalar or int: The index of the minimum value.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If this object has shape ().
        """

        if self._drank:
            raise ValueError('Scalar.argmin() does not support denominators')

        self._check_axis(axis, 'argmin()')      # make sure axis input is valid

        if self._shape == ():
            raise ValueError('no Scalar.argmin() for object with shape ()')

        if self._size == 0:
            ints = self.zeros(self.shape, dtype='int')
            return ints._zero_sized_result(axis)

        if not np.any(self._mask):
            result = Scalar(np.argmin(self._values, axis=axis), mask=False)

        # If all masked, use the argmin values but leave the result masked
        elif np.all(self._mask):
            result = Scalar(np.argmin(self._values, axis=axis), mask=True)

        # In this case, the values and mask are both arrays

        else:
            max_possible = Scalar._maxval(self._values.dtype)   # largest possible value
            new_values = self._values.copy()
            new_values[self._mask] = max_possible
            argmin = np.argmin(new_values, axis=axis)

            # Deal with completely masked items. Here, use the argmin of the unmasked
            # values.
            mask = np.all(self._mask, axis=axis)
            if np.any(mask):
                alt_argmin = np.argmin(self._values, axis=axis)
                if np.shape(mask):
                    argmin[mask] = alt_argmin[mask]
                else:
                    argmin = alt_argmin
                    mask = True
            else:
                mask = False

            result = Scalar(argmin, mask)

        # Convert result to a Python type if necessary
        if builtins is None:
            builtins = Qube.prefer_builtins()

        if builtins:
            return result.as_builtin(masked=masked)

        return result

    @staticmethod
    def maximum(*args):
        """A Scalar composed of the maximum among the given Scalars after they are all
        broadcasted to the same shape.

        Masked values are ignored in the comparisons. Derivatives are removed.
        """

        if len(args) == 0:
            raise ValueError('missing arguments to Scalar.maximum()')

        # Convert to scalars of the same shape
        scalars = []
        for arg in args:
            scalars.append(Scalar.as_scalar(arg, recursive=False))

        scalars = Qube.broadcast(*scalars, _protected=False)

        # Make sure there are no denominators
        for scalar in scalars:
            if scalar._drank:
                raise ValueError('Scalar.maximum() does not support denominators')

        # len == 1 case is easy
        if len(scalars) == 1:
            return scalars[0]

        # Convert to floats if any scalar uses floats
        floats_found = False
        ints_found = False
        for scalar in scalars:
            if scalar.is_float():
                floats_found = True
            if scalar.is_int():
                ints_found = True

        if floats_found and ints_found:
            scalars = [s.as_float() for s in scalars]

        # Create the scalar containing maxima
        result = scalars[0].copy()
        for scalar in scalars[1:]:
            antimask = Qube.and_(scalar._values > result._values,
                                 scalar.antimask)
            antimask = Qube.or_(antimask, result._mask)
            result[antimask] = scalar[antimask]

        result._clear_cache()
        return result

    @staticmethod
    def minimum(*args):
        """A Scalar composed of the minimum among the given Scalars after they
        are all broadcasted to the same shape.
        """

        if len(args) == 0:
            raise ValueError('missing arguments to Scalar.minimum()')

        # Convert to scalars of the same shape
        scalars = []
        for arg in args:
            scalars.append(Scalar.as_scalar(arg, recursive=False))

        scalars = Qube.broadcast(*scalars, _protected=False)

        # Make sure there are no denominators
        for scalar in scalars:
            if scalar._drank:
                raise ValueError('Scalar.minimum() does not support denominators')

        # len == 1 case is easy
        if len(scalars) == 1:
            return scalars[0]

        # Convert to floats if any scalar uses floats
        floats_found = False
        ints_found = False
        for scalar in scalars:
            if scalar.is_float():
                floats_found = True
            if scalar.is_int():
                ints_found = True

        if floats_found and ints_found:
            scalars = [s.as_float() for s in scalars]

        # Create the scalar containing minima
        result = scalars[0].copy()
        for scalar in scalars[1:]:
            antimask = Qube.and_(scalar._values < result._values,
                                 scalar.antimask)
            antimask = Qube.or_(antimask, result._mask)
            result[antimask] = scalar[antimask]

        return result

    def median(self, axis=None, *, builtins=None, masked=None, out=None):
        """The median of the unmasked values.

        Parameters:
            axis (int or tuple, optional): An integer axis or a tuple of axes. The median
                is determined across these axes, leaving any remaining axes in the
                returned value. If None (the default), then the median is performed across
                all axes of the object.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                the result is returned as a Python int or float instead of an instance of
                Scalar. Default is the value specified by Qube.prefer_builtins().
            masked: Value to return if builtins is True but the returned value is masked.
                Default is to return a masked value instead of a builtin type.
            out: Ignored. Enables "np.median(Scalar)" to work.

        Returns:
            Scalar or float or int: The median values.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.median() does not support denominators')

        self._check_axis(axis, 'median()')      # make sure axis input is valid

        if self._size == 0:
            return self.wod._zero_sized_result(axis)

        if self._shape == ():
            result = self.wod.as_float()

        elif not np.any(self._mask):
            result = Scalar(np.median(self._values, axis=axis), mask=False,
                            example=self)

        # If all masked, use the unmasked values but leave the result masked
        elif np.all(self._mask):
            result = Scalar(np.median(self._values, axis=axis), mask=True,
                            example=self)

        elif axis is None:
            result = Scalar(np.median(self._values[self.antimask]), mask=False,
                            example=self)

        else:
            # Interpret the axis selection
            if isinstance(axis, int):
                axis = (axis,)

            # Force all indices to be positive
            axes = tuple([a % self._ndims for a in axis])

            # Move them to the front
            dest = tuple(range(len(axes)))
            new_scalar = self.move_axis(axes, dest)

            # Flatten the leading axes
            new_scalar = new_scalar.reshape((-1,) + new_scalar._shape[len(axes):])

            # Sort along the leading axis, with masked values at the top
            max_possible = Scalar._maxval(self._values.dtype)
            new_values = new_scalar._values.copy()
            new_values[new_scalar._mask] = max_possible
            new_values = np.sort(new_values, axis=0)

            # Count the number of unmasked values for each trailing index
            if isinstance(new_scalar._mask, (bool, np.bool_)):
                if new_scalar._mask:
                    count = 0
                else:
                    count = self._values.size // new_values[0].size
            else:
                count = (self._values.size // new_values[0].size
                         - np.sum(new_scalar._mask, axis=0))

            # Define the indices of the middle one or two
            klo = np.maximum((count - 1) // 2, 0)
            khi = count // 2
            indices = tuple(np.indices(new_values.shape[1:]))
            values_lo = new_values[(klo,) + indices]
            values_hi = new_values[(khi,) + indices]

            # Derive the median
            new_values = 0.5 * (values_lo + values_hi)
            new_mask = (count == 0)

            # Fill in masked items using unmasked medians
            if np.any(new_mask):
                if np.shape(new_values):
                    new_values[new_mask] = np.median(self._values, axis=axis)[new_mask]
                else:
                    new_values = np.median(self._values, axis=axis)

            result = Scalar(new_values, new_mask, unit=self._unit)

        result = result.wod

        # Convert result to a Python type if necessary
        if builtins is None:
            builtins = Qube.prefer_builtins()

        if builtins:
            return result.as_builtin(masked=masked)

        return result

    def sort(self, axis=0):
        """The array sorted along the specified axis from minimum to maximum.

        Masked values appear at the end.

        Parameters:
            axis (int): An integer axis to sort along.

        Returns:
            Scalar: The sorted array.

        Raises:
            ValueError: If this object has denominators.
        """

        if self._drank:
            raise ValueError('Scalar.sort() does not support denominators')

        self._check_axis(axis, 'sort()')        # make sure axis input is valid

        if self._size == 0:
            return self.wod._zero_sized_result(axis)

        if not np.any(self._mask):
            result = Scalar(np.sort(self._values, axis=axis), mask=False,
                            unit=self._unit)

        else:
            max_possible = Scalar._maxval(self._values.dtype)
            new_values = self._values.copy()
            new_values[self._mask] = max_possible
            new_values = np.sort(new_values, axis=axis)

            # Create the new mask
            if np.shape(self._mask) == ():
                new_mask = self._mask
            else:
                new_mask = self._mask.copy()
                new_mask = np.sort(new_mask, axis=axis)

            # Construct the result
            result = Scalar(new_values, new_mask, unit=self._unit)

            # Replace the masked values by the max
            new_values[new_mask] = result.max()

        return result.wod

    #####################################################################################
    # Overrides of arithmetic operators
    #####################################################################################

    def reciprocal(self, *, recursive=True, nozeros=False):
        """An object equivalent to the reciprocal of this object.

        This is an override of :meth:`Qube.reciprocal`.

        Parameters:
            recursive (bool, optional): True to return the derivatives of the reciprocal
                too; otherwise, derivatives are removed.
            nozeros (bool, optional): False (the default) to mask out any zero-valued
                items in this object prior to the divide. Set to True only if you know in
                advance that this object has no zero-valued items.

        Returns:
            Scalar: The reciprocal of this object.

        Raises:
            ValueError: If this object has denominators.
            ValueError: If nozeros is True and a zero value is encountered.
        """

        if self._rank:
            raise ValueError('Scalar.reciprocal() does not support denominators')

        # mask out zeros if necessary
        if nozeros:
            denom = self
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    denom_inv_values = 1. / denom._values
                    denom_inv_mask = denom._mask
                except (ZeroDivisionError, RuntimeWarning):
                    raise ValueError('divide by zero in Scalar.reciprocal()')

        else:
            denom = self.mask_where_eq(0, replace=1)
            denom_inv_values = 1. / denom._values
            denom_inv_mask = denom._mask

        # Construct the object
        obj = Qube.__new__(type(self))
        obj.__init__(denom_inv_values, denom_inv_mask,
                     unit=Unit.unit_power(self._unit, -1))

        # Fill in derivatives if necessary
        if recursive and self._derivs:
            factor = -obj*obj       # At this point it has no derivs
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

    def identity(self):
        """An object of this subclass equivalent to the identity.

        This is an override of :meth:`Qube.identity`.

        Returns:
            Scalar: A read-only identity scalar with value 1.
        """

        # Scalar case
        if self.is_float():
            new_value = 1.
        else:
            new_value = 1

        # Construct the object
        return Scalar(new_value).as_readonly()

    ######################################################################################
    # Logical operators
    ######################################################################################

    def __le__(self, arg, *, builtins=True):
        """self <= arg, element-by-element "less than or equal".

        This is an override of :meth:`Qube.__le__`.

        Parameters:
            arg: The scalar to compare with.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                return a Python bool instead of a Boolean object.

        Returns:
            Boolean or bool: True where this scalar is less than or equal to the argument.

        Raises:
            ValueError: If either object has denominators.
        """

        arg = Scalar.as_scalar(arg)
        self._require_compatible_units(arg)
        if self._denom or arg._denom:
            self._disallow_denom('<=')

        compare = (self._values <= arg._values)

        # Return a Python bool if possible
        if builtins and not isinstance(compare, np.ndarray):
            if self._mask or arg._mask:
                return False
            return bool(compare)

        compare &= (self.antimask & arg.antimask)

        result = Qube._BOOLEAN_CLASS(compare)
        result._truth_if_all = True
        return result

    def __lt__(self, arg, *, builtins=True):
        """self < arg, element-by-element "less than".

        This is an override of :meth:`Qube.__lt__`.

        Parameters:
            arg: The scalar to compare with.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                return a Python bool instead of a Boolean object.

        Returns:
            Boolean or bool: True where this scalar is less than the argument.

        Raises:
            ValueError: If either object has denominators.
        """

        arg = Scalar.as_scalar(arg)
        self._require_compatible_units(arg)
        if self._denom or arg._denom:
            self._disallow_denom('<')

        compare = (self._values < arg._values)

        # Return a Python bool if possible
        if builtins and not isinstance(compare, np.ndarray):
            if self._mask or arg._mask:
                return False
            return bool(compare)

        compare &= (self.antimask & arg.antimask)

        result = Qube._BOOLEAN_CLASS(compare)
        result._truth_if_all = True
        return result

    def __ge__(self, arg, *, builtins=True):
        """self >= arg, element-by-element "less than or equal".

        This is an override of :meth:`Qube.__ge__`.

        Parameters:
            arg: The scalar to compare with.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                return a Python bool instead of a Boolean object.

        Returns:
            Boolean or bool: True where this scalar is greater than or equal to the
            argument.

        Raises:
            ValueError: If either object has denominators.
        """

        arg = Scalar.as_scalar(arg)
        self._require_compatible_units(arg)
        if self._denom or arg._denom:
            self._disallow_denom('>=')

        compare = (self._values >= arg._values)

        # Return a Python bool if possible
        if builtins and not isinstance(compare, np.ndarray):
            if self._mask or arg._mask:
                return False
            return bool(compare)

        compare &= (self.antimask & arg.antimask)

        result = Qube._BOOLEAN_CLASS(compare)
        result._truth_if_all = True
        return result

    def __gt__(self, arg, *, builtins=True):
        """self > arg, element-by-element "greater than".

        This is an override of :meth:`Qube.__gt__`.

        Parameters:
            arg: The scalar to compare with.
            builtins (bool, optional): If True and the result is a single unmasked scalar,
                return a Python bool instead of a Boolean object.

        Returns:
            Boolean or bool: True where this scalar is greater than the argument.

        Raises:
            ValueError: If either object has denominators.
        """

        arg = Scalar.as_scalar(arg)
        self._require_compatible_units(arg)
        if self._denom or arg._denom:
            self._disallow_denom('>')

        compare = (self._values > arg._values)

        # Return a Python bool if possible
        if builtins and not isinstance(compare, np.ndarray):
            if self._mask or arg._mask:
                return False
            return bool(compare)

        compare &= (self.antimask & arg.antimask)

        result = Qube._BOOLEAN_CLASS(compare)
        result._truth_if_all = True
        return result

    def __round__(self, digits):
        """This scalar rounded to the specified number of digits.

        Parameters:
            digits (int): The number of decimal digits to round to.

        Returns:
            Scalar: The rounded scalar.
        """

        return Scalar(np.round(self._values, digits), example=self)

    ######################################################################################
    # Other operators
    ######################################################################################

    def __abs__(self, *, recursive=True):
        """abs(self), element-by-element absolute value.

        This is an override of :meth:`Qube.__abs__`.

        Parameters:
            recursive (bool, optional): True to include the derivatives. For every
                element that has its sign flipped, the sign will also be flipped in that
                element's derivatives.

        Returns:
            Scalar: The absolute value.
        """

        # Construct a copy with absolute values
        obj = self.clone(recursive=False)
        obj._set_values(np.abs(self._values))

        # Fill in the derivatives, multiplied by sign(self)
        sign = self.wod.sign()
        if recursive and self._derivs:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv * sign)

        return obj

    def abs(self, *, recursive=True):
        """Element-by-element absolute value.

        Parameters:
            recursive (bool, optional): True to include the derivatives. If True, for
                every element that has its sign flipped, the sign will also be flipped in
                that element's derivatives.

        Returns:
            Scalar: The absolute value.
        """

        return self.__abs__(recursive=recursive)

    def _power_0(self, *, recursive=True):
        """This scalar raised to the power of 0.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: A scalar with value 1 and the same shape as this object.
        """

        x = self.ones(self._shape, dtype=Qube._dtype(self), mask=self._mask)
        if recursive:
            for key, deriv in self._derivs.items():
                x.insert_deriv(key, deriv.zeros(deriv._shape,
                                                numer=deriv._numer,
                                                denom=deriv._denom,
                                                mask=deriv._mask))
        return x

    def _power_1(self, *, recursive=True):
        """This scalar raised to the power of 1.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: This scalar unchanged.
        """

        return self if recursive else self.wod

    def _power_2(self, *, recursive=True):
        """This scalar raised to the power of 2.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: This scalar squared.
        """

        result = Scalar(self._values * self._values, self._mask,
                        unit=Unit.unit_power(self._unit, 2))

        if recursive and self._derivs:
            factor = 2. * self.wod
            for key, deriv in self._derivs.items():
                result.insert_deriv(key, factor * deriv)

        return result

    def _power_3(self, *, recursive=True):
        """This scalar raised to the power of 3.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: This scalar cubed.
        """

        x_sq = self._values * self._values
        result = Scalar(self._values * x_sq, self._mask,
                        unit=Unit.unit_power(self._unit, 3))

        if recursive and self._derivs:
            factor = Scalar(3. * x_sq, self._mask,
                            unit=Unit.unit_power(self._unit, 2))
            for key, deriv in self._derivs.items():
                result.insert_deriv(key, factor * deriv)

        return result

    def _power_4(self, *, recursive=True):
        """This scalar raised to the power of 4.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: This scalar raised to the fourth power.
        """

        x_sq = self._values * self._values
        result = Scalar(x_sq * x_sq, self._mask,
                        unit=Unit.unit_power(self._unit, 4))

        if recursive and self._derivs:
            factor = Scalar(4. * x_sq * self._values, self._mask,
                            unit=Unit.unit_power(self._unit, 3))
            for key, deriv in self._derivs.items():
                result.insert_deriv(key, factor * deriv)

        return result

    def _power_neg_1(self, *, recursive=True):
        """This scalar raised to the power of -1.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: The reciprocal of this scalar.
        """

        return self.reciprocal(recursive=recursive)

    def _power_half(self, *, recursive=True):
        """This scalar raised to the power of 1/2.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: The square root of this scalar.
        """

        return self.sqrt(recursive=recursive)

    def _power_neg_half(self, *, recursive=True):
        """This scalar raised to the power of -1/2.

        Parameters:
            recursive (bool, optional): True to include derivatives.

        Returns:
            Scalar: The reciprocal of the square root of this scalar.
        """

        return self.sqrt(recursive=recursive).reciprocal(recursive=recursive)

    _EASY_INT_POWERS = {
         0: _power_0,
         1: _power_1,
         2: _power_2,
         3: _power_3,
         4: _power_4,
        -1: _power_neg_1,               # noqa
    }

    _EASY_FLOAT_POWERS = {
         0.5: _power_half,
        -0.5: _power_neg_half,          # noqa
    }

    # Generic exponentiation, PolyMath scalar to a single scalar power
    def __pow__(self, expo, *, recursive=True):

        self._disallow_denom('**')

        # Handle the common and easy cases where there is only a single exponent
        if isinstance(expo, numbers.Integral):
            try:
                return Scalar._EASY_INT_POWERS[expo](self, recursive=recursive)
            except KeyError:
                pass

        if isinstance(expo, numbers.Real):
            try:
                return Scalar._EASY_FLOAT_POWERS[expo](self, recursive=recursive)
            except KeyError:
                pass

        # Interpret the exponent and mask if any
        if isinstance(expo, Scalar):
            if expo._rank:
                raise ValueError('"**" exponent requires scalar items')
            expo._require_unitless()
        else:
            expo = Scalar(expo)

        # 0-D case
        if not self._shape and not expo._shape:
            try:
                new_values = self._values ** expo._values
            except (ValueError, ZeroDivisionError):
                return self.masked_single(recursive=recursive)

            if not isinstance(new_values, numbers.Real):
                return self.masked_single(recursive=recursive)

            new_mask = False
            new_unit = Unit.unit_power(self._unit, expo._values)

        # Array case
        else:

            # Without this step, negative int exponents on int values truncate
            # to 0.
            if expo.is_int():
                if expo._shape:
                    if np.any(expo._values < 0):
                        expo = expo.as_float()
                elif expo._values < 0:
                    expo = expo.as_float()

            # Plow forward with the results blindly, then mask nan and inf.
            # Zero to a negative power creates a RuntTimeWarning, which needs to be
            # suppressed.
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                new_values = self._values ** expo._values

            new_mask = Qube.or_(self._mask, expo._mask)
            invalid = np.isnan(new_values) | np.isinf(new_values)
            if np.any(invalid):
                new_values[invalid] = 1.
                new_mask = Qube.or_(new_mask, invalid)

            # Check units and exponent
            if Unit.is_unitless(self._unit):
                new_unit = None
            elif expo._is_array:
                raise ValueError('Scalar with unit can only be raised to a single power')
            else:
                new_unit = Unit.unit_power(self._unit, expo._values)

        obj = Scalar.__new__(type(self))
        obj.__init__(new_values, new_mask, unit=new_unit, example=self)

        # Evaluate the derivatives if necessary
        if recursive and self._derivs:
            factor = expo * self.__pow__(expo-1, recursive=False)
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, factor * deriv)

        return obj

##########################################################################################
# Useful class constants
##########################################################################################

Scalar.ZERO   = Scalar(0).as_readonly()
Scalar.ONE    = Scalar(1).as_readonly()
Scalar.TWO    = Scalar(2).as_readonly()
Scalar.THREE  = Scalar(3).as_readonly()

Scalar.PI     = Scalar(np.pi).as_readonly()
Scalar.TWOPI  = Scalar(2 * np.pi).as_readonly()
Scalar.HALFPI = Scalar(np.pi / 2).as_readonly()

Scalar.MASKED = Scalar(1, True).as_readonly()

Scalar.INF    = Scalar(np.inf).as_readonly()
Scalar.NEGINF = Scalar(-np.inf).as_readonly()

##########################################################################################
# Once the load is complete, we can fill in a reference to the Scalar class
# inside the Qube object.
##########################################################################################

Qube._SCALAR_CLASS = Scalar

##########################################################################################
