##########################################################################################
# polymath/qube.py: Base class for all PolyMath subclasses.
##########################################################################################

import numpy as np
import numbers

from polymath.unit import Unit


class Qube(object):
    """The base class for all PolyMath subclasses.

    The PolyMath subclasses, e.g., Scalar, Vector3, Matrix3, etc., define one or more
    possibly multidimensional items. Unlike NumPy ndarrays, this class makes a clear
    distinction between the dimensions associated with the items and any additional,
    leading dimensions that define an array of such items.

    The "shape" is defined by the leading axes only, so a 2x2 array of 3x3 matrices would
    have shape (2,2,3,3) according to NumPy but has shape (2,2) according to PolyMath.
    Standard NumPy rules of broadcasting apply, but only on the array dimensions, not on
    the item dimensions. In other words, you can multiply a (2,2) array of 3x3 matrices by
    a (5,1,2) array of 3-vectors, yielding a (5,2,2) array of 3-vectors.

    PolyMath objects are designed as lightweight wrappers on NumPy ndarrays. All standard
    mathematical operators and indexing/slicing options are defined. One can generally mix
    PolyMath arithmetic with scalars, NumPy ndarrays, NumPy MaskedArrays, or anything
    array-like.

    In every object, a boolean mask is maintained in order to identify undefined array
    elements. Operations that would otherwise raise errors such as 1/0 and sqrt(-1) are
    masked out so that run-time errors can be avoided. See more about masks below.

    PolyMath objects also support embedded units using the Unit class. However, the
    internal values in a PolyMath object are always held in standard units of kilometers,
    seconds and radians, or arbitrary combinations thereof. The unit is primarily used
    to affect the appearance of numbers during input and output.

    PolyMath objects can be either read-only or read-write. Read-only objects are
    prevented from modification to the extent that Python makes this possible. Operations
    on read-only objects should always return read-only objects.

    PolyMath objects can track associated derivatives and partial derivatives, which are
    represented by other PolyMath objects. Mathematical operations generally carry all
    derivatives along so that, for example, if x.d_dt is the derivative of x with respect
    to t, then x.sin().d_dt will be the derivative of sin(x) with respect to t.

    The denominators of partial derivatives are represented by splitting the item shape
    into a numerator shape plus a denominator shape. As a result, for example, the partial
    derivatives of a Vector3 object (item shape (3,)) with respect to a Pair (item shape
    (2,)) will have overall item shape (3,2).

    The PolyMath subclasses generally do not constrain the shape of the denominator, just
    the numerator. As a result, the aforementioned partial derivatives can still be
    represented by a Vector3 object.

    Properties:
        shape (tuple):
            The leading axes of the object, i.e., those that are not considered part of
            the items.
        rank (int):
            The number of axes belonging to the items.
        nrank (int):
            The number of numerator axes associated with the items.
        drank (int):
            The number of denominator axes associated with the items.
        item (tuple):
            The shape of the individual items.
        numer (tuple):
            The shape of the numerator items.
        denom (tuple):
            The shape of the denominator items.
        values (numpy.ndarray, float, int, or bool):
            The object's data, with shape object.shape + object.item. If the object has a
            unit, then the values are in default units (km, sec, etc.) rather than in the
            specified unit.
        vals (numpy.ndarray, float, int, or bool):
            Alternative name for `values`.
        mask (numpy.ndarray or bool):
            The array's mask. A scalar False means the object is entirely unmasked; a
            scalar True means it is entirely masked. Otherwise, it is a boolean array of
            shape object.shape.
        unit (Unit or None):
            The unit of the array, if any. None indicates no unit.
        derivs (dict):
            A dictionary of the names and values of any derivatives, each represented by
            additional PolyMath object.
        readonly (bool):
            True if the object cannot (or at least should not) be modified. A determined
            user may be able to alter a read-only object, but the API makes this more
            difficult.
        size (int):
            The number of elements in the shape.
        isize (int):
            The number of elements in each item.
        nsize (int):
            The number of elements in the numerator of the items.
        dsize (int):
            The number of elements in the denominator of the items.
    """

    # This prevents binary operations of the form:
    #   <np.ndarray> <op> <Qube>
    # from executing the ndarray operation instead of the polymath operation
    __array_priority__ = 1

    # Global attribute to be used for testing
    _DISABLE_CACHE = False

    # If this global is set to True, the shrink/unshrink methods are disabled.
    # Calculations done with and without shrinking should always produce the same results,
    # although they may be slower with shrinking disabled. Used for testing and debugging.
    _DISABLE_SHRINKING = False

    # If this global is set to True, the unshrunk method will ignore any cached value of
    # its un-shrunken equivalent. Used for testing and debugging.
    _IGNORE_UNSHRUNK_AS_CACHED = False

    # Default class constants, to be overridden as needed by subclasses...
    _NRANK = None       # The number of numerator axes; None to leave this unconstrained.
    _NUMER = None       # Shape of the numerator; None to leave unconstrained.
    _FLOATS_OK = True   # True to allow floating-point numbers.
    _INTS_OK = True     # True to allow integers.
    _BOOLS_OK = True    # True to allow booleans.
    _UNITS_OK = True    # True to allow units; False to disallow them.
    _DERIVS_OK = True   # True to allow derivatives and denominators; False to disallow.

    def __new__(subtype, *values, **keywords):
        """Create a new, un-initialized object given a Qube subclass."""

        return object.__new__(subtype)

    def __init__(self, arg, mask=False, *, derivs={}, unit=None, nrank=None, drank=None,
                 example=None, default=None, op=''):
        """Default constructor.

        Parameters:
            arg (Qube, array-like, float, in, or bool), : An object to define the numeric
                value(s) of the returned object. If this object is read-only, then the
                returned object will be entirely read-only. Otherwise, the object will be
                read-writable. The values are generally given in standard units of km,
                seconds and radians, regardless of the specified unit.
            mask (Boolean, array-like, or bool, optional): The mask for the object. Use
                None to copy the mask from the example object. False (the default) leaves
                the object un-masked.
            derivs (dict, optional): Derivatives represented as PolyMath objects. Use None
                to make a copy of the derivs attribute of the example object, or {} (the
                default) for no derivatives. All derivatives are broadcasted to the shape
                of the object if necessary.
            unit (Unit, optional): The unit of the object. Use None to infer the unit from
                the example object; use False to suppress the unit.
            nrank (int, optional): The number of numerator axes in the returned object;
                None to derive the rank from the input data and/or the subclass.
            drank (int, optional): The number of denominator axes in the returned object;
                None to derive it from the input data and/or the subclass.
            example (Qube, optional): Another Qube object from which to copy any input
                arguments except derivs that have not been explicitly specified.
            default (array-like, float, int, or bool): Value to use where masked. This is
                typically a constant that will not "break" most arithmetic calculations.
                If it is an array, it must be of the same shape as the items.
            op (str, optional): Name of an operation to include in an error message if
                something goes wrong.

        Raises:
            TypeError: If the data type of `arg` or `mask` is invalid.
            TypeError: If `example` is not an instance of Qube.
            ValueError: If the shape of `mask` is incompatible with object.
            ValueError: If `derivs` or `unit` are specified but are disallowed by the
                Qube subclass.
            ValueError: If `nrank` is incompatible with the Qube subclass.
            ValueError: If `drank` is specified but the Qube subclass disallows
                derivatives.
            ValueError: If the dimensions of `arg` are incompatible with the subclass.
        """

        opstr = Qube._opstr(self, op)

        # Set defaults based on a Qube input
        if isinstance(arg, Qube):

            if derivs is None:
                derivs = arg._derivs.copy()     # shallow copy

            if unit is None:
                unit = arg._unit

            if nrank is None:
                nrank = arg._nrank
            elif nrank != arg._nrank:           # nranks _must_ be compatible
                self._nrank = nrank
                Qube._raise_incompatible_numers(op, self, arg)

            if drank is None:
                drank = arg._drank
            elif drank != arg._drank:           # dranks _must_ be compatible
                self._drank = drank
                Qube._raise_incompatible_denoms(op, self, arg)

            if default is None:
                default = arg._default

        # Set defaults based on an example object
        if example is not None:

            if not isinstance(example, Qube):
                raise TypeError(f'{opstr} example value is not a Qube subclass')

            if mask is None:
                mask = example._mask

            if unit is None and self._UNITS_OK:
                unit = example._unit

            if nrank is None and self._NRANK is None:
                nrank = example._nrank

            if drank is None:
                drank = example._drank

            if default is None:
                default = example._default

        # Validate inputs
        nrank = nrank or self._NRANK or 0
        drank = drank or 0
        rank = nrank + drank

        if derivs and not self._DERIVS_OK:
            raise ValueError(f'{opstr} derivatives are disallowed')

        if unit and not self._UNITS_OK:
            raise TypeError(f'{opstr} unit is disallowed: {unit}')

        if self._NRANK is not None:
            if nrank is not None and nrank != self._NRANK:
                raise ValueError(f'invalid {opstr} numerator rank: {nrank}')

        if drank and not self._DERIVS_OK:
            raise ValueError(f'{opstr} denominators are disallowed')

        # Get the value and check its shape
        (values, arg_mask) = Qube._as_values_and_mask(arg, opstr=opstr)
        full_shape = np.shape(values)
        if len(full_shape) < rank:
            raise ValueError(f'invalid {opstr} array shape {full_shape}: '
                             f'minimum rank = {nrank} + {drank}')

        dd = len(full_shape) - drank
        nn = dd - nrank
        denom = full_shape[dd:]
        numer = full_shape[nn:dd]
        item  = full_shape[nn:]
        shape = full_shape[:nn]

        # Fill in the values
        self._values = self._suitable_value(values, numer=numer, denom=denom,
                                            opstr=opstr)
        self._is_array = isinstance(self._values, np.ndarray)
        self._is_scalar = not self._is_array

        # Get the mask and check its shape
        mask = Qube.or_(arg_mask, Qube._as_mask(mask, opstr=opstr))
        collapse = isinstance(arg, np.ma.MaskedArray)
        self._mask = Qube._suitable_mask(mask, shape=shape, broadcast=True,
                                         collapse=collapse, check=False, opstr=opstr)

        # Fill in the remaining shape info
        self._shape = shape
        self._ndims = len(shape)
        self._rank  = rank
        self._nrank = nrank
        self._drank = drank
        self._item  = item
        self._numer = numer
        self._denom = denom
        self._size  = int(np.prod(shape))
        self._isize = int(np.prod(item))
        self._nsize = int(np.prod(numer))
        self._dsize = int(np.prod(denom))

        # Fill in the unit
        self._unit = None if Qube.is_one_false(unit) else unit

        # The object is read-only if the values array is read-only
        self._readonly = Qube._array_is_readonly(self._values)

        if self._readonly:
            Qube._array_to_readonly(self._mask)

        # Used for anything we want to cache in association with an object. This cache
        # will be cleared whenever the object is modified in any way.
        self._cache = {}

        # Install the derivs (converting to read-only if necessary)
        self._derivs = {}
        if derivs:
            self.insert_derivs(derivs)

        # Used only for if clauses; filled in when needed
        self._truth_if_any = False
        self._truth_if_all = False

        # Fill in the default
        if default is not None and np.shape(default) == item:
            pass
        elif hasattr(self, '_DEFAULT_VALUE') and drank == 0:
            default = self._DEFAULT_VALUE
        elif item:
            default = np.ones(item)
        else:
            default = 1

        dtype = Qube._dtype(self._values)
        self._default = Qube._casted_to_dtype(default, dtype)

    ######################################################################################
    # Builtin type support
    ######################################################################################

    _PREFER_BUILTIN_TYPES = False

    @staticmethod
    def prefer_builtins(status=None):
        """Set a global flag defining whether certain functions return a Python builtin
        type, rather than a Qube subclass, if possible.

        Parameters:
            status (bool, optional): True to favor Python builtin types; False otherwise.
                Omit this input to leave the global setting unchanged (but return it).

        Returns:
            bool: True if builtins are globally preferred; False otherwise.
        """

        if status is not None:
            Qube._PREFER_BUILTIN_TYPES = status

        return Qube._PREFER_BUILTIN_TYPES

    def as_builtin(self, masked=None):
        """This object as a Python built-in class (float, int, or bool) if the conversion
        can be done without loss of information.

        Parameters:
            masked (float, int, or bool, optional): Value to return if the shape of this
                object is () and it is masked.

        Returns:
            (Qube, float, int, bool, or None): This object's `values` attribute if its
            shape is () and it is unmasked; the value of `masked` if the shape is () and
            it is masked; otherwise, this object.
        """

        values = self._values
        if np.size(values) == 0:
            return self         # previously, erroneously returned `masked`
        if np.shape(values):
            return self

        # Now we know shape is ()
        if self._mask:
            return self if masked is None else masked

        if not self.is_unitless():
            return self

        if isinstance(values, (bool, np.bool_)):
            return bool(values)
        if isinstance(values, numbers.Integral):
            return int(values)
        if isinstance(values, numbers.Real):
            return float(values)

        return self     # This shouldn't happen                             # noqa

    ######################################################################################
    # Support functions
    ######################################################################################

    @staticmethod
    def _has_qube(arg):
        """True if the given list or tuple contains a Qube somewhere within."""

        if isinstance(arg, (list, tuple)):
            return (any(isinstance(item, Qube) for item in arg) or
                    any(Qube._has_qube(item) for item in arg))

        return False

    @staticmethod
    def _has_masked_array(arg):
        """True if the given list or tuple contains a MaskedArray somewhere within."""

        if isinstance(arg, (list, tuple)):
            return (any(isinstance(item, np.ma.MaskedArray) for item in arg) or
                    any(Qube._has_masked_array(item) for item in arg))

        return False

    @staticmethod
    def _as_values_and_mask(arg, opstr=''):
        """This object converted to a scalar or Numpy array with optional mask.

        Parameters:
            arg: object to convert to a scalar or array.
            opstr (str, optional): Name of operation string to include in any error
                message.

        Returns:
            tuple: (`value`, `mask`) as inferred from `arg`.

        Raises:
            TypeError: If the data type of `arg` is invalid.
        """

        if isinstance(arg, numbers.Real):
            return (arg, False)

        if isinstance(arg, np.ma.MaskedArray):
            return (arg.data, arg.mask)

        if isinstance(arg, np.ndarray):
            return (arg, False)

        if isinstance(arg, Qube):
            return (arg._values, arg._mask)

        if isinstance(arg, (list, tuple)):
            if Qube._has_qube(arg):
                merged = Qube.stack(*arg)
                return (merged._values, merged._mask)
            elif Qube._has_masked_array(arg):
                merged = np.ma.stack(*arg)
                return (merged.data, merged.mask)
            else:
                merged = np.array(arg)
                return (merged, False)

        if isinstance(arg, np.bool_):
            return (bool(arg), False)

        _opstr = ' ' + opstr if opstr else ''
        raise TypeError(f'invalid{_opstr} data type: {type(arg)}')

    @staticmethod
    def _as_mask(arg, *, invert=False, masked_value=True, opstr=''):
        """This argument converted to a scalar bool or boolean Numpy array.

        Parameters:
            arg: The object to convert to a mask.
            invert (bool, optional): True to return the logical not of the mask.
            masked_value (bool, optional): The value to use where the input argument is
               masked. This value is used _after_ `invert` is applied.
            opstr (str, optional): Name of operation to include in any error message.

        Returns:
            (bool or NumPy.ndarray): bool or boolean array suitable for us as a mask.

        Raises:
            TypeError: If the data type of `arg` is invalid for a mask.
        """

        # Handle most common cases first
        if isinstance(arg, (numbers.Real, np.bool_, type(None))):
            return bool(arg) != invert

        if type(arg) is np.ndarray:     # exact type, not a subclass
            if arg.dtype.kind == 'b' and not invert:
                return arg
            elif invert:
                return arg == 0
            else:
                return arg != 0

        # Convert a list or tuple to something else
        if isinstance(arg, (list, tuple)):
            if Qube._has_qube(arg):
                arg = Qube.stack(*arg)
            elif Qube._has_masked_array(arg):
                arg = np.ma.stack(*arg)
            else:
                arg = np.array(arg)
                return Qube._as_mask(arg, invert=invert,  masked_value=masked_value,
                                     opstr=opstr)

        # Handle an object with a possible mask
        if isinstance(arg, Qube):
            mask = arg._mask
            arg = arg._values
        elif isinstance(arg, np.ma.MaskedArray):
            mask = arg.mask
            arg = arg.data
        else:
            _opstr = ' ' + opstr if opstr else ''
            raise TypeError(f'invalid{_opstr} mask type: {type(arg).__name__}')

        # Handle a shapeless mask
        if isinstance(mask, (bool, np.bool_)):
            if mask:                        # entirely masked
                return bool(masked_value)
            else:                           # entirely unmasked
                return Qube._as_mask(arg, invert=invert, masked_value=masked_value,
                                     opstr=opstr)

        # Copy the arg and merge the mask
        if invert:
            merged = (arg == 0)
        else:
            merged = (arg != 0)

        merged[mask] = masked_value
        return merged

    @staticmethod
    def _suitable_mask(arg, shape, *, collapse=False, broadcast=False, invert=False,
                       masked_value=True, check=False, opstr=''):
        """This argument converted to a scalar bool or boolean Numpy array of suitable
        shape to use as a mask.

        Parameters:
            arg: The object to convert to a mask.
            shape (tuple): Shape of the required mask.
            collapse (bool, optional): True to merge the extraneous axes of a mask if its
                rank is greater than that of the given shape.
            expand (bool, optional): True to broadcast this mask if its rank is less than
                that of the given shape.
            invert (bool, optional): True to return the logical not of the mask.
            masked_value (bool, optional): The value to use where the input argument is
               nmasked. This value is used _after_ `invert` is applied.
            check (bool, optional): True to check for an array containing all False
                values, and if so, replace it with a single value of False.
            opstr (str, optional): Name of operation to include in any error message.

        Returns:
            (bool or NumPy.ndarray): bool or boolean mask array.

        Raises:
            TypeError: If the data type of `arg` is invalid for a mask.
            ValueError: If the mask is incompatible with the specified `shape`.
        """

        mask = Qube._as_mask(arg, invert=invert, masked_value=masked_value, opstr=opstr)

        if isinstance(mask, bool):
            return mask

        if mask.shape == shape:
            if check and not np.any(mask):
                return False
            return mask

        new_rank = len(shape)
        if collapse and mask.ndim > new_rank:
            axes = tuple(range(new_rank, mask.ndim))
            mask = np.any(mask, axis=axes)
            if not isinstance(mask, np.ndarray):
                return bool(mask)
            if mask.shape == shape:
                return mask

        if broadcast:
            try:
                mask = np.broadcast_to(mask, shape)
            except ValueError:
                pass
            else:
                Qube._array_to_readonly(mask)
                return mask

        opstr_ = opstr + ' ' if opstr else ''
        raise ValueError(f'{opstr_}object and mask shape mismatch: '
                         f'{shape}, {mask.shape}')

    @staticmethod
    def _dtype_and_value(arg, masked_value=0, opstr=''):
        """Tuple (dtype, value), where dtype is one of "float", "int", or "bool".

        The value is converted to a builtin type if it is scalar; otherwise it is returned
        as an array with its original dtype.

        Parameters:
            arg (Qube, array-like, float, int, or bool): Object to interpret.
            masked_value (float, int, or bool): Value to use where `arg` is masked.
            opstr (str, optional): Name of operation to include in any error message.

        Returns:
            tuple: (`dtype`, `value`), where `dtype` is one of "float", "int", or "bool",
                and `value` is the result of converting `arg` to a NumPy.ndarray, float,
                int, or bool.

        Raises:
            TypeError: If the type of `arg` is invalid.
        """

        # Handle the easy and common cases first
        if isinstance(arg, (bool, np.bool_)):
            return ('bool', bool(arg))

        if isinstance(arg, numbers.Integral):
            return ('int', int(arg))

        if isinstance(arg, numbers.Real):
            return ('float', float(arg))

        if isinstance(arg, np.ndarray):
            if arg.shape == ():         # shapeless array
                return Qube._dtype_and_value(arg[()], opstr=opstr)

            kind = arg.dtype.kind
            if kind == 'f':
                return ('float', arg)

            if kind in ('i', 'u'):
                return ('int', arg)

            if kind == 'b':
                return ('bool', arg)

            _opstr = ' ' + opstr if opstr else ''
            raise ValueError(f'unsupported{_opstr} dtype: {arg.dtype}')

        # Convert a list or tuple to something else
        if isinstance(arg, (list, tuple)):
            if Qube._has_qube(arg):
                arg = Qube.stack(*arg)
            elif Qube._has_masked_array(arg):
                arg = np.ma.stack(*arg)
            else:
                arg = np.array(arg)
                return Qube._dtype_and_value(arg, opstr=opstr)

        # Handle an object with a possible mask
        if isinstance(arg, Qube):
            mask = arg._mask
            arg = arg._values
        elif isinstance(arg, np.ma.MaskedArray):
            mask = arg.mask
            arg = arg.data
        else:
            _opstr = ' ' + opstr if opstr else ''
            raise TypeError(f'unsupported{_opstr} data type: {type(arg)}')

        # Interpret the argument ignoring its mask
        (dtype, arg) = Qube._dtype_and_value(arg, opstr=opstr)

        # Handle a shapeless mask
        if isinstance(mask, (bool, np.bool_)):
            if mask:                        # entirely masked
                return (dtype, Qube._casted_to_dtype(masked_value, dtype))
            else:                           # entirely unmasked
                return (dtype, arg)

        # Mask an array value
        arg = arg.copy()
        arg[mask] = masked_value
        return (dtype, arg)

    @staticmethod
    def _dtype(arg):
        """dtype of the given argument, one of "float", "int", or "bool"."""

        return Qube._dtype_and_value(arg)[0]

    @staticmethod
    def _casted_to_dtype(arg, dtype, masked_value=0):
        """This value casted to the specified dtype, one of "float", "int", or "bool".

        An object that is already of the requested type is returned unchanged.

        Note that converting floats to ints is always a "floor" operation, so -1.5 -> -2.

        Parameters:
            arg (Qube, array-like, float, int, or bool): Object to cast
            dtype (str): dtype to cast to, one of float", "int", or "bool".
            masked_value (float, int, or bool): Value to assign to a masked item in the
                case where the input argument is a Qube or MaskedArray.

        Returns:
            (numpy.ndarray, float, int, or bool): The result of the cast.
        """

        if isinstance(arg, (list, tuple)):
            arg = np.array(arg)

        if isinstance(arg, Qube):
            if arg._mask is False:
                arg = arg._values
            else:
                mask = arg._mask
                arg = arg.without_mask(recursive=False).copy()
                arg[mask] = masked_value
                arg = arg._values

        elif isinstance(arg, np.ma.MaskedArray):
            if arg.mask is False:
                arg = arg.data
            else:
                mask = arg.mask
                arg = arg.data.copy()
                arg[mask] = masked_value

        if isinstance(arg, np.ndarray):
            if arg.shape == ():
                return Qube._casted_to_dtype(arg[()], dtype)

            if dtype == 'float':
                if arg.dtype.kind == 'f':
                    return arg
                return np.asarray(arg, dtype=np.double)

            if dtype == 'int':
                if arg.dtype.kind in ('i', 'u'):
                    return arg
                return (arg // 1).astype('int')

            # must be bool
            if arg.dtype.kind == 'b':
                return arg

            return (arg != 0)

        # Handle shapeless
        if dtype == 'float':
            return float(arg)

        if dtype == 'int':
            if isinstance(arg, numbers.Integral):
                return int(arg)
            return int(arg // 1)

        # bool case
        if isinstance(arg, (bool, np.bool_)):
            return bool(arg)

        return (arg != 0)

    @classmethod
    def _suitable_dtype(cls, dtype='float', opstr=''):
        """The dtype for this Qube subclass closest to a given dtype.

        Parameters:
            cls (class): Qube subclass.
            dtype (str, optional): Default dtype, one of "float", "int", or "bool", to
                return if it is compatible with the subclass.
            opstr (str, optional): Name of the operation to include in any error message.

        Returns:
            str: One of "float", "int", or "bool".

        Raises:
            ValueError: If a suitable dtype cannot be determined.
        """

        if dtype == 'float':
            if cls._FLOATS_OK:
                return 'float'
            elif cls._INTS_OK:
                return 'int'
            else:
                return 'bool'

        elif dtype == 'int':
            if cls._INTS_OK:
                return 'int'
            elif cls._FLOATS_OK:
                return 'float'
            else:
                return 'bool'

        elif dtype == 'bool':
            if cls._BOOLS_OK:
                return 'bool'
            elif cls._INTS_OK:
                return 'int'
            else:
                return 'float'

        # Handle a NumPy dtype
        try:
            kind = np.dtype(dtype).kind
        except (TypeError, ValueError):
            pass
        else:
            if kind == 'f':
                return cls._suitable_dtype('float', opstr=opstr)
            if kind in ('i', 'u'):
                return cls._suitable_dtype('int', opstr=opstr)
            if kind == 'b':
                return cls._suitable_dtype('bool', opstr=opstr)

        _in_opstr = ' in ' + opstr if opstr else ''                             # noqa
        raise ValueError('invalid dtype{_in_opstr}: "{dtype}"')

    @classmethod
    def _suitable_numer(cls, numer=None, opstr=''):
        """The given numerator made suitable for this class; ValueError otherwise.

        Parameters:
            cls (class): Qube subclass.
            numer (tuple, optional): Numerator shape to make suitable for use; None to
                return the default numerator shape for this Qube subclass.
            opstr (str, optional): Name of operation to include in any error message.

        Returns:
            tuple: Numerator shape.

        Raises:
            ValueError: If `numer` is unspecified and `cls` does not have a default.
            ValueError: If `numer` is incompatible with `cls`.
        """

        if numer is None:
            if cls._NUMER is not None:
                return cls._NUMER

            if not cls._NRANK:
                return ()

            _in_opstr = ' in ' + opstr if opstr else ''
            raise ValueError(f'class {cls} does not have a default numerator{_in_opstr}')

        numer = tuple(numer)

        opstr = opstr or cls.__name__
        if ((cls._NUMER is not None and numer != cls._NUMER) or
            (cls._NRANK is not None and len(numer) != cls._NRANK)):             # noqa
            raise ValueError(f'invalid {opstr} numerator shape {numer}; '
                             f'must be {cls._NUMER}')

        return numer

    @classmethod
    def _suitable_value(cls, arg, *, numer=None, denom=(), expand=True, opstr=''):
        """This argument converted to a suitable value for this class.

        Parameters:
            cls (class): Qube subclass.
            arg (Qube, array-like, float, int, or bool): Object to be made suitable.
            numer (tuple, optional): Numerator shape; None for class default.
            denom (tuple, optional): Denominator shape.
            expand (bool, optional): True to expand the shape of the returned argument to
                the minimum required for the class; False to leave it with its original
                shape.
            opstr (str, optional): Name of operation to include in any error message.

        Returns:
            (numpy.ndarray, float, int, or bool): The value made suitable for `cls`.

        Raises:
            ValueError: If `arg` is incompatible with `cls`.
        """

        # Convert arg to a valid dtype
        (old_dtype, arg) = Qube._dtype_and_value(arg, opstr=opstr)
        new_dtype = cls._suitable_dtype(old_dtype, opstr=opstr)
        if new_dtype != old_dtype:
            arg = Qube._casted_to_dtype(arg, new_dtype)

        # Without expansion, we're done
        if not expand:
            return arg

        # Get the valid numerator
        numer = cls._suitable_numer(numer, opstr=opstr)

        # Expand the arg shape if necessary
        item = numer + denom
        if len(np.shape(arg)) < len(item):
            temp = np.empty(item, dtype=new_dtype)
            temp[...] = arg
            arg = temp

        return arg

    @staticmethod
    def or_(*masks):
        """The logical "or" of two or more masks, avoiding array operations if possible.

        Parameters:
            *masks (array-like or bool): One or more boolean masks.

        Returns:
            (np.ndarray or bool): New mask array or bool.
        """

        # Two inputs is most common
        if len(masks) == 2:
            mask0 = masks[0]
            mask1 = masks[1]

            if isinstance(mask0, (bool, np.bool_)):
                if mask0:
                    return True
                else:
                    return mask1

            if isinstance(mask1, (bool, np.bool_)):
                if mask1:
                    return True
                else:
                    return mask0

            if mask0 is mask1:          # can happen when objects share masks
                return mask0

            return mask0 | mask1

        # Handle one input
        if len(masks) == 1:
            return masks[0]

        # Handle three or more by recursion
        return Qube.or_(masks[0], Qube.or_(*masks[1:]))

    @staticmethod
    def and_(*masks):
        """The logical "and" of two or more masks, avoiding array operations if possible.

        Parameters:
            *masks (array-like or bool): One or more boolean masks.

        Returns:
            (np.ndarray or bool): New mask array or bool.
        """

        # Two inputs is most common
        if len(masks) == 2:
            mask0 = masks[0]
            mask1 = masks[1]

            if isinstance(mask0, (bool, np.bool_)):
                if mask0:
                    return mask1
                else:
                    return False

            if isinstance(mask1, (bool, np.bool_)):
                if mask1:
                    return mask0
                else:
                    return False

            if mask0 is mask1:          # can happen when objects share masks
                return mask0

            return mask0 & mask1

        # Handle one input
        if len(masks) == 1:
            return masks[0]

        # Handle three or more by recursion
        return Qube.and_(masks[0], Qube.and_(*masks[1:]))

    ######################################################################################
    # Alternative constructors
    ######################################################################################

    def clone(self, *, recursive=True, preserve=[], retain_cache=False):
        """Fast construction of a shallow copy.

        Parameters:
            recursive (bool, optional): True to clone the derivatives of this object;
                False to ignore them.
            preserve (list, optional): Name(s) of derivatives to include even if
                `recursive` is False.
            retain_cache (bool, optional): True to retain cache except "unshrunk" and
                "wod"; False to return clone with an empty cache.

        Returns:
            Qube: The shallow clone.
        """

        obj = Qube.__new__(type(self))

        # Transfer attributes other than derivatives and cache
        for attr, value in self.__dict__.items():
            if attr in ('_derivs', '_cache'):
                obj.__dict__[attr] = {}
            elif attr.startswith('d_d'):
                continue
            elif isinstance(value, dict):
                obj.__dict__[attr] = value.copy()
            else:
                obj.__dict__[attr] = value

        # Handle derivatives recursively
        if recursive:
            new_keys = set(self._derivs.keys())
        elif preserve:
            if isinstance(preserve, str):
                new_keys = {preserve}
            else:
                new_keys = set(preserve)
        else:
            new_keys = set()

        for key in new_keys:
            deriv = self._derivs[key]
            new_deriv = deriv.clone(recursive=False, retain_cache=retain_cache)
            obj.insert_deriv(key, new_deriv)

        # Handle cache
        if retain_cache:
            obj._cache = self._cache.copy()
            if 'shrunk' in obj._cache:
                del obj._cache['shrunk']
            if 'wod' in obj._cache:
                del obj._cache['wod']
        else:
            obj._cache = {}

        return obj

    @classmethod
    def zeros(cls, shape, dtype='float', *, numer=None, denom=(), mask=False):
        """New object of this class and shape, filled with zeros.

        Parameters:
            shape (tuple): Shape of the object.
            dtype (str, optional): One of "bool", "int", or "float", defining the data
                type. Ignored if `cls` has a default dtype.
            numer (tuple, optional): Numerator shape; None to use default for `cls`.
            denom (tuple, optional): Denominator shape.
            mask (array-like or bool, optional): Mask to apply.

        Returns:
            Qube: The new object.
        """

        dtype = cls._suitable_dtype(dtype)
        numer = cls._suitable_numer(numer)

        obj = Qube.__new__(cls)
        obj.__init__(np.zeros(shape + numer + denom, dtype=dtype),
                     mask=mask, drank=len(denom))
        return obj

    @classmethod
    def ones(cls, shape, dtype='float', *, numer=None, denom=(), mask=False):
        """New object of this class and shape, filled with ones.

        Parameters:
            shape (tuple): Shape of the object.
            dtype (str, optional): One of "bool", "int", or "float", defining the data
                type. Ignored if `cls` has a default dtype.
            numer (tuple, optional): Numerator shape; None to use default for `cls`.
            denom (tuple, optional): Denominator shape.
            mask (array-like or bool, optional): Mask to apply.

        Returns:
            Qube: The new object.
        """

        dtype = cls._suitable_dtype(dtype)
        numer = cls._suitable_numer(numer)

        obj = Qube.__new__(cls)
        obj.__init__(np.ones(shape + numer + denom, dtype=dtype),
                     mask=mask, drank=len(denom))
        return obj

    @classmethod
    def filled(cls, shape, fill=0, *, numer=None, denom=(), mask=False):
        """Internal object of this class and shape, filled with a constant.

        Parameters:
            shape (tuple): Shape of the object.
            dtype (str, optional): One of "bool", "int", or "float", defining the data
                type. Ignored if `cls` has a default dtype.
            numer (tuple, optional): Numerator shape; None to use default for `cls`.
            denom (tuple, optional): Denominator shape.
            mask (array-like or bool, optional): Mask to apply.

        Returns:
            Qube: The new object.

        Raises:
            ValueError: If `fill` is not compatible with the `cls`.
        """

        # Create example object with shape == ()
        example = Qube.__new__(cls)
        example.__init__(cls._suitable_value(fill, numer=numer, denom=denom),
                         drank=len(denom))

        # For a shapeless object, return the example
        if not shape:
            if not mask:
                return example
            example = example.remask(mask)
            return example

        # Return the filled object
        vals = np.empty(shape + example._item, dtype=example.dtype())
        vals[...] = example._values

        obj = Qube.__new__(cls)
        obj.__init__(vals, mask=mask, example=example, drank=len(denom))
        return obj

    ######################################################################################
    # Low-level access
    ######################################################################################

    def _set_values(self, values, mask=None, *, antimask=None, retain_cache=False):
        """Low-level method to update the values of an array.

        The read-only status of the object is defined by that of the given value.

        Parameters:
            values (array-like, float, int, or bool): New values.
            mask (array-like or bool, optional): New mask.
            antimask (array-like or bool, optional): If provided, then only the array
                locations associated with the antimask are modified.
            retain_cache (bool, optional): If True, the cache values are retained except
                for "unshrunk".

        Returns:
            Qube: This object, updated.

        Raises:
            TypeError: If the type of `values` or `mask` is invalid.
            ValueError: If the shape of `values`, `mask`, or `antimask` is invalid.
        """

        # Confirm shapes
        shape = np.shape(self._values)
        shape1 = np.shape(values)
        if shape1 != shape:
            raise ValueError(f'value shape mismatch: {shape1}, {shape}')

        if mask is not None:
            mshape = np.shape(mask)
            if mshape and mshape != shape:
                raise ValueError(f'mask shape mismatch: {mshape}, {shape}')

        # Update values
        if antimask is not None:
            ashape = np.shape(antimask)
            if ashape != shape:
                raise ValueError(f'antimask shape mismatch: {ashape}, {shape}')
            self._values[antimask] = values[antimask]
        else:
            if isinstance(values, np.generic):
                if isinstance(values, np.floating):
                    values = float(values)
                elif isinstance(values, np.integer):
                    values = int(values)
                else:
                    values = bool(values)
            self._values = values

        self._readonly = Qube._array_is_readonly(self._values)

        # Update the mask if necessary
        if mask is not None:
            if antimask is None:
                self._mask = mask
            elif isinstance(mask, np.ndarray):
                self._mask[antimask] = mask[antimask]
            else:
                if not isinstance(self._mask, np.ndarray):
                    old_mask = self._mask
                    self._mask = np.empty(self._shape, dtype=np.bool_)
                    self._mask.fill(old_mask)
                self._mask[antimask] = mask

        # Handle the cache
        if retain_cache and mask is None:
            if 'unshrunk' in self._cache:
                del self._cache['unshrunk']
        else:
            self._cache.clear()

        # Set the readonly state based on the values given
        if np.shape(self._mask):
            if self._readonly:
                self._mask = Qube._array_to_readonly(self._mask)
            elif Qube._array_is_readonly(self._mask):
                self._mask = self._mask.copy()

        return self

    def _new_values(self):
        """Low-level method to indicate that values have changed.

        This means "unshrunk" will be deleted from the cache if present.
        """

        if 'unshrunk' in self._cache:
            del self._cache['unshrunk']

    def _set_mask(self, mask, *, antimask=None, check=False):
        """Low-level method to update the mask of an array.

        The read-only status of the object will be preserved.

        Parameters:
            mask (array-like or bool, optional): New mask.
            antimask (array-like or bool, optional): If provided, then only the array
                locations associated with the antimask are modified.
            check (bool, optional): True to check for an array containing all False
                values, and if so, replace it with a single value of False.

        Returns:
            Qube: This object, updated.

        Raises:
            TypeError: If the type of `mask` is invalid.
            ValueError: If the mask is incompatible with the required shape.
        """

        # Cast the mask and confirm the shape
        mask = Qube._suitable_mask(mask, self._shape, check=check)
        is_readonly = self._readonly

        if antimask is None:
            self._mask = mask
        elif isinstance(mask, np.ndarray):
            self._mask[antimask] = mask[antimask]
        else:
            if not isinstance(self._mask, np.ndarray):
                old_mask = self._mask
                self._mask = np.empty(self._shape, dtype=np.bool_)
                self._mask.fill(old_mask)
            self._mask[antimask] = mask

        self._cache.clear()

        if isinstance(self._mask, np.ndarray):
            if is_readonly:
                self._mask = Qube._array_to_readonly(self._mask)

            elif Qube._array_is_readonly(self._mask):
                self._mask = self._mask.copy()

        return self

    ######################################################################################
    # Properties
    ######################################################################################

    @property
    def values(self):
        """The value of this object as a numpy.ndarray, float, int, or bool."""

        return self._values

    @property
    def vals(self):
        """The value of this object as a numpy.ndarray, float, int, or bool."""

        return self._values       # Handy shorthand

    @property
    def mvals(self):
        """This object as a NumPy ma.MaskedArray."""

        # Deal with a scalar
        if self._is_scalar:
            if self._mask:
                return np.ma.masked
            else:
                return np.ma.MaskedArray(self._values)

        # Deal with a scalar mask
        if isinstance(self._mask, (bool, np.bool_)):
            if self._mask:
                return np.ma.MaskedArray(self._values, True)
            else:
                return np.ma.MaskedArray(self._values)

        # For zero rank, the mask is already the right size
        if self._rank == 0:
            return np.ma.MaskedArray(self._values, self._mask)

        # Expand the mask
        mask = self._mask.reshape(self._shape + self._rank * (1,))
        mask = np.broadcast_to(mask, self._values.shape)
        return np.ma.MaskedArray(self._values, mask)

    @property
    def mask(self):
        """The boolean mask of this object as a NumPy.ndarray or bool."""

        return self._mask

    @property
    def antimask(self):
        """The inverse of the mask of this object, True wherever an element is valid."""

        if not Qube._DISABLE_CACHE and 'antimask' in self._cache:
            return self._cache['antimask']

        if isinstance(self._mask, np.ndarray):
            antimask = np.logical_not(self._mask)
            self._cache['antimask'] = antimask
            return antimask

        antimask = not self._mask
        self._cache['antimask'] = antimask
        return antimask

    @property
    def default(self):
        """The default element value for this object."""

        return self._default

    @property
    def unit_(self):
        """The Unit of this object."""

        return self._unit

    @property
    def units(self):
        """The Unit of this object; alternative name for `unit_`."""

        return self._unit

    @property
    def derivs(self):
        """The dictionary of derivatives of this object."""

        return self._derivs

    @property
    def shape(self):
        """The shape of this object as a tuple."""

        return self._shape

    @property
    def ndims(self):
        """The number of dimensions in this object (excluding items)."""

        return self._ndims          # alternative name

    @property
    def ndim(self):
        """The number of dimensions in this object (excluding items)."""

        return self._ndims

    @property
    def rank(self):
        """The rank of this object."""

        return self._rank

    @property
    def nrank(self):
        """The rank of the element numerator in this object."""

        return self._nrank

    @property
    def drank(self):
        """The rank of the element denominator in this object."""

        return self._drank

    @property
    def item(self):
        """The shape of the elements in this object as a tuple."""

        return self._item

    @property
    def numer(self):
        """The shape of the element numerator in this object as a tuple."""

        return self._numer

    @property
    def denom(self):
        """The shape of the element denominator in this object as a tuple."""

        return self._denom

    @property
    def size(self):
        """The number of elements in this object's shape."""

        return self._size

    @property
    def isize(self):
        """The number of components in this object's items."""

        return self._isize

    @property
    def nsize(self):
        """The number of numerator components in this object's items."""

        return self._nsize

    @property
    def dsize(self):
        """The number of denominator components in this object's items."""

        return self._dsize

    @property
    def readonly(self):
        """True if this object is read-only; False otherwise."""

        return self._readonly

    ######################################################################################
    # Cache support
    ######################################################################################

    def _clear_cache(self):
        """Clear the cache."""

        self._cache.clear()

    def _find_corners(self):
        """Update the corner indices such that everything outside this defined "hypercube"
        is masked.
        """

        if self._ndims == 0:
            return None

        index0 = self._ndims * (0,)
        if isinstance(self._mask, (bool, np.bool_)):
            if self._mask:
                return (index0, index0)
            else:
                return (index0, self._shape)

        lower = []
        upper = []
        antimask = self.antimask

        for axis in range(self._ndims):
            other_axes = list(range(self._ndims))
            del other_axes[axis]

            occupied = np.any(antimask, tuple(other_axes))
            indices = np.where(occupied)[0]
            if len(indices) == 0:
                return (index0, index0)

            lower.append(indices[0])
            upper.append(indices[-1] + 1)

        return (tuple(lower), tuple(upper))

    @property
    def corners(self):
        """Corners of a "hypercube" that contain all the unmasked array elements.

        Returns:
            (tuple, tuple): The first tuple defines the lower coordinates of the unmasked
            region, and the second tuple defines the upper coordinates.
        """

        if not Qube._DISABLE_CACHE and 'corners' in self._cache:
            return self._cache['corners']

        corners = self._find_corners()
        self._cache['corners'] = corners
        return corners

    @staticmethod
    def _slicer_from_corners(corners):
        """A slice object based on corners specified as a tuple of indices."""

        slice_objects = []
        for axis in range(len(corners[0])):
            slice_objects.append(slice(corners[0][axis], corners[1][axis]))

        return tuple(slice_objects)

    @staticmethod
    def _shape_from_corners(corners):
        """Array shape based on corner indices."""

        shape = []
        for axis in range(len(corners[0])):
            shape.append(corners[1][axis] - corners[0][axis])

        return tuple(shape)

    @property
    def _slicer(self):
        """A slice object containing all the array elements inside the current corners."""

        if not Qube._DISABLE_CACHE and 'slicer' in self._cache:
            return self._cache['slicer']

        slicer = Qube._slicer_from_corners(self.corners)
        self._cache['slicer'] = slicer
        return slicer

    ######################################################################################
    # Derivative operations
    ######################################################################################

    def insert_deriv(self, key, deriv, *, override=True):
        """Insert or replace a derivative in this object.

        To prevent recursion, any internal derivatives of a derivative object are stripped
        away. If the object is read-only, then derivatives will also be converted to
        read-only.

        Derivatives cannot be integers. They are converted to floating-point if necessary.

        You cannot replace the pre-existing value of a derivative in a read-only object
        unless you explicit set override=True. However, inserting a new derivative into a
        read-only object is not prevented.

        Parameters:
            key (str): The name of the derivative. Each derivative also becomes accessible
                as an object attribute with "d_d" in front of the name. For example, the
                time-derivative of this object might be keyed by "t", in which case it can
                also be accessed as attribute "d_dt".
            deriv (Qube): The derivative. Derivatives must have the same leading shape and
                the same numerator as the object; denominator items are used for partial
                derivatives.
            override (bool, optional): True to allow the value of a pre-existing
                derivative to be replaced.

        Returns:
            Qube: This object after the derivative has been inserted.

        Raises:
            TypeError: If the derivative class is invalid or if derivatives are disallowed
                for the object class.
            ValueError: If the shape is invalid, or if the key already exists when
                `override` is False.
        """

        if not self._DERIVS_OK:
            raise TypeError(f'derivatives are disallowed in class {type(self).__name__}')

        # Make sure the derivative is compatible with the object
        if not isinstance(deriv, Qube):
            raise TypeError(f'invalid class for derivative "{key}" in '
                            f'{type(self).__name__} object: {type(deriv).__name__}')

        if self._numer != deriv._numer:
            raise ValueError(f'shape mismatch for numerator of derivative "{key}" in '
                             f'{type(self).__name__} object: '
                             f'{deriv._numer}, {self._numer}')

        if self.readonly and (key in self._derivs) and not override:
            raise ValueError(f'derivative "{key}" cannot be replaced in '
                             f'{type(self).__name__} object; is read-only')

        # Prevent recursion, convert to floating point
        deriv = deriv.wod.as_float()

        # Match readonly of parent if necessary
        if self._readonly and not deriv._readonly:
            deriv = deriv.clone(recursive=False).as_readonly()

        # Save in the derivative dictionary and as an attribute
        if deriv._shape != self._shape:
            deriv = deriv.broadcast_to(self._shape)

        self._derivs[key] = deriv
        setattr(self, 'd_d' + key, deriv)

        self._cache.clear()
        return self

    def insert_derivs(self, derivs, *, override=False):
        """Insert or replace the derivatives in this object from a dictionary.

        You cannot replace the pre-existing values of any derivative in a read-only object
        unless you explicit set override=True. However, inserting a new derivative into a
        read-only object is not prevented.

        Parameters:
            derivs (dict): The dictionary of derivatives keyed by their names.
            override (bool, optional): True to allow the value of a pre-existing
                derivative to be replaced.

        Returns:
            Qube: This object after the derivatives has been inserted.

        Raises:
            TypeError: If a derivative class is invalid.
            ValueError: If derivatives are disallowed for the object, if a shape is
                invalid, or if a key already exists when `override` is False.
        """

        # Check every insert before proceeding with any
        if self.readonly and not override:
            for key in derivs:
                if key in self._derivs:
                    raise ValueError(f'derivative "{key}" cannot be replaced in '
                                     '{type(self).__name__} object; object is read-only')

        # Insert derivatives
        for key, deriv in derivs.items():
            self.insert_deriv(key, deriv, override=override)

        return self

    def delete_deriv(self, key, *, override=False):
        """Delete a single derivative from this object, given the key.

        Derivatives cannot be deleted from a read-only object without explicitly setting
        override=True.

        Parameters:
            key (str): The key of the derivative to remove. If the key does not exist,
                the object is unchanged.
            override (bool, optional): True to allow the deleting of derivatives from a
                read-only object.

        Raises:
            ValueError: If this object is read-only and `override` is False.
        """

        if not override:
            self.require_writeable()

        if key in self._derivs.keys():
            del self._derivs[key]
            del self.__dict__['d_d' + key]

        self._cache.clear()

    def delete_derivs(self, *, override=False, preserve=None):
        """Delete all derivatives from this object.

        Derivatives cannot be deleted from a read-only object without explicitly setting
        `override=True`.

        Parameters:
            override (bool, optional): True to allow the deleting of derivatives from a
                read-only object.
            preserve (list, tuple or set, optional): The names of derivatives to retain.
                All others are removed.

        Raises:
            ValueError: If this object is read-only and `override` is False.
        """

        if not override:
            self.require_writeable()

        # If something is being preserved...
        if preserve:

            # Delete derivatives not on the list
            for key in self._derivs.keys():
                if key not in preserve:
                    self.delete_deriv(key, override)

            return

        # Delete all derivatives
        for key in self._derivs.keys():
            delattr(self, 'd_d' + key)

        self._derivs = {}
        self._cache.clear()

    def without_derivs(self, *, preserve=None):
        """A shallow copy of this object without derivatives.

        A read-only object remains read-only, and is cached for later use.

        Parameters:
            preserve (list, tuple, or set, optional): The names of derivatives to retain.
                All others are removed.

        Returns:
            Qube: The copy, with the same subclass as self.
        """

        if not self._derivs:
            return self

        # If something is being preserved...
        if preserve:
            if isinstance(preserve, str):
                preserve = [preserve]

            if not any([p for p in preserve if p in self._derivs]):
                return self.wod

            # Create a fast copy with derivatives
            obj = self.clone(recursive=True)

            # Delete derivatives not on the list
            deletions = []
            for key in obj._derivs:
                if key not in preserve:
                    deletions.append(key)

            for key in deletions:
                obj.delete_deriv(key, override=True)

            return obj

        # Return a fast copy without derivatives
        return self.wod

    @property
    def wod(self):
        """A shallow clone without derivatives, cached.

        Read-only objects remain read-only.
        """

        if not self._derivs:
            return self

        if not Qube._DISABLE_CACHE and 'wod' in self._cache:
            return self._cache['wod']

        wod = Qube.__new__(type(self))
        wod.__init__(self._values, self._mask, example=self)
        for key, attr in self.__dict__.items():
            if key.startswith('d_d'):
                pass
            elif isinstance(attr, Qube):
                wod.__dict__[key] = attr.wod
            else:
                wod.__dict__[key] = attr

        wod._derivs = {}
        wod._cache['wod'] = wod
        self._cache['wod'] = wod
        return wod

    def without_deriv(self, key):
        """A shallow copy of this object without a particular derivative.

        A read-only object remains read-only.

        Parameters:
            key (str): The key of the derivative to remove.

        Returns:
            Qube: The copy, with the same subclass as self.
        """

        if key not in self._derivs:
            return self

        result = self.clone(recursive=True)
        del result._derivs[key]

        return result

    def with_deriv(self, key, value, *, method='insert'):
        """A shallow copy of this object with a derivative inserted or
        added.

        A read-only object remains read-only.

        Parameters:
            key (str): The key of the derivative to insert.
            value (Qube): The value for this derivative.
            method (str): How to insert the derivative, one of these options:`

                * "`insert`": Iinsert the new derivative; raise a ValueError if a
                  derivative of the same name already exists.
                * "`replace`":  Replace an existing derivative of the same name.
                * "`add`": Add this derivative to an existing derivative of the same name.

        Returns:
            Qube: The copy, with the same subclass as self.

        Raises:
            ValueError: If `method` is "insert" and a derivative of the given name already
                exists.
        """

        result = self.clone(recursive=True)

        if method not in ('insert', 'replace', 'add'):
            raise ValueError('invalid with_deriv method: ' + repr(method))

        if key in result._derivs:
            if method == 'insert':
                raise ValueError(f'derivative "{key}" already exists in '
                                 f'{type(self).__name__} object')
            if method == 'add':
                value = value + result._derivs[key]

        result.insert_deriv(key, value)
        return result

    def rename_deriv(self, key, new_key, *, method='insert'):
        """A shallow copy of this object with a derivative renamed.

        A read-only object remains read-only.

        Parameters:
            key (str): The current key of the derivative.
            new_key (str): The new name of the derivative.
            method (str): How to rename the derivative, one of these options:`

                * "`insert`": Iinsert the new derivative; raise a ValueError if a
                  derivative of the same name already exists.
                * "`replace`":  Replace an existing derivative of the same name.
                * "`add`": Add this derivative to an existing derivative of the same name.

        Returns:
            Qube: The copy, with the same subclass as self.

        Raises:
            KeyError: If the `key` derivative does not exist.
            ValueError: If `method` is "insert" and a derivative of the given name already
                exists.
        """

        result = self.with_deriv(new_key, self._derivs[key], method=method)
        result = result.without_deriv(key)
        return result

    def unique_deriv_name(self, key, *objects):
        """A unique name for a derivative to apply to one or more objects.

        Parameters:
            key (str): The name to use, with a suffix appended if needed.
            *objects (Qube): One or more Qube objects.

        Returns:
            str: The given key, or with a numeric suffix if needed to make it unique.
        """

        # Make a list of all the derivative keys
        all_keys = set(self._derivs.keys())
        for obj in objects:
            if not hasattr(obj, 'derivs'):
                continue
            all_keys |= set(obj._derivs.keys())

        # Return the proposed key if it is unused
        if key not in all_keys:
            return key

        # Otherwise, tack on a number and iterate until the name is unique
        i = 0
        while True:
            unique = key + str(i)
            if unique not in all_keys:
                return unique

            i += 1

    ######################################################################################
    # Unit operations
    ######################################################################################

    def set_unit(self, unit, *, override=False):
        """Set the unit of this object.

        Parameters:
            unit (Unit or None): The new unit.
            override (bool, optional): If True, the unit can be modified on a read-only
                object.

        Raises:
            ValueError: If this object is read-only and `override` is False.
        """

        if not self._UNITS_OK:
            if Unit.is_unitless(unit):
                return
            raise TypeError(f'units are disallowed in class {type(self).__name__}')

        if not override:
            self.require_writeable()

        unit = Unit.as_unit(unit)

        Unit.require_compatible(unit, self._unit)
        self._unit = unit
        self._cache.clear()

    def without_unit(self, *, recursive=True):
        """A shallow copy of this object without units.

        A read-only object remains read-only. If recursive is True, derivatives are also
        stripped of their units.

        Parameters:
            recursive (bool, optional): True to include derivatives with their units
                stripped; False to omit all derivatives.

        Returns:
            Qube: A shallow copy of this object with the unit stripped.
        """

        if self._unit is None and not self._derivs:
            return self

        obj = self.clone(recursive=recursive)
        obj._unit = None
        return obj

    def into_unit(self, recursive=False):
        """The values property of this object, converted to its unit.

        Parameters:
            recursive (bool, optional): If True, also return the derivatives converted to
                their units.

        Returns:
            (numpy.ndarray, float, int, bool, or tuple): The values attribute of this
            object, converted to this object's units. If `recursive` is True, it returns a
            tuple (`values`, `derivs`), where `derivs` is a dictionary of the derivative
            values converted to their units.
        """

        if self._unit is None or self._unit.into_unit_factor == 1.:
            values = self._values
        else:
            values = Unit.into_unit(self._unit, self._values)

        if not recursive:
            return values

        derivs = {}
        for key, deriv in self._derivs.items():
            derivs[key] = Unit.into_unit(deriv._unit, deriv._values)

        return (values, derivs)

    def confirm_unit(self, unit):
        """Raises a ValueError if the unit is not compatible with this object.

        Parameters:
            unit (Unit or None): The new unit.

        Returns:
            Qube: This object.

        Raises:
            ValueError: If this object has a unit that are incompatible with the new unit.
        """

        if not Unit.can_match(self._unit, unit):
            raise ValueError(f'units are not compatible with {type(self).__name__} '
                             f'object: {unit}, {self._unit}')

        return self

    def is_unitless(self):
        """True if this object is unitless."""

        return Unit.is_unitless(self._unit)

    def _require_unitless(self, op=''):
        """Raise a ValueError if this object is not unitless.

        Parameters:
            info (str, optional): An info string to embed into the error message.

        Raises:
            ValueError: If units are present.
        """

        if self.is_unitless():
            return

        Unit.require_unitless(self._unit, info=self._opstr(op))

    def _require_angle(self, op=''):
        """Raise a ValueError if this object is not either unitless or has a dimension of
        angle.

        Parameters:
            op (str, optional): Operation name to embed into the error message.

        Raises:
            ValueError: If units are not compatible with an angle.
        """

        if Unit.is_angle(self._unit):
            return

        Unit.require_angle(self._unit, info=self._opstr(op))

    def _require_compatible_units(self, arg, op=''):
        """Raise a ValueError if these objects do not have compatible units.

        Parameters:
            op (str, optional): Operation name to embed into the error message.

        Raises:
            ValueError: If units are not compatible.
        """

        if not isinstance(arg, Qube):
            return True

        if Unit.can_match(self._unit, arg._unit):
            return True

        Unit.require_compatible(self._unit, arg._unit, info=self._opstr(op))

    ######################################################################################
    # Read-only/read-write operations
    ######################################################################################

    @staticmethod
    def _array_is_readonly(arg):
        """True if the argument is a read-only NumPy ndarray.

        False means that it is either a writable array or a scalar.
        """

        if not isinstance(arg, np.ndarray):
            return False

        return (not arg.flags['WRITEABLE'])

    @staticmethod
    def _array_to_readonly(arg):
        """Make the given argument read-only if it is a NumPy ndarray; then return it."""

        if not isinstance(arg, np.ndarray):
            return arg

        arg.flags['WRITEABLE'] = False
        return arg

    def as_readonly(self, *, recursive=True):
        """Convert this object to read-only. It is modified in place and returned.

        If this object is already read-only, it is returned as is. Otherwise, the internal
        _values and _mask arrays are modified as necessary. Once this happens, the
        internal arrays will also cease to be writable in any other object that shares
        them.

        Note that `as_readonly()` cannot be undone. Use `copy()` to create a writable copy
        of a readonly object.

        Parameters:
            recursive (bool, optional): True also to convert the derivatives to read-only;
                False to strip the derivatives.

        Returns:
            Qube: This object, converted to read-only if necessary.
        """

        # If it is already read-only, return
        if self._readonly:
            return self

        # Update the value if it is an array
        Qube._array_to_readonly(self._values)
        Qube._array_to_readonly(self._mask)
        self._readonly = True

        # Update anything cached
        if not Qube._DISABLE_CACHE:
            for key, value in self._cache.items():
                if isinstance(value, Qube):
                    self._cache[key] = value.as_readonly(recursive=recursive)

        # Update the derivatives
        if recursive:
            for key in self._derivs:
                self._derivs[key].as_readonly()

        return self

    def match_readonly(self, arg):
        """Convert the read-only status of this object equal to that of another.

        Parameters:
            arg (Qube): An existing Qube subclass.

        Returns:
            Qube: This object converted to read-only.

        Raises:
            ValueError: If this object is read-only but the `arg` is not.
        """

        if arg._readonly:
            return self.as_readonly()
        elif self._readonly:
            raise ValueError(f'{type(self).__name__} object is read-only')

        return self

    def require_writeable(self, force=False):
        """Ensure that this object is writeable.

        Parameters:
            force (bool, optional): True to return a new copy if this object is read-only;
                otherwise, if this object is not writeable, raise a ValueError.

        Returns:
            Qube: This object if already writeable; otherwise a new writeable copy.

        Raises:
            ValueError: If this object is read-only but `force` is False.
        """

        if self._readonly:
            if force:
                return self.copy(recursive=True, readonly=True)
            raise ValueError(f'{type(self).__name__} object is read-only')

        # Sometimes the array is writeable but a shared mask is not
        if np.shape(self._mask) and not self._mask.flags['WRITEABLE']:
            self.remask(self._mask.copy())

        # It's possible that a derivative is read-only
        for key, deriv in self._derivs.items():
            if deriv._readonly:
                self._derivs[key] = deriv.copy(recursive=False, readonly=False)

        return self

    def require_writable(self, force=False):
        """Ensure that this object is writeable.

        DEPRECATED NAME; use require_writeable().

        Parameters:
            force (bool, optional): True to return a new copy if this object is read-only;
                otherwise, if this object is not writeable, raise a ValueError.

        Returns:
            Qube: This object if already writeable; otherwise a new writeable copy.

        Raises:
            ValueError: If this object is read-only but `force` is False.
        """

        return self.require_writeable(force=force)

    ######################################################################################
    # Copying operations and conversions
    ######################################################################################

    def copy(self, *, recursive=True, readonly=False):
        """Deep copy operation with additional options.

        Parameters:
            recursive (bool, optional): True to copy the derivatives; False, to return an
                object without derivatives.
            readonly (bool, optional): True to return a read-only copy, or this object if
                it is already read-only. Otherwise, this return is guaranteed to be an
                entirely new copy, independent of this object and suitable for
                modification.

        Returns:
            Qube: A copy of this object.
        """

        # Create a shallow copy
        obj = self.clone(recursive=False)

        # Copying a readonly object is easy
        if self._readonly and readonly:
            return obj

        # Copy the values
        if self._is_array:
            obj._values = self._values.copy()
        else:
            obj._values = self._values

        # Copy the mask
        if isinstance(self._mask, np.ndarray):
            obj._mask = self._mask.copy()
        else:
            obj._mask = self._mask

        obj._cache = {}

        # Set the read-only state
        if readonly:
            obj.as_readonly()
        else:
            obj._readonly = False

        # Make the derivatives read-only if necessary
        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.copy(recursive=False, readonly=readonly))

        return obj

    # Python-standard copy function
    def __copy__(self):
        """An independent, writeable copy of this object."""

        return self.copy(recursive=True, readonly=False)

    ######################################################################################
    # Value tests
    ######################################################################################

    @staticmethod
    def as_one_bool(value):
        """Convert a single value to a bool; leave other values unchanged."""

        if not isinstance(value, np.ndarray):
            return bool(value)

        return value

    @staticmethod
    def is_one_true(value):
        """True if the value is a single boolean True."""

        if isinstance(value, (bool, np.bool_)):
            return bool(value)

        return False

    @staticmethod
    def is_one_false(value):
        """True if the value is a single boolean False."""

        if isinstance(value, (bool, np.bool_)):
            return not bool(value)

        return False

    @staticmethod
    def _is_one_value(value):
        """True if the value is a Python numeric or a NumPy numeric scalar."""

        return isinstance(value, numbers.Real)

    ######################################################################################
    # Conversions
    ######################################################################################

    def dtype(self):
        """One of "float", "int", or "bool", depending this object's value."""

        return Qube._dtype(self._values)

    def is_numeric(self):
        """True if this object contains numbers; False if boolean."""

        if isinstance(self._values, (bool, np.bool_)):
            return False
        if isinstance(self._values, np.ndarray) and self._values.dtype.kind == 'b':
            return False
        return True

    def as_numeric(self, *, recursive=True):
        """A numeric version of this object.

        Booleans are converted to Scalars.

        Parameters:
            recursive (bool, optional): True to include any derivatives; False to remove
                them.

        Returns:
            Qube: This object if it is already numeric; a Boolean is converted to a
            Scalar.
        """

        if self.is_numeric():
            return self if recursive else self.wod

        values = int(self._values) if self._is_scalar else self._values.astype(np.int8)
        return Qube._SCALAR_CLASS(values, self._mask, example=self, op='as_numeric()')

    def is_float(self):
        """True if this object contains floats; False if ints or booleans."""

        if isinstance(self._values, np.ndarray):
            return self._values.dtype.kind == 'f'
        return isinstance(self._values, float)

    def as_float(self, *, recursive=True, copy=False, builtins=False):
        """A floating-point version of this object.

        Booleans are converted to Scalars.

        Parameters:
            recursive (bool, optional): True to include any derivatives; False to remove
                them.
            copy (bool, optional): True to ensure that a new object with an independent
                copy of the values is returned.
            builtins (bool, optional): True to return a Python float if the returned value
                has shape (), is unmasked, and has no derivatives.

        Returns:
            Qube: The result.

        Raises:
            TypeError: If this object cannot contain floats.
        """

        if (builtins and self._is_scalar and not self._mask
                and not (recursive and self._derivs)):
            return float(self._values)

        if isinstance(self._values, np.ndarray) and self._values.dtype.kind == 'f':
            if copy:
                return self.__copy__(recursive=recursive)
            return self if recursive else self.wod

        cls = type(self)
        if cls is Qube._BOOLEAN_CLASS:
            cls = Qube._SCALAR_CLASS

        if not cls._FLOATS_OK:
            raise TypeError(f'{cls.__name__} object cannot contain floats')

        if self._is_scalar:
            values = float(self._values)
        else:
            values = self._values.astype(np.float64)
        derivs = self._derivs if recursive else {}

        obj = Qube.__new__(cls)
        obj.__init__(values, self._mask, derivs=derivs, example=self, op='as_float()')
        return obj

    def is_int(self):
        """True if this object contains ints; False if floats or booleans."""

        if isinstance(self._values, np.ndarray):
            return self._values.dtype.kind in 'iu'
        if isinstance(self._values, bool):
            return False
        return isinstance(self._values, int)

    def as_int(self, copy=False, builtins=False):
        """An integer version of this object.

        Booleans are converted to Scalars.

        Parameters:
            copy (bool, optional): True to ensure that a new object with an independent
                copy of the values is returned.
            builtins (bool, optional): True to return a Python float if the returned value
                has shape (), is unmasked, and has no derivatives.

        Returns:
            Qube or int: The result.

        Raises:
            TypeError: If this object cannot contain integers.
       """

        if builtins and self._is_scalar and not self._mask:
            return int(self._values)

        if isinstance(self._values, np.ndarray) and self._values.dtype.kind in 'iu':
            return self.__copy__() if copy else self

        cls = type(self)
        if cls is Qube._BOOLEAN_CLASS:
            cls = Qube._SCALAR_CLASS

        if not cls._INTS_OK:
            raise TypeError(f'{cls.__name__} object cannot contain ints')

        if self._is_scalar:
            values = int(self._values // 1)
        elif self._values.dtype.kind == 'b':
            values = self._values.astype(np.int8)
        else:
            values = (self._values // 1).astype(np.int64)

        obj = Qube.__new__(cls)
        obj.__init__(values, self._mask, example=self, op='as_int()')
        return obj

    def is_bool(self):
        """True if this object contains booleans; False otherwise."""

        if isinstance(self._values, np.ndarray):
            return self._values.dtype.kind == 'b'
        return isinstance(self._values, bool)

    def as_bool(self, copy=False, builtins=False):
        """A boolean version of this object.

        Scalars are converted to Booleans.

        Parameters:
            copy (bool, optional): True to ensure that a new object with an independent
                copy of the values is returned.
            builtins (bool, optional): True to return a Python float if the returned value
                has shape (), is unmasked, and has no derivatives.

        Returns:
            Qube: A copy of object converted to bools; if the values are already bools and
                `copy` is False, this object is returned unchanged.

        Raises:
            TypeError: If this object cannot contain bools.
        """

        if builtins and self._is_scalar and not self._mask:
            return bool(self._values)

        if isinstance(self._values, np.ndarray) and self._values.dtype.kind == 'b':
            return self.__copy__() if copy else self

        cls = type(self)
        if cls is Qube._SCALAR_CLASS:
            cls = Qube._BOOLEAN_CLASS

        if not cls._INTS_OK:
            raise TypeError(f'{cls.__name__} object cannot contain bools')

        values = bool(self._values) if self._is_scalar else self._values.astype(np.bool_)
        obj = Qube.__new__(cls)
        obj.__init__(values, self._mask, example=self, op='as_bool()')
        return obj

    def as_this_type(self, arg, *, recursive=True, coerce=True, op=''):
        """The argument converted to this class and data type.

        If the object is already of the correct class and type, it is returned unchanged.

        Parameters:
            arg (array-like, float, int, or bool): The object to the class of this object.
                If the argument is a scalar or NumPy ndarray, a new instance of this
                object's class is created.
            recursive (bool, optional): True to convert the derivatives as well.
            coerce (bool, optional): True to coerce the data type silently; False to leave
                the data type unchanged.
            op (str, optional): Name of operator to use in an error message.

        Returns:
            Qube: The argument converted to the type of this object.
        """

        # If the classes already match, we might return the argument as is
        if type(arg) is type(self):
            obj = arg
        else:
            obj = None

        # Initialize the new values and mask; track other attributes
        if not isinstance(arg, Qube):
            arg = Qube(arg, example=self, op=op)

        if arg._nrank != self._nrank:
            Qube._raise_incompatible_numers(op, self, arg)

        new_vals = arg._values
        new_mask = arg._mask
        new_unit = arg._unit
        has_derivs = bool(arg._derivs)
        is_readonly = arg._readonly

        # Convert the value types if necessary
        changed = False
        if coerce:
            casted = Qube._casted_to_dtype(new_vals, Qube._dtype(self._values))
            changed = casted is not new_vals
            new_vals = casted

        # Convert the unit if necessary
        if new_unit and not self._UNITS_OK:
            new_unit = None
            changed = True

        # Validate derivs
        if has_derivs and not self._DERIVS_OK:
            changed = True
        if has_derivs and not recursive:
            changed = True

        # Construct the new object if necessary
        if changed or obj is None:
            obj = Qube.__new__(type(self))
            obj.__init__(new_vals, new_mask, unit=new_unit, drank=arg._drank,
                         example=self)
            is_readonly = False

        # Update the derivatives if necessary
        if recursive and has_derivs:
            derivs_changed = False
            new_derivs = {}
            for key, deriv in arg._derivs.items():
                new_deriv = self.as_this_type(deriv, recursive=False, coerce=False, op=op)
                if new_deriv is not deriv:
                    derivs_changed = True
                new_derivs[key] = new_deriv

            if derivs_changed or (arg is not obj):
                if is_readonly:
                    obj = obj.copy(recursive=False)
                obj.insert_derivs(new_derivs)

        return obj

    def cast(self, classes):
        """A shallow copy of this object casted to another Qube subclass.

        Parameters:
            classes (class or list): A Qube subclass or list of subclasses. The object
                will be casted to the first suitable class in the list.

        Returns:
            Qube: A shallow copy of this object. If the object is already of the selected
            class or if no suitable class is found, it is returned without modification.
        """

        # Convert a single class to a tuple
        if isinstance(classes, type):
            classes = (classes,)

        # For each class in the list...
        for cls in classes:

            # If this is already the class of this object, return it as is
            if cls is type(self):
                return self

            # Exclude the class if it is incompatible
            if cls._NUMER is not None and cls._NUMER != self._numer:
                continue
            if cls._NRANK is not None and cls._NRANK != self._nrank:
                continue

            # Construct the new object
            obj = Qube.__new__(cls)
            obj.__init__(self._values, self._mask, derivs=self._derivs,
                         example=self)
            return obj

        # If no suitable class was found, return this object unmodified
        return self

    def as_all_constant(self, constant=None, *, recursive=True):
        """A shallow, read-only copy of this object with constant values.

        Derivatives are all set to zero. The mask is unchanged.

        Parameters:
            constant (array-like, float, int, or bool, optional): The constant value for
                each item. This must have the same shape as this object's items. Use None
                for values of zero appropriate to the Qube subclass.

        Returns:
            Qube: A shallow copy of this object with constant values.
        """

        if constant is None:
            constant = self.zero()

        constant = self.as_this_type(constant, recursive=False)

        obj = self.clone(recursive=False)
        obj._set_values(Qube.broadcast(constant, obj)[0]._values)
        obj.as_readonly()

        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.as_all_constant(recursive=False))

        return obj

    def as_size_zero(self, axis=0, *, recursive=True):
        """A shallow, read-only copy of this object with size zero.

        Parameters:
            axis (int, optional): The axis index (positive or negative) to collapse to
                length zero; the other axes are left unchanged. Use None for an object of
                shape (0,).

        Returns:
            Qube: A shallow copy of this object with size zero.
        """

        obj = Qube.__new__(type(self))

        if self._shape == ():
            new_values = np.array([self._values])[:0]
            new_mask = np.array([self._mask])[:0]
        elif axis is None:
            new_values = self._values.ravel()[:0]
            new_mask = np.asarray(self._mask).ravel()[:0]
        else:
            if axis == 0:
                indx = slice(0, 0)
            else:
                indx = (Ellipsis, slice(0, 0))

            new_values = self._values[indx]

            if np.shape(self._mask):
                new_mask = self._mask[indx]
            else:
                new_mask = np.array([self._mask])[indx]

        obj.__init__(new_values, new_mask, example=self)

        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.as_size_zero(axis=axis, recursive=False))

        return obj

    ######################################################################################
    # Object mask operations
    ######################################################################################

    def is_all_masked(self):
        """True if this object is entirely masked."""

        return np.all(self._mask)

    def count_masked(self):
        """The number of masked items in this object."""

        if isinstance(self._mask, np.ndarray):
            return np.sum(self._mask)

        return self._size if self._mask else 0

    def count_unmasked(self):
        """The number of unmasked items in this object."""

        if isinstance(self._mask, np.ndarray):
            return self._size - np.sum(self._mask)

        return 0 if self._mask else self._size

    def masked_single(self, *, recursive=True):
        """An object of this subclass containing one masked value."""

        if not self._rank:
            new_value = self._default
        else:
            new_value = self._default.copy()

        obj = Qube.__new__(type(self))
        obj.__init__(new_value, True, example=self)

        if recursive and self._derivs:
            for key, value in self._derivs.items():
                obj.insert_deriv(key, value.masked_single(recursive=False))

        obj.as_readonly()
        return obj

    def without_mask(self, *, recursive=True):
        """A shallow copy of this object without its mask. Note that masked values will be
        revealed.

        Parameters:
            recursive (bool, optional): True to unmask any derivatives; False to strip
                derivatives.

        Returns:
            Qube: This object without a mask.
        """

        obj = self.clone(recursive=recursive)
        obj._set_mask(False)

        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.without_mask())

        return obj

    def as_all_masked(self, *, recursive=True):
        """A shallow copy of this object with everything masked.

        Parameters:
            recursive (bool, optional): True to mask any derivatives; False to strip
                derivatives.

        Returns:
            Qube: This object but fully masked.
        """

        obj = self.clone(recursive=recursive)
        obj._set_mask(True)

        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.as_all_masked(recursive=False))

        return obj

    def as_one_masked(self, *, recursive=True):
        """This object reduced to shape () and masked.

        Parameters:
            recursive (bool, optional): True to mask any derivatives; False to strip
                derivatives.

        Returns:
            Qube: This object but fully masked and with shape ()
        """

        return self.flatten()[0].as_all_masked()

    def remask(self, mask, *, recursive=True, check=True):
        """A shallow copy of this object with a replaced mask.

        This is much quicker than masked_where(), for cases where only the mask of this
        object is changing.

        Parameters:
            mask (array-like or bool): The new mask to be applied to the object.
            recursive (bool, optional): True to apply the same mask to any derivatives.
            check (bool, optional): True to check for an array containing all False
                values, and if so, replace it with a single value of False.

        Returns:
            Qube: A shallow copy of this object with a new mask.

        Raises:
            TypeError: If the data type of `mask` is invalid.
            ValueError: If the mask is incompatible with the required shape.
        """

        mask = Qube._suitable_mask(mask, self._shape, check=check)

        # Construct the new object
        obj = self.clone(recursive=False)
        obj._set_mask(mask)

        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.remask(mask, recursive=False, check=False))

        return obj

    def remask_or(self, mask, *, recursive=True, check=True):
        """A shallow copy of this object, in which the current mask is "or-ed" with the
        given mask.

        This is much quicker than masked_where(), for cases where only the mask is
        changing.

        Parameters:
            mask (array-like or bool): The new mask to be applied to the object.
            recursive (bool, optional): True to apply the same mask to any derivatives.
            check (bool, optional): True to check for an array containing all False
                values, and if so, replace it with a single value of False.

        Returns:
            Qube: A shallow copy of this object with a new mask.

        Raises:
            TypeError: If the data type of `mask` is invalid for a mask.
            ValueError: If the mask is incompatible with the required shape.
        """

        mask = Qube._suitable_mask(mask, self._shape, check=check)

        # Construct the new object
        obj = self.clone(recursive=False)
        obj._set_mask(Qube.or_(self._mask, mask))

        if recursive:
            for key, deriv in self._derivs.items():
                obj.insert_deriv(key, deriv.remask(mask, recursive=False, check=False))

        return obj

    def expand_mask(self, *, recursive=True):
        """A shallow copy where a single mask value of True or False is converted to an
        array.

        If the object's mask is already an array, it is returned unchanged.

        Parameters:
            recursive (bool, optional): True to expand the mask of any derivatives.

        Returns:
            Qube: A shallow copy of this object with an expanded mask.
        """

        if np.shape(self._mask) and not (recursive and self._derivs):
            return self

        # Clone the object only if necessary
        obj = None
        if not isinstance(self._mask, np.ndarray):
            obj = self.clone(recursive=True)
            if obj._mask:
                obj._set_mask(np.ones(self._shape, dtype=np.bool_))
            else:
                obj._set_mask(np.zeros(self._shape, dtype=np.bool_))

        # Clone any derivs only if necessary
        new_derivs = {}
        if recursive:
            for key, deriv in self._derivs.items():
                mask_before = deriv._mask
                new_deriv = deriv.expand_mask(recursive=False)
                if mask_before is not new_deriv._mask:
                    new_derivs[key] = new_deriv

        # If nothing has changed, return self
        if obj is None and not new_derivs:
            return self

        # Return the modified object
        if obj is None:
            obj = self.clone(recursive=True)

        for key, deriv in new_derivs.items():
            obj.insert_deriv(key, deriv, override=True)

        return obj

    def collapse_mask(self, *, recursive=True):
        """A shallow copy where a mask entirely containing either True or False is
        converted to a single boolean.

        Parameters:
            recursive (bool, optional): True to collapse the mask of any derivatives.

        Returns:
            Qube: A shallow copy of this object with a collapsed mask.
        """

        if not isinstance(self._mask, np.ndarray) and not (recursive and self._derivs):
            return self

        # Clone the object only if necessary
        obj = None
        if np.shape(self._mask):
            if not np.any(self._mask):
                obj = self.clone(recursive=True)
                obj._set_mask(False)
            elif np.all(self._mask):
                obj = self.clone(recursive=True)
                obj._set_mask(True)

        # Clone any derivs only if necessary
        new_derivs = {}
        if recursive:
            for key, deriv in self._derivs.items():
                mask_before = deriv._mask
                new_deriv = deriv.collapse_mask(recursive=False)
                if mask_before is not new_deriv._mask:
                    new_derivs[key] = new_deriv

        # If nothing has changed, return self
        if obj is None and not new_derivs:
            return self

        # Return the modified object
        if obj is None:
            obj = self.clone(recursive=True)

        for key, deriv in new_derivs.items():
            obj.insert_deriv(key, deriv, override=True)

        return obj

    def as_mask_where_nonzero(self):
        """A boolean scalar or NumPy ndarray where values are nonzero and unmasked."""

        return (self._values != 0) & self.antimask

    def as_mask_where_zero(self):
        """A boolean scalar or NumPy ndarray where values are zero and unmasked."""

        return (self._values == 0) & self.antimask

    def as_mask_where_nonzero_or_masked(self):
        """A boolean scalar or NumPy ndarray where values are nonzero or masked."""

        return (self._values != 0) | self._mask

    def as_mask_where_zero_or_masked(self):
        """A boolean scalar or NumPy ndarray where values are zero or masked."""

        return (self._values == 0) | self._mask

    ######################################################################################
    # I/O operations
    ######################################################################################

    def __repr__(self):
        """Express the value as a string.

        The format of the returned string is `Class([value, value, ...], suffixes, ...)`,
        where the quanity inside square brackets is the result of str() applied to a NumPy
        ndarray.

        The suffixes are, in order...

        * "denom=(shape)" if the object has a denominator;
        * "mask" if the object has a mask
        * the name of the unit of the object has a unit
        * the names of all the derivatives in alphabetical order

        Returns:
            str: String representation
        """

        return self.__str__()

    def __str__(self):
        """Express the value as a string.

        The format of the returned string is `Class([value, value, ...], suffixes, ...)`,
        where the quanity inside square brackets is the result of str() applied to a NumPy
        ndarray.

        The suffixes are, in order...

        * "denom=(shape)" if the object has a denominator;
        * "mask" if the object has a mask
        * the name of the unit of the object has a unit
        * the names of all the derivatives in alphabetical order

        Returns:
            str: String representation
        """

        suffix = []

        # Indicate the denominator shape if necessary
        if self._denom != ():
            suffix += ['denom=' + str(self._denom)]

        # Masked objects have a suffix ', mask'
        is_masked = np.any(self._mask)
        if is_masked:
            suffix += ['mask']

        # Objects with a unit include the unit in the suffix
        if not self.is_unitless():
            suffix += [str(self._unit)]

        # Objects with derivatives include a list of the names
        if self._derivs:
            keys = list(self._derivs.keys())
            keys.sort()
            for key in keys:
                suffix += ['d_d' + key]

        # Generate the value string
        scaled = self.into_unit(recursive=False)    # apply the unit
        if self._is_scalar:
            if is_masked:
                string = '--'
            else:
                string = str(scaled)
        elif is_masked:
            temp = Qube(scaled, self._mask, example=self, derivs={})
            string = str(temp.mvals)[1:-1]
        else:
            string = str(scaled)[1:-1]

        # Add an extra set of brackets around derivatives
        if self._denom:
            string = '[' + string + ']'

        # Concatenate the results
        if len(suffix) == 0:
            suffix = ''
        else:
            suffix = '; ' + ', '.join(suffix)

        return type(self).__name__ + '(' + string + suffix + ')'

    def _opstr(self, /, op):
        """An operation string to use in an error message for this class.

        Parameters:
            op (str): Name of the operation.

        Returns:
            str: The class name followed by the operation, updated for an error message.
        """

        name = self.__name__ if isinstance(self, type) else type(self).__name__

        if not op:
            return name

        if op[0].isalpha():
            return name + '.' + op

        return name + ' "' + op + '"'

    def _disallow_denom(self, op):
        """Raise ValueError if this object has a denominator.

        Parameters:
            op (str): Name of the operation to appear in the error message.
        """

        if self._drank:
            raise ValueError(self._opstr(op) + ' does not support denominators')

    def _require_scalar(self, op):
        """Raise ValueError if this object has rank > 0.

        Parameters:
            op (str): Name of the operation to appear in the error message.
        """

        if self._nrank:
            raise ValueError(self._opstr(op) + ' requires scalar items')

    def _require_axis_in_range(self, axis, rank, op, name='axis'):
        """Raise ValueError if a given axis index is out of range.

        Parameters:
            axis (int): Axis index, positive or negative.
            rank (int): Rank of an array for indexing.
            op (str): Name of the operation to appear in the error message.
            name (str, optional): Name of axis variable.

        Raises:
            ValueError: If axis < -rank or >= rank.
        """

        if axis < -rank or axis >= rank:
            opstr = self._opstr(op)
            raise ValueError(f'{opstr} {name} is out of range ({-rank},{rank}): {axis}')

    ######################################################################################
    # from_scalars() special method
    ######################################################################################

    @classmethod
    def from_scalars(cls, *scalars, recursive=True, readonly=False, classes=[]):
        """A new instance constructed from Scalars or arrays given as arguments.

        Defined as a class method so it can also be used to generate instances of any 1-D
        subclass.

        Parameters:
            *scalars (Qube, array-like, float, or int):
                One or more Scalars or objects that can be converted to Scalars.
            recursive (bool, optional):
                True to construct the derivatives as the union of the derivatives of all
                the components' derivatives. False to return an object without
                derivatives.
            readonly (bool, optional):
                True to return a read-only object; False (the default) to return something
                potentially writable.
            classes: (class or list[class]):
                A list defining the preferred class of the returned object. The first
                suitable class in the list will be used; default is [Vector].

        Returns:
            Qube: A new object constructed from the inputs and using the first suitable
            class within `classes`.

        Raises:
            ValueError: If two of the `scalars` have incompatible denominators.
        """

        # Convert to scalars and broadcast to the same shape
        args = []
        for arg in scalars:
            scalar = Qube._SCALAR_CLASS.as_scalar(arg)
            args.append(scalar)

        scalars = Qube.broadcast(*args, recursive=recursive)

        # Tabulate the properties and construct the value array
        new_unit = None
        new_denom = None

        arrays = []
        masks = []
        deriv_dicts = []
        has_derivs = False
        dtype = np.int64
        for scalar in scalars:
            arrays.append(scalar._values)
            masks.append(scalar._mask)

            new_unit = new_unit or scalar._unit
            Unit.require_match(new_unit, scalar._unit)

            if new_denom is None:
                new_denom = scalar._denom
            elif new_denom != scalar._denom:
                raise ValueError(f'incompatible denominators in {cls}.from_scalars(): '
                                 f'{scalar._denom}, {new_denom}')

            deriv_dicts.append(scalar._derivs)
            if len(scalar._derivs):
                has_derivs = True

            # Remember any floats encountered
            if scalar.is_float():
                dtype = np.float64

        # Construct the values array
        new_drank = len(new_denom)
        new_values = np.array(arrays, dtype=dtype)
        new_values = np.rollaxis(new_values, 0, new_values.ndim - new_drank)

        # Construct the mask (scalar or array)
        masks = Qube.broadcast(*masks)
        new_mask = Qube.or_(*masks)

        # Construct the object
        obj = Qube.__new__(cls)
        obj.__init__(new_values, new_mask, unit=new_unit, nrank=scalars[0]._nrank + 1,
                     drank=new_drank)
        obj = obj.cast(classes)

        # Insert derivatives if necessary
        if recursive and has_derivs:
            new_derivs = {}

            # Find one example of each derivative
            examples = {}
            for deriv_dict in deriv_dicts:
                for key, deriv in deriv_dict.items():
                    examples[key] = deriv

            for key, example in examples.items():
                items = []
                if example._item:
                    missing_deriv = Qube(np.zeros(example._item), nrank=example._nrank,
                                         drank=example._drank, op='from_scalars()')
                else:
                    missing_deriv = 0.

                for deriv_dict in deriv_dicts:
                    items.append(deriv_dict.get(key, missing_deriv))

                new_derivs[key] = Qube.from_scalars(*items, recursive=False,
                                                    readonly=readonly, classes=classes)
            obj.insert_derivs(new_derivs)

        return obj

##########################################################################################
