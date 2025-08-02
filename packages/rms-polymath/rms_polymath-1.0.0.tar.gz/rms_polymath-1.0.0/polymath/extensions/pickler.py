########################################################################################
# polymath/extensions/pickle.py
########################################################################################
"""This module supports the "pickling" of polymath objects.

Because objects such as backplanes can be numerous and also quite large, we provide a
variety of methods, both lossless and lossy, for compressing them during storage. As one
example of optimization, only the un-masked elements of an object are stored; upon
retrieval, all masked elements will have the value of the object's :attr:`~Qube._default
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

**digits** (`str or int`): The number of digits to preserve.

* "double": preserve full precision using lossless **fpzip** compression.
* "single": convert the array to single precision and then store it using lossless
  **fpzip** compression.
* an integer 7-16, defining the number of significant digits to preserve.

**reference** (`str or float`): How to interpret a numeric value of **digits**.

* "fpzip": Use lossy **fpzip** compression, preserving the given number of digits.
* a number: Preserve every number to the exact same absolute precision, scaling the number
  of **digits** by this value. For example, if **digits** = 8 and **reference** = 100,
  all values will be rounded to the nearest 1.e-6 before storage. This method uses option
  3 above, where values are converted to integers for storage.

The remaining options for **reference** provide a variety of ways to allow a reference
number to be generated automatically.

* "smallest": Absolute accuracy will be 10**(-digits) times the non-zero array value
  closest to zero. This option guarantees that every value will preserve at least the
  requested number of digits. This is reasonable if you expect all values to fall within a
  similar dynamic range.
* "largest": Absolute accuracy will be 10**(-digits) times the value in the array furthest
  from zero. This option is useful for arrays that contain a limited range of values, such
  as the components of a unit vector or angles that are known to fall between zero and
  2*pi. In this case, it is probably not necessary to preserve the extra precision in
  values that just happen to fall very close zero.
* "mean": Absolute accuracy will be 10**(-digits) times the mean of the absolute values
  in the array.
* "median": UAbsolute accuracy will be 10**(-digits) times the median of the absolute
  values in the array. This is a good choice if a minority of values in the array are very
  different from the others, such as noise spikes or undefined geometry. In such a case,
  we want the precision to be based on the more "typical" values.
* "logmean": Absolute accuracy will be 10**(-digits) times the log-mean of the absolute
  values in the array.
"""

import bz2
import fpzip
import numpy as np
import numbers
import sys
import warnings

from polymath.qube import Qube

PICKLE_VERSION = (1, 0)

# How many elements in an array before lossy compression might be used.
_FPZIP_ENCODING_CUTOFF = 200
_PICKLE_WARNINGS = False
_PICKLE_DEBUG = False   # If True, __setstate__ includes encoding info
_DEFAULT_PICKLE_DIGITS = ('double', 'double')
_DEFAULT_PICKLE_REFERENCE = ('fpzip', 'fpzip')

# Useful constants relevant to IEEE floats
assert sys.float_info.mant_dig == 53, 'Serious trouble: floats are not IEEE'
_SINGLE_DIGITS = np.log10(2**23)    # 6.92
_DOUBLE_DIGITS = np.log10(2**52)    # 15.65
_LOG10_BIT = np.log10(2.)

@staticmethod
def _pickle_debug(debug):
    global _PICKLE_DEBUG
    _PICKLE_DEBUG = debug


