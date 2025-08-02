[![GitHub release; latest by date](https://img.shields.io/github/v/release/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/releases)
[![Test Status](https://img.shields.io/github/actions/workflow/status/SETI/rms-polymath/run-tests.yml?branch=main)](https://github.com/SETI/rms-polymath/actions)
[![Documentation Status](https://readthedocs.org/projects/rms-polymath/badge/?version=latest)](https://rms-polymath.readthedocs.io/en/latest/?badge=latest)
[![Code coverage](https://img.shields.io/codecov/c/github/SETI/rms-polymath/main?logo=codecov)](https://codecov.io/gh/SETI/rms-polymath)
<br />
[![PyPI - Version](https://img.shields.io/pypi/v/rms-polymath)](https://pypi.org/project/rms-polymath)
[![PyPI - Format](https://img.shields.io/pypi/format/rms-polymath)](https://pypi.org/project/rms-polymath)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rms-polymath)](https://pypi.org/project/rms-polymath)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rms-polymath)](https://pypi.org/project/rms-polymath)
<br />
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/SETI/rms-polymath/latest)](https://github.com/SETI/rms-polymath/commits/main/)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/commits/main/)
[![GitHub last commit](https://img.shields.io/github/last-commit/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/commits/main/)
<br />
[![Number of GitHub open issues](https://img.shields.io/github/issues-raw/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/issues)
[![Number of GitHub closed issues](https://img.shields.io/github/issues-closed-raw/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/issues)
[![Number of GitHub open pull requests](https://img.shields.io/github/issues-pr-raw/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/pulls)
[![Number of GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed-raw/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/pulls)
<br />
![GitHub License](https://img.shields.io/github/license/SETI/rms-polymath)
[![Number of GitHub stars](https://img.shields.io/github/stars/SETI/rms-polymath)](https://github.com/SETI/rms-polymath/stargazers)
![GitHub forks](https://img.shields.io/github/forks/SETI/rms-polymath)

# Introduction

`PolyMath` expands on the NumPy module and introduces a variety of additional data types
and features to simplify 3-D geometry calculations. It is a product of the the [PDS
Ring-Moon Systems Node](https://pds-rings.seti.org).

# Installation

The `PolyMath` module is available via the `rms-polymath` package on PyPI and can be installed with:

```sh
pip install rms-polymath
```

# Getting Started

The typical way to use this is just to include this line in your programs:

    import polymath

or

    from polymath import (Boolean, Matrix, Matrix3, Pair, Quaternion, Qube, Scalar, Unit,
                          Vector, Vector3)

# Features

The PolyMath classes are:

* `Scalar`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.scalar.Scalar):
  A single zero-dimensional number.
* `Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector.Vector):
  An arbitrary 1-D object.
* `Pair`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.pair.Pair):
  A subclass of `Vector` representing a vector with two coordinates.
* `Vector3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3):
  A subclass of `Vector` representing a vector with three coordinates.
* `Matrix`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix.Matrix):
  An arbitrary 2-D matrix.
* `Matrix3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix3.Matrix3):
  A subclass of `Matrix` representing a unitary 3x3 rotation matrix.
* `Quaternion`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.quaternion.Quaternion):
  A subclass of `Vector` representing a 4-component quaternion.
* `Boolean`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.boolean.Boolean):
  A True or False value.
* `Qube`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.qube.Qube):
The superclass of all of the above, supporting objects of arbitrary dimension.

Importantly, each of these classes can represent not just a single object, but also an
arbitrary array of these objects. Mathematical operations on arrays follow NumPy's rules
of "broadcasting"; see
[https://numpy.org/doc/stable/user/basics.broadcasting.html](https://numpy.org/doc/stable/user/basics.broadcasting.html)
for
these details. The key advantage of PolyMath's approach is that it separates each object's
shape from any internal dimensions (e.g., (3,3) for a `Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix3.Matrix3)
object), largely eliminating
any need to ever do "index bookkeeping". For example, suppose **S** is a Scalar and **V** is a
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector.Vector).
Then, in PolyMath, you can write:

    S * V

whereas, in NumPy, you would have to write:

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
  `shrink`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.shrink)
  method to speed up math operations by excluding all the masked
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

* **los** is a single
  `Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
  that represents the lines of sight represented by
  each sample in the data product. If the product is a 1000x1000 image, then **los** will
  have an internal shape of (1000,1000). If the product is a single detector, then **los**
  will have no internal shape.

* **time** is a
  `Scalar`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.scalar.Scalar)
  that represents the time that the photons arrived at the detector.
  If the instrument is a simple, shuttered camera, then all photons arrive at the same
  time and **time** can have a single value. However, if a raster-scanning device obtains
  a 1000x1000 image, then **time** will have an internal shape of (1000,1000), with each
  element representing the unique arrival time at that pixel. For a "pushbroom" camera,
  the detector receives the image line by line, so **time** will have an internal shape of
  (1000,1) or (1,1000), depending on the orientation of the detector.

* **cmatrix** is a
  `Matrix3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix3.Matrix3)
  that represents the rotation matrix from the instrument's
  internal coordinates to the J2000 frame, which is fixed relative to the sky. If the
  instrument is not rotating during an observation, then a single matrix is required.
  However, if the camera is on a rotating platform and it samples photons at different
  times, then **cmatrix** may need to have an internal shape of (1000,1000) to describe a
  1000x1000 image. Furthermore, the rate of change of **cmatrix** can be described by a
  derivative with respect to time. When one calculates where the lines of sight
  intercepted a target body, the time derivative of **cmatrix** can then be used to
  determine the amount of smear in the image.

Although different types of data products might have very different internal
representations, PolyMath makes it possible to write a geometry calculation just once and
then re-use it for all of these situations.

As a specific example, OOPS can determine where each line of sight sampled by a data
product intercepted the surface of a particular planetary body. The intercept points are
represented by a single
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
given in the body's coordinate frame. From this
object, it is straightforward to derive latitude, longitude, emission angle, etc. If the
product is a 1000x1000 image, then the
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
will have an internal shape of
(1000,1000). Furthermore, if the body does not entirely fill the field of view, the lines
of sight that did not intercept the body are masked. It is not uncommon for a body to only
partially fill a field of view. In this case, OOPS can speed up calculations, sometimes
substantially, by omitting the masked elements of the
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
object.

## Math Operations

All standard mathematical operators and indexing/slicing options are defined for PolyMath
objects, where appropriate: `+`, `-`, `*`, `/`, `%`, `//`,`**`, along with their in-place
variants. Equality tests `==`, `!=` are available for all objects; comparison operators
`<`, `<=`, `>`, `>=` are supported for Scalars and Booleans. Where appropriate, methods
such as
`abs()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.qube.Qube.abs),
`len()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.len),
`mean()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mean),
`sum()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.sum),
`identity()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.identity),
`reciprocal()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.reciprocal),
`int()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.int),
`Matrix.inverse()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix.Matrix.inverse),
and
`Matrix.transpose()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix.Matrix.transpose)
(or property `Matrix.T`).

`Scalar`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.scalar.Scalar):
support most common math functions such as
`sin()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.sin),
`cos()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.cos),
`tan()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.tan),
`arcsin()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.arcsin),
`arccos()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.arccos),
`arctan()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.arctan),
`arctan2()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.arctan2),
`sqrt()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.sqrt),
`log()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.log),
`exp()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.exp),
`sign()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.sign),
`int()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.int),
`frac()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.frac),
`min()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.min),
`max()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.max),
`argmin()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.argmin),
`argmax()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.argmax),
`minimum()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.minimum),
`maximum()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.maximum),
`median()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.median),
and
`sort()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.sort).
It also supports quadratic equations via
`solve_quadratic()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.solve_quadratic)
and
`eval_quadratic()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.eval_quadratic).

`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector.Vector):
support functions such as
`norm()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.norm),
`norm_sq()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.norm_sq),
`unit()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.unit),
`dot()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.dot),
`cross()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.cross),
`ucross()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.ucross),
`outer()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.outer)
(outer product),
`perp()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.perp)
(perpendicular vector),
`proj()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.proj)
(projection), and
`sep()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.sep)
(separation angle).
Element-by-element operations are also supported using
`element_mul()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.element_mul)
and
`element_div()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.element_div).

`Vector3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3):
supports additional functions such as
`from_ra_dec_length()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.from_ra_dec_length),
`to_ra_dec_length()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.to_ra_dec_length),
`from_cylindrical()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.from_cylindrical),
`to_cylindrical()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.to_cylindrical),
`longitude()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.longitude),
`latitude()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.latitude),
`spin()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.spin)
(rotate one vector about another), and
`offset_angles()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector3.offset_angles)
(the angles from the three primary axes).

