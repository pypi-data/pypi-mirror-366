##########################################################################################
# polymath/__init__.py
##########################################################################################
"""\
################
PolyMath Library
################

PDS Ring-Moon Systems Node, SETI Institute

PolyMath expands on the NumPy module and introduces a variety of additional data types
and features to simplify 3-D geometry calculations. It is a product of the the [PDS
Ring-Moon Systems Node](https://pds-rings.seti.org). The PolyMath classes are:

* :class:`Scalar`: A single zero-dimensional number=.
* :class:`Vector`: An arbitrary 1-D object.
* :class:`Pair`: A subclass of `Vector` representing a vector with two coordinates.
* :class:`Vector3`: A subclass of `Vector` representing a vector with three coordinates.
* :class:`Matrix`: An arbitrary 2-D matrix.
* :class:`Matrix3`: A subclass of `Matrix` representing a unitary 3x3 rotation matrix.
* :class:`Quaternion`: A subclass of `Vector` representing a 4-component quaternion.
* :class:`Boolean`: A True or False value.
* :class:`Qube`: The superclass of all of the above, supporting objects of arbitrary
  dimension.

Importantly, each of these classes can represent not just a single object, but also an
arbitrary array of these objects. Mathematical operations on arrays follow NumPy's rules
of "broadcasting"; see https://numpy.org/doc/stable/user/basics.broadcasting.html for
these details. The key advantage of PolyMath's approach is that it separates each object's
shape from any internal dimensions (e.g., (3,3) for a :class:`Matrix3` object), largely
eliminating any need to ever do "index bookkeeping". For example, suppose **S** is a
:class:`Scalar` and **V** is a :class:`Vector`. Then, in PolyMath, you can write::

    S * V

whereas, in NumPy, you would have to write::

    S[..., np.newaxis] * V

to get the same result. This capability makes it possible to write out algorithms as if
each operation is on a single vector, scalar, or matrix, ignoring the internal
dimensionality of each PolyMath object.

PolyMath has the following additional features:

* **Derivatives**: An object can have arbitrary derivatives, or an array thereof. These
  get carried through all math operations so, for example, if **X.d_dt** is the derivative
  of **X** with respect to **t**, then **X.sin().d_dt** is the derivative of **sin(X)**
  with respect to **t**. This means that you can write out math operations in the most
  straightforward manner, without worrying about how any derivatives get calculated.
* **Masks**: Objects can have arbitrary boolean masks, which are equal to True where the
  object's value is undefined. This is similar to NumPy's MaskedArray class, but with
  added capabilities. For example, if an object is mostly masked, you can use the
  :meth:`~Qube.shrink` method to speed up math operations by excluding all the masked
  elements.
* **Units**: Objects can have arbitrary units, as defined by PolyMath's `Unit` class.
* **Read-only** status: It is easy to define an object to be read-only, which will then
  prevent it from being modified further. This can be useful for preventing NumPy errors
  that can arise when multiple objects share memory (a common situation) and one of them
  gets modified by accident.
* **Indexing**: An object can be indexed in a variety of ways that expand upon NumPy's
  indexing rules.
* **Pickling**: Python's `pickle` module can be used to save and re-load objects in a way
  that makes for extremely efficient storage.

PolyMath provides the mathematical underpinnings of the OOPS Library. As an illustration
of its power, here are some examples of how OOPS uses PolyMath objects to describe a data
product:

* **los** is a single :class:`Vector3` that represents the lines of sight represented by
  each sample in the data product. If the product is a 1000x1000 image, then **los** will
  have an internal shape of (1000,1000). If the product is a single detector, then **los**
  will have no internal shape.

* **time** is a :class:`Scalar` that represents the time that the photons arrived at the
  detector. If the instrument is a simple, shuttered camera, then all photons arrive at
  the same time and **time** can have a single value. However, if a raster-scanning device
  obtains a 1000x1000 image, then **time** will have an internal shape of (1000,1000),
  with each element representing the unique arrival time at that pixel. For a "pushbroom"
  camera, the detector receives the image line by line, so **time** will have an internal
  shape of (1000,1) or (1,1000), depending on the orientation of the detector.

* **cmatrix** is a :class:`Matrix3` that represents the rotation matrix from the
  instrument's internal coordinates to the J2000 frame, which is fixed relative to the
  sky. If the instrument is not rotating during an observation, then a single matrix is
  required. However, if the camera is on a rotating platform and it samples photons at
  different times, then **cmatrix** may need to have an internal shape of (1000,1000) to
  describe a 1000x1000 image. Furthermore, the rate of change of **cmatrix** can be
  described by a derivative with respect to time. When one calculates where the lines of
  sight intercepted a target body, the time derivative of **cmatrix** can then be used to
  determine the amount of smear in the image.

Although different types of data products might have very different internal
representations, PolyMath makes it possible to write a geometry calculation just once and
then re-use it for all of these situations.

As a specific example, OOPS can determine where each line of sight sampled by a data
product intercepted the surface of a particular planetary body. The intercept points are
represented by a single :class:`Vector3` given in the body's coordinate frame. From this
object, it is straightforward to derive latitude, longitude, emission angle, etc. If the
product is a 1000x1000 image, then the :class:`Vector3` will have an internal shape of
(1000,1000). Furthermore, if the body does not entirely fill the field of view, the lines
of sight that did not intercept the body are masked. It is not uncommon for a body to only
partially fill a field of view. In this case, OOPS can speed up calculations, sometimes
substantially, by omitting the masked elements of the :class:`Vector3` object.

************************
Math Operations
************************

All standard mathematical operators and indexing/slicing options are defined for PolyMath
objects, where appropriate: `+`, `-`, `*`, `/`, `%`, `//`,`**`, along with their in-place
variants. Equality tests `==`, `!=` are available for all objects; comparison operators
`<`, `<=`, `>`, `>=` are supported for Scalars and Booleans. Where appropriate, methods
such as :meth:`~Qube.abs`, :meth:`~Qube.len`, :meth:`~Qube.mean`, :meth:`~Qube.sum`,
:meth:`~Qube.identity`, :meth:`~Qube.reciprocal`, :meth:`~Scalar.int`,
:meth:`Matrix.inverse`, and :meth:`Matrix.transpose` (or property :attr:`Matrix.T`).

:class:`Scalar` supports most common math functions such as :meth:`~Scalar.sin`,
:meth:`~Scalar.cos`, :meth:`~Scalar.tan`, :meth:`~Scalar.arcsin`, :meth:`~Scalar.arccos`,
:meth:`~Scalar.arctan`, :meth:`~Scalar.arctan2`, :meth:`~Scalar.sqrt`,
:meth:`~Scalar.log`, :meth:`~Scalar.exp`, :meth:`~Scalar.sign`, :meth:`~Scalar.int`,
:meth:`~Scalar.frac`, :meth:`~Scalar.min`, :meth:`~Scalar.max`, :meth:`~Scalar.argmin`,
:meth:`~Scalar.argmax`, :meth:`~Scalar.minimum`, :meth:`~Scalar.maximum`,
:meth:`~Scalar.median`, and :meth:`~Scalar.sort`. It also supports quadratic equations via
:meth:`~Scalar.solve_quadratic` and :meth:`~Scalar.eval_quadratic`.

:class:`Vector` supports functions such as :meth:`~Vector.norm`, :meth:`~Vector.norm_sq`,
:meth:`~Vector.unit`, :meth:`~Vector.dot`, :meth:`~Vector.cross`, :meth:`~Vector.ucross`,
:meth:`~Vector.outer` (outer product), :meth:`~Vector.perp` (perpendicular vector),
:meth:`~Vector.proj` (projection), and :meth:`~Vector.sep` (separation angle).
Element-by-element operations are also supported using :meth:`~Vector.element_mul` and
:meth:`~Vector.element_div`.

:class:`Vector3` supports additional functions such as
:meth:`~Vector3.from_ra_dec_length`, :meth:`~Vector3.to_ra_dec_length`,
:meth:`~Vector3.from_cylindrical`, :meth:`~Vector3.to_cylindrical`,
:meth:`~Vector3.longitude`, :meth:`~Vector3.latitude`, :meth:`~Vector3.spin` (rotate one
vector about another), and :meth:`~Vector3.offset_angles` (the angles from the three
primary axes).

:class:`Pair` supports additional functions such as :meth:`~Pair.swapxy`,
:meth:`~Pair.rot90` (for rotation by a multiple of 90 degrees), and :meth:`~Pair.angle`
(for the vector's angular direction).

:class:`Matrix3` functions :meth:`~Matrix3.rotate` and :meth:`~Matrix3.unrotate` apply a
rotation to another object. Methods :meth:`~Matrix3.x_rotation`,
:meth:`~Matrix3.y_rotation`, :meth:`~Matrix3.z_rotation`, :meth:`~Matrix3.axis_rotation`,
:meth:`~Matrix3.pole_rotation`, :meth:`~Matrix3.from_euler`, and :meth:`~Matrix3.unitary`
are convenient, alternative ways to define a rotation matrix. Use
:meth:`~Matrix3.to_euler` and :meth:`~Matrix3.to_quaternion` to reverse these definitions.

:class:`Quaternion` supports functions such as :meth:`~Quaternion.conj` (conjugate),
:meth:`~Quaternion.to_parts` (for the Scalar and Vector3 components),
:meth:`~Quaternion.from_parts` (to construct from the Scalar and Vector3 components),
:meth:`~Quaternion.to_rotation` (for the transform as a direction Vector3 and rotation
angle), :meth:`~Quaternion.from_matrix3`, :meth:`~Quaternion.to_matrix3`,
:meth:`~Quaternion.from_euler`, and :meth:`~Quaternion.to_euler`.

The :attr:`~Qube.values` (or :attr:`~Qube.vals`) property of each object returns its value
as a NumPy array. For Scalar objects with no shape, :attr:`~Qube.values` is a
Python-native value of float or int; for Boolean objects with no shape,
:attr:`~Qube.values` is a Python-native bool.

One can generally mix PolyMath arithmetic with scalars, NumPy ndarrays, NumPy
MaskedArrays, or anything array-like.

************************
Shapes and Broadcasting
************************

The PolyMath subclasses, e.g., :class:`Scalar`, :class:`Vector3`, and :class:`Matrix3`,
define one or more possibly multidimensional items. Unlike NumPy ndarrays, this class
makes a clear distinction between the dimensions associated with the items and any
additional, leading dimensions that define an array of such items.

Each object's :attr:`~Qube.shape` property contains the shape of its leading axes, whereas
its :attr:`~Qube.item` property defines the shape of individual elements. For example, a
2x2 array of :class:`Matrix3` objects would have `shape=(2,2)` and `items=(3,3)`. Its
:attr:`~Qube.values` property would be a NumPy array with shape (2,2,3,3). In addition,
:attr:`~Qube.ndims` (or :attr:`~Qube.ndim`) contains the number of dimensions in the
shape; :attr:`~Qube.size` is the number of items; :attr:`~Qube.rank` is the number of
dimensions in the items; :attr:`~Qube.isize` is the number of item elements.

To change the shape of an object, use methods :meth:`~Qube.reshape`,
:meth:`~Qube.flatten`, :meth:`~Qube.move_axis`, :meth:`~Qube.roll_axis`, and
:meth:`~Qube.swap_axes`. These all return a shallow copy of an object, which shares memory
with the original object.

Standard NumPy rules of broadcasting apply, but only on the :attr:`~Qube.shape`
dimensions, not on the :attr:`~Qube.item` dimensions. For example, if you multiply a
:class:`Matrix3` with shape (2,2) by a :class:`Vector3` object with shape (5,1,2), you
would get a new (rotated) :class:`Vector3` object with shape (5,2,2). See the complete
rules of broadcasting here:

https://numpy.org/doc/stable/user/basics.broadcasting.html

If necessary, you can explicitly broadcast objects to a new shape using methods
:meth:`~Qube.broadcast` and :meth:`~Qube.broadcast_to`; these return shallow, read-only
copies. Use :meth:`~Qube.broadcasted_shape` to determine the shape that will result from
an operation involving multiple PolyMath objects and NumPy arrays.

*****************
Derivatives
*****************

PolyMath objects can track associated derivatives and partial derivatives, which are
represented by a dictionary of other PolyMath objects. A common use case is to let **X**
be a :class:`Vector3` object describing the position of one or more bodies or points on a
surface and to use the time-derivative of **X** to describe the velocity. The
:attr:`~Qube.derivs` property of an object is a dictionary of each derivative, keyed by
its name. For example, a time-derivative is often keyed by **t**. For convenience, you can
also reference each derivative by the attribute name "d_d" plus the key, so the
time-derivative of **X** can be accessed via **X.d_dt**. This feature makes it possible to
write an algorithm describing the positions of bodies or features, and to have any
time-derivatives carried along in the calculation with no additional programming effort.

The denominators of partial derivatives are represented by splitting the item shape into a
numerator shape plus a denominator shape. As a result, for example, the partial
derivatives of a :class:`Vector3` object (item shape (3,)) with respect to a :class:`Pair`
(item shape (2,)) will have overall item shape (3,2). Properties :attr:`~Qube.numer` gives
the numerator shape, :attr:`~Qube.nrank` is the number of dimensions, and
:attr:`~Qube.nsize` gives the number of elements. Similarly, :attr:`~Qube.denom` is the
denominator shape, :attr:`~Qube.drank` is the number of dimensions, and
:attr:`~Qube.dsize` is the number of elements.

The PolyMath subclasses generally do not constrain the shape of the denominator, just
the numerator. As a result, the aforementioned partial derivatives can still be
represented by a :class:`Vector3` object.

Methods :meth:`~Qube.insert_deriv`, :meth:`~Qube.insert_derivs`,
:meth:`~Qube.delete_deriv`, :meth:`~Qube.delete_derivs`, and :meth:`~Qube.rename_deriv`
can be used to add, remove, or modify derivatives after it has been constructed. You can
also obtain a shallow copy of an object with one or more derivatives removed using
:meth:`~Qube.without_deriv` and :meth:`~Qube.without_derivs`. For convenience, the
:attr:`~Qube.wod` property is equivalent to :meth:`~Qube.without_derivs`. Note that the
presence of derivatives inside an object can slow computational performance significantly,
so it can useful to suppress derivatives from a calculation if they are not needed. Note
that many math functions have a `recursive` option that defaults to True; set it to False
to ignore derivatives within the given calculation.

A number of methods are focused on modifying the numerator and denominator components of
objects: :meth:`~Qube.extract_numer`, :meth:`~Qube.extract_denom`,
:meth:`~Qube.extract_denoms`, :meth:`~Qube.slice_numer`, :meth:`~Qube.transpose_numer`,
:meth:`~Qube.reshape_numer`, :meth:`~Qube.flatten_numer`, :meth:`~Qube.transpose_denom`,
:meth:`~Qube.reshape_denom`, :meth:`~Qube.flatten_denom`, :meth:`~Qube.join_items`,
:meth:`~Qube.split_items`, and :meth:`~Qube.swap_items`.

The function :meth:`~Qube.chain` can be used for chain-multiplication of derivatives; this
is also implemented via the "@" operator.

****************
Masks
****************

Every object has a boolean mask, which identifies undefined values or array elements.
Operations that would otherwise raise errors such as 1/0 and sqrt(-1) are masked, so that
run-time warnings and exceptions can be avoided. A common use case is to have a
"backplane" array describing the geometric content of a planetary image, where the mask
identifies the pixels that do not intersect the surface.

Each object has a property :attr:`~Qube.mask`, which contains the mask. A single value of
False means that the object is entirely unmasked; a single value of True means it is
entirely masked. Otherwise, :attr:`~Qube.mask` is a NumPy array with boolean values, with
a shape that matches that of the object itself (excluding its items). For example, a
:class:`Vector3` object with shape (5,2) could have a :attr:`~Qube.mask` value represented
by a NumPy array of shape (5,2), even though its :attr:`~Qube.values` property has shape
(5,2,3).

The :attr:`~Qube.mvals` property of an object returns its :attr:`~Qube.values` property as
a NumPy MaskedArray.

Each object also has a property :attr:`~Qube.antimask`, which is the "logical not" of the
:attr:`~Qube.mask`. Use the :attr:`~Qube.antimask` as an index to select only the unmasked
elements of an object. You can also use the :meth:`~Qube.shrink` method to temporarily
eliminate masked elements from an object, potentially speeding up calculations; use
:meth:`~Qube.unshrink` when you are done to restore the original shape.

Under normal circumstances, a masked value should be understood to mean, "this value
does not exist." For example, a calculation of observed intercept points on a moon is
masked if a line of sight missed the moon, because that line of sight does not exist. This
is similar to NumPy's not-a-number ("NaN") concept, but there are important differences.
For example,

* Two masked values of the same class are considered equal. This is different from the
  behavior of NaN.
* Unary and binary operations involving masked values always return masked values.
* Because masked values are treated as if they do not exist, :meth:`~Scalar.max` returns
  the maximum among the unmasked values; :meth:`~Qube.all` returns True if all the
  unmasked values are True (or nonzero).

However, PolyMath also provides boolean methods to support an alternative interpretation
of masked values as indeterminate rather than nonexistent. These follow the rules of
"three-valued logic":

* :meth:`~Qube.tvl_and` returns False if one value is False but the other is masked,
  because the result would be False regardless of the second value.
* :meth:`~Qube.tvl_or` returns True if one value is True but the other is masked, because
  the result would be True regardless of the second value.
* :meth:`~Qube.tvl_all` returns True only if and only all values are True; if any value is
  False, it returns False; if the only values are True or indeterminate, its value is
  indeterminate (meaning masked).
* :meth:`~Qube.tvl_any` returns True if any value is True; it returns False if every value
  is False; if the only values are False or indeterminate, its value is indeterminate.
* :meth:`~Qube.tvl_eq` and :meth:`~Qube.tvl_ne` are indeterminate if either value is
  indeterminate.

You can only define an object's mask at the time it is constructed. To change a mask, use
:meth:`~Qube.remask` or :meth:`~Qube.remask_or`, which return a shallow copy of the object
(sharing memory with the original) but with a new mask. You can also use a variety of
methods to construct an object with a new mask: :meth:`~Qube.mask_where`,
:meth:`~Qube.mask_where_eq`, :meth:`~Qube.mask_where_ge`, :meth:`~Qube.mask_where_gt`,
:meth:`~Qube.mask_where_le`, :meth:`~Qube.mask_where_lt`, :meth:`~Qube.mask_where_ne`,
:meth:`~Qube.mask_where_between`, :meth:`~Qube.mask_where_outside`, and
:meth:`~Qube.clip`.

****************
Units
****************

PolyMath objects also support embedded unit using the :class:`Unit` class. However, the
internal values in a PolyMath object are always held in standard units of kilometers,
seconds and radians, or arbitrary combinations thereof. The unit is primarily used to
affect the appearance of numbers during input and output. The :attr:`~Qube.unit_` or
:attr:`~Qube.units` property of any object will reveal the class:`Unit` object, or
possibly None if the object is unitless.

A :class:`Unit` allows for exact conversions between units. It is described by three
integer exponents applying to dimensions of length, time, and angle. Conversion factors
are describe by three (usually) integer values representing a numerator, denominator, and
an exponent on pi. For example, :attr:`Unit.DEGREE` is represented by exponents (0,0,1)
and factors (1,180,1), indicating that the conversion factor is `pi/180`. Most other
common units are described by class constants; see the :class:`Unit` class for details.

Normally, you specify the unit of an object at the time it is constructed. However, the
method :meth:`~Qube.set_unit` is available to set the :attr:`~Qube.unit_` property
afterward.

*****************
Read-only Objects
*****************

PolyMath objects can be either read-only or read-write. Read-only objects are prevented
from modification to the extent that Python makes this possible. Operations on read-only
objects should always return read-only objects.

The :meth:`~Qube.as_readonly` method can be used to set an object (and its
derivatives) to read-only status. It is not possible to convert an object from
read-only back to read-write; use :meth:`~Qube.copy` instead. The
:attr:`~Qube.readonly` property is True if the object is read-only; False if it is
read-write.

************************
Alternative Constructors
************************

Aside from the explicit constructor methods, numerous methods are available to construct
objects from other objects. Methods include :meth:`~Qube.copy`, :meth:`~Qube.clone`,
:meth:`~Qube.cast`, :meth:`~Qube.zeros`, :meth:`~Qube.ones`, :meth:`~Qube.filled`,
:meth:`~Qube.as_this_type`, :meth:`~Qube.as_all_constant`, :meth:`~Qube.as_size_zero`,
:meth:`~Qube.masked_single`, :meth:`~Qube.as_numeric`, :meth:`~Qube.as_float`,
:meth:`~Qube.as_int`, and :meth:`~Qube.as_bool`. There are also methods to convert between
classes, such as :meth:`Vector.from_scalars`, :meth:`Vector.to_scalar`,
:meth:`Vector.to_scalars`, :meth:`Matrix3.twovec` (a rotation matrix defined by two
vectors), :meth:`Matrix.row_vector`, :meth:`Matrix.row_vectors`,
:meth:`Matrix.column_vector`, Matrix.column_vectors`, and Matrix.to_vector`.

******************
Indexing
******************

Using an index on a Qube object is very similar to using one on a NumPy array, but
there are a few important differences. For purposes of retrieving selected values from
an object:

* True and False can be applied to objects with shape (). True leaves the object
  unchanged; False masks the object.

* An index of True selects the entire associated axis in the object, equivalent to a colon
  or `slice(None)`. An index of False reduces the associated axis to length one and masks
  the object entirely.

* A :class:`Boolean` object can be used as an index. If this index is unmasked, it is the
  same as indexing with a boolean NumPy ndarray. If it is masked, the values of the
  returned object are masked wherever the :class:`Boolean`'s value is masked. When using a
  :class:`Boolean` index to set items inside an object, locations where the
  :class:`Boolean` index are masked are not changed.

* A :class:`Scalar` object composed of integers can be used as an index. If this index is
  unmasked, it is equivalent to indexing with an integer or integer NumPy ndarray. If it
  is masked, the values of the returned object are masked wherever the :class:`Scalar` is
  masked. When using a :class:`Scalar` index to set items inside an object, locations
  where the :class:`Scalar` index are masked are not changed.

* A :class:`Pair` object composed of integers can be used as an index. Each `(i,j)` value
  is treated is the index of two consecutive axes, and the associated value is returned.
  Where the :class:`Pair` is masked, a masked value is returned. Similarly, a
  :class:`Vector` with three or more integer elements is treated as the index of three or
  more consecutive axes.

* As in NumPy, an integer valued array can be used to index a PolyMath object. In this
  case, the shape of the index array appears within the shape of the returned object. For
  example, if `A` has shape `(6,7,8,9)` and `B` has shape `(3,1)`, then `A[B]` has shape
  `(3,1,7,8,9)`; `A[:,B]` has shape `(6,3,1,8,9)`, and `A[...,B]` has shape `(6,7,8,3,1)`.

* When multiple arrays are used for indexing at the same time, the broadcasted shape of
  these array appears at the location of the first array-valued index. In the same example
  as above, suppose `C` has shape `(4,)`. Then `A[B,C]` has shape `(3,4,8,9)`, `A[:,B,C]`
  has shape `(6,3,4,9)`, and `A[:,B,:,C]` has shape `(6,3,4,8)`. Note that this behavior
  is slightly different from how NumPy handles indexing with multiple arrays.

Several methods can be used to convert PolyMath objects to objects than be used for
indexing NumPy arrays. You can obtain integer indices from :meth:`Scalar.as_index`,
:meth:`Vector.as_index`, :meth:`Scalar.as_index_and_mask`, and
:meth:`Vector.as_index_and_mask`. You can obtain boolean masks from
:meth:`Boolean.as_index`, :meth:`~Qube.as_mask_where_nonzero`,
:meth:`~Qube.as_mask_where_zero`, :meth:`~Qube.as_mask_where_nonzero_or_masked`, and
:meth:`~Qube.as_mask_where_zero_or_masked`.

******************
Iterators
******************

Every Polymath object can be used as an iterator, in which case it performs an iteration
over the object's leading axis. Alternatively, :meth:`~Qube.ndenumerate` iterates over
every item in a multidimensional object.

******************
Pickling
******************

Because objects such as backplanes can be numerous and also quite large, we provide a
variety of methods, both lossless and lossy, for compressing them during storage. As one
example of optimization, only the un-masked elements of an object are stored; upon
retrieval, all masked elements will have the value of the object's :attr:`~Qube.default`
attribute.

Arrays with integer elements are losslessly compressed using BZ2 compression. The numeric
range is checked and values are stored using the fewest number of bytes sufficient to
cover the range. Arrays with boolean elements are converted to bit arrays and then
compressed using BZ2. These steps allow for extremely efficient data storage.

This module employs a variety of options for compressing floating point values.

1. Very small arrays are stored using BZ2 compression.
2. Constant arrays are stored as a single value plus a shape.
3. Array values are divided by a specified constant and then stored as integers, using BZ2
   compression, as described above.
4. Arrays are compressed, with or without loss, using **fpzip**. This is a highly
   effective algorithm, especially for arrays such as backplanes that often exhibit smooth
   variations from pixel to pixel. See https://pypi.org/project/rms-fpzip/.

For each object, the user can define the floating-point compression method using
:meth:`~Qube.set_pickle_digits`. One can also define the global default compression method
using :meth:`~Qube.set_default_pickle_digits`. The inputs to these functions are as
follows:

**digits** (`str, int, or float`): The number of digits to preserve.

* "double": preserve full precision using lossless **fpzip** compression.
* "single": convert the array to single precision and then store it using lossless
  **fpzip** compression.
* an number 7-16, defining the number of significant digits to preserve.

**reference** (`str or float`): How to interpret a numeric value of **digits**.

* "fpzip": Use lossy **fpzip** compression, preserving the given number of digits.
* a number: Preserve every number to the exact same absolute precision, scaling the number
  of **digits** by this value. For example, if **digits** = 8 and **reference** = 100,
  all values will be rounded to the nearest 1.e-6 before storage. This method uses option
  3 above, where values are converted to integers for storage.

The remaining options for **reference** provide a variety of ways for its value to be
generated automatically.

* "smallest": Absolute accuracy will be `10**(-digits)` times the non-zero array value
  closest to zero. This option guarantees that every value will preserve at least the
  requested number of digits. This is reasonable if you expect all values to fall within a
  similar dynamic range.
* "largest": Absolute accuracy will be `10**(-digits)` times the value in the array
  furthest from zero. This option is useful for arrays that contain a limited range of
  values, such as the components of a unit vector or angles that are known to fall between
  zero and `2*pi`. In this case, it is probably not necessary to preserve the extra
  precision in values that just happen to fall very close zero.
* "mean": Absolute accuracy will be `10**(-digits)` times the mean of the absolute values
  in the array.
* "median": Absolute accuracy will be `10**(-digits)` times the median of the absolute
  values in the array. This is a good choice if a minority of values in the array are very
  different from the others, such as noise spikes or undefined geometry. In such a case,
  we want the precision to be based on the more "typical" values.
* "logmean": Absolute accuracy will be `10**(-digits)` times the log-mean of the absolute
  values in the array.
"""

from polymath.boolean    import Boolean
from polymath.matrix     import Matrix
from polymath.matrix3    import Matrix3
from polymath.pair       import Pair
from polymath.polynomial import Polynomial
from polymath.quaternion import Quaternion
from polymath.qube       import Qube
from polymath.scalar     import Scalar
from polymath.unit       import Unit
from polymath.vector     import Vector
from polymath.vector3    import Vector3

import polymath.extensions

try:
    from ._version import __version__
except ImportError:                         # pragma nocover
    __version__ = 'Version unspecified'

__all__ = [
    'Boolean',
    'Matrix',
    'Matrix3',
    'Pair',
    'Polynomial',
    'Quaternion',
    'Qube',
    'Scalar',
    'Unit',
    'Vector',
    'Vector3',
]

##########################################################################################