def set_pickle_digits(self, digits='double', reference='fpzip'):
    """Set the desired number of decimal digits of precision in the storage of this
    object's floating-point values and their derivatives.

    This attribute is ignored for integer and boolean values.

    Parameters:
        digits (int, float, str or tuple, optional):
            The number of digits to preserve when pickling this object. If two values are
            given, the second applies to any derivatives. If a number is specified, this
            is the number of decimal digits to preserve when this object is pickled. It
            need not be an integer. It is truncated to the range supported by single and
            double precision. Alternatively, use "double" to preserve full double
            precision; use "single" for single precision.

        reference (int, float, str or tuple, optional):
            A value defining the number to use when assessing how many digits are
            preserved. If two values are given, the second applies to any derivatives. If
            a number is specified, the number of `digits` will be relative to this value.
            For example, if the `reference=100` and `digits=8`, the absolute precision
            will be 1.e-6. Alternatively, use one of these strings to let the precision be
            referenced to the values in the array: "smallest", "largest", "mean",
            "median", "logmean", or "fpzip".

    Notes:
        The reference options are:

            * "smallest": Reference precision to the value closest to zero. This option
              guarantees that the requested number of digits are preserved for every
              value.
            * "largest": Reference precision to the value furthest from zero; this is a
              good choice for values that are known to have a limited range that includes
              zero, e.g., the components of a unit vector, or an angle between zero and
              two pi.
            * "mean": Reference the mean absolute value.
            * "median": Reference the median absolute value. This is a good choice if a
              minority of values are very different from the others, but those values
              should not dominate the precision determination.
            * "logmean": Reference the mean of the log of absolute values.
            * "fpzip": Employ fpzip compression.
    """

    reference = _validate_pickle_reference(reference)
    digits = _validate_pickle_digits(digits, reference)

    self._pickle_digits = digits
    self._pickle_reference = reference

    # Handle derivatives
    if self._derivs:
        deriv_digits = (digits[1], digits[1])
        deriv_reference = (reference[1], reference[1])

        for deriv in self._derivs.values():
            deriv._pickle_digits = deriv_digits
            deriv._pickle_reference = deriv_reference


@staticmethod
def set_default_pickle_digits(digits='double', reference='fpzip'):
    """Set the default number of decimal digits of precision in the storage of
    floating-point values and their derivatives.

    Parameters:
        digits (int, float, str or tuple, optional):
            The number of digits to preserve when pickling this object. If two values are
            given, the second applies to any derivatives. If a number is specified, this
            is the number of decimal digits to preserve when this object is pickled. It
            need not be an integer. It is truncated to the range supported by single and
            double precision. Alternatively, use "double" to preserve full double
            precision; use "single" for single precision.
        reference (int, float, str or tuple, optional):
            A value defining the number to use when assessing how many digits are
            preserved. If two values are given, the second applies to any derivatives. If
            a number is specified, the number of `digits` will be relative to this value.
            For example, if the `reference=100` and `digits=8`, the precision will be
            1.e-6. Alternatively, use one of these strings to let the precision be
            referenced to the values in the array: "smallest", "largest", "mean",
            "median", "logmean", or "fpzip".

    Notes:
        The reference options are:

            * "smallest": Reference precision to the value closest to zero. This option
              guarantees that the requested number of digits are preserved for every
              value.
            * "largest": Reference precision to the value furthest from zero; this is a
              good choice for values that are known to have a limited range that includes
              zero, e.g., the components of a unit vector, or an angle between zero and
              two pi.
            * "mean": Reference the mean absolute value.
            * "median": Reference the median absolute value. This is a good choice if a
              minority of values are very different from the others, but those values
              should not dominate the precision determination.
            * "logmean": Reference the mean of the log of absolute values.
            * "fpzip": Employ fpzip compression.
    """

    global _DEFAULT_PICKLE_DIGITS, _DEFAULT_PICKLE_REFERENCE

    reference = _validate_pickle_reference(reference)
    _DEFAULT_PICKLE_REFERENCE = reference
    _DEFAULT_PICKLE_DIGITS = _validate_pickle_digits(digits, reference)


def pickle_digits(self):
    """The digits of floating-point precision to include when pickling this object and its
    derivatives.

    Returns:
        (str, float, or int): One of "double", "single", or a number of digits roughly in
        the range 7-16.
    """

    if not hasattr(self, '_pickle_digits') or self._pickle_digits is None:
        self._pickle_digits = _DEFAULT_PICKLE_DIGITS

    return self._pickle_digits


def pickle_reference(self):
    """The reference value to use when determining the number of digits of floating-point
    precision in this object and its derivatives.

    Returns:
        (str, float, or int): One of "fpzip", "smallest", "largest", "mean", "median",
        "logmean", or a number.
    """

    if (not hasattr(self, '_pickle_reference')
            or self._pickle_reference is None):
        self._pickle_reference = _DEFAULT_PICKLE_REFERENCE

    return self._pickle_reference