`Pair`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.pair.Pair):
supports additional functions such as
`swapxy()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Pair.swapxy),
`rot90()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Pair.rot90)
(for
rotation by a multiple of 90 degrees), and
`angle()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Pair.angle)
(for the vector's angular
direction).

`Matrix3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix3.Matrix3):
functions
`rotate()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.rotate)
and
`unrotate()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.unrotate)
apply a rotation
to another object. Methods
`x_rotation()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.x_rotation),
`y_rotation()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.y_rotation),
`z_rotation()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.z_rotation),
`axis_rotation()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.axis_rotation),
`pole_rotation()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.pole_rotation),
`from_euler()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.from_euler),
and
`unitary()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.unitary)
are convenient, alternative ways to define a rotation matrix. Use
`to_euler()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.to_euler)
and
`to_quaternion()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.to_quaternion)
to reverse these definitions.

`Quaternion`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.quaternion.Quaternion):
supports functions such as
`conj()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.conj)
(conjugate),
`to_parts()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.to_parts)
(for the Scalar and Vector3 components),
`from_parts()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.from_parts)
(to construct from the Scalar and Vector3 components),
`to_rotation()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.to_rotation)
(for the transform as a direction Vector3 and rotation
angle),
`from_matrix3()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.from_matrix3),
`to_matrix3()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.to_matrix3),
`from_euler()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.from_euler),
and
`to_euler()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Quaternion.to_euler).

The `values` (or `vals`) property of each object returns its value
as a NumPy array. For `Scalar` objects with no shape, `values` is a
Python-native value of float or int; for `Boolean` objects with no shape,
`values` is a Python-native bool.

One can generally mix PolyMath arithmetic with scalars, NumPy ndarrays, NumPy
MaskedArrays, or anything array-like.

## Shapes and Broadcasting

The PolyMath subclasses, e.g.,
`Scalar`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.scalar.Scalar),
`Vector3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3),
and
`Matrix3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix3.Matrix3),
define one or more possibly multidimensional items. Unlike NumPy ndarrays, this class
makes a clear distinction between the dimensions associated with the items and any
additional, leading dimensions that define an array of such items.

Each object's `shape` property contains the shape of its leading axes, whereas
its `item` property defines the shape of individual elements. For example, a
2x2 array of `Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix3.Matrix3)
objects would have `shape=(2,2)` and `items=(3,3)`. Its
`values` property would be a NumPy array with shape `(2,2,3,3)`. In addition,
`ndims` (or `ndim`) contains the number of dimensions in the
shape; `size` is the number of items; `rank` is the number of
dimensions in the items; `isize` is the number of item elements.

