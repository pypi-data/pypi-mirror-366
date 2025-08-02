import ctypes, os, sys, platform, sysconfig
from ctypes import Structure, c_float, c_double, c_int, c_int8, c_int16, c_int32, c_int64, c_uint8, c_uint16, c_uint32, c_uint64, c_size_t, c_void_p, c_char_p, POINTER
from typing import *

def _get_lib_path():
  pkg_dir = os.path.dirname(__file__)
  possible_names = ['array', 'libarray']
  possible_exts = ['.pyd', '.dll', '.so', '.dylib', sysconfig.get_config_var('EXT_SUFFIX') or '']
  search_dirs = [pkg_dir, os.path.join(pkg_dir, 'lib'), os.path.join(pkg_dir, '..', 'build')]

  for search_dir in search_dirs:
    if not os.path.exists(search_dir): continue
    for root, dirs, files in os.walk(search_dir):
      for file in files:
        for name in possible_names:
          if file.startswith(name) and any(file.endswith(ext) for ext in possible_exts if ext):
            return os.path.join(root, file)
  
  raise FileNotFoundError(f'Could not find array library in {search_dirs}. Available files: {[f for d in search_dirs if os.path.exists(d) for f in os.listdir(d)]}')

lib = ctypes.CDLL(_get_lib_path())
class DType: FLOAT32, FLOAT64, INT8, INT16, INT32, INT64, UINT8, UINT16, UINT32, UINT64, BOOL = range(11)
class DTypeValue(ctypes.Union): _fields_ = [('f32', c_float), ('f64', c_double), ('i8', c_int8), ('i16', c_int16), ('i32', c_int32), ('i64', c_int64), ('u8', c_uint8), ('u16', c_uint16), ('u32', c_uint32), ('u64', c_uint64), ('boolean', c_uint8)]
class CArray(Structure): _fields_ = [('data', c_void_p), ('strides', POINTER(c_int)), ('backstrides', POINTER(c_int)), ('shape', POINTER(c_int)), ('size', c_size_t), ('ndim', c_size_t), ('dtype', c_int), ('is_view', c_int)]

def _setup_func(name, argtypes, restype):
  func = getattr(lib, name)
  func.argtypes, func.restype = argtypes, restype
  return func