def _check_pickle_digits(self):
    """Validate the pickle attributes."""

    if hasattr(self, '_pickle_reference'):
        reference = self._pickle_reference
    else:
        reference = None

    reference = _validate_pickle_reference(reference)
    self._pickle_reference = reference

    if hasattr(self, '_pickle_digits'):
        digits = self._pickle_digits
    else:
        digits = None

    self._pickle_digits = _validate_pickle_digits(digits, reference)

    for key, deriv in self._derivs.items():
        if not hasattr(deriv, '_pickle_digits'):
            deriv._pickle_digits = 2 * self._pickle_digits[1:]
        if not hasattr(deriv, '_pickle_reference'):
            deriv._pickle_reference = 2 * self._pickle_reference[1:]


def _validate_pickle_digits(digits, reference):
    """Validate and return the pickle digit values."""

    original_digits = digits

    if digits is None:
        digits = 'double'

    if isinstance(digits, list):
        digits = tuple(digits)

    elif not isinstance(digits, tuple):
        digits = (digits, digits)

    new_digits = []
    try:
        for k, digit in enumerate(digits[:2]):
            if isinstance(digit, numbers.Real):
                if not isinstance(reference[k], numbers.Real):
                    digit = min(max(_SINGLE_DIGITS, float(digit)), _DOUBLE_DIGITS)
            elif digit not in {'single', 'double'}:
                raise ValueError('invalid pickle digits: ' + repr(digit))

            new_digits.append(digit)

    except (ValueError, IndexError, TypeError):
        raise ValueError('invalid pickle digits: ' + repr(original_digits))

    return tuple(new_digits)


def _validate_pickle_reference(references):
    """Validate and return the pickle reference values."""

    original_references = references    # Flake8 thinks this variable is unused # noqa

    if references is None:
        references = 'fpzip'

    if isinstance(references, list):
        references = tuple(references)

    elif not isinstance(references, tuple):
        references = (references, references)

    try:
        references = references[:2]
        for reference in references[:2]:
            if isinstance(reference, numbers.Real):
                pass
            elif reference not in {'smallest', 'largest', 'mean', 'median', 'logmean',
                                   'fpzip'}:
                raise ValueError('invalid pickle reference {reference!r}')

    except (ValueError, IndexError, TypeError):
        raise ValueError('invalid pickle reference {original_references!r}')

    return references

################################################################################
# Support for fpzip compression and decompression
################################################################################