To change the shape of an object, use methods
`reshape()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.reshape),
`flatten()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.flatten),
`move_axis()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.move_axis),
`roll_axis()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.roll_axis),
and
`swap_axes()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.swap_axes).
These all return a shallow copy of an object, which shares memory
with the original object.

Standard NumPy rules of broadcasting apply, but only on the `shape`
dimensions, not on the `item` dimensions. For example, if you multiply a
`Matrix3`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.matrix3.Matrix3)
with shape (2,2) by a
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
object with shape (5,1,2), you
would get a new (rotated)
`Vector`
object with shape (5,2,2). See the complete
rules of broadcasting here:
[https://numpy.org/doc/stable/user/basics.broadcasting.html](https://numpy.org/doc/stable/user/basics.broadcasting.html)

If necessary, you can explicitly broadcast objects to a new shape using methods
`broadcast()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.broadcast)
and
`broadcast_to()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.broadcast_to);
these return shallow, read-only
copies. Use
`broadcasted_shape()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.broadcasted_shape)
to determine the shape that will result from
an operation involving multiple PolyMath objects and NumPy arrays.

## Derivatives

PolyMath objects can track associated derivatives and partial derivatives, which are
represented by a dictionary of other PolyMath objects. A common use case is to let **X**
be a
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector.Vector):
object describing the position of one or more bodies or points on a
surface and to use the time-derivative of **X** to describe the velocity. The
`derivs` property of an object is a dictionary of each derivative, keyed by
its name. For example, a time-derivative is often keyed by **t**. For convenience, you can
also reference each derivative by the attribute name "`d_d`" plus the key, so the
time-derivative of **X** can be accessed via **X.d_dt**. This feature makes it possible to
write an algorithm describing the positions of bodies or features, and to have any
time-derivatives carried along in the calculation with no additional programming effort.

