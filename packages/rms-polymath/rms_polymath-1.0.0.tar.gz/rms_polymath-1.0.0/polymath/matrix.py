##########################################################################################
# polymath/matrix.py: Matrix subclass ofse PolyMath base class
##########################################################################################

from __future__ import division, print_function
import numpy as np
import warnings

from polymath.qube    import Qube
from polymath.scalar  import Scalar
from polymath.boolean import Boolean
from polymath.vector  import Vector
from polymath.vector3 import Vector3
from polymath.unit    import Unit


class Matrix(Qube):
    """A Qube of arbitrary 2-D matrices.

    This class represents arbitrary 2D matrices in the PolyMath framework and provides
    operations for matrix arithmetic, transposition, and inversion.
    """

    _NRANK = 2          # The number of numerator axes.
    _NUMER = None       # Shape of the numerator.
    _FLOATS_OK = True   # True to allow floating-point numbers.
    _INTS_OK = False    # True to allow integers.
    _BOOLS_OK = False   # True to allow booleans.
    _UNITS_OK = True    # True to allow units; False to disallow them.
    _DERIVS_OK = True   # True to allow derivatives and denominators; False to disallow.

    _DEBUG = False      # Set to True for some debugging tasks
    _DELTA = np.finfo(float).eps * 3     # Cutoff used in unary()

    @staticmethod
    def as_matrix(arg, *, recursive=True):
        """Convert the argument to a Matrix if possible.

        Parameters:
            arg: The object to convert to a Matrix.
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Matrix: The argument converted to a Matrix.
        """

        if type(arg) is Matrix:
            return arg if recursive else arg.wod

        if isinstance(arg, Qube):

            # Convert a Vector with drank=1 to a Matrix
            if isinstance(arg, Vector) and arg._drank == 1:
                return arg.join_items([Matrix])

            arg = Matrix(arg._values, arg._mask, example=arg)
            return arg if recursive else arg.wod

        return Matrix(arg)

    def row_vector(self, row, *, recursive=True, classes=(Vector3, Vector)):
        """The selected row of a Matrix as a Vector.

        If the Matrix is M x N, then this will return a Vector of length N. By default, if
        N == 3, it will return a Vector3 object instead.

        Parameters:
            row: Index of the row to return.
            recursive (bool, optional): True to return corresponding vectors of
                derivatives.
            classes (tuple, optional): A list of classes; an instance of the first
                suitable class is returned.

        Returns:
            Vector or Vector3: The selected row as a vector.
        """

        return self.extract_numer(0, row, recursive=recursive, classes=classes)

    def row_vectors(self, *, recursive=True, classes=(Vector3, Vector)):
        """A tuple of Vector objects, one for each row of this Matrix.

        If the Matrix is M x N, then this will return M Vectors of length N. By default,
        if N == 3, it will return Vector3 objects instead.

        Parameters:
            recursive (bool, optional): True to return corresponding vectors of
                derivatives.
            classes (tuple, optional): A list of classes; instances of the first
                suitable class are returned.

        Returns:
            tuple: A tuple of Vector objects, one for each row.
        """

        vectors = []
        for row in range(self._numer[0]):
            vectors.append(self.extract_numer(0, row, recursive=recursive,
                                              classes=classes))

        return tuple(vectors)

    def column_vector(self, column, *, recursive=True, classes=(Vector3, Vector)):
        """The selected column of a Matrix as a Vector.

        If the Matrix is M x N, then this will return a Vector of length M. By default, if
        M == 3, it will return a Vector3 object instead.

        Parameters:
            column: Index of the column to return.
            recursive (bool, optional): True to return corresponding vectors of
                derivatives.
            classes (tuple, optional): A list of classes; an instance of the first
                suitable class is returned.

        Returns:
            Vector or Vector3: The selected column as a vector.
        """

        return self.extract_numer(1, column, recursive=recursive, classes=classes)

    def column_vectors(self, recursive=True, classes=(Vector3, Vector)):
        """A tuple of Vector objects, one for each column of this Matrix.

        If the Matrix is M x N, then this will return N Vectors of length M. By default,
        if M == 3, it will return Vector3 objects instead.

        Parameters:
            recursive (bool, optional): True to return corresponding vectors of
                derivatives.
            classes (tuple, optional): A list of classes; instances of the first suitable
                class are returned.

        Returns:
            tuple: A tuple of Vector objects, one for each column.
        """

        vectors = []
        for col in range(self._numer[1]):
            vectors.append(self.extract_numer(1, col, recursive=recursive,
                                              classes=classes))

        return tuple(vectors)

    def to_vector(self, axis, indx, *, recursive=True, classes=[]):
        """One of the components of a Matrix as a Vector.

        Parameters:
            axis: Axis index from which to extract vector.
            indx: Index of the vector along this axis.
            classes (list, optional): A list of the Vector subclasses to return. The first
                valid one will be used.
            recursive (bool, optional): True to extract the derivatives as well.

        Returns:
            Vector: One component of the Matrix as a Vector.
        """

        return self.extract_numer(axis, indx, list(classes) + [Vector],
                                  recursive=recursive)

    def to_scalar(self, /, indx0, indx1, *, recursive=True):
        """One of the elements of a Matrix as a Scalar.

        Parameters:
            indx0 (int): Index along the first matrix axis.
            indx1 (int): Index along the second matrix axis.
            recursive (bool, optional): True to extract the derivatives as well.

        Returns:
            Scalar: One element of the Matrix as a Scalar.
        """

        vector = self.extract_numer(0, indx0, Vector, recursive=recursive)
        return vector.extract_numer(0, indx1, Scalar, recursive=recursive)

    @staticmethod
    def from_scalars(*args, recursive=True, shape=None, classes=[]):
        """Construct a Matrix or subclass by combining scalars.

        Parameters:
            *args: Any number of Scalars or arguments that can be casted to Scalars. They
                need not have the same shape, but it must be possible to broadcast them to
                the same shape. A value of None is converted to a zero-valued Scalar that
                matches the denominator shape of the other arguments.
            recursive (bool, optional): True to include all the derivatives. The returned
                object will have derivatives representing the union of all the derivatives
                found amongst the scalars.
            shape (tuple, optional): The Matrix's item shape. If not specified but the
                number of Scalars is a perfect square, a square matrix is returned.
            classes (list, optional): An arbitrary list defining the preferred class of
                the returned object. The first suitable class in the list will be used.
                Default is [Matrix].

        Returns:
            Matrix: A Matrix constructed from the given scalars.

        Raises:
            TypeError: If the input would result in an int matrix, which is not allowed.
            ValueError: If the number of Scalars does not match the specified shape.
        """

        # Create the Vector object
        vector = Vector.from_scalars(*args, recursive=recursive)

        # Int matrices are disallowed
        if vector.is_int():
            raise TypeError('Matrix.from_scalars() requires objects with data type float')

        # Determine the shape
        if shape is not None:
            if len(shape) != 2:
                raise ValueError(f'invalid Matrix item shape: {shape}')

            size = shape[0] * shape[1]
            if len(args) != shape:
                raise ValueError('incorrect number of Scalars for Matrix.from_scalars() '
                                 f'with shape {shape}')
            shape = tuple(shape)

        else:
            dim = int(np.sqrt(len(args)))
            size = dim * dim
            if size != len(args):
                raise ValueError('incorrect number of Scalars for Matrix.from_scalars() '
                                 'with square shape')
            shape = (dim, dim)

        return vector.reshape_numer(shape, list(classes) + [Matrix], recursive=True)

    def is_diagonal(self, *, delta=0.):
        """A Boolean equal to True where the matrix is diagonal.

        Masked matrices return True.

        Parameters:
            delta (float, optional): The fractional limit on what can be treated as
                equivalent to zero in the off-diagonal terms. It is scaled by the RMS
                value of all the elements in the matrix.

        Returns:
            Boolean: True where the matrix is diagonal.

        Raises:
            ValueError: If the matrix is not square or has denominators.
        """

        size = self.item[0]
        if size != self.item[1]:
            raise ValueError(f'{type(self).__name__}.is_diagonal() requires a square '
                             f'matrix; shape is {self._numer}')

        if self._drank:
            raise ValueError(f'{type(self).__name__}.is_diagonal() does not support '
                             'denominators')

        # If necessary, calculate the matrix RMS
        if delta != 0.:
            # rms, scaled to be unity for an identity matrix
            rms = (np.sqrt(np.sum(np.sum(self._values**2, axis=-1), axis=-1)) / size)

        # Flatten the value array
        values = self._values.reshape(self._shape + (size * size,))

        # Slice away the last element
        sliced = values[..., :-1]

        # Reshape so that only elemenents in the first column can be nonzero
        reshaped = sliced.reshape(self._shape + (size-1, size + 1))

        # Slice away the first column
        sliced = reshaped[..., 1:]

        # Convert back to 1-D items
        reshaped = sliced.reshape(self._shape + ((size - 1) * size,))

        # Compare
        if delta == 0:
            compare = (reshaped == 0.)
        else:
            compare = (np.abs(reshaped) <= (delta * rms)[..., np.newaxis])

        compare = np.all(compare, axis=-1)

        # Apply mask
        if np.shape(compare) == ():
            if self._mask:
                compare = True
        elif np.shape(self._mask) == ():
            if self._mask:
                compare.fill(True)
        else:
            compare[self._mask] = True

        return Boolean(compare)

    def transpose(self, *, recursive=True):
        """The transpose of this matrix.

        Parameters:
            recursive (bool, optional): True to include the transposed derivatives; False
                to return an object without derivatives.

        Returns:
            Matrix: Transpose of this matrix.
        """

        return self.transpose_numer(0, 1, recursive=recursive)

    @property
    def T(self):
        """The transpose of this matrix.

        Returns:
            Matrix: Transpose of this matrix with derivatives included.
        """

        return self.transpose_numer(0, 1, recursive=True)

    def inverse(self, *, recursive=True, nozeros=False):
        """The inverse of this matrix.

        The returned object will have the same subclass as this object. Matrices with
        determinant equal to zero are masked.

        Parameters:
            recursive (bool, optional): True to include the derivatives of the inverse.
            nozeros (bool, optional): False to mask out any matrices with zero-valued
                determinants. Set to True only if you know in advance that all
                determinants are nonzero.

        Returns:
            Matrix: Inverse of this matrix. It will have the same subclass as this object.
                Matrices with a determinant equal to zero will be masked.

        Raises:
            ValueError: If the matrix is not square or has denominators.
            ValueError: If `nozeros` is True but a determinant of zero is encountered.
        """

        # Validate array
        if self._numer[0] != self._numer[1]:
            raise ValueError(f'{type(self).__name__}.inverse() requires a square matrix; '
                             f'shape is {self._numer}')

        if self._drank:
            raise ValueError(f'{type(self).__name__}.inverse() does not support '
                             'denominators')

        # Check determinant if necessary
        new_mask = self._mask
        if not nozeros:
            det = np.linalg.det(self._values)

            # Mask out un-invertible matrices and replace with identify matrices
            mask = (det == 0.)
            if np.any(mask):
                self._values[mask] = np.diag(np.ones(self._numer[0]))
                new_mask = Qube.or_(self._mask, mask)

        # Invert the array
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                new_values = np.linalg.inv(self._values)
            except (RuntimeWarning, np.linalg.LinAlgError):
                raise ValueError(f'{type(self).__name__}.inverse() input is singular')

        # Construct the result
        obj = Matrix(new_values, new_mask, unit=Unit.unit_power(self._unit, -1))

        # Fill in derivatives
        if recursive and self._derivs:
            new_derivs = {}

            # -M^-1 * dM/dt * M^-1
            for key, deriv in self._derivs.items():
                new_derivs[key] = -obj * deriv * obj

            obj.insert_derivs(new_derivs)

        return obj

    def unitary(self):
        """The nearest unitary matrix as a Matrix3.

        Uses the algorithm from
        https://wikipedia.org/wiki/Orthogonal_matrix#Nearest_orthogonal_matrix

        Returns:
            Matrix3: The nearest unitary (orthogonal) matrix.

        Raises:
            ValueError: If the matrix has denominators or is not 3x3.
        """

        # Algorithm from
        #    https://wikipedia.org/wiki/Orthogonal_matrix#Nearest_orthogonal_matrix
        MAX_ITERS = 10      # Adequate iterations unless convergence is failing

        m0 = self.wod
        if m0._drank:
            raise ValueError(f'{type(self).__name__}.unitary() does not support '
                             'denominators')

        if m0._numer != (3, 3):
            raise ValueError(f'{type(self).__name__}.unitary() requires 3x3 matrix as '
                             'input')

        # Iterate...
        m0 = Matrix(m0)     # can't do certain math operations on Matrix3 subclass
        next_m = m0
        for i in range(MAX_ITERS):
            m = next_m
            next_m = 2. * m0 * (m.inverse() * m0 + m0.T * m).inverse()
            rms = Qube.rms(next_m * next_m.T - Matrix.IDENTITY3)

            if Matrix._DEBUG:
                sorted = np.sort(rms._values.ravel())
                print(i, sorted[-4:])

            if rms.max() <= Matrix._DELTA:
                break

        new_mask = (rms._values > Matrix._DELTA)
        if not np.any(new_mask):
            new_mask = self._mask
        elif self._mask is not False:
            new_mask |= self._mask

        return Qube._MATRIX3_CLASS(next_m._values, new_mask)