_array_funcs = {
  'create_array': ([POINTER(c_float), c_size_t, POINTER(c_int), c_size_t, c_int], POINTER(CArray)), 'delete_array': ([POINTER(CArray)], None), 'delete_data': ([POINTER(CArray)], None),
  'delete_shape': ([POINTER(CArray)], None), 'delete_strides': ([POINTER(CArray)], None), 'print_array': ([POINTER(CArray)], None), 'out_data': ([POINTER(CArray)], POINTER(c_float)),
  'out_shape': ([POINTER(CArray)], POINTER(c_int)), 'out_strides': ([POINTER(CArray)], POINTER(c_int)), 'out_size': ([POINTER(CArray)], c_int), 'contiguous_array': ([POINTER(CArray)], POINTER(CArray)),
  'is_contiguous_array': ([POINTER(CArray)], POINTER(CArray)), 'make_contiguous_inplace_array': ([POINTER(CArray)], POINTER(CArray)), 'transpose_array': ([POINTER(CArray)], POINTER(CArray)),
  'view_array': ([POINTER(CArray)], POINTER(CArray)), 'is_view_array': ([POINTER(CArray)], POINTER(CArray)), 'cast_array': ([POINTER(CArray), c_int], POINTER(CArray)), 'cast_array_simple': ([POINTER(CArray), c_int], POINTER(CArray)),
  'get_dtype_size': ([c_int], c_size_t), 'get_dtype_name': ([c_int], c_char_p), 'get_item_array': ([POINTER(CArray), POINTER(c_int)], float),
  'set_item_array': ([POINTER(CArray), POINTER(c_int), c_float], None), 'get_linear_index': ([POINTER(CArray), POINTER(c_int)], c_int),
  'dtype_to_float32': ([c_void_p, c_int, c_size_t], c_float), 'float32_to_dtype': ([c_float, c_void_p, c_int, c_size_t], None),
  'convert_to_float32': ([c_void_p, c_int, c_size_t], POINTER(c_float)), 'convert_from_float32': ([POINTER(c_float), c_void_p, c_int, c_size_t], None),
  'allocate_dtype_array': ([c_int, c_size_t], c_void_p), 'copy_with_dtype_conversion': ([c_void_p, c_int, c_void_p, c_int, c_size_t], None),
  'cast_array_dtype': ([c_void_p, c_int, c_int, c_size_t], c_void_p), 'is_integer_dtype': ([c_int], c_int),
  'is_float_dtype': ([c_int], c_int), 'is_unsigned_dtype': ([c_int], c_int), 'is_signed_dtype': ([c_int], c_int),
  'clamp_to_int_range': ([c_double, c_int], c_int64), 'clamp_to_uint_range': ([c_double, c_int], c_uint64),
  'get_dtype_priority': ([c_int], c_int), 'promote_dtypes': ([c_int, c_int], c_int),
  'add_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'add_scalar_array': ([POINTER(CArray), c_float], POINTER(CArray)),
  'add_broadcasted_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'sub_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'sub_scalar_array': ([POINTER(CArray), c_float], POINTER(CArray)), 'sub_broadcasted_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'mul_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'mul_scalar_array': ([POINTER(CArray), c_float], POINTER(CArray)),
  'mul_broadcasted_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'div_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'div_scalar_array': ([POINTER(CArray), c_float], POINTER(CArray)), 'div_broadcasted_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'pow_array': ([POINTER(CArray), c_float], POINTER(CArray)), 'pow_scalar': ([c_float, POINTER(CArray)], POINTER(CArray)),
  'log_array': ([POINTER(CArray)], POINTER(CArray)), 'exp_array': ([POINTER(CArray)], POINTER(CArray)), 'neg_array': ([POINTER(CArray)], POINTER(CArray)),
  'neg_array': ([POINTER(CArray)], POINTER(CArray)), 'sqrt_array': ([POINTER(CArray)], POINTER(CArray)), 'sign_array': ([POINTER(CArray)], POINTER(CArray)),
  'abs_array': ([POINTER(CArray)], POINTER(CArray)), 'matmul_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'batch_matmul_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'broadcasted_matmul_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'dot_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'sin_array': ([POINTER(CArray)], POINTER(CArray)), 'sinh_array': ([POINTER(CArray)], POINTER(CArray)),
  'cos_array': ([POINTER(CArray)], POINTER(CArray)), 'cosh_array': ([POINTER(CArray)], POINTER(CArray)),
  'tan_array': ([POINTER(CArray)], POINTER(CArray)), 'tanh_array': ([POINTER(CArray)], POINTER(CArray)),
  'equal_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'not_equal_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'greater_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'greater_equal_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'smaller_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'smaller_equal_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'equal_scalar': ([POINTER(CArray), c_float], POINTER(CArray)), 'not_equal_scalar': ([POINTER(CArray), c_float], POINTER(CArray)),
  'greater_scalar': ([POINTER(CArray), c_float], POINTER(CArray)), 'greater_equal_scalar': ([POINTER(CArray), c_float], POINTER(CArray)),
  'smaller_scalar': ([POINTER(CArray), c_float], POINTER(CArray)), 'smaller_equal_scalar': ([POINTER(CArray), c_float], POINTER(CArray)),
  'reshape_array': ([POINTER(CArray), POINTER(c_int), c_int], POINTER(CArray)), 'squeeze_array': ([POINTER(CArray), c_int], POINTER(CArray)),
  'expand_dims_array': ([POINTER(CArray), c_int], POINTER(CArray)), 'flatten_array': ([POINTER(CArray)], POINTER(CArray)),
  'sum_array': ([POINTER(CArray), c_int, ctypes.c_bool], POINTER(CArray)), 'min_array': ([POINTER(CArray), c_int, ctypes.c_bool], POINTER(CArray)),
  'max_array': ([POINTER(CArray), c_int, ctypes.c_bool], POINTER(CArray)), 'mean_array': ([POINTER(CArray), c_int, ctypes.c_bool], POINTER(CArray)),
  'var_array': ([POINTER(CArray), c_int, c_int], POINTER(CArray)), 'std_array': ([POINTER(CArray), c_int, c_int], POINTER(CArray)),
}