The denominators of partial derivatives are represented by splitting the item shape into a
numerator shape plus a denominator shape. As a result, for example, the partial
derivatives of a `Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
object (item shape (3,)) with respect to a :class:`Pair`
(item shape (2,)) will have overall item shape (3,2). Properties `numer` gives
the numerator shape, `nrank` is the number of dimensions, and
`nsize` gives the number of elements. Similarly, `denom` is the
denominator shape, `drank` is the number of dimensions, and
`dsize` is the number of elements.

The PolyMath subclasses generally do not constrain the shape of the denominator, just
the numerator. As a result, the aforementioned partial derivatives can still be
represented by a
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
object.

Methods
`insert_deriv()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.insert_deriv),
`insert_derivs()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.insert_derivs),
`delete_deriv()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.delete_deriv),
`delete_derivs()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.delete_derivs),
and
`rename_deriv()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.rename_deriv)
can be used to add, remove, or modify derivatives after it has been constructed. You can
also obtain a shallow copy of an object with one or more derivatives removed using
`without_deriv()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.without_deriv)
and
`without_derivs()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.without_derivs).
For convenience, the
`wod` property is equivalent to
`without_derivs()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.without_derivs).
Note that the
presence of derivatives inside an object can slow computational performance significantly,
so it can useful to suppress derivatives from a calculation if they are not needed. Note
that many math functions have a `recursive` option that defaults to True; set it to False
to ignore derivatives within the given calculation.

A number of methods are focused on modifying the numerator and denominator components of
objects:
`extract_numer()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.extract_numer),
`extract_denom()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.extract_denom),
`extract_denoms()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.extract_denoms),
`slice_numer()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.slice_numer),
`transpose_numer()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.transpose_numer),
`reshape_numer()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.reshape_numer),
`flatten_numer()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.flatten_numer),
`transpose_denom()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.transpose_denom),
`reshape_denom()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.reshape_denom),
`flatten_denom()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.flatten_denom),
`join_items()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.join_items),
`split_items()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.split_items),
and
`swap_items()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.swap_items).

The function
`chain()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.chain)
can be used for chain-multiplication of derivatives; this
is also implemented via the `@` operator.

## Masks

Every object has a boolean mask, which identifies undefined values or array elements.
Operations that would otherwise raise errors such as 1/0 and sqrt(-1) are masked, so that
run-time warnings and exceptions can be avoided.  A common use case is to have a
"backplane" array describing the geometric content of a planetary image, where the mask
identifies the pixels that do not intersect the surface.

Each object has a property `mask`, which contains the mask. A single value of
False means that the object is entirely unmasked; a single value of True means it is
entirely masked. Otherwise, `mask` is a NumPy array with boolean values, with
a shape that matches that of the object itself (excluding its `items`). For example, a
`Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector3.Vector3)
object with shape `(5,2)` could have a `mask` value represented
by a NumPy array of shape `(5,2)`, even though its `values` property has shape
`(5,2,3)`.

