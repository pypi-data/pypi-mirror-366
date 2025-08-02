/**
  @file core.h header file for core.cpp & array
  * contains core components & functions for array creation/deletion
  * entry point to all the array functions
  * includes only basic core functionalities, ops are on different file
  * compile it as:
    *- '.so': g++ -shared -fPIC -o libarray.so core/core.cpp core/dtype.cpp array.cpp cpu/maths_ops.cpp cpu/helpers.cpp cpu/utils.cpp cpu/red_ops.cpp cpu/binary_ops.cpp
    *- '.dll': g++ -shared -o libarray.dll core/core.cpp core/dtype.cpp array.cpp cpu/maths_ops.cpp cpu/helpers.cpp cpu/utils.cpp cpu/red_ops.cpp cpu/binary_ops.cpp
    *- '.dylib': g++ -dynamiclib -o libarray.dylib core/core.cpp core/dtype.cpp array.cpp cpu/maths_ops.cpp cpu/helpers.cpp cpu/utils.cpp cpu/red_ops.cpp cpu/binary_ops.cpp
*/

#ifndef __CORE__H__
#define __CORE__H__

#include <stdlib.h>
#include "dtype.h"

typedef struct Array {
  void* data;           // raw data pointer (can be any dtype)
  int* strides;
  int* backstrides;
  int* shape;
  size_t size;
  size_t ndim;
  dtype_t dtype;        // data type of the array
  int is_view;          // flag to indicate if this is a view of another array
} Array;

extern "C" {
  // array initialization & deletion related function
  Array* create_array(float* data, size_t ndim, int* shape, size_t size, dtype_t dtype);
  void delete_array(Array* self);
  void delete_shape(Array* self);
  void delete_data(Array* self);
  void delete_strides(Array* self);
  void print_array(Array* self);
  float* out_data(Array* self);
  int* out_shape(Array* self);
  int* out_strides(Array* self);
  int out_size(Array* self);
  float get_item_array(Array* self, int* indices);
  void set_item_array(Array* self, int* indices, float value);
  int get_linear_index(Array* self, int* indices);


  // contiguous array ops
  int is_contiguous_array(Array* self);
  Array* contiguous_array(Array* self); // making array contiguous - returns new contiguous array
  void make_contiguous_inplace_array(Array* self);
  
  // view operations
  Array* view_array(Array* self);
  Array* reshape_view(Array* self, int* new_shape, size_t new_ndim);
  Array* slice_view(Array* self, int* start, int* end, int* step);

  // dtype casting management functions
  Array* cast_array(Array* self, dtype_t new_dtype);
  Array* cast_array_simple(Array* self, dtype_t new_dtype);

  // utility functions
  int is_view_array(Array* self);
  Array* copy_array(Array* self);
}

#endif  //!__CORE__H__