from typing import *
from ctypes import c_int, c_float
from .._cbase import CArray, lib, DType
from .._core import array
from .._helpers import DtypeHelp, ShapeHelp

def normalize(a: array, mode: str="mm") -> array:
  assert mode in ["mm", "std", "rms"], "only supports 'rms', 'mm' & 'std' normalization ops"
  if mode == "mm": result_ptr = lib.mm_norm_array(a.data).contents
  elif mode == "std": result_ptr = lib.std_norm_array(a.data).contents
  else: result_ptr = lib.rms_norm_array(a.data).contents
  out = array(result_ptr, a.dtype)
  out.shape, out.size, out.ndim, out.strides = a.shape, a.size, a.ndim, a.strides
  return out

def _l1_norm_magnitude(a: array) -> array:
  flat_data = a.flatten().tolist()
  if isinstance(flat_data, (int, float)): flat_data = [flat_data]
  sum_val = 0.0
  for val in flat_data: sum_val += abs(val)  
  out = array([sum_val], a.dtype)
  out.shape, out.size, out.ndim, out.strides = (), 1, 0, ()
  return out

def _l2_norm_magnitude(a: array) -> array:
  flat_data = a.flatten().tolist()
  if isinstance(flat_data, (int, float)): flat_data = [flat_data]
  sum_val = 0.0
  for val in flat_data: sum_val += val * val
  magnitude = sum_val ** 0.5
  out = array([magnitude], a.dtype)
  out.shape, out.size, out.ndim, out.strides = (), 1, 0, ()
  return out

def l1_norm(a: array, mag: bool = False) -> array:
  out = array(lib.l1_norm_array(a.data).contents, a.dtype)
  out.shape, out.size, out.ndim, out.strides = a.shape, a.size, a.ndim, a.strides
  return (_l1_norm_magnitude(a), out) if mag else out

def l2_norm(a: array, mag: bool = False) -> array:
  out = array(lib.l2_norm_array(a.data).contents, a.dtype)
  out.shape, out.size, out.ndim, out.strides = a.shape, a.size, a.ndim, a.strides
  return (_l2_norm_magnitude(a), out) if mag else out

def unit_norm(a: array) -> array:
  out = array(lib.unit_norm_array(a.data).contents, a.dtype)
  out.shape, out.size, out.ndim, out.strides = a.shape, a.size, a.ndim, a.strides
  return out

def robust_norm(a: array) -> array:
  out = array(lib.robust_norm_array(a.data).contents, a.dtype)
  out.shape, out.size, out.ndim, out.strides = a.shape, a.size, a.ndim, a.strides
  return out