The `mvals` property of an object returns its `values` property as a NumPy MaskedArray.

Each object also has a property `antimask`, which is the "logical not" of the
`mask`. Use the `antimask` as an index to select only the unmasked
elements of an object. You can also use the
`shrink()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.shrink)
method to temporarily
eliminate masked elements from an object, potentially speeding up calculations; use
`unshrink()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.unshrink)
when you are done to restore the original shape.

Under normal circumstances, a masked value should be understood to mean, "this value
does not exist." For example, a calculation of observed intercept points on a moon is
masked if a line of sight missed the moon, because that line of sight does not exist. This
is similar to NumPy's not-a-number ("NaN") concept, but there are important differences.
For example,

* Two masked values of the same class are considered equal. This is different from the
  behavior of NaN.
* Unary and binary operations involving masked values always return masked values.
* Because masked values are treated as if they do not exist,
`max()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.max)
returns
  the maximum among the unmasked values;
`all()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.all)
returns True if all the
  unmasked values are True (or nonzero).

However, PolyMath also provides boolean methods to support an alternative interpretation
of masked values as indeterminate rather than nonexistent. These follow the rules of
"three-valued logic:

* `tvl_and()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.tvl_and)
  returns False if one value is False but the other is masked,
  because the result would be False regardless of the second value.
* `tvl_or()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.tvl_or)
  returns True if one value is True but the other is masked, because
  the result would be True regardless of the second value.
* `tvl_all()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.tvl_all)
  returns True only if and only all values are True; if any value is
  False, it returns False; if the only values are True or indeterminate, its value is
  indeterminate (meaning masked).
* `tvl_any()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.tvl_any)
  returns True if any value is True; it returns False if every value
  is False; if the only values are False or indeterminate, its value is indeterminate.
* `tvl_eq()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.tvl_eq)
  and
  `tvl_ne()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.tvl_ne)
  are indeterminate if either value is
  indeterminate.

You can only define an object's mask at the time it is constructed. To change a mask, use
`remask()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.remask)
or
`remask_or()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.remask_or),
which return a shallow copy of the object
(sharing memory with the original) but with a new mask. You can also use a variety of
methods to construct an object with a new mask:
`mask_where()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where),
`mask_where_eq()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_eq),
`mask_where_ge()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_ge),
`mask_where_gt()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_gt),
`mask_where_le()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_le),
`mask_where_lt()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_lt),
`mask_where_ne()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_ne),
`mask_where_between()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_between),
`mask_where_outside()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.mask_where_outside),
and
`clip()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.clip).

## Units

PolyMath objects also support embedded unit using the
`Unit`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.unit.Unit)
class. However, the
internal values in a PolyMath object are always held in standard units of kilometers,
seconds and radians, or arbitrary combinations thereof. The unit is primarily used to
affect the appearance of numbers during input and output. The `unit_` or
`units` property of any object will reveal the
`Unit`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.unit.Unit)
object, or
possibly None if the object is unitless.

A `Unit`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.unit.Unit)
allows for exact conversions between units. It is described by three
integer exponents applying to dimensions of length, time, and angle. Conversion factors
are describe by three (usually) integer values representing a numerator, denominator, and
an exponent on pi. For example, `Unit.DEGREE` is represented by exponents (0,0,1)
and factors (1,180,1), indicating that the conversion factor is `pi/180`. Most other common
units are described by class constants; see the
`Unit`
class for details.