_utils_funcs = {
  'zeros_like_array': ([POINTER(CArray)], POINTER(CArray)), 'ones_like_array': ([POINTER(CArray)], POINTER(CArray)),
  'zeros_array': ([POINTER(c_int), c_size_t, c_size_t, c_int], POINTER(CArray)), 'ones_array': ([POINTER(c_int), c_size_t, c_size_t, c_int], POINTER(CArray)),
  'randn_array': ([POINTER(c_int), c_size_t, c_size_t, c_int], POINTER(CArray)), 'randint_array': ([c_int, c_int, POINTER(c_int), c_size_t, c_size_t, c_int], POINTER(CArray)),
  'uniform_array': ([c_int, c_int, POINTER(c_int), c_size_t, c_size_t, c_int], POINTER(CArray)), 'fill_array': ([c_float, POINTER(c_int), c_size_t, c_size_t, c_int], POINTER(CArray)),
  'linspace_array': ([c_float, c_float, c_float, POINTER(c_int), c_size_t, c_size_t, c_int], POINTER(CArray)), 'arange_array': ([c_float, c_float, c_float, c_int], POINTER(CArray))
}

_vector_funcs = {
  'vector_dot': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'vector_matrix_dot': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'vector_inner': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'vector_outer': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'vector_cross': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'vector_cross_axis': ([POINTER(CArray), POINTER(CArray), c_int], POINTER(CArray)),
  'det_array': ([POINTER(CArray)], POINTER(CArray)), 'batched_det_array': ([POINTER(CArray)], POINTER(CArray)),
  'eig_array': ([POINTER(CArray)], POINTER(CArray)), 'batched_eig_array': ([POINTER(CArray)], POINTER(CArray)),
  'eigv_array': ([POINTER(CArray)], POINTER(CArray)), 'batched_eigv_array': ([POINTER(CArray)], POINTER(CArray)),
  'eigh_array': ([POINTER(CArray)], POINTER(CArray)), 'batched_eigh_array': ([POINTER(CArray)], POINTER(CArray)),
  'eighv_array': ([POINTER(CArray)], POINTER(CArray)), 'batched_eighv_array': ([POINTER(CArray)], POINTER(CArray)),
  'clip_array': ([POINTER(CArray), c_float], POINTER(CArray)), 'clamp_array': ([POINTER(CArray), c_float, c_float], POINTER(CArray)),
  'mm_norm_array': ([POINTER(CArray)], POINTER(CArray)), 'std_norm_array': ([POINTER(CArray)], POINTER(CArray)), 'robust_norm_array': ([POINTER(CArray)], POINTER(CArray)),
  'rms_norm_array': ([POINTER(CArray)], POINTER(CArray)), 'unit_norm_array': ([POINTER(CArray)], POINTER(CArray)),
  'l1_norm_array': ([POINTER(CArray)], POINTER(CArray)), 'l2_norm_array': ([POINTER(CArray)], POINTER(CArray)),
  'qr_array': ([POINTER(CArray)], POINTER(POINTER(CArray))), 'batched_qr_array': ([POINTER(CArray)], POINTER(POINTER(CArray))),
  'lu_array': ([POINTER(CArray)], POINTER(POINTER(CArray))), 'batched_lu_array': ([POINTER(CArray)], POINTER(POINTER(CArray))),
  'inv_array': ([POINTER(CArray)], POINTER(CArray)), 'solve_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)), 'lstsq_array': ([POINTER(CArray), POINTER(CArray)], POINTER(CArray)),
  'svd_array': ([POINTER(CArray)], POINTER(POINTER(CArray))), 'cholesky_array': ([POINTER(CArray)], POINTER(CArray))
}

for name, (argtypes, restype) in _array_funcs.items(): _setup_func(name, argtypes, restype)
for name, (argtypes, restype) in _utils_funcs.items(): _setup_func(name, argtypes, restype)
for name, (argtypes, restype) in _vector_funcs.items(): _setup_func(name, argtypes, restype)