# Algorithm has been validated but code has not been tested
#     def solve(self, values, recursive=True):
#         """Solve for the Vector X that satisfies A X = B, for this square matrix
#         A and a Vector B of results."""
#
#         b = Vector.as_vector(values, recursive=True)
#
#         size = self.item[0]
#         if size != self.item[1]:
#             raise ValueError('solver requires a square Matrix')
#
#         if self._drank:
#             raise ValueError('solver does not suppart a Matrix with a ' +
#                              'denominator')
#
#         if size != b.item[0]:
#             raise ValueError('Matrix and Vector have incompatible sizes')
#
#         # Easy cases: X = A-1 B
#         if size <= 3:
#             if recursive:
#                 return self.inverse(True) * b
#             else:
#                 return self.inverse(False) * b.wod
#
#         new_shape = Qube.broadcasted_shape(self._shape, b._shape)
#
#         # Algorithm is simpler with matrix indices rolled to front
#         # Also, Vector b's elements are placed after the elements of Matrix a
#
#         ab_vals = np.empty((size,size+1) + new_shape)
#         rolled = np.rollaxis(self._values, -1, 0)
#         rolled = np.rollaxis(rolled, -1, 0)
#
#         ab_vals[:,:-1] = rolled
#         ab_vals[:,-1] = b._values
#
#         for k in range(size-1):
#             # Zero out the leading coefficients from each row at each iteration
#             ab_saved = ab_vals[k+1:,k:k+1]
#             ab_vals[k+1:,k:] *= ab_vals[k,k:k+1]
#             ab_vals[k+1:,k:] -= ab_vals[k,k:] * ab_saved
#
#         # Now work backward solving for values, replacing Vector b
#         for k in range(size,0):
#             ab_vals[ k,-1] /= ab_vals[k,k]
#             ab_vals[:k,-1] -= ab_vals[k,-1] * ab_vals[:k,k]
#
#         ab_vals[0,-1] /= ab_vals[0,0]
#
#         x = np.rollaxis(ab_vals[:,-1], 0, len(shape))
#
#         x = Vector(x, self._mask | b._mask, derivs={},
#                       unit=Unit._unit_div(self._unit, b._unit))
#
#         # Deal with derivatives if necessary
#         # A x = B
#         # A dx/dt + dA/dt x = dB/dt
#         # A dx/dt = dB/dt - dA/dt x
#
#         if recursive and (self._derivs or b._derivs):
#             derivs = {}
#             for key in self._derivs:
#                 if key in b._derivs:
#                     values = b._derivs[key] - self._derivs[key] * x
#                 else:
#                     values = -self._derivs[k] * x
#
#             derivs[key] = self.solve(values, recursive=False)
#
#             for key in b._derivs:
#                 if key not in self._derivs:
#                     derivs[key] = self.solve(b._derivs[k], recursive=False)
#
#             self.insert_derivs(derivs)
#
#         return x

    ######################################################################################
    # Overrides of superclass operators
    ######################################################################################

    def __abs__(self):
        """Raise a TypeError; absolute value is not defined for matrices.

        This is an override of :meth:`Qube.__abs__`.
        """

        Qube._raise_unsupported_op('abs()', self)

    def __floordiv__(self, /, arg):
        """Raise a TypeError; floor division is not defined for matrices.

        This is an override of :meth:`Qube.__floordiv__`.
        """

        Qube._raise_unsupported_op('//', self, arg)

    def __rfloordiv__(self, /, arg):
        """Raise a TypeError; floor division is not defined for matrices.

        This is an override of :meth:`Qube.__rfloordiv__`.
        """

        Qube._raise_unsupported_op('//', arg, self)

    def __ifloordiv__(self, /, arg):
        """Raise a TypeError; floor division is not defined for matrices.

        This is an override of :meth:`Qube.__ifloordiv__`.
        """

        Qube._raise_unsupported_op('//=', self, arg)

    def __mod__(self, /, arg):
        """Raise a TypeError; modulo is not defined for matrices.

        This is an override of :meth:`Qube.__mod__`.
        """

        Qube._raise_unsupported_op('%', self, arg)

    def __rmod__(self, /, arg):
        """Raise a TypeError; modulo is not defined for matrices.

        This is an override of :meth:`Qube.__rmod__`.
        """

        Qube._raise_unsupported_op('%', arg, self)

    def __imod__(self, /, arg):
        """Raise a TypeError; modulo is not defined for matrices.

        This is an override of :meth:`Qube.__imod__`.
        """

        Qube._raise_unsupported_op('%=', self, arg)

    def identity(self):
        """An identity matrix of the same size and subclass as this.

        This method overrides :meth:`Qube.identity`.

        Raises:
            ValueError: If the matrix is not square.
        """

        size = self._numer[0]

        if self._numer[1] != size:
            raise ValueError(f'{type(self).__name__}.identity() requires a square '
                             f'matrix; shape is {self._numer}')

        values = np.zeros((size, size))
        for i in range(size):
            values[i, i] = 1.

        obj = Qube.__new__(type(self))
        obj.__init__(values)

        return obj.as_readonly()

    ######################################################################################
    # Overrides of arithmetic operators
    ######################################################################################

    def reciprocal(self, *, recursive=True, nozeros=False):
        """Return an object equivalent to the reciprocal of this object.

        For a Matrix, the reciprocal is the inverse. This overrides
        :meth:`Qube.reciprocal`.

        Parameters:
            recursive (bool, optional): True to return the derivatives of the reciprocal
                too; otherwise, derivatives are removed.
            nozeros (bool, optional): False to mask out any matrices with zero-valued
                determinants. Set to True only if you know in advance that all
                determinants are nonzero.

        Returns:
            Matrix: The matrix inverse.

        Raises:
            ValueError: If the matrix is not square, has denominators, or has a
                determinant of zero.
        """

        return self.inverse(recursive=recursive, nozeros=nozeros)

