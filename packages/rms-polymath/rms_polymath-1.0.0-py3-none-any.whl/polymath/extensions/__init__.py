################################################################################
# polymath/extensions/__init__.py
################################################################################

from polymath.qube import Qube

from polymath.extensions import broadcaster
Qube.broadcast_into_shape = broadcaster.broadcast_into_shape
Qube.broadcast_to       = broadcaster.broadcast_to
Qube.broadcasted_shape  = broadcaster.broadcasted_shape
Qube.broadcast          = broadcaster.broadcast

from polymath.extensions import indexer
Qube.__getitem__        = indexer.__getitem__
Qube.__setitem__        = indexer.__setitem__
Qube._prep_index        = indexer._prep_index
Qube._prep_scalar_index = indexer._prep_scalar_index

from polymath.extensions import item_ops
Qube.extract_numer      = item_ops.extract_numer
Qube.extract_denom      = item_ops.extract_denom
Qube.extract_denoms     = item_ops.extract_denoms
Qube.slice_numer        = item_ops.slice_numer
Qube.transpose_numer    = item_ops.transpose_numer
Qube.reshape_numer      = item_ops.reshape_numer
Qube.flatten_numer      = item_ops.flatten_numer
Qube.transpose_denom    = item_ops.transpose_denom
Qube.reshape_denom      = item_ops.reshape_denom
Qube.flatten_denom      = item_ops.flatten_denom
Qube.join_items         = item_ops.join_items
Qube.split_items        = item_ops.split_items
Qube.swap_items         = item_ops.swap_items
Qube.chain              = item_ops.chain

from polymath.extensions import iterator
Qube.__iter__           = iterator.__iter__
Qube.ndenumerate        = iterator.ndenumerate

from polymath.extensions import math_ops
Qube.__pos__            = math_ops.__pos__
Qube.__neg__            = math_ops.__neg__
Qube.__abs__            = math_ops.__abs__
Qube.abs                = math_ops.abs
Qube.__len__            = math_ops.__len__
Qube.len                = math_ops.len
Qube.__add__            = math_ops.__add__
Qube.__radd__           = math_ops.__radd__
Qube.__iadd__           = math_ops.__iadd__
Qube._add_derivs        = math_ops._add_derivs
Qube.__sub__            = math_ops.__sub__
Qube.__rsub__           = math_ops.__rsub__
Qube.__isub__           = math_ops.__isub__
Qube._sub_derivs        = math_ops._sub_derivs
Qube.__mul__            = math_ops.__mul__
Qube.__rmul__           = math_ops.__rmul__
Qube.__imul__           = math_ops.__imul__
Qube._mul_by_number     = math_ops._mul_by_number
Qube._mul_by_scalar     = math_ops._mul_by_scalar
Qube._mul_derivs        = math_ops._mul_derivs
Qube.__truediv__        = math_ops.__truediv__
Qube.__rtruediv__       = math_ops.__rtruediv__
Qube.__itruediv__       = math_ops.__itruediv__
Qube._div_by_number     = math_ops._div_by_number
Qube._div_by_scalar     = math_ops._div_by_scalar
Qube._div_derivs        = math_ops._div_derivs
Qube.__floordiv__       = math_ops.__floordiv__
Qube.__rfloordiv__      = math_ops.__rfloordiv__
Qube.__ifloordiv__      = math_ops.__ifloordiv__
Qube._floordiv_by_number = math_ops._floordiv_by_number
Qube._floordiv_by_scalar = math_ops._floordiv_by_scalar
Qube.__mod__            = math_ops.__mod__
Qube.__rmod__           = math_ops.__rmod__
Qube.__imod__           = math_ops.__imod__
Qube._mod_by_number     = math_ops._mod_by_number
Qube._mod_by_scalar     = math_ops._mod_by_scalar
Qube.__pow__            = math_ops.__pow__
Qube._compatible_arg    = math_ops._compatible_arg
Qube.__eq__             = math_ops.__eq__
Qube.__ne__             = math_ops.__ne__
Qube.__lt__             = math_ops.__lt__
Qube.__gt__             = math_ops.__gt__
Qube.__le__             = math_ops.__le__
Qube.__ge__             = math_ops.__ge__
Qube.__bool__           = math_ops.__bool__
Qube.__float__          = math_ops.__float__
Qube.__int__            = math_ops.__int__
Qube.__invert__         = math_ops.__invert__
Qube.__and__            = math_ops.__and__
Qube.__rand__           = math_ops.__rand__
Qube.__or__             = math_ops.__or__
Qube.__ror__            = math_ops.__ror__
Qube.__xor__            = math_ops.__xor__
Qube.__rxor__           = math_ops.__rxor__
Qube.__iand__           = math_ops.__iand__
Qube.__ior__            = math_ops.__ior__
Qube.__ixor__           = math_ops.__ixor__
Qube.logical_not        = math_ops.logical_not
Qube.any                = math_ops.any
Qube.all                = math_ops.all
Qube.any_true_or_masked = math_ops.any_true_or_masked
Qube.all_true_or_masked = math_ops.all_true_or_masked
Qube.reciprocal         = math_ops.reciprocal
Qube.zero               = math_ops.zero
Qube.identity           = math_ops.identity
Qube.sum                = math_ops.sum
Qube.mean               = math_ops.mean
Qube._raise_unsupported_op      = math_ops._raise_unsupported_op
Qube._raise_incompatible_shape  = math_ops._raise_incompatible_shape
Qube._raise_incompatible_numers = math_ops._raise_incompatible_numers
Qube._raise_incompatible_denoms = math_ops._raise_incompatible_denoms
Qube._raise_dual_denoms         = math_ops._raise_dual_denoms