Normally, you specify the unit of an object at the time it is constructed. However, the
method
`set_unit()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.set_unit)
is available to set the `unit` property afterward.

## Read-only Objects

PolyMath objects can be either read-only or read-write. Read-only objects are prevented
from modification to the extent that Python makes this possible. Operations on read-only
objects should always return read-only objects.

The
`as_readonly()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_readonly)
method can be used to set an object (and its
derivatives) to read-only status. It is not possible to convert an object from
read-only back to read-write; use
`copy()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.copy)
instead. The
`readonly` property is True if the object is read-only; False if it is
read-write.

## Alternative Constructors

Aside from the explicit constructor methods, numerous methods are available to construct
objects from other objects. Methods include
`copy()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.copy),
`clone()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.clone),
`cast()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.cast),
`zeros()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.zeros),
`ones()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.ones),
`filled()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.filled),
`as_this_type()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_this_type),
`as_all_constant()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_all_constant),
`as_size_zero()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_size_zero),
`masked_single()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.masked_single),
`as_numeric()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_numeric),
`as_float()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_float),
`as_int()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_int),
and
`as_bool()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_bool).
There are also methods to convert between
classes, such as
`Vector.from_scalars()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.Vector.from_scalars),
`Vector.to_scala()r`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.Vector.to_scalar),
`Vector.to_scalars()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.Vector.to_scalars),
`Matrix3.twovec()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix3.twovec),
(a rotation matrix defined by two
vectors),
`Matrix.row_vector()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix.Matrix.row_vector),
`Matrix.row_vectors()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix.Matrix.row_vectors),
`Matrix.column_vector()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix.Matrix.column_vector),
`Matrix.column_vectors()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix.Matrix.column_vectors),
and
`Matrix.to_vector()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Matrix.Matrix.to_vector),

## Indexing

Using an index on a Qube object is very similar to using one on a NumPy array, but
there are a few important differences. For purposes of retrieving selected values from
an object:

* True and False can be applied to objects with shape `()`. True leaves the object
  unchanged; False masks the object.

* An index of True selects the entire associated axis in the object, equivalent to a
  colon or `slice(None)`. An index of False reduces the associated axis to length one
  and masks the object entirely.

* A
  `Boolean`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.boolean.Boolean):
  object can be used as an index. If this index is unmasked, it is the same
  as indexing with a boolean NumPy ndarray. If it is masked, the values of the
  returned object are masked wherever the `Boolean`'s value is masked. When using a
  `Boolean` index to set items inside an object, locations where the `Boolean` index are
  masked are not changed.

* A
  `Scalar`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.scalar.Scalar):
  object composed of integers can be used as an index. If this index is
  unmasked, it is equivalent to indexing with an integer or integer NumPy ndarray. If
  it is masked, the values of the returned object are masked wherever the `Scalar`
  masked. When using a `Scalar` index to set items inside an object, locations where the
  `Scalar` index are masked are not changed.

* A
  `Pair`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.pair.Pair):
  object composed of integers can be used as an index. Each `(i,j)` value is
  treated is the index of two consecutive axes, and the associated value is returned.
  Where the `Pair` is masked, a masked value is returned. Similarly, a
  `Vector`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.vector.Vector):
  with three
  or more integer elements is treated as the index of three or more consecutive axes.

* As in NumPy, an integer valued array can be used to index a PolyMath object. In this
  case, the shape of the index array appears within the shape of the returned object.
  For example, if `A` has shape `(6,7,8,9)` and `B` has shape `(3,1)`, then `A[B]` has shape
  `(3,1,7,8,9)`; `A[:,B]` has shape `(6,3,1,8,9)`, and `A[...,B]` has shape `(6,7,8,3,1)`.

* When multiple arrays are used for indexing at the same time, the broadcasted shape
  of these array appears at the location of the first array-valued index. In the same
  example as above, suppose `C` has shape `(4,)`. Then `A[B,C]` has shape `(3,4,8,9)`,
  `A[:,B,C]` has shape `(6,3,4,9)`, and `A[:,B,:,C]` has shape `(6,3,4,8)`. Note that this
  behavior is slightly different from how NumPy handles indexing with multiple arrays.

Several methods can be used to convert PolyMath objects to objects than be used for
indexing NumPy arrays. You can obtain integer indices from
`Scalar.as_index()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.Scalar.as_index),
`Vector.as_index()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.Vector.as_index),
`Scalar.as_index_and_mask()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Scalar.Scalar.as_index_and_mask), and
`Vector.as_index_and_mask()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Vector.Vector.as_index_and_mask). You can obtain boolean masks from
`Boolean.as_index()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Boolean.Boolean.as_index),
`as_mask_where_nonzero()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_mask_where_nonzero),
`as_mask_where_zero()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_mask_where_zero),
`as_mask_where_nonzero_or_masked()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_mask_where_nonzero_or_masked),
and
`as_mask_where_zero_or_masked()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.as_mask_where_zero_or_masked).

