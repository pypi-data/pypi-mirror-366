#include <stdio.h>
#include <stdlib.h>
#include "array_ops.h"
#include "cpu/ops_array.h"

Array* matmul_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != 2 || b->ndim != 2) {
    fprintf(stderr, "Both arrays must be 2D for matrix multiplication\n");
    exit(EXIT_FAILURE);
  }
  if (a->shape[1] != b->shape[0]) {
    fprintf(stderr, "Inner dimensions must match for matrix multiplication: %d != %d\n", a->shape[1], b->shape[0]);
    exit(EXIT_FAILURE);
  }

  // converting both arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* b_float = convert_to_float32(b->data, b->dtype, b->size);
  if (a_float == NULL || b_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    if (b_float) free(b_float);
    exit(EXIT_FAILURE);
  }

  int* result_shape = (int*)malloc(2 * sizeof(int));    // result shape: [a->shape[0], b->shape[1]]
  if (result_shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    exit(EXIT_FAILURE);
  }
  result_shape[0] = a->shape[0];
  result_shape[1] = b->shape[1];  // result is A rows × B rows (since we're doing A @ B^T)
  size_t result_size = result_shape[0] * result_shape[1];

  float* out = (float*)malloc(result_size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    free(result_shape);
    exit(EXIT_FAILURE);
  }

  // performing optimized matrix multiplication (regular A @ B)
  matmul_array_ops(a_float, b_float, out, a->shape, b->shape);
  dtype_t result_dtype = promote_dtypes(a->dtype, b->dtype);
  Array* result = create_array(out, 2, result_shape, result_size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  free(result_shape);
  return result;
}

Array* batch_matmul_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != 3 || b->ndim != 3) {
    fprintf(stderr, "Both arrays must be 3D for batch matrix multiplication\n");
    exit(EXIT_FAILURE);
  }
  if (a->shape[0] != b->shape[0]) {
    fprintf(stderr, "Batch dimensions must match: %d != %d\n", a->shape[0], b->shape[0]);
    exit(EXIT_FAILURE);
  }
  if (a->shape[2] != b->shape[1]) {
    fprintf(stderr, "Inner dimensions must match for batch matrix multiplication: %d != %d\n", a->shape[2], b->shape[1]);
    exit(EXIT_FAILURE);
  }

  // converting both arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* b_float = convert_to_float32(b->data, b->dtype, b->size);

  if (a_float == NULL || b_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    if (b_float) free(b_float);
    exit(EXIT_FAILURE);
  }

  // result shape: [batch_size, a->shape[1], b->shape[2]]
  int* result_shape = (int*)malloc(3 * sizeof(int));
  if (result_shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    exit(EXIT_FAILURE);
  }
  result_shape[0] = a->shape[0];
  result_shape[1] = a->shape[1];
  result_shape[2] = b->shape[2];
  size_t result_size = result_shape[0] * result_shape[1] * result_shape[2];

  float* out = (float*)malloc(result_size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    free(result_shape);
    exit(EXIT_FAILURE);
  }

  // calculate strides for batch matmul
  int a_strides[3] = {a->shape[1] * a->shape[2], a->shape[2], 1};
  int b_strides[3] = {b->shape[1] * b->shape[2], b->shape[2], 1};

  batch_matmul_array_ops(a_float, b_float, out, a->shape, b->shape, a_strides, b_strides);
  dtype_t result_dtype = promote_dtypes(a->dtype, b->dtype);
  Array* result = create_array(out, 3, result_shape, result_size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  free(result_shape);
  return result;
}

Array* broadcasted_matmul_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != 2 || b->ndim != 3) {
    fprintf(stderr, "First array must be 2D and second array must be 3D for broadcasted matrix multiplication\n");
    exit(EXIT_FAILURE);
  }
  if (a->shape[1] != b->shape[1]) {
    fprintf(stderr, "Inner dimensions must match for broadcasted matrix multiplication: %d != %d\n", a->shape[1], b->shape[1]);
    exit(EXIT_FAILURE);
  }

  // converting both arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* b_float = convert_to_float32(b->data, b->dtype, b->size);

  if (a_float == NULL || b_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    if (b_float) free(b_float);
    exit(EXIT_FAILURE);
  }

  // result shape: [b->shape[0], a->shape[0], b->shape[2]]
  int* result_shape = (int*)malloc(3 * sizeof(int));
  if (result_shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    exit(EXIT_FAILURE);
  }
  result_shape[0] = b->shape[0];
  result_shape[1] = a->shape[0];
  result_shape[2] = b->shape[2];
  size_t result_size = result_shape[0] * result_shape[1] * result_shape[2];

  float* out = (float*)malloc(result_size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    free(result_shape);
    exit(EXIT_FAILURE);
  }

  // calculate strides
  int a_strides[2] = {a->shape[1], 1};
  int b_strides[3] = {b->shape[1] * b->shape[2], b->shape[2], 1};

  broadcasted_matmul_array_ops(a_float, b_float, out, a->shape, b->shape, a_strides, b_strides);
  dtype_t result_dtype = promote_dtypes(a->dtype, b->dtype);
  Array* result = create_array(out, 3, result_shape, result_size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  free(result_shape);
  return result;
}

Array* dot_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != 1 || b->ndim != 1) {
    fprintf(stderr, "Both arrays must be 1D for dot product\n");
    exit(EXIT_FAILURE);
  }
  if (a->size != b->size) {
    fprintf(stderr, "Arrays must have the same size for dot product: %zu != %zu\n", a->size, b->size);
    exit(EXIT_FAILURE);
  }

  // converting both arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* b_float = convert_to_float32(b->data, b->dtype, b->size);

  if (a_float == NULL || b_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    if (b_float) free(b_float);
    exit(EXIT_FAILURE);
  }

  // result is a scalar (0D array)
  int* result_shape = (int*)malloc(1 * sizeof(int));
  if (result_shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    exit(EXIT_FAILURE);
  }
  result_shape[0] = 1;

  float* out = (float*)malloc(sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    free(result_shape);
    exit(EXIT_FAILURE);
  }

  dot_array_ops(a_float, b_float, out, a->size);
  dtype_t result_dtype = promote_dtypes(a->dtype, b->dtype);
  Array* result = create_array(out, 0, NULL, 1, result_dtype);  // 0D array for scalar
  free(a_float);
  free(b_float);
  free(out);
  free(result_shape);
  return result;
}

Array* batch_dot_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != 2 || b->ndim != 2) {
    fprintf(stderr, "Both arrays must be 2D for batch dot product\n");
    exit(EXIT_FAILURE);
  }
  if (a->shape[0] != b->shape[0] || a->shape[1] != b->shape[1]) {
    fprintf(stderr, "Arrays must have the same shape for batch dot product\n");
    exit(EXIT_FAILURE);
  }

  // converting both arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* b_float = convert_to_float32(b->data, b->dtype, b->size);

  if (a_float == NULL || b_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    if (b_float) free(b_float);
    exit(EXIT_FAILURE);
  }

  // result shape: [batch_count]
  int* result_shape = (int*)malloc(1 * sizeof(int));
  if (result_shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    exit(EXIT_FAILURE);
  }
  result_shape[0] = a->shape[0];
  size_t result_size = result_shape[0];

  float* out = (float*)malloc(result_size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    free(b_float);
    free(result_shape);
    exit(EXIT_FAILURE);
  }

  batch_dot_array_ops(a_float, b_float, out, a->shape[0], a->shape[1]);
  dtype_t result_dtype = promote_dtypes(a->dtype, b->dtype);
  Array* result = create_array(out, 1, result_shape, result_size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  free(result_shape);
  return result;
}