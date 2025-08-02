##########################################################################################
# polymath/vector3.py: Vector3 subclass of PolyMath Vector
##########################################################################################

from __future__ import division
import numpy as np
import numbers

from polymath.qube   import Qube
from polymath.scalar import Scalar
from polymath.vector import Vector


class Vector3(Vector):
    """Represent 3-dimensional vectors in the PolyMath framework.

    This class provides specialized functionality for working with 3-element vectors,
    including coordinate transformations and 3D operations.
    """

    _NRANK = 1          # The number of numerator axes.
    _NUMER = (3,)       # Shape of the numerator.
    _FLOATS_OK = True   # True to allow floating-point numbers.
    _INTS_OK = False    # True to allow integers.
    _BOOLS_OK = False   # True to allow booleans.
    _UNITS_OK = True    # True to allow units; False to disallow them.
    _DERIVS_OK = True   # True to allow derivatives and denominators; False to disallow.
    _DEFAULT_VALUE = np.array([1., 1., 1.])

    @staticmethod
    def as_vector3(arg, *, recursive=True):
        """Convert the argument to Vector3 if possible.

        Parameters:
            arg (object): The object to convert to Vector3.
            recursive (bool, optional): If True, derivatives will also be
                converted.

        Returns:
            Vector3: The converted Vector3 object.
        """

        if isinstance(arg, Vector3):
            return arg if recursive else arg.wod

        if isinstance(arg, Qube):

            # Collapse a 1x3 or 3x1 Matrix down to a Vector
            if arg._numer in ((1, 3), (3, 1)):
                return arg.flatten_numer(Vector3, recursive=recursive)

            # For any suitable Qube, move numerator items to the denominator
            if arg.rank > 1 and arg._numer[0] == 3:
                arg = arg.split_items(1, Vector3)

            arg = Vector3(arg)
            return arg if recursive else arg.wod

        return Vector3(arg)

    @staticmethod
    def from_scalars(x, y, z, *, recursive=True, readonly=False):
        """Construct a Vector3 by combining three scalars.

        Parameters:
            x (Scalar or convertible): First component of the vector.
            y (Scalar or convertible): Second component of the vector.
            z (Scalar or convertible): Third component of the vector.
            recursive (bool, optional): True to include all the derivatives. The returned
                object will have derivatives representing the union of all the derivatives
                found among x, y and z.
            readonly (bool, optional): True to return a read-only object; False to return
                something potentially writable.

        Returns:
            Vector3: A new Vector3 object constructed from the three scalars.

        Notes:
            Input arguments need not have the same shape, but it must be possible to cast
            them to the same shape. A value of None is converted to a zero-valued Scalar
            that matches the denominator shape of the other arguments.
        """

        return Qube.from_scalars(x, y, z, recursive=recursive, readonly=readonly,
                                 classes=[Vector3])

    @staticmethod
    def from_ra_dec_length(ra, dec, length=1., *, recursive=True):
        """Construct a Vector3 from right ascension, declination and optional length.

        Parameters:
            ra (Scalar): Right ascension in radians.
            dec (Scalar): Declination in radians.
            length (Scalar, optional): Length of the vector.
            recursive (bool, optional): True to include all the derivatives. The returned
                object will have derivatives representing the union of all the derivatives
                in ra, dec and length.

        Returns:
            Vector3: A new Vector3 object constructed from the spherical coordinates.

        Notes:
            Input arguments need not have the same shape, but it must be possible to cast
            them to the same shape.
        """

        ra  = Scalar.as_scalar(ra, recursive=recursive)
        dec = Scalar.as_scalar(dec, recursive=recursive)

        cos_dec = dec.cos()
        x = cos_dec * ra.cos()
        y = cos_dec * ra.sin()
        z = dec.sin()

        result = Vector3.from_scalars(x, y, z, recursive=recursive)

        if isinstance(length, numbers.Real) and length == 1.:
            return result
        else:
            return Scalar.as_scalar(length, recursive=recursive) * result

    def to_ra_dec_length(self, *, recursive=True):
        """Return a tuple (ra, dec, length) from this Vector3.

        Parameters:
            recursive (bool, optional): True to include the derivatives.

        Returns:
            tuple: (**ra**, **dec**, **length**) where all three are Scalars; **ra** and
            **dec** are in radians.
        """

        (x, y, z) = self.to_scalars(recursive=recursive)
        length = self.norm(recursive=recursive)

        ra = y.arctan2(x) % Scalar.TWOPI
        dec = (z/length).arcsin()

        return (ra, dec, length)

    @staticmethod
    def from_cylindrical(radius, longitude, z=0., *, recursive=True):
        """Construct a Vector3 from cylindrical coordinates.

        Parameters:
            radius (Scalar): Distance from the cylindrical axis.
            longitude (Scalar): Longitude in radians. Zero is along the x-axis.
            z (Scalar, optional): Distance above/below the equatorial plane.
            recursive (bool, optional): True to include all the derivatives. The returned
                object will have derivatives representing the union of all the derivatives
                in radius, longitude and z.

        Returns:
            Vector3: A new Vector3 object constructed from the cylindrical coordinates.

        Notes:
            Input arguments need not have the same shape, but it must be possible to cast
            them to the same shape.
        """

        radius  = Scalar.as_scalar(radius, recursive=recursive)
        longitude = Scalar.as_scalar(longitude, recursive=recursive)
        z = Scalar.as_scalar(z, recursive=recursive)

        x = radius * longitude.cos(recursive=recursive)
        y = radius * longitude.sin(recursive=recursive)

        return Vector3.from_scalars(x, y, z, recursive=recursive)

    def to_cylindrical(self, *, recursive=True):
        """Return a tuple (radius, longitude, z) from this Vector3.

        Parameters:
            recursive (bool, optional): True to include the derivatives.

        Returns:
            tuple: (**radius**, **longitude**, **z**), where all three are Scalars and
            **longitude** is in radians.
        """

        (x, y, z) = self.to_scalars(recursive=recursive)
        radius = (x**2 + y**2).sqrt(recursive=recursive)

        longitude = y.arctan2(x, recursive=recursive) % Scalar.TWOPI

        return (radius, longitude, z)

    def longitude(self, *, recursive=True):
        """Return the longitude (azimuthal angle) of this Vector3.

        Parameters:
            recursive (bool, optional): True to include the derivatives.

        Returns:
            Scalar: The longitude in radians, measured from the X-axis toward the Y-axis.
        """

        x = self.to_scalar(0, recursive=recursive)
        y = self.to_scalar(1, recursive=recursive)
        return y.arctan2(x) % Scalar.TWOPI

    def latitude(self, *, recursive=True):
        """Return the latitude (elevation angle) of this Vector3.

        Parameters:
            recursive (bool, optional): True to include the derivatives.

        Returns:
            Scalar: The latitude in radians, measured from the equatorial plane toward the
            Z-axis.
        """

        z = self.to_scalar(2, recursive=recursive)
        length = self.norm(recursive=recursive)
        return (z/length).arcsin()

    # Most operations are inherited from Vector. These include:
    #     def extract_scalar(self, axis, recursive=True)
    #     def as_scalars(self, recursive=True)
    #     def as_column(self, recursive=True)
    #     def as_row(self, recursive=True)
    #     def as_diagonal(self, recursive=True)
    #     def dot(self, arg, recursive=True)
    #     def norm(self, recursive=True)
    #     def unit(self, recursive=True)
    #     def cross(self, arg, recursive=True)
    #     def ucross(self, arg, recursive=True)
    #     def outer(self, arg, recursive=True)
    #     def perp(self, arg, recursive=True)
    #     def proj(self, arg, recursive=True)
    #     def sep(self, arg, recursive=True)
    #     def cross_product_as_matrix(self, recursive=True)
    #     def element_mul(self, arg, recursive=True):
    #     def element_div(self, arg, recursive=True):
    #     def __abs__(self)

    def spin(self, pole, angle=None, *, recursive=True):
        """Return this Vector3 rotated about a pole vector.

        Parameters:
            pole (Vector3): The pole vector about which to rotate.
            angle (Scalar, optional): The rotation angle in radians. If None, the angle is
                determined from the pole vector's magnitude.
            recursive (bool, optional): True to include the derivatives.

        Returns:
            Vector3: The rotated vector.

        Notes:
            If angle is None, the pole vector's magnitude is used as the rotation angle.
        """

        pole = Vector3.as_vector3(pole, recursive=recursive)

        if angle is None:
            norm = pole.norm()
            angle = norm.arcsin()
            zaxis = pole / norm
        else:
            angle = Scalar.as_scalar(angle, recursive=recursive)
            mask = (angle == 0.)
            if np.any(mask):
                pole = pole.mask_where_eq(Vector3.ZERO, Vector3.ZAXIS, remask=False)
            zaxis = pole.unit()

        z = self.dot(zaxis, recursive=recursive)
        perp = self - z * zaxis
        r = perp.norm()
        perp = perp.mask_where_eq(Vector3.ZERO, Vector3.XAXIS, remask=False)
        xaxis = perp.unit()
        yaxis = zaxis.cross(xaxis)
        return r * (angle.cos() * xaxis + angle.sin() * yaxis) + z * zaxis

    def offset_angles(self, vector, *, recursive=True):
        """Return the angular offset between this Vector3 and another.

        Parameters:
            vector (Vector3): The vector to measure the offset from.
            recursive (bool, optional): True to include the derivatives.

        Returns:
            tuple: (**longitude_offset**, **latitude_offset**) angles in radians.
        """

        vector = Vector3.as_vector3(vector, recursive=recursive)

        (self, vector) = Vector3.broadcast(self, vector, recursive=recursive)
        (x0, y0, z0) = self.unit().to_scalars()
        (x , y , z ) = vector.unit().to_scalars()

        # Start with this vector. The first rotation is about the Y-axis, where a
        # positive rotation angle increases x if the vector is near the Z-axis. We need
        # this rotation to change x0 to x, because x will be conserved in the second
        # rotation.

        # When viewed down the Y-axis, the length of this vector is conserved during the
        # rotation.
        norm0 = (x0**2 + z0**2).sqrt()
        yrot = (x/norm0).arcsin() - (x0/norm0).arcsin()

        # This is the vector after the first rotation; its y coordinate is unchanged.
        z1 = (1 - x**2 - y0**2).sqrt()
        # The new unit vector is (x, y0, z1)

        # The second rotation is about the X-axis and needs to match the final value of y.
        # If this is accomplished, then the z-values will match automatically. A positive
        # rotation about the X-axis decreases y.

        # When viewed down the X-axis, the length of this vector is conserved during the
        # rotation.
        norm1 = (y0**2 + z1**2).sqrt()
        xrot = (y0/norm1).arcsin() - (y/norm1).arcsin()

        return (yrot, xrot)

##########################################################################################
# A set of useful class constants
##########################################################################################

Vector3.ZERO   = Vector3((0., 0., 0.)).as_readonly()
Vector3.ONES   = Vector3((1., 1., 1.)).as_readonly()
Vector3.XAXIS  = Vector3((1., 0., 0.)).as_readonly()
Vector3.YAXIS  = Vector3((0., 1., 0.)).as_readonly()
Vector3.ZAXIS  = Vector3((0., 0., 1.)).as_readonly()
Vector3.MASKED = Vector3((1, 1, 1), True).as_readonly()

Vector3.ZERO_POS_VEL = Vector3((0., 0., 0.)).as_readonly()
Vector3.ZERO_POS_VEL.insert_deriv('t', Vector3.ZERO).as_readonly()

Vector3.IDENTITY = Vector3([(1, 0, 0), (0, 1, 0), (0, 0, 1)], drank=1).as_readonly()

Vector3.AXES = (Vector3.XAXIS, Vector3.YAXIS, Vector3.ZAXIS)

##########################################################################################
# Once defined, register with Qube class
##########################################################################################

Qube._VECTOR3_CLASS = Vector3

##########################################################################################
