#ifndef __OPS_ARRAY__H__
#define __OPS_ARRAY__H__

#include <stddef.h>

extern "C" {
  void matmul_array_ops(float* a, float* b, float* out, int* shape1, int* shape2);
  void batch_matmul_array_ops(float* a, float* b, float* out, int* shape1, int* shape2, int* strides1, int* strides2);
  void broadcasted_matmul_array_ops(float* a, float* b, float* out, int* shape1, int* shape2, int* strides1, int* strides2);
  void dot_array_ops(float* a, float* b, float* out, size_t size);
  void batch_dot_array_ops(float* a, float* b, float* out, size_t batch_count, size_t vector_size);
}

#endif  //!__BINARY_OPS__H__