##########################################################################################
# Useful class constants
##########################################################################################

Matrix.IDENTITY2 = Matrix([[1, 0], [0, 1]]).as_readonly()
Matrix.IDENTITY3 = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).as_readonly()

Matrix.MASKED2 = Matrix([[1, 1], [1, 1]], True).as_readonly()
Matrix.MASKED3 = Matrix([[1, 1, 1], [1, 1, 1], [1, 1, 1]], True).as_readonly()

Matrix.ZERO33 = Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]]).as_readonly()
Matrix.UNIT33 = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).as_readonly()

Matrix.ZERO3_ROW = Matrix([[0, 0, 0]]).as_readonly()
Matrix.XAXIS_ROW = Matrix([[1, 0, 0]]).as_readonly()
Matrix.YAXIS_ROW = Matrix([[0, 1, 0]]).as_readonly()
Matrix.ZAXIS_ROW = Matrix([[0, 0, 1]]).as_readonly()

Matrix.ZERO3_COL = Matrix([[0], [0], [0]]).as_readonly()
Matrix.XAXIS_COL = Matrix([[1], [0], [0]]).as_readonly()
Matrix.YAXIS_COL = Matrix([[0], [1], [0]]).as_readonly()
Matrix.ZAXIS_COL = Matrix([[0], [0], [1]]).as_readonly()

##########################################################################################
# Once defined, register with base class
##########################################################################################

Qube._MATRIX_CLASS = Matrix

##########################################################################################