## Iterators

Every Polymath object can be used as an iterator, in which case it performs an iteration
over the object's leading axis. Alternatively,
`ndenumerate()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.ndenumerate)
iterates over
every item in a multidimensional object.

## Pickling

Because objects such as backplanes can be numerous and also quite large, we provide a
variety of methods, both lossless and lossy, for compressing them during storage. As one
example of optimization, only the un-masked elements of an object are stored; upon
retrieval, all masked elements will have the value of the object's `default`
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
   variations from pixel to pixel. See
   [https://pypi.org/project/rms-fpzip](https://pypi.org/project/rms-fpzip).

For each object, the user can define the floating-point compression method using
`set_pickle_digits()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.set_pickle_digits).
One can also define the global default compression method
using
`set_default_pickle_digits()`[![image](https://raw.githubusercontent.com/SETI/rms-polymath/main/icons/link.png)](https://rms-polymath.readthedocs.io/en/latest/module.html#polymath.Qube.set_default_pickle_digits).
The inputs to these functions are as
follows:

**digits** (`str, int, or float`): The number of digits to preserve.

* "double": preserve full precision using lossless **fpzip** compression.
* "single": convert the array to single precision and then store it using lossless
  **fpzip** compression.
* an number 7-16, defining the number of significant digits to preserve.

**reference** (`str or float`): How to interpret a numeric value of **digits**.

* "fpzip": Use lossy **fpzip** compression, preserving the given number of digits.
* a number: Preserve every number to the exact same absolute precision, scaling the number
  of **digits** by this value. For example, if `digits=8` and `reference=100`,
  all values will be rounded to the nearest `1.e-6` before storage. This method uses option
  3 above, where values are converted to integers for storage.

The remaining options for **reference** provide a variety of ways for its value to be
generated automatically.

* "smallest": Absolute accuracy will be `10**(-digits)` times the non-zero array value
  closest to zero. This option guarantees that every value will preserve at least the
  requested number of digits. This is reasonable if you expect all values to fall within a
  similar dynamic range.
* "largest": Absolute accuracy will be `10**(-digits)` times the value in the array furthest
  from zero. This option is useful for arrays that contain a limited range of values, such
  as the components of a unit vector or angles that are known to fall between zero and
  `2*pi`. In this case, it is probably not necessary to preserve the extra precision in
  values that just happen to fall very close zero.
* "mean": Absolute accuracy will be `10**(-digits)` times the mean of the absolute values
  in the array.
* "median": Absolute accuracy will be `10**(-digits)` times the median of the absolute
  values in the array. This is a good choice if a minority of values in the array are very
  different from the others, such as noise spikes or undefined geometry. In such a case,
  we want the precision to be based on the more "typical" values.
* "logmean": Absolute accuracy will be `10**(-digits)` times the log-mean of the absolute
  values in the array.

# Contributing

Information on contributing to this package can be found in the
[Contributing Guide](https://github.com/SETI/rms-polymath/blob/main/CONTRIBUTING.md).

# Links

- [Documentation](https://rms-polymath.readthedocs.io)
- [Repository](https://github.com/SETI/rms-polymath)
- [Issue tracker](https://github.com/SETI/rms-polymath/issues)
- [PyPi](https://pypi.org/project/rms-polymath)

# Licensing

This code is licensed under the [Apache License v2.0](https://github.com/SETI/rms-polymath/blob/main/LICENSE).