from polymath.extensions import mask_ops
Qube.mask_where         = mask_ops.mask_where
Qube.mask_where_eq      = mask_ops.mask_where_eq
Qube.mask_where_ne      = mask_ops.mask_where_ne
Qube.mask_where_le      = mask_ops.mask_where_le
Qube.mask_where_ge      = mask_ops.mask_where_ge
Qube.mask_where_lt      = mask_ops.mask_where_lt
Qube.mask_where_gt      = mask_ops.mask_where_gt
Qube.mask_where_between = mask_ops.mask_where_between
Qube.mask_where_outside = mask_ops.mask_where_outside
Qube.clip               = mask_ops.clip
Qube.is_below           = mask_ops.is_below
Qube.is_above           = mask_ops.is_above
Qube.is_outside         = mask_ops.is_outside
Qube.is_inside          = mask_ops.is_inside

from polymath.extensions import vector_ops
Qube._mean_or_sum       = vector_ops._mean_or_sum
Qube._check_axis        = vector_ops._check_axis
Qube._zero_sized_result = vector_ops._zero_sized_result
Qube.dot                = vector_ops.dot
Qube.norm               = vector_ops.norm
Qube.norm_sq            = vector_ops.norm_sq
Qube.cross              = vector_ops.cross
Qube.outer              = vector_ops.outer
Qube.as_diagonal        = vector_ops.as_diagonal
Qube.rms                = vector_ops.rms

from polymath.extensions import pickler
Qube.pickle             = pickler       # help(Qube.pickle) shows the docstring
Qube.__getstate__       = pickler.__getstate__
Qube.__setstate__       = pickler.__setstate__
Qube._encode_floats     = pickler._encode_floats
Qube._decode_floats     = pickler._decode_floats
Qube._encode_ints       = pickler._encode_ints
Qube._decode_ints       = pickler._decode_ints
Qube._encode_bools      = pickler._encode_bools
Qube._decode_bools      = pickler._decode_bools
Qube.pickle_digits      = pickler.pickle_digits
Qube.pickle_reference   = pickler.pickle_reference
Qube.set_pickle_digits         = pickler.set_pickle_digits
Qube.set_default_pickle_digits = pickler.set_default_pickle_digits
Qube._check_pickle_digits      = pickler._check_pickle_digits
Qube._pickle_debug             = pickler._pickle_debug

from polymath.extensions import shaper
Qube.reshape            = shaper.reshape
Qube.flatten            = shaper.flatten
Qube.swap_axes          = shaper.swap_axes
Qube.roll_axis          = shaper.roll_axis
Qube.move_axis          = shaper.move_axis
Qube.stack              = shaper.stack

from polymath.extensions import shrinker
Qube.shrink             = shrinker.shrink
Qube.unshrink           = shrinker.unshrink

from polymath.extensions import tvl
Qube.tvl_and            = tvl.tvl_and
Qube.tvl_or             = tvl.tvl_or
Qube.tvl_any            = tvl.tvl_any
Qube.tvl_all            = tvl.tvl_all
Qube.tvl_eq             = tvl.tvl_eq
Qube.tvl_ne             = tvl.tvl_ne
Qube.tvl_lt             = tvl.tvl_lt
Qube.tvl_gt             = tvl.tvl_gt
Qube.tvl_le             = tvl.tvl_le
Qube.tvl_ge             = tvl.tvl_ge
Qube._tvl_op            = tvl._tvl_op

################################################################################
