##########################################################################################
# polymath/polynomial.py: Polynomial subclass of Vector
##########################################################################################

import numpy as np

from polymath.qube   import Qube
from polymath.scalar import Scalar
from polymath.vector import Vector
from polymath.unit   import Unit


class Polynomial(Vector):
    """Represent polynomials in the PolyMath framework.

    This is a Vector subclass in which the elements are interpreted as the coefficients of
    a polynomial in a single variable x. Coefficients appear in order of decreasing
    exponent. Mathematical operations, polynomial root-solving are supported. Coefficients
    can have derivatives and these can be used to determine derivatives of the values or
    roots.
    """

    _INTS_OK = False    # Only floating-point coefficients are allowed

    def __init__(self, *args, **kwargs):
        """Initialize a Polynomial object.

        Parameters:
            *args: Arguments to pass to the Vector constructor. If a single argument is a
                subclass of Vector, it is quickly converted to class Polynomial.
            **kwargs: Keyword arguments to pass to the Vector constructor.

        Notes:
            If a single argument is a subclass of Vector, it is quickly converted to class
            Polynomial. Otherwise, the constructor takes the same inputs as the
            constructor for class Vector.
        """

        # For a subclass of Vector, transfer all attributes
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], Vector):
            for key, value in args[0].__dict__.items():
                self.__dict__[key] = value

            # Convert derivatives to class Polynomial if necessary
            if type(self) is not Polynomial:
                derivs = {}
                for key, value in args[0].derivs.items():
                    derivs[key] = Polynomial(value)

                self._derivs = derivs

        # Otherwise use the Vector class constructor
        else:
            super(Polynomial, self).__init__(*args, **kwargs)

    @property
    def order(self):
        """The order of the polynomial, i.e., the largest exponent.

        Returns:
            int: The order of the polynomial.
        """

        return self.item[-self._drank - 1] - 1

    @staticmethod
    def as_polynomial(arg, *, recursive=True):
        """A shallow copy of the given object as class Polynomial.

        Parameters:
            arg: Object to convert to Polynomial.
            recursive (bool, optional): True to include derivatives in the conversion.

        Returns:
            Polynomial: The converted object as a Polynomial.
        """

        if isinstance(arg, Vector):
            if not recursive:
                arg = arg.wod

            return Polynomial(arg)

        vector = Vector.as_vector(arg)
        if recursive:
            return Polynomial(vector)
        else:
            return Polynomial(vector.wod)

    def as_vector(self, *, recursive=True):
        """A shallow copy of this Polynomial as class Vector.

        Parameters:
            recursive (bool, optional): True to include derivatives in the conversion.

        Returns:
            Vector: This polynomial converted to a Vector.
        """

        obj = Qube.__new__(Vector)
        for key, value in self.__dict__.items():
            obj.__dict__[key] = value

        derivs = {}
        if recursive:
            for key, value in self._derivs.items():
                derivs[key] = self.as_vector(recursive=False)

        obj.insert_derivs(derivs)
        return obj

    def at_least_order(self, order, *, recursive=True):
        """A shallow copy with at least this minimum order.

        Extra leading polynomial coefficients are filled with zeros.

        Parameters:
            order (int): Minimum order of the Polynomial.
            recursive (bool, optional): True to include derivatives in the conversion.

        Returns:
            Polynomial: A copy with at least the specified minimum order.
        """

        if self.order >= order:
            if recursive:
                return self
            else:
                return self.wod

        new_values = np.zeros(self._shape + (order+1,))
        new_values[..., -self.order-1:] = self._values

        result = Polynomial(new_values, self._mask, derivs={}, example=self)
        if recursive and self._derivs:
            for key, value in self._derivs.items():
                result.insert_deriv(key, value.at_least_order(order, recursive=False))

        return result

    def set_order(self, order, *, recursive=True):
        """This Polynomial expressed with exactly this order.

        Extra polynomial coefficients are filled with zeros. If this Polynomial exceeds
        this order requested, raise an exception.

        Parameters:
            order (int): Exact order of the Polynomial.
            recursive (bool, optional): True to include derivatives in the conversion.

        Returns:
            Polynomial: A copy with exactly the specified order.

        Raises:
            ValueError: If this Polynomial exceeds the order requested.
        """

        if self.order > order:
            raise ValueError(f'Polynomial of order {self.order} exceeds intended order '
                             f'{order}')

        return self.at_least_order(order, recursive=recursive)

    def invert_line(self, *, recursive=True):
        """The inversion of this linear polynomial.

        Parameters:
            recursive (bool, optional): True to include derivatives in the conversion.

        Returns:
            Polynomial: The inverted linear polynomial.

        Raises:
            ValueError: If the polynomial is not first-order.
        """

        if self.order != 1:
            raise ValueError('invert_line requires a first-order polynomial')

        # y = a x + b
        # y - b = a x
        # y/a - b/a = x

        (a, b) = self.to_scalars(recursive=recursive)

        a_inv = 1. / a
        return Polynomial(Vector.from_scalars(a_inv, -b * a_inv), recursive=recursive)

    ######################################################################################
    # Math operations
    ######################################################################################

    def __neg__(self):
        """Return the negation of this polynomial.

        Returns:
            Polynomial: The negated polynomial.
        """

        return Polynomial(-self.as_vector())

    def __add__(self, arg):
        """Add this polynomial to another polynomial or scalar.

        Parameters:
            arg: The polynomial or scalar to add to this polynomial.

        Returns:
            Polynomial: The sum of the polynomials.
        """

        arg = Polynomial.as_polynomial(arg).at_least_order(self.order)
        self = self.at_least_order(arg.order)
        return Polynomial(self.as_vector() + arg.as_vector())

    def __radd__(self, arg):
        """Add this polynomial to another polynomial or scalar (right addition).

        Parameters:
            arg: The polynomial or scalar to add to this polynomial.

        Returns:
            Polynomial: The sum of the polynomials.
        """

        return self.__add__(arg)

    def __iadd__(self, arg):
        """Add another polynomial to this polynomial in-place.

        Parameters:
            arg: The polynomial to add to this polynomial.

        Returns:
            Polynomial: This polynomial modified in-place.
        """

        arg = Polynomial.as_polynomial(arg).set_order(self.order)
        self.super().__iadd__(arg.super())
        return self

    def __sub__(self, arg):
        """Subtract another polynomial or scalar from this polynomial.

        Parameters:
            arg: The polynomial or scalar to subtract from this polynomial.

        Returns:
            Polynomial: The difference of the polynomials.
        """

        arg = Polynomial.as_polynomial(arg).at_least_order(self.order)
        self = self.at_least_order(arg.order)
        return Polynomial(self.super() - arg.super())

    def __rsub__(self, arg):
        """Subtract this polynomial from another polynomial or scalar.

        Parameters:
            arg: The polynomial or scalar from which to subtract this polynomial.

        Returns:
            Polynomial: The difference of the polynomials.
        """

        arg = Polynomial.as_polynomial(arg).at_least_order(self.order)
        self = self.at_least_order(arg.order)
        return Polynomial(arg.super() - self.super())

    def __isub__(self, arg):
        """Subtract another polynomial from this polynomial in-place.

        Parameters:
            arg: The polynomial to subtract from this polynomial.

        Returns:
            Polynomial: This polynomial modified in-place.
        """

        arg = Polynomial.as_polynomial(arg).set_order(self.order)
        self.super().__isub__(arg.super())
        return self

    def __mul__(self, arg):
        """Multiply this polynomial by another polynomial or scalar.

        Parameters:
            arg: The polynomial or scalar to multiply with this polynomial.

        Returns:
            Polynomial: The product of the polynomials.

        Raises:
            ValueError: If the polynomials have incompatible denominators.
        """

        # Support for Polynomial multiplication
        if isinstance(arg, Polynomial):
            if self._drank != arg._drank:
                raise ValueError('incompatible denominators for multiply')

            new_order = self.order + arg.order
            new_shape = Qube.broadcasted_shape(self._shape, arg._shape)
            new_values = np.zeros(new_shape + (new_order + 1,))
            new_mask = Qube.or_(self._mask, arg._mask)

            # It's simpler to work in order of increasing powers
            tail_indx = self._drank * (slice(None),)
            indx = (Ellipsis, slice(None, None, -1)) + tail_indx
            self_values = self._values[indx]
            arg_values  = arg._values[indx]

            # Perform the multiplication
            kstop = arg._values.shape[-self._drank - 1]
            dk    = self._values.shape[-self._drank - 1]
            for k in range(kstop):
                new_indx = (Ellipsis, slice(k, k+dk)) + tail_indx
                arg_indx = (Ellipsis, slice(k, k+1))  + tail_indx
                new_values[new_indx] += arg_values[arg_indx] * self_values

            result = Polynomial(new_values[indx], new_mask, derivs={},
                                unit=Unit._mul_units(self._unit, arg._unit))

            # Deal with derivatives
            derivs = {}
            for key, value in self._derivs.items():
                derivs[key] = arg.wod * value

            for key, value in arg._derivs.items():
                if key in derivs:
                    derivs[key] = derivs[key] + self.wod * value
                else:
                    derivs[key] = self.wod * value

            result.insert_derivs(derivs)

            return result

        return Polynomial(self.as_vector() * arg)

    def __rmul__(self, arg):
        """Multiply another polynomial or scalar by this polynomial.

        Parameters:
            arg: The polynomial or scalar to multiply with this polynomial.

        Returns:
            Polynomial: The product of the polynomials.
        """
        return self.__mul__(arg)

    def __imul__(self, arg):
        """Multiply this polynomial by another polynomial or scalar in-place.

        Parameters:
            arg: The polynomial or scalar to multiply with this polynomial.

        Returns:
            Polynomial: This polynomial modified in-place.
        """

        # Multiplying by a zero-order Polynomial is valid
        if isinstance(arg, Vector) and arg.item == (1,):
            arg = arg.to_scalar(0)

        super(Polynomial, self).__imul__(arg)
        return Polynomial(self)

    def __truediv__(self, arg):
        """Divide this polynomial by another polynomial or scalar.

        Parameters:
            arg: The polynomial or scalar by which to divide this polynomial.

        Returns:
            Polynomial: The quotient of the polynomials.
        """

        # Dividing by a zero-order Polynomial is valid
        if isinstance(arg, Vector) and arg.item == (1,):
            arg = arg.to_scalar(0)

        return Polynomial(self.as_vector() / arg)

    def __itruediv__(self, arg):
        """Divide this polynomial by another polynomial or scalar in-place.

        Parameters:
            arg: The polynomial or scalar by which to divide this polynomial.

        Returns:
            Polynomial: This polynomial modified in-place.
        """

        # Dividing by a zero-order Polynomial is valid
        if isinstance(arg, Vector) and arg.item == (1,):
            arg = arg.to_scalar(0)

        super(Polynomial, self).__itruediv__(arg)
        return Polynomial(self)

    def __pow__(self, arg):
        """Raise this polynomial to the specified power.

        Parameters:
            arg: The exponent (must be a non-negative integer).

        Returns:
            Polynomial: This polynomial raised to the specified power.

        Raises:
            ValueError: If the exponent is negative or not an integer.
        """

        if arg < 0 or arg != int(arg):
            raise ValueError('Polynomial exponents must be non-negative integers')

        if arg == 0:
            return Polynomial([1.])

        return Polynomial(self.as_vector() ** arg)

    def __eq__(self, arg):
        """Check if this polynomial equals another polynomial.

        Parameters:
            arg: The polynomial to compare with this polynomial.

        Returns:
            bool: True if the polynomials are equal, False otherwise.
        """

        arg = Polynomial.as_polynomial(arg).at_least_order(self.order)
        self = self.at_least_order(arg.order)
        return arg.as_vector() == self.as_vector()

    def __ne__(self, arg):
        """Check if this polynomial does not equal another polynomial.

        Parameters:
            arg: The polynomial to compare with this polynomial.

        Returns:
            bool: True if the polynomials are not equal, False otherwise.
        """

        arg = Polynomial.as_polynomial(arg).at_least_order(self.order)
        self = self.at_least_order(arg.order)
        return arg.as_vector() != self.as_vector()

    ######################################################################################
    # Special Polynomial operations
    ######################################################################################

    def deriv(self, recursive=True):
        """Return the first derivative of this Polynomial.

        Parameters:
            recursive (bool, optional): True to evaluate derivatives as well.
                Defaults to True.

        Returns:
            Polynomial: The derivative polynomial.
        """

        if self.order <= 0:
            new_values = np.zeros(self._values.shape)
        else:
            indx1 = (Ellipsis, slice(0, -1)) + self._drank * (slice(None, None),)
            indx2 = (Ellipsis,)              + self._drank * (np.newaxis,)
            new_values = self._values[indx1] * np.arange(self.order, 0, -1)[indx2]

        result = Polynomial(new_values, self._mask, derivs={}, example=self)

        if recursive and self._derivs:
            for key, value in self._derivs.items():
                result.insert_deriv(key, value.deriv(recursive=False))

        return result

    def eval(self, x, recursive=True):
        """Evaluate the polynomial at x.

        Parameters:
            x: Scalar at which to evaluate the Polynomial.
            recursive (bool, optional): True to evaluate derivatives as well.
                Defaults to True.

        Returns:
            Scalar: A Scalar of values. Note that the shapes of self and x are
                broadcasted together.
        """

        if self.order == 0:
            if recursive:
                return Scalar(example=self)
            else:
                return Scalar(example=self.wod)

        x = Scalar.as_scalar(x, recursive=recursive)
        x_powers = [1., x]
        x_power = x
        for k in range(1, self.order):
            x_power *= x
            x_powers.append(x_power)

        x_powers = Vector.from_scalars(*(x_powers[::-1]))

        return Qube.dot(self, x_powers, 0, 0, (Scalar,), recursive=recursive)

    def roots(self, recursive=True):
        """Find the roots of the polynomial.

        Parameters:
            recursive (bool, optional): True to evaluate derivatives at the roots
                as well. Defaults to True.

        Returns:
            Scalar: A Scalar of roots. This has the same shape as self but an extra
                leading axis matching the order of the polynomial. The leading index
                selects among the roots of the polynomial. Roots appear in increasing
                order and without any duplicates. If fewer real roots exist, the set of
                roots is padded at the end with masked values.

        Raises:
            ValueError: If the polynomial is of order zero.
        """

        # Constant case is easy
        if self.order == 0:
            # a = 0
            raise ValueError('no roots of a order-zero Polynomial')

        # Linear case is easy
        if self.order == 1:
            # a x + b = 0
            (a, b) = self.to_scalars(recursive=recursive)
            result = -b / a
            return result.reshape((1,) + result._shape)

        # Quadratic case is easy
        if self.order == 2:
            # a x^2 + b x + c = 0
            (a, b, c) = self.to_scalars(recursive=recursive)
            (x0, x1) = Scalar.solve_quadratic(a, b, c, recursive=recursive)
            x1 = x1.mask_where(x1 == x0)        # mask duplicated solutions
            return Qube.stack(x0, x1).sort(axis=0)

        # Method for higher-order polynomials stolen from np.roots; see:
        #    https://github.com/numpy/numpy
        #               /blob/v1.14.0/numpy/lib/polynomial.py#L153-L235
        #     p[0] * x**n + p[1] * x**(n-1) + ... + p[n-1]*x + p[n]

        # Copy polynomial coefficients
        coefficients = self._values.copy()

        # Convert the mask to an array
        if np.isscalar(self._mask):
            if self._mask:
                poly_mask = np.ones(self._shape, dtype='bool')
            else:
                poly_mask = np.zeros(self._shape, dtype='bool')
        else:
            poly_mask = self._mask.copy()

    # Method stolen from np.roots; see
    # https://github.com/numpy/numpy/blob/v1.14.0/numpy/lib/polynomial.py#L153-L235
    #     p[0] * x**n + p[1] * x**(n-1) + ... + p[n-1]*x + p[n]

        # Mask out any cases where all coefficients are zero
        all_zeros = np.all(coefficients == 0., axis=-1)
        if np.any(all_zeros):

            # Problem is now 1 * x**n = 0 so solution is no longer undefined
            coefficients[all_zeros, 0] = 1.
            poly_mask |= all_zeros

