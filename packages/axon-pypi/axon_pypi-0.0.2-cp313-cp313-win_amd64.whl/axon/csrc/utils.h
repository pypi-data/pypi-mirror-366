#ifndef __UTILS__H__
#define __UTILS__H__

#include <stdlib.h>
#include "core/core.h"
#include "core/dtype.h"

extern "C" {
  // array creation functions with dtype support
  Array* zeros_like_array(Array* a);
  Array* zeros_array(int* shape, size_t size, size_t ndim, dtype_t dtype);
  Array* ones_like_array(Array* a);
  Array* ones_array(int* shape, size_t size, size_t ndim, dtype_t dtype);
  Array* randn_array(int* shape, size_t size, size_t ndim, dtype_t dtype);
  Array* randint_array(int low, int high, int* shape, size_t size, size_t ndim, dtype_t dtype);
  Array* uniform_array(int low, int high, int* shape, size_t size, size_t ndim, dtype_t dtype);
  Array* fill_array(float fill_val, int* shape, size_t size, size_t ndim, dtype_t dtype);
  Array* linspace_array(float start, float step, float end, int* shape, size_t size, size_t ndim, dtype_t dtype);
  Array* arange_array(float start, float stop, float step, dtype_t dtype);
}

#endif