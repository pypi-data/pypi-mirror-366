##########################################################################################
# polymath/vector.py: Vector subclass of PolyMath base class
##########################################################################################

from __future__ import division
import numpy as np

from polymath.qube   import Qube
from polymath.scalar import Scalar
from polymath.unit   import Unit


class Vector(Qube):
    """Representation of 1-D vectors of arbitrary length in the PolyMath framework.

    This class handles arbitrary length one-dimensional vectors and provides operations
    for vector arithmetic, dot products, and other mathematical operations.
    """

    _NRANK = 1          # The number of numerator axes.
    _NUMER = None       # Shape of the numerator.
    _FLOATS_OK = True   # True to allow floating-point numbers.
    _INTS_OK = True     # True to allow integers.
    _BOOLS_OK = False   # True to allow booleans.
    _UNITS_OK = True    # True to allow units; False to disallow them.
    _DERIVS_OK = True   # True to allow derivatives and denominators; False to disallow.

    def __init__(self, arg, *args, **kwargs):
        """Initialize a Vector object.

        Parameters:
            arg (ndarray, float, int, list, or tuple): The input data to construct
                the Vector. A Python scalar will be converted to an array of shape (1,).
            *args: Additional arguments passed to the Qube constructor.
            **kwargs: Additional "keyword=value" arguments passd to the Qube constructor.
        """

        if isinstance(arg, (float, int)):
            arg = np.array([arg])

        super(Vector, self).__init__(arg, *args, **kwargs)

    @staticmethod
    def as_vector(arg, *, recursive=True):
        """Convert the argument to a Vector if possible.

        Parameters:
            arg (object): The object to convert to Vector.
            recursive (bool, optional): If True, derivatives will also be converted.

        Returns:
            Vector: The converted Vector object.
        """

        if isinstance(arg, Vector):
            return arg if recursive else arg.wod

        if isinstance(arg, Qube):

            # Collapse a 1xN or Nx1 MatrixN down to a Vector
            if arg._nrank == 2 and (arg._numer[0] == 1 or arg._numer[1] == 1):
                return arg.flatten_numer(Vector, recursive=recursive)

            # Convert Scalar to shape (1,)
            if arg._nrank == 0:
                if arg._is_array:
                    new_values = arg._values.reshape(arg._shape + (1,) + arg.item)
                else:
                    new_values = np.array([arg._values])

                result = Vector(new_values, arg._mask, nrank=1, drank=arg._drank,
                                derivs={}, example=arg)

                if recursive and arg._derivs:
                    for key, value in arg._derivs.items():
                        result.insert_deriv(key, Vector.as_vector(value, recursive=False))
                return result

            # Default conversion
            derivs = arg._derivs if recursive else {}
            return Vector(arg, derivs=derivs)

        return Vector(arg)

    def to_scalar(self, indx, *, recursive=True):
        """Return one of the components of this Vector as a Scalar.

        Parameters:
            indx (int): Index of the vector component.
            recursive (bool, optional): True to include the derivatives.

        Returns:
            Scalar: The component at the specified index.
        """

        return self.extract_numer(0, indx, Scalar, recursive=recursive)

    def to_scalars(self, *, recursive=True):
        """Return all the components of this Vector as a tuple of Scalars.

        Parameters:
            recursive (bool, optional): True to include the derivatives.

        Returns:
            tuple: A tuple containing each component as a Scalar.
        """

        results = []
        for i in range(self._numer[0]):
            results.append(self.extract_numer(0, i, Scalar, recursive=recursive))

        return tuple(results)

    def to_pair(self, axes=(0, 1), *, recursive=True):
        """Return a Pair containing two selected components of this Vector.

        Overrides the default method to include an 'axes' argument, which can extract any
        two components of a Vector very efficiently.

        Parameters:
            axes (tuple, optional): Indices of the two components to extract, positive or
                negative.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Pair: A Pair object containing the two selected components.
        """

        size = self._numer[0]
        for k, i in enumerate(axes):
            if i < -size or i >= size:
                raise IndexError(f'axes[{k}] out of range ({-size},{size}) in '
                                 f'{type(self).__name__}.to_pair()')

        i0, i1 = axes
        j0 = i0 % size
        j1 = i1 % size
        dj = j1 - j0
        if dj % size == 0:
            raise IndexError(f'duplicated axes in {type(self).__name__}.to_pair(): '
                             f'{i0}, {i1}')

        stop = j1 + np.sign(dj)
        if (stop == 0 and dj > 0) or (stop == -1 and dj < 0):
            stop = None

        indx = (Ellipsis, slice(j0, stop, dj)) + self._drank * (slice(None),)
        result = Qube._PAIR_CLASS(self._values[indx], self._mask, derivs={},
                                  example=self)

        if recursive and self._derivs:
            for key, deriv in self._derivs.items():
                result.insert_deriv(key, deriv.to_pair(axes=(j0, j1), recursive=False))

        return result

    @staticmethod
    def from_scalars(*args, recursive=True, readonly=False):
        """Construct a Vector by combining scalar components.

        Parameters:
            *args: Scalar objects defining the vector's components. They need not have the
                same shape, but it must be possible to cast them to the same shape. A
                value of None is converted to a zero-valued Scalar that matches the
                denominator shape of the other arguments.

            recursive (bool, optional): True to include all the derivatives. The returned
                object will have derivatives representing the union of all the derivatives
                found among the arguments.

            readonly (bool, optional): True to return a read-only object; False to return
                something potentially writable.

        Returns:
            Vector: A vector constructed from the provided scalar components.
        """

        return Qube.from_scalars(*args, classes=[Vector], recursive=recursive,
                                 readonly=readonly)

    def as_index(self, masked=None):
        """Convert this object to a form suitable for indexing a NumPy array.

        The returned object is a tuple of NumPy arrays, each containing indices along the
        corresponding axis of the array being indexed.

        Parameters:
            masked (scalar, list, tuple, or array, optional): The index or indices to
                insert in place of masked items. If None and the object contains masked
                elements, the array will be flattened and masked elements will be skipped
                over.

        Returns:
            tuple: A tuple of NumPy arrays suitable for indexing.
        """

        (index, mask) = self.as_index_and_mask((masked is None), masked)
        return index

    def as_index_and_mask(self, purge=False, masked=None):
        """Convert this object to a form suitable for indexing and masking an array.

        Parameters:
            purge (bool, optional): True to eliminate masked elements from the index;
                False to retain them but leave them masked.
            masked (scalar, optional): The index value to insert in place of any masked
                item. This may be needed because each value in the returned index array
                must be an integer and in range. If None, masked values in the index will
                retain their unmasked values when the index is applied.

        Returns:
            tuple: A tuple containing (index, mask), where index is suitable for
            indexing a NumPy ndarray and mask indicates which values are masked.

        Raises:
            TypeError: If this object contains floating-point values.
            ValueError: If this object has a unit or a denominator.
        """

        if self.is_float():
            raise TypeError('floating-point indexing is not permitted')

        self._require_unitless('as_index_and_mask()')
        self._disallow_denom('as_index_and_mask()')

        # If nothing is masked, this is easy
        if not np.any(self._mask):
            return (tuple(np.rollaxis(self._values.astype(np.intp), -1, 0)), False)

        # If purging...
        if purge:
            # If all masked...
            if Qube.is_one_true(self._mask):
                return ((), False)

            # If partially masked...
            new_values = self._values[self.antimask]
            return (tuple(np.rollaxis(new_values.astype(np.intp), -1, 0)), False)

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

        return (tuple(np.rollaxis(new_values, -1, 0)), self._mask)

    def int(self, top=None, remask=False, clip=False, inclusive=True, shift=None):
        """Return an integer (floor) version of this Vector.

        If this object already contains integers, it is returned as is. Otherwise, a copy
        is returned with values converted to np.intp. Derivatives are always removed and
        units are disallowed.

        Class Scalar has a similar method :meth:`Scalar.int`.

        Parameters:
            top (tuple, optional): Tuple of maximum integer values for each component,
                equivalent to the array shape.
            remask (bool, optional): If True, values less than zero or greater than the
                specified top values (if provided) are masked.
            clip (bool or tuple of bool, optional): If True, values less than zero or
                greater than the specified top values are clipped. Use a tuple of booleans
                to handle the axes differently.
            inclusive (bool or tuple of bool, optional): True to leave the top limits
                unmasked; False to mask them. Use a tuple of booleans to handle the axes
                differently.
            shift (bool or tuple of bool, optional): True to shift any occurrences of the
                top limit down by one; False to leave them unchanged. Use a tuple of
                booleans to handle the axes differently. Default is None, which sets shift
                to match the value of inclusive.

        Returns:
            Vector: An integer version of this Vector.

        Raises:
            ValueError: If this object has a unit or a denominator.
        """

        def _as_tuple(item, name):
            # Quick internal method to make sure top, inclusive and shift are tuples or
            # lists of the correct length.
            if isinstance(item, (list, tuple)):
                if len(item) != self._numer[0]:
                    raise ValueError(f'{type(self).__name__}.int() {name} does not match '
                                     f'item shape {self._numer}: ({len(item)},)')
            else:
                item = len(top) * (item,)
            return item

        self._require_unitless('int()')
        self._disallow_denom('int()')

        if top is None:
            # If `top` is None, we only care about negatives and only `remask` and `clip`
            # matter.
            neg_mask = self._values < 0
            if not np.any(neg_mask):
                return self.wod.as_int()

            if self.is_int() and not clip:      # avoid a copy if we can
                obj = self.clone(recursive=False)
            else:
                obj = self.as_int(copy=True)
                if clip:
                    obj._values[neg_mask] = 0

            if remask:
                axes = tuple(range(-self._rank, 0))
                new_mask = Qube.or_(self._mask, np.any(neg_mask, axis=axes))
                obj._set_mask(new_mask)

            return obj

        # Handle `top`
        top = _as_tuple(top, 'top')
        clip = _as_tuple(clip, 'clip')
        inclusive = _as_tuple(inclusive, 'inclusive')
        if shift is None:
            shift = inclusive
        else:
            shift = _as_tuple(shift, 'shift')

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

        # For each axis...
        for k in range(self._item[-1]):
            if shift[k] and not clip[k]:    # shift is unneeded if clip is True
                top_value = (self._values[..., k] == top[k])
                if self._shape:
                    values[top_value, k] -= 1
                elif top_value:
                    values[k] -= 1

            if remask:
                is_outside = Scalar.is_outside(self._values[..., k], 0, top[k],
                                               inclusive[k])

            if clip[k]:
                values[..., k] = np.clip(values[..., k], 0, top[k] - 1)

            if remask:
                mask |= is_outside

        result = Qube.__new__(type(self))
        result.__init__(values, mask, example=self)
        return result

    def as_column(self, recursive=True):
        """Convert the Vector to an Nx1 column matrix.

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Matrix: An Nx1 matrix representation of this Vector.
        """

        return self.reshape_numer(self._numer + (1,), Qube._MATRIX_CLASS,
                                  recursive=recursive)

    def as_row(self, *, recursive=True):
        """Convert the Vector to a 1xN row matrix.

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Matrix: A 1xN matrix representation of this Vector.
        """

        return self.reshape_numer((1,) + self._numer, Qube._MATRIX_CLASS,
                                  recursive=recursive)

    def as_diagonal(self, *, recursive=True):
        """Convert the vector to a diagonal matrix.

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Matrix: A diagonal matrix where the diagonal elements are the components
            of this Vector.
        """

        return Qube.as_diagonal(self, 0, Qube._MATRIX_CLASS, recursive=recursive)

    def dot(self, arg, *, recursive=True):
        """Calculate the dot product of this vector and another.

        Parameters:
            arg (Vector or vector-like): The vector to dot with this one.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Scalar: The dot product as a Scalar.
        """

        arg = self.as_this_type(arg, recursive=recursive, coerce=False)
        return Qube.dot(self, arg, 0, 0, classes=[Scalar], recursive=recursive)

    def norm(self, *, recursive=True):
        """Calculate the Euclidean length (magnitude) of this Vector.

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Scalar: The Euclidean norm of this Vector.
        """

        return Qube.norm(self, 0, classes=[Scalar], recursive=recursive)

    def norm_sq(self, *, recursive=True):
        """Calculate the squared length of this Vector.

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Scalar: The squared Euclidean norm of this Vector.
        """

        return Qube.norm_sq(self, 0, classes=[Scalar], recursive=recursive)

    def unit(self, *, recursive=True):
        """Convert this vector to a unit vector (normalized to length 1).

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: A unit vector in the same direction as this Vector.
        """

        if recursive:
            return self / self.norm(recursive=True)
        else:
            return self.wod / self.norm(recursive=False)

    def with_norm(self, norm=1., *, recursive=True):
        """Scale this vector to the specified length.

        Parameters:
            norm (float or Scalar, optional): The desired length.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: A vector in the same direction as this one but with the specified
            length.
        """

        norm = Scalar.as_scalar(norm, recursive=recursive)

        if recursive:
            return self * (norm / self.norm(recursive=True))
        else:
            return self.wod * (norm / self.norm(recursive=False))

    def cross(self, arg, *, recursive=True):
        """Calculate the cross product of this vector with another.

        Parameters:
            arg (Vector or vector-like): The vector to cross with this one.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: The cross product vector. For 3-vectors, returns a Vector; for
            2-vectors, returns a Scalar.
        """

        arg = self.as_this_type(arg, recursive=recursive, coerce=False)

        # type(self) is for 3-vectors, Scalar is for 2-vectors...
        return Qube.cross(self, arg, 0, 0, classes=(type(self), Scalar),
                          recursive=recursive)

    def ucross(self, arg, *, recursive=True):
        """Calculate the unit vector in the direction of the cross product.

        Works only for vectors of length 3.

        Parameters:
            arg (Vector or vector-like): The vector to cross with this one.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: A unit vector in the direction of the cross product.
        """

        return self.cross(arg, recursive=recursive).unit(recursive=recursive)

    def outer(self, arg, *, recursive=True):
        """Return the outer product of two vectors, resulting in a Matrix.

        Parameters:
            arg (Vector or vector-like): The vector to compute the outer product with.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Matrix: The outer product matrix.
        """

        arg = Vector.as_vector(arg, recursive=recursive)
        return Qube.outer(self, arg, Qube._MATRIX_CLASS, recursive=recursive)

    def perp(self, arg, *, recursive=True):
        """Return the component of this vector perpendicular to another.

        Parameters:
            arg (Vector or vector-like): The vector to calculate perpendicular component
                with.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: The component of this vector perpendicular to the argument.
        """

        # Convert arg to a unit vector
        arg = self.as_this_type(arg, recursive=recursive, coerce=False).unit()
        if not recursive:
            self = self.wod

        # Return the component of this vector perpendicular to the arg
        return self - arg * self.dot(arg, recursive=recursive)

    def proj(self, arg, *, recursive=True):
        """Return the component of this vector projected onto another.

        Parameters:
            arg (Vector or vector-like): The vector to project onto.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: The component of this vector projected onto the argument.
        """

        # Convert arg to a unit vector
        arg = self.as_this_type(arg, recursive=recursive, coerce=False).unit()

        # Return the component of this vector projected into the arg
        return arg * self.dot(arg, recursive=recursive)

    def sep(self, arg, *, recursive=True):
        """Calculate the separation angle between this vector and another.

        Works for vectors of length 2 or 3.

        Parameters:
            arg (Vector or vector-like): The vector to calculate the separation angle
                with.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Scalar: The separation angle in radians.
        """

        # Translated from the SPICE source code for VSEP().

        # Convert to unit vectors a and b. These define an isoceles triangle.
        a = self.unit(recursive=recursive)
        b = self.as_this_type(arg, recursive=recursive, coerce=False).unit()

        # This is the separation angle:
        #   angle = 2 * arcsin(|a-b| / 2)
        # However, this formula becomes less accurate for angles near pi. For
        # these angles, we reverse b and calculate the supplementary angle.
        sign = a.dot(b).sign().mask_where_eq(0, 1, remask=False)
        b = b * sign

        arg = 0.5 * (a - b).norm()
        angle = 2. * sign * arg.arcsin() + (sign < 0.) * np.pi

        return angle

    def cross_product_as_matrix(self, *, recursive=True):
        """Convert to a Matrix whose multiply equals a cross product with this vector.

        This method creates a 3×3 antisymmetric matrix that, when multiplied with another
        vector, produces the same result as the cross product of this vector with that
        vector.

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Matrix: A 3×3 matrix that represents the cross product operation.

        Raises:
            ValueError: If this Vector doesn't have exactly 3 components or if it
                has denominators.
        """

        if self._numer != (3,):
            raise ValueError(f'{type(self).__name__}.cross_product_as_matrix() requires '
                             'item shape (3,)')

        self._disallow_denom('cross_product_as_matrix()')

        # Roll the numerator axis to the end if necessary
        if self._drank == 0:
            old_values = self._values
        else:
            old_values = np.rollaxis(self._values, -self._drank - 1,
                                     len(self._values._shape))

        # Fill in the matrix elements
        new_values = np.zeros(self._shape + self._denom + (3, 3),
                              dtype=self._values.dtype)
        new_values[..., 0, 1] = -old_values[..., 2]
        new_values[..., 0, 2] =  old_values[..., 1]
        new_values[..., 1, 2] = -old_values[..., 0]
        new_values[..., 1, 0] =  old_values[..., 2]
        new_values[..., 2, 0] = -old_values[..., 1]
        new_values[..., 2, 1] =  old_values[..., 0]

        # Roll the denominator axes back to the end
        for i in range(self._drank):
            new_values = np.rollaxis(new_values, -3, len(new_values._shape))

        obj = Qube._MATRIX_CLASS(new_values, self._mask, derivs={}, example=self)

        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.cross_product_as_matrix(recursive=False))

        return obj

    def element_mul(self, arg, *, recursive=True):
        """Perform element-by-element multiplication of two vectors.

        Parameters:
            arg (Vector or vector-like): The vector to multiply element-wise.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: The element-wise product of this vector and the argument.

        Raises:
            ValueError: If the numerator shapes are incompatible or if both this
                vector and the argument have denominators.
        """

        # Convert to this class if necessary
        original_arg = arg
        arg = self.as_this_type(arg, recursive=recursive, coerce=False)

        # If it had no unit originally, it should not have a unit now
        if not isinstance(original_arg, Qube):
            arg = arg.without_unit()

        # Validate
        if arg._numer != self._numer:
            Qube._raise_incompatible_numers('element_mul()', self, arg)

        if self._drank > 0 and arg._drank > 0:
            Qube._raise_dual_denoms('element_mul()', self, arg)

        # Reshape value arrays as needed
        if arg._drank:
            self_values = self._values.reshape(self._values.shape + arg._drank * (1,))
        else:
            self_values = self._values

        if self._drank:
            arg_values = arg._values.reshape(arg._values.shape + self._drank * (1,))
        else:
            arg_values = arg._values

        # Construct the object
        obj = Qube.__new__(type(self))
        obj.__init__(self_values * arg_values, Qube.or_(self._mask, arg._mask),
                     derivs={},
                     unit=Unit.mul_units(self._unit, arg._unit),
                     drank=self._drank + arg._drank,
                     example=self)

        # Insert derivatives if necessary
        if recursive:
            new_derivs = {}
            for key, self_deriv in self._derivs.items():
                new_derivs[key] = self_deriv.element_mul(arg.wod, recursive=False)

            for key, arg_deriv in arg._derivs.items():
                term = self.wod.element_mul(arg_deriv, recursive=False)
                if key in new_derivs:
                    new_derivs[key] += term
                else:
                    new_derivs[key] = term

            obj.insert_derivs(new_derivs)

        return obj

    def element_div(self, arg, recursive=True):
        """Perform element-by-element division of two vectors.

        Parameters:
            arg (Vector or vector-like): The vector to divide by element-wise.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: The element-wise division of this vector by the argument.

        Raises:
            ValueError: If the numerator shapes are incompatible or if the argument
                has a denominator.
        """

        # Convert to this class if necessary
        if not isinstance(arg, Qube):
            arg = self.as_this_type(arg, recursive=recursive, coerce=False)
            arg = arg.without_unit()

        # Validate
        if arg._numer != self._numer:
            Qube._raise_incompatible_numers('element_div()', self, arg)

        if arg._drank > 0:
            raise ValueError(f'{type(self).__name__}.element_div() operand cannot have a '
                             'denominator')

        # Mask out zeros in divisor
        zero_mask = (arg._values == 0.)
        if np.any(zero_mask):
            divisor = arg._values.copy()
            divisor[zero_mask] = 1.

            # Reduce the zero mask over the item axes
            zero_mask = np.any(zero_mask, axis=tuple(range(-arg._nrank, 0)))
            divisor_mask = Qube.or_(arg._mask, zero_mask)

        else:
            divisor = arg._values
            divisor_mask = arg._mask

        # Re-shape the divisor array if necessary to match the dividend shape
        if self._drank:
            divisor = divisor.reshape(divisor.shape + self._drank * (1,))

        # Construct the ratio object
        obj = Qube.__new__(type(self))
        obj.__init__(self._values / divisor, Qube.or_(self._mask, divisor_mask),
                     drank=self.drank,
                     unit=Unit.div_units(self._unit, arg._unit))

        # Insert the derivatives if necessary
        if recursive:
            new_derivs = {}

            if self._derivs:
                arg_inv = Qube.__new__(type(self))
                arg_inv.__init__(1. / divisor, divisor_mask,
                                 unit=Unit.unit_power(arg._unit, -1))

                for key, self_deriv in self._derivs.items():
                    new_derivs[key] = self_deriv.element_mul(arg_inv)

            if arg._derivs:
                arg_inv_sq = Qube.__new__(type(self))
                arg_inv_sq.__init__(divisor**(-2), divisor_mask,
                                    unit=Unit.unit_power(arg._unit, -1))
                factor = self.wod.element_mul(arg_inv_sq)

                for key, arg_deriv in arg._derivs.items():
                    term = arg_deriv.element_mul(factor)

                    if key in new_derivs:
                        new_derivs[key] -= term
                    else:
                        new_derivs[key] = -term

            obj.insert_derivs(new_derivs)

        return obj

    def vector_scale(self, factor, recursive=True):
        """Stretch this Vector along a direction defined by a scaling vector.

        Components of the vector perpendicular to the scaling vector are unchanged. The
        scaling amount is determined by the magnitude of the scaling vector.

        Parameters:
            factor (Vector): A Vector defining the direction and magnitude of the scaling.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: A copy of this Vector scaled according to the scaling vector.
        """

        projected = self.proj(factor, recursive=recursive)

        if recursive:
            return self + (projected.norm() - 1) * projected
        else:
            return self.wod + (projected.norm() - 1) * projected

    def vector_unscale(self, factor, recursive=True):
        """Un-stretch this Vector along a direction defined by a scaling vector.

        Components of the vector perpendicular to the scaling vector are unchanged.
        The un-scaling amount is determined by the magnitude of the scaling vector.

        Parameters:
            factor (Vector): A Vector defining the direction and magnitude of the scaling.
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Vector: A copy of this Vector un-scaled according to the scaling vector.
        """

        return self.vector_scale(factor / factor.norm_sq(recursive=recursive),
                                 recursive=recursive)

    @classmethod
    def combos(cls, *args):
        """Create a vector with every combination of components of given scalars.

        Masks are also combined in the analogous manner. Units and derivatives are
        ignored.

        Parameters:
            *args: Scalar objects to combine.

        Returns:
            Vector: A vector with shape defined by concatenating the shapes of all the
            arguments.

        Raises:
            ValueError: If any scalar input has a denominator.
        """

        scalars = []
        newshape = []
        dtype = np.int_
        for arg in args:
            scalar = Scalar.as_scalar(arg)
            if scalar._drank:
                raise ValueError(f'{cls}.combos() does not support denominators')

            scalars.append(scalar)
            newshape += list(scalar._shape)
            if scalar.is_float():
                dtype = np.float64

        newshape = tuple(newshape)
        newrank = len(newshape)
        data = np.empty(newshape + (len(args),), dtype=dtype)
        mask = np.zeros(newshape, dtype='bool')

        before = 0
        after = newrank
        for i, scalar in enumerate(scalars):
            scalar = scalar.reshape(before * (1,) + scalar._shape
                                    + (after - scalar._ndims) * (1,))
            data[..., i] = scalar._values
            mask |= scalar._mask

            before += scalar._ndims
            after -= scalar._ndims

        if not np.any(mask):
            mask = False

        return cls(data, mask)

    def mask_where_component_le(self, axis, limit, replace=None, remask=True):
        """Return a copy with masked values where a component is <= a limit.

        Creates a copy of this object where values of a specified component that
        are less than or equal to a limit value are masked.

        Parameters:
            axis (int): The index of the component to use for comparison.
            limit (scalar or Scalar): The limiting value or a Scalar of limiting values.
            replace (scalar or array, optional): A single replacement value or an array
                of replacement values, inserted at every masked location. Use None to
                leave values unchanged.
            remask (bool, optional): True to include the new mask in the object's mask;
                False to replace the values but leave them unmasked.

        Returns:
            Vector: A copy with masked or replaced values where the component is less than
            or equal to the limit. If no items need to be masked, this object is returned
            unchanged.
        """

        scalar = self.to_scalar(axis)
        return self.mask_where(scalar <= limit, replace=replace, remask=remask)

    def mask_where_component_ge(self, axis, limit, replace=None, remask=True):
        """Return a copy with masked values where a component is >= a limit.

        Creates a copy of this object where values of a specified component that
        are greater than or equal to a limit value are masked.

        Parameters:
            axis (int): The index of the component to use for comparison.
            limit (scalar or Scalar): The limiting value or a Scalar of limiting values.
            replace (scalar or array, optional): A single replacement value or an array
                of replacement values, inserted at every masked location. Use None to
                to leave values unchanged.
            remask (bool, optional): True to include the new mask in the object's mask;
                False to replace the values but leave them unmasked.

        Returns:
            Vector: A copy with masked or replaced values where the component is greater
            than or equal to the limit. If no items need to be masked, this object is
            returned unchanged.
        """

        scalar = self.to_scalar(axis)
        return self.mask_where(scalar >= limit, replace=replace, remask=remask)

    def mask_where_component_lt(self, axis, limit, replace=None, remask=True):
        """Return a copy with masked values where a component is < a limit.

        Creates a copy of this object where values of a specified component that
        are less than a limit value are masked.

        Parameters:
            axis (int): The index of the component to use for comparison.
            limit (scalar or Scalar): The limiting value or a Scalar of limiting values.
            replace (scalar or array, optional): A single replacement value or an array
                of replacement values, inserted at every masked location. Use None to
                leave values unchanged.
            remask (bool, optional): True to include the new mask in the object's mask;
                False to replace the values but leave them unmasked.

        Returns:
            Vector: A copy with masked or replaced values where the component is less than
            the limit. If no items need to be masked, this object is returned unchanged.
        """

        scalar = self.to_scalar(axis)
        return self.mask_where(scalar < limit, replace=replace, remask=remask)

    def mask_where_component_gt(self, axis, limit, replace=None, remask=True):
        """Return a copy with masked values where a component is > a limit.

        Creates a copy of this object where values of a specified component that
        are greater than a limit value are masked.

        Parameters:
            axis (int): The index of the component to use for comparison.
            limit (scalar or Scalar): The limiting value or a Scalar of limiting values.
            replace (scalar or array, optional): A single replacement value or an array
                of replacement values, inserted at every masked location. Use None to
                leave values unchanged.
            remask (bool, optional): True to include the new mask in the object's mask;
                False to replace the values but leave them unmasked.

        Returns:
            Vector: A copy with masked or replaced values where the component is greater
            than the limit. If no items need to be masked, this object is returned
            unchanged.
        """

        scalar = self.to_scalar(axis)
        return self.mask_where(scalar > limit, replace=replace, remask=remask)

    def clip_component(self, axis, lower, upper, remask=False):
        """Return a copy with component values clipped to specified range.

        Creates a copy of this object where values of a specified component that are
        outside a given range are shifted to the closest in-range value.

        Parameters:
            axis (int): The index of the component to use for comparison.
            lower (scalar or Scalar): The lower limit for clipping; None to ignore. This
                can be a single scalar or a Scalar object of the same shape as the object.
            upper (scalar or Scalar): The upper limit for clipping; None to ignore. This
                can be a single scalar or a Scalar object of the same shape as the object.
            remask (bool, optional): True to mask the clipped values in the object's mask;
                False to replace the values but leave them unmasked.

        Returns:
            Vector: A copy with clipped component values. If no items need to be clipped,
            this object is returned unchanged.

        Raises:
            ValueError: If this Vector has denominators.
        """

        self._disallow_denom('clip_component()')

        vector = self.copy()
        mask = vector._mask
        compt = vector.to_scalar(axis)      # shares memory with vector

        if lower is not None:
            lower = Scalar.as_scalar(lower)
            clipping_mask = (compt._values < lower._values) & lower.antimask
            if np.shape(lower._values):
                compt._values[clipping_mask] = lower._values[clipping_mask]
            elif vector._shape:
                compt._values[clipping_mask] = lower._values
            elif clipping_mask:
                vector._values[axis] = lower._values

            if remask:
                mask = Qube.or_(mask, clipping_mask)

        if upper is not None:
            upper = Scalar.as_scalar(upper)
            clipping_mask = (compt._values > upper._values) & upper.antimask
            if np.shape(upper._values):
                compt._values[clipping_mask] = upper._values[clipping_mask]
            elif vector._shape:
                compt._values[clipping_mask] = upper._values
            elif clipping_mask:
                vector._values[axis] = upper

            if remask:
                mask = Qube.or_(mask, clipping_mask)

        if remask and np.any(mask):
            vector._set_mask(mask)

        return vector

    ############################################################################
    # Overrides of superclass operators
    ############################################################################

    def __abs__(self, recursive=True):
        """Return the Euclidean norm of this Vector.

        Parameters:
            recursive (bool, optional): If True, include derivatives in the result.

        Returns:
            Scalar: The Euclidean norm (magnitude) of the Vector.
        """

        return self.norm(recursive=recursive)

    def identity(self):
        """Raise an error as identity is not supported for Vectors.

        Raises:
            ValueError: Always, as identity operation is not supported for Vectors.
        """

        Qube._raise_unsupported_op('identity()', self)

    def reciprocal(self, nozeros=False):
        """Return the reciprocal of this Vector as a Jacobian..

        This Vector must be a Jacobian, i.e., the derivative of one Vector with respect to
        another. The reciprocal is therefore the matrix inverse, the derivative of the
        second vector with respect to the first.

        This method overrides :meth:`~extensions.math_ops.reciprocal` for the base class.

        Parameters:
            nozeros (bool, optional): False to mask out any matrices with zero-valued
                determinants. Set to True only if you know in advance that all
                determinants are nonzero.

        Raises:
            ValueError: If the two Vectors do not have the same dimension (meaning the
                matrix in not square).
            ValueError: If `nozeros` is True but a determinant of zero is encountered.
        """

        if self._drank != 1:
            raise TypeError(f'{type(self).__name__}.reciprocal() is not supported '
                            'unless it represents a Jacobian')

        matrix = self.join_items(classes=[Qube._MATRIX_CLASS])
        inverse = matrix.inverse(nozeros=nozeros, recursive=False)
        return inverse.split_items(1, classes=[type(self)])

##########################################################################################
# A set of useful class constants
##########################################################################################

Vector.ZERO3   = Vector((0., 0., 0.)).as_readonly()
Vector.XAXIS3  = Vector((1., 0., 0.)).as_readonly()
Vector.YAXIS3  = Vector((0., 1., 0.)).as_readonly()
Vector.ZAXIS3  = Vector((0., 0., 1.)).as_readonly()
Vector.MASKED3 = Vector((1, 1, 1), True).as_readonly()

Vector.ZERO2   = Vector((0., 0.)).as_readonly()
Vector.XAXIS2  = Vector((1., 0.)).as_readonly()
Vector.YAXIS2  = Vector((0., 1.)).as_readonly()
Vector.MASKED2 = Vector((1, 1), True).as_readonly()

##########################################################################################
# Once defined, register with Qube class
##########################################################################################

Qube._VECTOR_CLASS = Vector

##########################################################################################