#     N = len(p)
#     if N > 1:
#         # build companion matrix and find its eigenvalues (the roots)
#         A = diag(np.ones((N-2,), p.dtype), -1)
#         A[0,:] = -p[1:] / p[0]
#         roots = np.linalg.eigvals(A)
#     else:
#         roots = np.array([])

        # Shift coefficients till the leading coefficient is nonzero
        shifts = (coefficients[..., 0] == 0.)
        total_shifts = np.zeros(shifts._shape, dtype='int')
        while np.any(shifts):
            coefficients[shifts, :-1] = coefficients[shifts, 1:]
            coefficients[shifts, -1] = 0.
            total_shifts += shifts
            shifts = (coefficients[..., 0] == 0.)

        # Implement the NumPy solution, array-based
        matrix = np.empty(self._shape + (self.order, self.order))
        matrix[..., :, :] = np.diag(np.ones((self.order - 1,)), -1)
        matrix[..., 0, :] = -coefficients[..., 1:] / coefficients[..., 0:1]
        roots = np.linalg.eigvals(matrix)
        roots = np.rollaxis(roots, -1, 0)

        # Convert the roots to a real Scalar
        is_complex = np.imag(roots) != 0.
        root_values = np.real(roots)
        root_mask = poly_mask[np.newaxis, ...] | is_complex

        # Mask extraneous zeros
        # Handily, they always show up first in the array of roots
        max_shifts = total_shifts.max()
        for k in range(max_shifts):
            root_mask[total_shifts > k, k] = True

        roots = Scalar(root_values, Qube.as_one_bool(root_mask))
        roots = roots.sort(axis=0)

        # Mask duplicated values
        mask_changed = False
        for k in range(1, self.order):
            mask = ((roots._values[k, ...] == roots._values[k - 1, ...])
                    & ~roots._mask[k, ...])
            if np.any(mask):
                root_mask[k, ...] |= mask
                mask_changed = True

        if mask_changed:
            roots = Scalar(root_values, Qube.as_one_bool(root_mask))
            roots = roots.sort(axis=0)

        # Deal with derivatives if necessary
        #
        # Sum_j c[j] x**j = 0
        #
        # Sum_j dc[j]/dt x**j + Sum_j c[j] j x**(j-1) dx/dt = 0
        #
        # dx/dt = -Sum_j dc[j]/dt x**j / Sum_j c[j] j x**(j-1)

        if recursive:
            for key, value in self._derivs.items():
                deriv = (-value.eval(roots, recursive=False) /
                         self.deriv.eval(roots, recursive=False))
                roots.insert_deriv(key, deriv)

        return roots

##########################################################################################