def fpzip_compress(array, digits=16, dtype=np.float64):
    """Return an fpzip-compressed array plus the number of bits that have been zeroed."""

    array = np.require(array, dtype=dtype, requirements=['C', 'A', 'W'])
    shape = array.shape

    # Determine the precision
    # The "precision" input to fpzip.compress is not well documented. I found this:
    # https://github.com/LLNL/fpzip/blob/develop/include/fpzip.h
    #
    # The library ... allows specifying how many bits of precision to retain by truncating
    # each floating-point value and discarding the least significant bits; the remaining
    # bits are compressed losslessly.  The precision is limited to integers 2-32 for
    # floats. For doubles, precisions 4-64 are supported in increments of two bits.  The
    # decompressed data is returned in full precision with any truncated bits zeroed.
    #
    # Experimentation shows that the number of truncated bits is 64-precision for double
    # precision and 32-precision for single.

    dtype = np.dtype(dtype)
    if dtype.itemsize == 8:
        zeroed_bits = int((_DOUBLE_DIGITS - digits) / _LOG10_BIT)
        zeroed_bits = min(max(0, zeroed_bits), 64)
        zeroed_bits = 2 * (zeroed_bits // 2)
        precision = 64 - zeroed_bits
    else:
        zeroed_bits = int((_SINGLE_DIGITS - digits) / _LOG10_BIT)
        zeroed_bits = min(max(0, zeroed_bits), 32)
        precision = 32 - zeroed_bits

    # Limit dimensions to four
    if array.ndim > 4:
        shape = (-1,) + shape[-3:]
        array = array.reshape(shape)
    else:
        shape = array.shape

    # Two fpzip exceptions appear often enough to need to be addressed.
    #
    # fpzip.FpzipWriteError: Compression failed. memory buffer overflow
    #   This appears to be related to arrays with relatively few elements and with those
    #   elements spread across too many axes. The functioning workaround is to reduce the
    #   number of axes and try again. Also, the value of _FPZIP_ENCODING_CUTOFF above
    #   appears to be large enough to minimize these occurrences.
    #
    # fpzip.FpzipWriteError: Compression failed. precision not supported
    #   This occurs if the requested precision is too small, or if it is odd for
    #   double-precision arrays. The workaround is to increase the precision and try
    #   again.

    first_exception = None
    initial_precision = precision
    initial_shape = shape

    while True:
        array = array.reshape(shape)
        try:
            fpzip_bytes = fpzip.compress(array, precision=precision)

        except fpzip.FpzipWriteError as e:

            # Save first exception in case we need it later
            if first_exception is None:
                first_exception = e

            # "Compression failed. precision not supported"
            if 'precision not supported' in str(e):
                if precision == 0:
                    raise first_exception
                precision += (dtype.itemsize//4)    # add 2 if double, 1 if single

            # "Compression failed. memory buffer overflow"
            elif 'memory buffer overflow' in str(e):
                if len(shape) == 1:
                    raise first_exception
                shape = (-1,) + shape[2:]           # reduce the number of axes
                array = array.reshape(shape)

            # Unknown exception
            else:
                raise

        else:
            # Raise any warnings
            if _PICKLE_WARNINGS and first_exception is not None:
                if precision != initial_precision:
                    warnings.warn('fpzip.compress increased precision from '
                                  f'{initial_precision} to {precision}')
                if shape != initial_shape:
                    warnings.warn('fpzip.compress reduced shape from '
                                  f'{initial_shape} to {shape}')

            return (fpzip_bytes, zeroed_bits)


def fpzip_decompress(fpzip_bytes, shape, bits):
    """Return an fpzip-decompressed array with compensation for any compression
    bias.
    """

    floats = fpzip.decompress(fpzip_bytes).astype(np.float64).reshape(shape)

    if bits == 0:
        return floats

    # fpzip does lossy compression by zeroing out a specified number of least significant
    # bits in the mantissa. In practice, this means that, after decompression, all numbers
    # are systematically closer to zero.
    #
    # If the number of truncated bits is N, then on average, the integer mantissas will be
    # closer to zero by (2**N - 1)/2. For example, if two bits have been zeroed out, then
    # the mean value lost is the average of (0, 1, 2, 3), which is 1.5. Our solution is to
    # add back a pattern of values that roughly alternates between 2**(N-1) - 1 and
    # 2**(N-1). For example, if N == 2, that would be an alternation between 1 and 2; if N
    # == 8, the alternation would be between 127 and 128.
    #
    # However, a strict alternation would have very small but systematic affects on an
    # object with an even number of items, such as a Pair, Quaternion, or even-sided
    # matrix. So instead, we follow a repeating pattern of 14 offsets. This will only have
    # a systematic affect on an object if the number of items is a multiple of 14, which
    # is an unlikely case.

    # This is a randomly generated sequence of 7 items, either (0, 1) or (1, 0).
    BIT_SEQUENCE = np.array([0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1])

    # bits is the number of trailing bits that have been zeroed
    # Create an alternating pattern of integer offsets as discussed above.
    offset = 2**(bits-1)
    pattern = np.array([offset-1, offset])[BIT_SEQUENCE]
    repeats = (floats.size + len(pattern) - 1) // len(pattern)
    pattern = np.broadcast_to(pattern, (repeats, len(pattern)))
    pattern = pattern.ravel()[:floats.size]

    # Add the new trailing bits of the mantissa
    if floats.dtype.itemsize == 8:
        view = floats.ravel().view(dtype='uint64')
        pattern = pattern.astype('uint64')
    else:
        view = floats.ravel().view(dtype='uint32')
        pattern = pattern.astype('uint32')

    view += pattern

    return floats

################################################################################
# Support for compression using integers plus an offset and scale factor
################################################################################

def _encode_one_float_array(values, digits, reference):
    """Encode one array into a tuple for the specified digits precision.

    Parameters:
        values (ndarray): Array of floats to encode.
        digits (float): Number of digits to preserve.
        reference (str or float): One of 'smallest', 'largest', 'mean', 'median',
            'logmean', 'fpzip', or a number.

    Returns:
        tuple: Encoded array in one of several formats depending on the compression method
        used.
    """

    # Handle fpzip method first
    if reference == 'fpzip':
        (fpzip_bytes, bits) = fpzip_compress(values, digits=digits)
        return ('fpzip', values.shape, bits, fpzip_bytes)

    # Prep the array
    shape = values.shape
    raveled = values.ravel()

    # Determine the range
    minval = np.min(values)
    maxval = np.max(values)
    span = maxval - minval

    # Handle a constant
    if span == 0.:
        return ('constant', shape, minval)

    # Determine the number of digits to be accommodated by the offset
    if isinstance(reference, numbers.Real):
        max_value = max(-minval, maxval)
        digits = digits + np.log10(max_value / reference)
        ref_value = max_value

    else:
        abs_values = np.abs(raveled[raveled != 0.])     # exclude zeros here
        if reference == 'smallest':
            ref_value = np.min(abs_values)
        elif reference == 'largest':
            ref_value = np.max(abs_values)
        elif reference == 'mean':
            ref_value = np.mean(abs_values)
        elif reference == 'median':
            ref_value = np.median(abs_values)
        elif reference == 'logmean':
            ref_value = np.exp(np.mean(np.log(abs_values)))
        else:
            raise ValueError('invalid reference %s' % repr(reference))

    precision = ref_value * 10.**(-digits)
    unique_values_needed = span / precision + 1
    bytes_needed = np.log(unique_values_needed) / np.log(256)
    nbytes = -int(-bytes_needed // 1)               # nbytes is rounded up

    # In nbytes > 6, better to use double precision plus fpzip
    if nbytes > 6:
        (fpzip_bytes, bits) = fpzip_compress(values)
        return ('float64', shape, bits, fpzip_bytes)

    # Sometimes the test reveals that single precision fpzip is best
    if nbytes == 4 and digits <= _SINGLE_DIGITS:
        (fpzip_bytes, bits) = fpzip_compress(values, dtype=np.float32)
        return ('float32', shape, bits, fpzip_bytes)

    # Set the offset as the minimum; scale for an unsigned int
    scale_factor = (256. ** nbytes) / span
    scale_factor *= (1. - sys.float_info.epsilon)
    # We require span * scale_factor to be less than  2**n by just a little bit, so it
    # truncates to 2**n - 1.
    new_values = scale_factor * (raveled - minval)

    # Select the dtype to encode
    dtype = 'uint8' if nbytes % 2 else 'uint32' if nbytes == 4 else 'uint16'

    # Convert to contiguous, significant bytes as quickly as possible
    if nbytes in (1, 2, 4):
        bz2_ints = new_values.astype(dtype)
    elif nbytes == 3:
        new_values = new_values.astype('uint32')
        bz2_ints = new_values.view('uint8').reshape(-1, 4)[:, :3].copy()
    elif nbytes == 5:
        new_values = new_values.astype('uint64')
        bz2_ints = new_values.view('uint8').reshape(-1, 8)[:, :nbytes].copy()
    else:   # nbytes == 6
        new_values = new_values.astype('uint64')
        bz2_ints = new_values.view('uint16').reshape(-1, 4)[:, :3].copy()

    # To reverse:
    #   values = new_values/scale_factor + minval + 0.5/scale_factor
    # The last term is to make sure the restored values are not systematically smaller
    # than they were originally

    return ('scaled', shape, dtype, nbytes,
            1./scale_factor, minval + 0.5/scale_factor, bz2.compress(bz2_ints))


def _encode_floats(values, rank, digits, reference):
    """Complete encoding of a floating-point array.

    A tuple is returned in one of these forms:
        ('literal', array)
        ('float64', shape, fpzipped array)
        ('float32', shape, fpzipped array)
        ('constant', shape, single value)
        ('scaled', shape, dtype, nbytes, scale_factor, offset, bz-compressed
                   unsigned ints)
            where:
                dtype is one of 'uint8', 'uint16', 'uint32'
                nbytes is the number of bytes in each encoded item
            The correctly scaled return value is
                values = scale_factor * uints + offset
        ('items', shape, item_rank, list of individual encoded items)

    Parameters:
        values (ndarray): Array of values to encode.
        rank (int): Rank of the individual items in this array.
        digits (str or float): 'float64', 'float32', or number of digits to
            preserve.
        reference (str): One of 'smallest', 'largest', 'mean', 'median',
            'logmean', or 'fpzip'.

    Returns:
        tuple: Encoded array in one of several formats depending on the
            compression method used.
    """

    shape = values.shape
    item = shape[-rank:] if rank else ()
    item_size = int(np.prod(item))

    # Deal with a small object quickly
    if values.size <= _FPZIP_ENCODING_CUTOFF:
        array = np.require(values, dtype=np.float64, requirements=['C', 'A'])
        return ('literal', array)

    # Handle "single" and "double"
    if digits == 'double':
        (fpzip_bytes, bits) = fpzip_compress(values)
        return ('float64', shape, bits, fpzip_bytes)

    if digits == 'single':
        (fpzip_bytes, bits) = fpzip_compress(values, dtype=np.float32)
        return ('float32', shape, bits, fpzip_bytes)

    # Handle shapeless items
    if item == ():
        return _encode_one_float_array(values, digits, reference)

    # Encode each item element separately for better encoding, because ranges
    # can be very different.

    # Isolate the leading and trailing items into a 2-D array
    array = values.reshape((-1,) + (item_size,))
    array = array.swapaxes(0, 1)            # item axis first
    array = np.require(array, requirements=['C', 'A'])

    encoded = []
    for element in array:
        encoded.append(_encode_one_float_array(element, digits, reference))

    return ('items', shape, rank, encoded)


def _decode_scaled_uints(encoded):
    """Decode a scaled, compressed array of unsigned integers."""

    (_, shape, dtype, nbytes, scale_factor, offset, bz2_bytes) = encoded
    bz2_ints = np.frombuffer(bz2.decompress(bz2_bytes), dtype=dtype)

    # Convert given number of bytes to an int as quickly as possible
    if nbytes == 3:
        new_ints = np.zeros(shape, dtype='uint32')
        view = new_ints.view('uint8').reshape(-1, 4)
        view[:, :3] = bz2_ints.reshape(-1, nbytes)
    elif nbytes in (5, 7):
        new_ints = np.zeros(shape, dtype='uint64')
        view = new_ints.view('uint8').reshape(-1, 8)
        view[:, :nbytes] = bz2_ints.reshape(-1, nbytes)
    elif nbytes == 6:
        new_ints = np.zeros(shape, dtype='uint64')
        view = new_ints.view('uint16').reshape(-1, 4)
        view[:, :3] = bz2_ints.reshape(-1, 3)
    else:
        new_ints = bz2_ints

    return scale_factor * new_ints.reshape(shape) + offset


def _decode_floats(encoded):
    """Complete decoding of a floating-point array."""

    method = encoded[0]

    if method in ('float32', 'float64', 'fpzip'):
        (_, shape, bits, fpzip_bytes) = encoded
        return fpzip_decompress(fpzip_bytes, shape, bits)

    if method == 'literal':
        return encoded[1]

    if method == 'constant':
        (_, shape, constant) = encoded
        values = np.empty(shape)
        values.fill(constant)
        return values

    if method == 'scaled':
        return _decode_scaled_uints(encoded)

    # Must be 'items'
    if method != 'items':
        raise ValueError('unrecognized method for decoding: %s' % method)

    (_, shape, item_rank, items) = encoded
    if len(items) == 1:
        return _decode_floats(items[0]).reshape(shape)

    # Create an empty buffer with flattened item axes first, so each item index
    # points to a contiguous array
    values = np.empty((len(items),) + shape[:-item_rank])
    for k, item in enumerate(items):
        values[k] = _decode_floats(item)

    # Fix the item axes and make contiguous
    return np.moveaxis(values, 0, -1).copy().reshape(shape)


def _encode_ints(values):
    """Encode an integer array using BZ2 compression."""

    if not values.flags['CONTIGUOUS']:
        values = values.copy()

    return bz2.compress(values)


def _decode_ints(values, shape):
    """Decode an integer array using BZ2 decompression."""

    bz2_bytes = bz2.decompress(values)
    return np.frombuffer(bz2_bytes, dtype='int').reshape(shape)


def _encode_bools(values):
    """Encode a boolean array using packbits + BZ2 compression."""

    if not values.flags['CONTIGUOUS']:
        values = values.copy()

    return bz2.compress(np.packbits(values))


def _decode_bools(values, shape, size):
    """Decode a boolean array using BZ2 decompression."""

    bz2_bytes = bz2.decompress(values)
    packed = np.frombuffer(bz2_bytes, dtype='uint8')
    bools = np.unpackbits(packed).astype('bool')
    bools = bools[:size]
    return bools.reshape(shape)

################################################################################
# __getstate__ and __setstate__
################################################################################

def __getstate__(self):
    """The state is defined by a dictionary containing most of the Qube attributes.

    "_cache" is removed.

    "_mask", and "_values" are replaced by encodings, as discussed below.

    "PICKLE_VERSION" is added, with a value defined by the current version.

    New attribute "MASK_ENCODING" is a list of the steps that have been applied to the
    mask. Each item in the list is a tuple, one of:

    * ('CORNERS', corners), where corners is the tuple returned by Qube._find_corners()
    * ('BOOL', shape, size), where the mask has been converted to packed bits and
      BZ2-compressed; shape is its final shape; size is its final size.

    The list will be empty if no compression has been applied.

    New attribute "VALS_ENCODING" is a list of the steps that have been applied to the
    values. Each item in the list is a tuple, one of:
    * ('ALL_MASKED',) if the object is fully masked, so no values are saved.
    * ('ANTIMASKED',) if the antimask has been applied.
    * ('FLOAT', digits, reference) for any floating-point compression performed.
    * ('BOOL', shape, size) if packbits plus BZ2 compression was performed.
    * ('INT', shape) if BZ2 compression of integers was performed.
    """

    # Start with a shallow clone; save derivatives for later
    clone = self.clone(recursive=False)

    # Add the new attributes (or placeholders)
    clone.PICKLE_VERSION = PICKLE_VERSION
    clone.VALS_ENCODING = []
    clone.MASK_ENCODING = []

    _check_pickle_digits(clone)

    # For a single value, nothing changes
    if isinstance(self._values, (numbers.Real, np.bool_)):
        antimask = None             # used below

    # For a fully masked object, remove the values
    elif np.all(self._mask):
        clone._mask = True         # convert to bool if it's an array
        clone._values = None
        clone.VALS_ENCODING.append(('ALL_MASKED',))
        antimask = None

    # Otherwise, _values is an array and not fully masked
    else:

        ############################
        # Encode the mask array
        ############################

        if not np.any(self._mask):
            clone._mask = False    # convert to bool if it's an array

        mask_shape = np.shape(clone._mask)

        if mask_shape:
            # If any "edges" of the mask array are all True, save the corners
            # and reduce the mask size
            corners = self.corners
            if Qube._shape_from_corners(corners) != self._shape:
                clone.MASK_ENCODING.append(('CORNERS', corners))
                clone._mask = self._mask[self._slicer].copy()

            clone.MASK_ENCODING.append(('BOOL', clone._mask.shape, clone._mask.size))
            clone._mask = _encode_bools(clone._mask)

        ############################
        # Encode the values array
        ############################

        # Select the antimasked values; otherwise, flatten the shape axes.
        # At this point, the values array is always 2-D.
        if mask_shape:
            antimask = self.antimask
            clone._values = clone._values[antimask]
            clone.VALS_ENCODING.append(('ANTIMASKED',))
        else:
            antimask = None

        # Floating-point arrays receive special handling for improved
        # compression
        dtype = self.dtype()
        if dtype == 'float':
            _check_pickle_digits(clone)
            digits = clone._pickle_digits[0]
            reference = clone._pickle_reference[0]
            clone.VALS_ENCODING.append(('FLOAT', digits, reference))
            clone._values = _encode_floats(clone._values, rank=len(self._item),
                                           digits=digits, reference=reference)

        # Integers use straight BZ2-encoding
        elif dtype == 'int':
            shape = clone._values.shape
            clone.VALS_ENCODING.append(('INT', shape))
            clone._values = _encode_ints(clone._values)

        # Booleans use BZ2-encoding of the packed bits
        else:
            shape = clone._values.shape
            size = clone._values.size
            clone.VALS_ENCODING.append(('BOOL', shape, size))
            clone._values = _encode_bools(clone._values)

    ############################
    # Process the derivatives
    ############################

    # We replace the each derivative by a tuple:
    #   (class, __getstate__ value).
    # However, we first modify each derivative, applying the antimask, if any, and
    # removing its own mask. This avoids the duplication of masks.

    if self._derivs:
        deriv_digits = 2 * clone._pickle_digits[1:]
        deriv_reference = 2 * clone._pickle_reference[1:]

        for key, deriv in self._derivs.items():
            new_deriv = deriv.clone(recursive=False)
            if not hasattr(new_deriv, '_pickle_digits'):
                new_deriv._pickle_digits = deriv_digits
            if not hasattr(new_deriv, '_pickle_reference'):
                new_deriv._pickle_reference = deriv_reference

            if antimask is None:
                new_deriv = deriv
            else:
                new_deriv._values = deriv._values[antimask]
                new_deriv._mask = False

            clone._derivs[key] = (type(deriv), new_deriv.__getstate__())

    return clone.__dict__


def __setstate__(self, state):

    # Handle renamed keys
    if '_units_' in state:
        state['_unit'] = state['_units_']
        del state['_units_']
        keys = list(state.keys())
        for key in keys:
            if key.endswith('_'):
                state[key[:-1]] = state[key]
                del state[key]

    self.__dict__ = state

    if _PICKLE_DEBUG:
        mask_encoding = list(self.MASK_ENCODING)
        vals_encoding = list(self.VALS_ENCODING)
        self.ENCODED_MASK = self._mask
        self.ENCODED_VALS = self._values
    else:
        mask_encoding = self.MASK_ENCODING
        vals_encoding = self.VALS_ENCODING
        delattr(self, 'PICKLE_VERSION')
        delattr(self, 'VALS_ENCODING')
        delattr(self, 'MASK_ENCODING')

    ############################
    # Decode the mask
    ############################

    mask_is_writable = not bool(mask_encoding)  # True if mask was not encoded
    while mask_encoding:
        encoding = mask_encoding.pop()
        method = encoding[0]

        if method == 'BOOL':
            (_, shape, size) = encoding
            self._mask = _decode_bools(self._mask, shape, size)
            mask_is_writable = True

        elif method == 'CORNERS':
            (_, corners) = encoding
            new_mask = np.ones(self._shape, dtype='bool')
            slicer = Qube._slicer_from_corners(corners)
            new_mask[slicer] = self._mask
            self._mask = new_mask
            mask_is_writable = True

        else:
            raise ValueError('unrecognized mask encoding: ' + str(encoding[0]))

    # Define the antimask
    if np.shape(self._mask):
        antimask = np.logical_not(self._mask)
    else:
        antimask = None

    # Decode the values
    values_is_writable = not bool(vals_encoding)    # True if values not encoded
    while vals_encoding:
        encoding = vals_encoding.pop()
        method = encoding[0]

        if method == 'INT':
            (_, shape) = encoding
            self._values = _decode_ints(self._values, shape)

        elif method == 'BOOL':
            (_, shape, size) = encoding
            self._values = _decode_bools(self._values, shape, size)
            values_is_writable = True

        elif method == 'FLOAT':
            self._values = _decode_floats(self._values)
            values_is_writable = True

        elif method == 'ANTIMASKED':
            if antimask is None:
                raise ValueError('missing antimask for decoding')
            new_values = np.empty(self._shape + self._item,
                                  dtype=Qube._dtype(self._default))
            new_values[...] = self._default
            new_values[antimask] = self._values
            self._values = new_values
            values_is_writable = True

        elif method == 'ALL_MASKED':
            new_values = np.empty(self._shape + self._item,
                                  dtype=Qube._dtype(self._default))
            new_values[...] = self._default
            self._values = new_values
            values_is_writable = True

        else:
            raise ValueError('unrecognized values encoding: ' + str(encoding))

    ############################
    # Set readonly status
    ############################

    if self._readonly:
        self.as_readonly()
    else:
        if not mask_is_writable:
            self._mask = self._mask.copy()
        if not values_is_writable:
            self._values = self._values.copy()

    ############################
    # Expand the derivatives
    ############################

    for key, deriv_tuple in self._derivs.items():
        (class_, deriv) = deriv_tuple
        new_deriv = Qube.__new__(class_)
        new_deriv.__setstate__(deriv)

        if antimask is not None:
            new_values = np.empty(self._shape + new_deriv._item)
            new_values[...] = new_deriv._default
            new_values[antimask] = new_deriv._values
            new_deriv._values = new_values
            new_deriv._mask = self._mask

        if deriv['_readonly']:
            new_deriv.as_readonly()

        self.insert_deriv(key, new_deriv)

##########################################################################################
