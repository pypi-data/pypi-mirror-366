##########################################################################################
# polymath/matrix3.py: Matrix3 subclass of PolyMath Matrix class
##########################################################################################

from __future__ import division
import numpy as np

from polymath.qube    import Qube
from polymath.scalar  import Scalar
from polymath.vector3 import Vector3
from polymath.matrix  import Matrix
from polymath.unit    import Unit


class Matrix3(Matrix):
    """Represent 3x3 rotation matrices in the PolyMath framework.

    This class provides functionality for working with 3x3 rotation matrices, including
    creating matrices from rotations about axes and converting between different
    rotation representations.
    """

    _NRANK = 2          # The number of numerator axes.
    _NUMER = (3, 3)     # Shape of the numerator.
    _FLOATS_OK = True   # True to allow floating-point numbers.
    _INTS_OK = False    # True to allow integers.
    _BOOLS_OK = False   # True to allow booleans.
    _UNITS_OK = False   # True to allow units; False to disallow them.
    _DERIVS_OK = True   # True to allow derivatives and denominators; False to disallow.
    _DEFAULT_VALUE = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])

    @staticmethod
    def as_matrix3(arg, *, recursive=True):
        """Convert the argument to Matrix3. The result is not checked to be unitary.

        Quaternions are converted to matrices.

        Parameters:
            arg: The object to convert to Matrix3.
            recursive (bool, optional): True to include derivatives in the returned
                result.

        Returns:
            Matrix3: The argument converted to a Matrix3.
        """

        if isinstance(arg, Matrix3):
            return arg if recursive else arg.wod

        if isinstance(arg, Qube):
            if isinstance(arg, Qube._QUATERNION_CLASS):
                return arg.to_matrix3(recursive=recursive)

            arg = Matrix3(arg._values, arg._mask, example=arg)
            return arg if recursive else arg.wod

        return Matrix3(arg)

    @staticmethod
    def twovec(vector1, axis1, vector2, axis2, *, recursive=True):
        """A rotation matrix defined by two vectors.

        The returned matrix rotates to a right-handed coordinate frame having vector1
        pointing along a specified axis (axis1=0 for X, 1 for Y, 2 for Z) and vector2
        pointing into the half-plane defined by (axis1, axis2).

        Parameters:
            vector1 (Vector or array-like): The first vector that defines the rotation.
            axis1 (int): The axis to which vector1 should point (0=X, 1=Y, 2=Z).
            vector2 (Vector or array-like): The second vector that defines the rotation.
            axis2 (int): The axis defining the half-plane for vector2 (0=X, 1=Y, 2=Z).
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Matrix3: A rotation matrix determined by the input vectors.

        Raises:
            ValueError: If an input Vector has a denominator, or if any derivatives have
                mismatched denominators.
        """

        # Based on the SPICE source code for TWOVEC()

        # Make shapes and types consistent
        unit1 = Vector3.as_vector3(vector1).unit(recursive=recursive)
        vector2 = Vector3.as_vector3(vector2, recursive=recursive)
        (unit1, vector2) = Qube.broadcast(unit1, vector2)

        # Denominators are disallowed
        if unit1._denom or vector2._denom:
            raise ValueError('Matrix3.twovec() does not support denominators')

        # Define the remaining two columns of the matrix
        axis3 = 3 - axis1 - axis2
        if (3 + axis2 - axis1) % 3 == 1:        # if (0,1), (1,2) or (2,0)
            unit3 = unit1.ucross(vector2, recursive=recursive)
            unit2 = unit3.ucross(unit1, recursive=recursive)
        else:
            unit3 = vector2.ucross(unit1, recursive=recursive)
            unit2 = unit1.ucross(unit3, recursive=recursive)

        # Assemble the values into an array
        array = np.empty(unit1._shape + (3, 3))
        array[..., axis1, :] = unit1._values
        array[..., axis2, :] = unit2._values
        array[..., axis3, :] = unit3._values

        # Construct the result
        result = Matrix3(array, Qube.or_(unit1._mask, vector2._mask))

        # Fill in derivatives if necessary
        if recursive and (unit1._derivs or vector2._derivs):

            # Find all the derivatives and their denominator shapes
            denoms = {}
            for key, deriv in unit1._derivs.items():
                denoms[key] = deriv._denom
            for key, deriv in vector2._derivs.items():
                if key in denoms:
                    if deriv._denom != denoms[key]:
                        raise ValueError(f'derivative "{key}" denominator mismatch in '
                                         f'Matrix3.twovec(): {denoms[key]}, '
                                         f'{deriv._denom}')
                else:
                    denoms[key] = vector2._derivs[key].denom

            derivs = {}
            for key, denom in denoms.items():
                drank = len(denom)
                deriv = np.zeros(unit1._shape + (3, 3) + denom)

                suffix = (drank + 1) * (slice(None),)
                if key in unit1._derivs:
                    deriv[(Ellipsis, axis1) + suffix] = unit1._derivs[key]._values
                if key in unit2._derivs:
                    deriv[(Ellipsis, axis2) + suffix] = unit2._derivs[key]._values
                if key in unit3._derivs:
                    deriv[(Ellipsis, axis3) + suffix] = unit3._derivs[key]._values

                derivs[key] = Matrix3(deriv, mask=result._mask, drank=drank)

            result.insert_derivs(derivs)

        if unit1.readonly and vector2.readonly:
            result = result.as_readonly()

        return result

    @staticmethod
    def x_rotation(angle, *, recursive=True):
        """A rotation matrix about X-axis.

        The returned matrix rotates a vector counterclockwise about the X-axis by the
        specified angle in radians. The same matrix rotates a coordinate system clockwise
        by the same angle.

        Parameters:
            angle (Scalar, np.ndarray, or float): The rotation angle in radians.
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Matrix3: A rotation matrix about the X-axis.

        Raises:
            ValueError: If the angle has an invalid unit
        """

        angle = Scalar.as_scalar(angle)
        Unit.require_angle(angle._unit)

        cos_angle = np.cos(angle._values)
        sin_angle = np.sin(angle._values)

        values = np.zeros(angle._shape + (3, 3))
        values[..., 1, 1] =  cos_angle
        values[..., 1, 2] =  sin_angle
        values[..., 2, 1] = -sin_angle
        values[..., 2, 2] =  cos_angle
        values[..., 0, 0] =  1.

        obj = Matrix3(values.reshape(angle._shape + (3, 3)))

        if recursive and angle._derivs:
            matrix = np.zeros(angle._shape + (3, 3))
            matrix[..., 1, 1] = -sin_angle
            matrix[..., 1, 2] =  cos_angle
            matrix[..., 2, 1] = -cos_angle
            matrix[..., 2, 2] = -sin_angle

            for key, deriv in angle._derivs.items():
                obj.insert_deriv(key, Matrix(matrix * deriv))

        return obj

    @staticmethod
    def y_rotation(angle, *, recursive=True):
        """A rotation matrix about Y-axis.

        The returned matrix rotates a vector counterclockwise about the Y-axis by the
        specified angle in radians. The same matrix rotates a coordinate system clockwise
        by the same angle.

        Parameters:
            angle (Scalar, array-like, or float: The rotation angle in radians.
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Matrix3: A rotation matrix about the Y-axis.

        Raises:
            ValueError: If the angle has an invalid unit
        """

        angle = Scalar.as_scalar(angle)
        Unit.require_angle(angle._unit)

        cos_angle = np.cos(angle._values)
        sin_angle = np.sin(angle._values)

        values = np.zeros(angle._shape + (3, 3))
        values[..., 0, 0] =  cos_angle
        values[..., 0, 2] =  sin_angle
        values[..., 2, 0] = -sin_angle
        values[..., 2, 2] =  cos_angle
        values[..., 1, 1] =  1.

        obj = Matrix3(values.reshape(angle._shape + (3, 3)))

        if recursive and angle._derivs:
            matrix = np.zeros(angle._shape + (3, 3))
            matrix[..., 0, 0] = -sin_angle
            matrix[..., 0, 2] =  cos_angle
            matrix[..., 2, 0] = -cos_angle
            matrix[..., 2, 2] = -sin_angle

            for key, deriv in angle._derivs.items():
                obj.insert_deriv(key, Matrix(matrix * deriv))

        return obj

    @staticmethod
    def z_rotation(angle, *, recursive=True):
        """A rotation matrix about Z-axis.

        The returned matrix rotates a vector counterclockwise about the Z-axis by the
        specified angle in radians. The same matrix rotates a coordinate system clockwise
        by the same angle.

        Parameters:
            angle: The rotation angle in radians.
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Matrix3: A rotation matrix about the Z-axis.

        Raises:
            ValueError: If the angle has an invalid unit
        """

        angle = Scalar.as_scalar(angle)
        Unit.require_angle(angle._unit)

        cos_angle = np.cos(angle._values)
        sin_angle = np.sin(angle._values)

        values = np.zeros(angle._shape + (3, 3))
        values[..., 0, 0] =  cos_angle
        values[..., 0, 1] = -sin_angle
        values[..., 1, 0] =  sin_angle
        values[..., 1, 1] =  cos_angle
        values[..., 2, 2] =  1.

        obj = Matrix3(values.reshape(angle._shape + (3, 3)))

        if recursive and angle._derivs:
            matrix = np.zeros(angle._shape + (3, 3))
            matrix[..., 0, 0] = -sin_angle
            matrix[..., 0, 1] = -cos_angle
            matrix[..., 1, 0] =  cos_angle
            matrix[..., 1, 1] = -sin_angle

            for key, deriv in angle._derivs.items():
                obj.insert_deriv(key, Matrix(matrix * deriv))

        return obj

    @staticmethod
    def axis_rotation(angle, axis=2, *, recursive=True):
        """A rotation matrix about one of the three primary axes.

        The returned matrix rotates a vector counterclockwise by the specified angle about
        the specified axis (0 for X, 1 for Y, 2 for Z). The same matrix rotates a
        coordinate system clockwise by the same angle.

        Parameters:
            angle: The rotation angle in radians.
            axis (int, optional): The axis to rotate around (0=X, 1=Y, 2=Z).
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Matrix3: A rotation matrix about the specified axis.
        """

        axis = axis % 3

        if axis == 2:
            return Matrix3.z_rotation(angle, recursive=recursive)

        if axis == 0:
            return Matrix3.x_rotation(angle, recursive=recursive)

        return Matrix3.y_rotation(angle, recursive=recursive)

    @staticmethod
    def pole_rotation(ra, dec):
        """Create a rotation matrix to a frame defined by right ascension and declination.

        The returned matrix rotates coordinates into a frame where the Z-axis is defined
        by (ra, dec) and the X-axis points along the new equatorial plane's ascending node
        on the original equator.

        Parameters:
            ra: The right ascension of the Z-axis in radians.
            dec: The declination of the Z-axis in radians.

        Returns:
            Matrix3: A rotation matrix to the frame defined by (ra,dec).

        Raises:
            ValueError: If ra or dec has an invalid unit.

        Notes:
            Derivatives are not supported.
        """

        ra = Scalar.as_scalar(ra)
        Unit.require_angle(ra._unit)

        cos_ra = np.cos(ra._values)
        sin_ra = np.sin(ra._values)

        dec = Scalar.as_scalar(dec)
        Unit.require_angle(dec._unit)

        cos_dec = np.cos(dec._values)
        sin_dec = np.sin(dec._values)

        values = np.stack([-sin_ra,            cos_ra,           0.,
                           -cos_ra * sin_dec, -sin_ra * sin_dec, cos_dec,
                            cos_ra * cos_dec,  sin_ra * cos_dec, sin_dec],      # noqa
                          axis=-1)
        return Matrix3(values.reshape(values.shape[:-1] + (3, 3)))

    def rotate(self, arg, *, recursive=True):
        """Rotate an object by this Matrix3, returning an instance of the same subclass.

        Parameters:
            arg: The object to rotate.
            recursive (bool, optional): If True, the rotated derivatives are included in
                the object returned.

        Returns:
            Qube: The rotated object of the same type as the input.
        """

        # Rotation of a vector or matrix
        if arg._nrank > 0:
            return Qube.dot(self, arg, -1, 0, classes=[type(arg)], recursive=recursive)

        # Rotation of a scalar leaves it unchanged
        else:
            return arg

    def unrotate(self, arg, *, recursive=True):
        """Rotate an object by the inverse of this Matrix3, returning the same subclass.

        Parameters:
            arg: The object to unrotate.
            recursive (bool, optional): If True, the un-rotated derivatives are included
                in the object returned.

        Returns:
            Qube: The unrotated object of the same type as the input.
        """

        # Rotation of a vector or matrix
        if arg._nrank > 0:
            return Qube.dot(self, arg, -2, 0, classes=[type(arg)], recursive=recursive)

        # Rotation of a scalar leaves it unchanged
        else:
            return arg

    ######################################################################################
    # Overrides of arithmetic operators
    ######################################################################################

    def __neg__(self):
        """Raise a TypeError; "-self" is not permitted for Matrix3 objects.

        This is an override of :meth:`Qube.__neg__`.
        """

        Qube._raise_unsupported_op('-', self)

    def __add__(self, /, arg):
        """Raise a TypeError; "self + arg" is not permitted for Matrix3 objects.

        This is an override of :meth:`Qube.__add__`.
        """

        Qube._raise_unsupported_op('+', self, arg)

    def __radd__(self, /, arg):
        """Raise a TypeError; "arg + self" is not permitted for Matrix3 objects.

        This is an override of :meth:`Qube.__radd__`.
        """

        Qube._raise_unsupported_op('+', self, arg)

    def __iadd__(self, /, arg):
        """Raise a TypeError; "self += arg" is not permitted for Matrix3 objects.

        This is an override of :meth:`Qube.__iadd__`.
        """

        Qube._raise_unsupported_op('+=', self, arg)

    def __sub__(self, /, arg):
        """Raise a TypeError; "self - arg" is not permitted for Matrix3 objects.

        This is an override of :meth:`Qube.__sub__`.
        """

        Qube._raise_unsupported_op('-', self, arg)

    def __rsub__(self, /, arg):
        """Raise a TypeError; "arg - self" is not permitted for Matrix3 objects.

        This is an override of :meth:`Qube.__rsub__`.
        """

        Qube._raise_unsupported_op('-', self, arg)

    def __isub__(self, /, arg):
        """Raise a TypeError; "self -= arg" is not permitted for Matrix3 objects.

        This is an override of :meth:`Qube.__isub__`.
        """

        Qube._raise_unsupported_op('-=', self, arg)

    def __mul__(self, /, arg, *, recursive=True):
        """self * arg, matrix multiplication.

        Matrix3 times Scalar returns the same type of Scalar. This overrides
        :meth:`Qube.__mul__`.

        Parameters:
            arg: The object to multiply with this Matrix3.
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Qube: The result of the multiplication.

        Raises:
            ValueError: If multiplication with the given type is not supported.
        """

        # Convert arg to a Scalar if necessary
        original_arg = arg
        if not isinstance(arg, Qube):
            try:
                arg = Scalar.as_scalar(arg)
            except (ValueError, TypeError):
                Qube._raise_unsupported_op('*', self, original_arg)

        # Rotate a scalar, returning the scalar unchanged except for new derivs
        if arg._nrank == 0:
            return arg.wod if not recursive else arg

        # For every other purpose, use the default multiply
        return Qube.__mul__(self, original_arg)

    def __rmul__(self, /, arg, *, recursive=True):
        """arg * self, matrix multiplication.

        Matrix3 times Scalar returns the same type of Scalar. This overrides
        :meth:`Qube.__rmul__`.

        Parameters:
            arg: The object to multiply with this Matrix3.
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Qube: The result of the multiplication.

        Raises:
            ValueError: If multiplication with the given type is not supported.
        """

        # Attempt a conversion to Matrix3
        original_arg = arg
        try:
            arg = Matrix3.as_matrix3(arg)
        except (ValueError, TypeError):
            Qube._raise_unsupported_op('=', self, original_arg)

        # For every other purpose, use the default multiply
        return Qube.__mul__(arg, self)

    def __imul__(self, /, arg):
        """self * arg, in-place matrix multiplication.

        This overrides :meth:`Qube.__imul__`.

        Parameters:
            arg: The Matrix3 by which to multiply this Matrix3.

        Returns:
            Matrix3: This object, the result of the multiplication.

        Raises:
            ValueError: If arg cannot be converted to a Matrix3 or if this Matrix3 is not
                writeable.
        """

        self.require_writeable()

        # Attempt a conversion to Matrix3
        original_arg = arg
        try:
            arg = Matrix3.as_matrix3(arg)
        except (ValueError, TypeError):
            Qube._raise_unsupported_op('*=', self, original_arg)

        result = Qube.__imul__(self, arg)
        self._set_values(result._values, result._mask, example=self)
        return self

    def reciprocal(self, *, recursive=True, nozeros=False):
        """Return the reciprocal of this Matrix3, which is its transpose.

        Parameters:
            recursive (bool, optional): True to return the derivatives of the reciprocal
                too; otherwise, derivatives are removed.
            nozeros (bool, optional): Ignored for Matrix3.

        Returns:
            Matrix3: The transpose of this matrix.
        """

        return self.transpose(recursive=recursive)

    ######################################################################################
    # Decomposition into rotations
    #
    # From: http://www.lfd.uci.edu/~gohlke/code/transformations.py.html
    #
    # A triple of Euler angles can be applied/interpreted in 24 ways, which can be
    # specified using a 4 character string or encoded 4-tuple:
    #
    #   Axes 4-string: e.g. 'sxyz' or 'ryxy'
    #
    #   - first character : rotations are applied to 's'tatic or 'r'otating
    #     frame
    #   - remaining characters : successive rotation axis 'x', 'y', or 'z'
    #
    #   Axes 4-tuple: e.g. (0, 0, 0, 0) or (1, 1, 1, 1)
    #
    #   - inner axis: code of axis ('x':0, 'y':1, 'z':2) of rightmost matrix.
    #   - parity : even (0) if inner axis 'x' is followed by 'y', 'y' is followed by 'z',
    #     or 'z' is followed by 'x'. Otherwise odd (1).
    #   - repetition : first and last axis are same (1) or different (0).
    #   - frame : rotations are applied to static (0) or rotating (1) frame.
    ######################################################################################

    # axis sequences for Euler angles
    _NEXT_AXIS = [1, 2, 0, 1]

    # map axes strings to/from tuples of inner axis, parity, repetition, frame
    _AXES2TUPLE = {
        'sxyz': (0, 0, 0, 0), 'sxyx': (0, 0, 1, 0), 'sxzy': (0, 1, 0, 0),
        'sxzx': (0, 1, 1, 0), 'syzx': (1, 0, 0, 0), 'syzy': (1, 0, 1, 0),
        'syxz': (1, 1, 0, 0), 'syxy': (1, 1, 1, 0), 'szxy': (2, 0, 0, 0),
        'szxz': (2, 0, 1, 0), 'szyx': (2, 1, 0, 0), 'szyz': (2, 1, 1, 0),
        'rzyx': (0, 0, 0, 1), 'rxyx': (0, 0, 1, 1), 'ryzx': (0, 1, 0, 1),
        'rxzx': (0, 1, 1, 1), 'rxzy': (1, 0, 0, 1), 'ryzy': (1, 0, 1, 1),
        'rzxy': (1, 1, 0, 1), 'ryxy': (1, 1, 1, 1), 'ryxz': (2, 0, 0, 1),
        'rzxz': (2, 0, 1, 1), 'rxyz': (2, 1, 0, 1), 'rzyz': (2, 1, 1, 1)}

    _TUPLE2AXES = dict((v, k) for k, v in _AXES2TUPLE.items())

    _EPSILON = 1.e-15
    _TWOPI = 2. * np.pi

    @staticmethod
    def from_euler(ai, aj, ak, axes='rzxz'):
        """Create a homogeneous rotation matrix from Euler angles and axis sequence.

        Parameters:
            ai: First Euler angle (roll).
            aj: Second Euler angle (pitch).
            ak: Third Euler angle (yaw).
            axes (str, optional): One of 24 axis sequences as string or encoded tuple.

        Returns:
            Matrix3: A rotation matrix representing the specified Euler angles.

        Raises:
            KeyError: If the axes string is not recognized.
            ValueError: If any of the angles has an invalid unit.

        Examples:
            >>> R = Matrix3.from_euler(1, 2, 3, 'syxz')
            >>> np.allclose(np.sum(R[0]), -1.34786452)
            True
            >>> R = Matrix3.from_euler(1, 2, 3, (0, 1, 0, 1))
            >>> np.allclose(np.sum(R[0]), -0.383436184)
            True
        """

        ai = Scalar.as_scalar(ai)
        aj = Scalar.as_scalar(aj)
        ak = Scalar.as_scalar(ak)
        Unit.require_angle(ai._unit)
        Unit.require_angle(aj._unit)
        Unit.require_angle(ak._unit)

        (ai, aj, ak) = Qube.broadcast(ai, aj, ak)

        axes = axes.lower()
        try:
            (firstaxis, parity, repetition, frame) = Matrix3._AXES2TUPLE[axes]
        except (AttributeError, KeyError):
            Matrix3._TUPLE2AXES[axes]   # validation
            firstaxis, parity, repetition, frame = axes

        i = firstaxis
        j = Matrix3._NEXT_AXIS[i + parity]
        k = Matrix3._NEXT_AXIS[i - parity + 1]

        if frame:
            (ai, ak) = (ak, ai)

        if parity:
            (ai, aj, ak) = (-ai, -aj, -ak)

        si = ai.sin()._values
        sj = aj.sin()._values
        sk = ak.sin()._values

        ci = ai.cos()._values
        cj = aj.cos()._values
        ck = ak.cos()._values

        cc = ci * ck
        cs = ci * sk

        sc = si * ck
        ss = si * sk

        matrix = np.empty(ai._shape + (3, 3))
        if repetition:
            matrix[..., i, i] =  cj
            matrix[..., i, j] =  sj * si
            matrix[..., i, k] =  sj * ci
            matrix[..., j, i] =  sj * sk
            matrix[..., j, j] = -cj * ss + cc
            matrix[..., j, k] = -cj * cs - sc
            matrix[..., k, i] = -sj * ck
            matrix[..., k, j] =  cj * sc + cs
            matrix[..., k, k] =  cj * cc - ss
        else:
            matrix[..., i, i] =  cj * ck
            matrix[..., i, j] =  sj * sc - cs
            matrix[..., i, k] =  sj * cc + ss
            matrix[..., j, i] =  cj * sk
            matrix[..., j, j] =  sj * ss + cc
            matrix[..., j, k] =  sj * cs - sc
            matrix[..., k, i] = -sj
            matrix[..., k, j] =  cj * si
            matrix[..., k, k] =  cj * ci

        return Matrix3(matrix, Qube.or_(ai._mask, aj._mask, ak._mask))

    def to_euler(self, axes='rzxz'):
        """Convert this Matrix3 to three Euler angles given a specified axis sequence.

        Parameters:
            axes (str, optional): One of 24 axis sequences as string or encoded tuple.

        Returns:
            tuple: Three Scalars representing the Euler angles (roll, pitch, yaw).

        Raises:
            KeyError: If the axes string is not recognized.

        Notes:
            Many Euler angle triplets can describe one matrix.

        Examples:
            >>> R0 = Matrix3.from_euler(1, 2, 3, 'syxz')
            >>> al, be, ga = R0.to_euler('syxz')
            >>> R1 = Matrix3.from_euler(al, be, ga, 'syxz')
            >>> np.allclose(R0, R1)
            True
        """

        try:
            firstaxis, parity, repetition, frame = Matrix3._AXES2TUPLE[axes.lower()]
        except (AttributeError, KeyError):
            Matrix3._TUPLE2AXES[axes]   # validation
            firstaxis, parity, repetition, frame = axes

        i = firstaxis
        j = Matrix3._NEXT_AXIS[i+parity]
        k = Matrix3._NEXT_AXIS[i-parity+1]

        matvals = self._values[np.newaxis]
        if repetition:
            sy = np.sqrt(matvals[..., i, j]**2 + matvals[..., i, k]**2)

            ax = np.arctan2(matvals[..., i, j],  matvals[..., i, k])
            ay = np.arctan2(sy,                  matvals[..., i, i])
            az = np.arctan2(matvals[..., j, i], -matvals[..., k, i])

            mask = (sy <= Matrix3._EPSILON)
            if np.any(mask):
                ax[mask] = np.arctan2(-matvals[..., j, k], matvals[..., j, j])
                ay[mask] = np.arctan2( sy,                 matvals[..., i, i])
                az[mask] = 0.

        else:
            cy = np.sqrt(matvals[..., i, i]**2 + matvals[..., j, i]**2)

            ax = np.arctan2( matvals[..., k, j], matvals[..., k, k])
            ay = np.arctan2(-matvals[..., k, i], cy)
            az = np.arctan2( matvals[..., j, i], matvals[..., i, i])

            mask = (cy <= Matrix3._EPSILON)
            if np.any(mask):
                ax[mask] = np.arctan2(-matvals[..., j, k], matvals[..., j, j])[mask]
                ay[mask] = np.arctan2(-matvals[..., k, i], cy)[mask]
                az[mask] = 0.

        if parity:
            ax, ay, az = -ax, -ay, -az
        if frame:
            ax, az = az, ax

        return (Scalar(ax[0] % Matrix3._TWOPI, self._mask),
                Scalar(ay[0] % Matrix3._TWOPI, self._mask),
                Scalar(az[0] % Matrix3._TWOPI, self._mask))

    def to_quaternion(self, recursive=True):
        """Convert this Matrix3 to an equivalent unit Quaternion.

        Parameters:
            recursive (bool, optional): True to include derivatives in the result.

        Returns:
            Quaternion: A unit quaternion representing the same rotation.
        """

        return Qube._QUATERNION_CLASS.from_matrix3(self, recursive=recursive)

    def sum(self, axis=None, *, recursive=True, builtins=None, out=None):
        """Calculate the sum of the unmasked values along the specified axis.

        This operation is not supported for Matrix3 objects. This overrides
        :meth:`Qube.sum`.

        Parameters:
            axis (int or tuple, optional): The axis or axes over which the sum is to be
                performed, leaving any remaining axes in the returned value. If not
                specified, the sum is performed across all axes.
            recursive (bool, optional): True to include the sums of the derivatives
                inside the returned Scalar.
            builtins: If True and the result is a single unmasked scalar, the result is
                returned as a Python int or float instead of as an instance of Qube.
                Default is specified by Qube.prefer_builtins().
            out: Ignored. Enables "np.sum(Qube)" to work.

        Raises:
            TypeError: Always raised as this method is not supported for Matrix3.
        """

        raise TypeError('Matrix3.sum() is not supported')

    def mean(self, axis=None, *, recursive=True, builtins=None, dtype=None, out=None):
        """Calculate the mean of the unmasked values along the specified axis.

        This operation is not supported for Matrix3 objects. This overrides
        :meth:`Qube.mean`.

        Parameters:
            axis (int or tuple, optional): The axis or axes over which the mean is to be
                performed, leaving any remaining axes in the returned value. If not
                specified, the mean is performed across all axes.
            recursive (bool, optional): True to include the means of the derivatives
                inside the returned Scalar.
            builtins: If True and the result is a single unmasked scalar, the
                result is returned as a Python int or float instead of as an
                instance of Scalar. Default is specified by Qube.prefer_builtins().
            dtype: Ignored. Enables "np.mean(Qube)" to work.
            out: Ignored. Enables "np.mean(Qube)" to work.

        Raises:
            TypeError: Always raised as this method is not supported for Matrix3.
        """

        raise TypeError('Matrix3.mean() is not supported')

    def __getstate__experimental(self):
        """Override Qube.__getstate__ to save the Matrix3 as a unit Quaternion.

        This is an experimental method for potentially more efficient serialization.

        Returns:
            dict: The state dictionary for pickling.

        Notes:
            This method needs more testing, especially regarding derivatives.
        """

        # TODO: Seems like a good idea, but needs more testing, especially regarding
        # derivatives.

        # Prepare the clone
        clone = self.clone(recursive=True)
        clone._check_pickle_digits()
        clone._mask = Qube.as_one_bool(clone._mask)   # collapse mask

        # Don't bother using special processing on small objects
        if self._size < 30 or clone._mask is True:
            return Qube.__getstate__(self)

        # Because a Matrix3 can be represented by a unit Quaternion, we can obtain
        # excellent compression by converting it.
        quaternion = clone.to_quaternion(recursive=True)

        # Also, because a quaternion and its negative define the same rotation, we can
        # force the first element to be positive and then we don't need to save it,
        # because the rotation can be derived from the remaining components.

        sign = np.sign(quaternion._values[..., 0])
        quaternion *= sign
        clone._values = quaternion._values[..., 1:]

        # Replace the Matrix3 derivatives with the Quaternion derivatives
        clone._derivs = quaternion._derivs

        clone.CONVERTED_TO_QUATERNION = True
        return Qube.__getstate__(clone)

    def __setstate__experimental(self, state):
        """Override of Qube.__setstate__ to convert from unit Quaternion back to Matrix3.
        """

        # Apply default _setstate_
        Qube.__setstate__(self, state)

        if not hasattr(self, 'CONVERTED_TO_QUATERNION'):
            return

        # Expand the Quaternion values and fill in missing scalar
        qvals = np.empty(self._shape + (4,))
        qvals[..., 1:] = self._values
        qvals[..., 0] = np.sqrt(1. - np.sum(self._values**2, axis=-1))

        # Convert the quaternion and derivatives to Matrix3
        q = Qube._QUATERNION_CLASS(qvals, derivs=state['_derivs'])
        matrix3 = q.to_matrix3()

        self._values = matrix3._values
        self._derivs = matrix3._derivs
        delattr(self, 'CONVERTED_TO_QUATERNION')

        return

##########################################################################################
# Useful class constants
##########################################################################################

Matrix3.IDENTITY = Matrix3([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).as_readonly()
Matrix3.MASKED   = Matrix3([[1, 0, 0], [0, 1, 0], [0, 0, 1]], True).as_readonly()

##########################################################################################
# Once defined, register with Qube class
##########################################################################################

Qube._MATRIX3_CLASS = Matrix3

##########################################################################################
