#include <stdio.h>
#include <stdlib.h>
#include "cpu/ops_shape.h"
#include "shape_ops.h"

Array* transpose_array(Array* a) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }  
  int ndim = a->ndim;
  int* result_shape = (int*)malloc(ndim * sizeof(int));
  if (result_shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  // creating the result shape (reversed dimensions)
  for (int i = 0; i < ndim; i++) { result_shape[i] = a->shape[ndim - 1 - i]; }
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  // performing transpose based on dimensions
  // IMPORTANT: passing the ORIGINAL shape to transpose functions, not the result shape
  switch(ndim) {
    case 1: transpose_1d_array_ops(a_float, out, a->shape); break;
    case 2: transpose_2d_array_ops(a_float, out, a->shape); break;
    case 3: transpose_3d_array_ops(a_float, out, a->shape); break;
    default:
    if (ndim > 3) { transpose_ndim_array_ops(a_float, out, a->shape, a->ndim); }
    else {
      fprintf(stderr, "Transpose supported only for 1-3 dimensional arrays\n");
      free(a_float);
      free(out);
      free(result_shape);
      exit(EXIT_FAILURE);
    }
  }
  dtype_t result_dtype = a->dtype;
  Array* result = create_array(out, ndim, result_shape, a->size, result_dtype);
  free(a_float);
  free(out);
  free(result_shape);
  return result;
}

Array* reshape_array(Array* a, int* new_shape, int new_ndim) {
  if (a == NULL || new_shape == NULL) {
    fprintf(stderr, "Array or shape pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  int* shape = (int*)malloc(new_ndim * sizeof(int));
  if (shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }

  // copying new shape and calculate new size
  size_t new_size = 1;
  for (int i = 0; i < new_ndim; i++) {
    shape[i] = new_shape[i];
    new_size *= shape[i];
  }
  if (new_size != a->size) {
    fprintf(stderr, "Can't reshape the array. array's size doesn't match the target size: %zu != %zu\n", a->size, new_size);
    free(shape);
    exit(EXIT_FAILURE);
  }
  // converting array to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  // performing reshape (basically just copy data)
  reassign_array_ops(a_float, out, a->size);
  dtype_t result_dtype = a->dtype;    // reshaping preserves the original dtype
  Array* result = create_array(out, new_ndim, shape, a->size, result_dtype);
  free(a_float);
  free(out);
  free(shape);
  return result;
}

Array* squeeze_array(Array* a, int axis) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  int new_ndim = 0;
  int* temp_shape = (int*)malloc(a->ndim * sizeof(int));
  if (temp_shape == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }

  // if axis is -1, remove all dimensions of size 1
  if (axis == -1) {
    for (int i = 0; i < a->ndim; i++) {
      if (a->shape[i] != 1) {
        temp_shape[new_ndim] = a->shape[i];
        new_ndim++;
      }
    }
  } else {
    // validate axis
    if (axis < 0 || axis >= a->ndim) {
      fprintf(stderr, "axis %d is out of bounds for array of dimension %zu\n", axis, a->ndim);
      free(temp_shape);
      exit(EXIT_FAILURE);
    }
    if (a->shape[axis] != 1) {
      fprintf(stderr, "cannot select an axis to squeeze out which has size not equal to one\n");
      free(temp_shape);
      exit(EXIT_FAILURE);
    }
    // remove specific axis
    for (int i = 0; i < a->ndim; i++) {
      if (i != axis) {
        temp_shape[new_ndim] = a->shape[i];
        new_ndim++;
      }
    }
  }

  // handling edge case where all dimensions are squeezed out
  if (new_ndim == 0) {
    new_ndim = 1;
    temp_shape[0] = 1;
  }
  int* shape = (int*)malloc(new_ndim * sizeof(int));
  for (int i = 0; i < new_ndim; i++) { shape[i] = temp_shape[i]; }
  free(temp_shape);

  // converting array to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  reassign_array_ops(a_float, out, a->size);  // performing squeeze (basically just copy data)
  dtype_t result_dtype = a->dtype;  // squeeze preserves the original dtype
  Array* result = create_array(out, new_ndim, shape, a->size, result_dtype);
  free(a_float);
  free(out);
  free(shape);
  return result;
}

Array* expand_dims_array(Array* a, int axis) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  
  int new_ndim = a->ndim + 1;
  if (axis < 0) {
    axis = new_ndim + axis;   // normalizing negative axis
  }
  // validating axis
  if (axis < 0 || axis >= new_ndim) {
    fprintf(stderr, "axis %d is out of bounds for array of dimension %d\n", axis, new_ndim);
    exit(EXIT_FAILURE);
  }
  int* shape = (int*)malloc(new_ndim * sizeof(int));
  // create new shape with expanded dimension
  int old_idx = 0;
  for (int i = 0; i < new_ndim; i++) {
    if (i == axis) { shape[i] = 1; }
    else { shape[i] = a->shape[old_idx]; old_idx++; }
  }

  // converting array to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  reassign_array_ops(a_float, out, a->size);   // performing expand_dims (basically just copy data)
  dtype_t result_dtype = a->dtype;  // expand_dims preserves the original dtype
  Array* result = create_array(out, new_ndim, shape, a->size, result_dtype);
  free(a_float);
  free(out);
  free(shape);
  return result;
}

Array* flatten_array(Array* a) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  int new_ndim = 1;
  int* shape = (int*)malloc(new_ndim * sizeof(int));
  shape[0] = a->size;   // flattened array has single dimension with size equal to total elements
  // converting array to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  reassign_array_ops(a_float, out, a->size);  // performing flatten (basically just copy data)
  dtype_t result_dtype = a->dtype;  // flatten preserves the original dtype
  Array* result = create_array(out, new_ndim, shape, a->size, result_dtype);
  free(a_float);
  free(out);
  free(shape);
  return result;
}

Array* equal_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != b->ndim) {
    fprintf(stderr, "Arrays must have same dimensions %d and %d for equal\n", a->ndim, b->ndim);
    exit(EXIT_FAILURE);
  }

  // checking if shapes match
  for (size_t i = 0; i < a->ndim; i++) {
    if (a->shape[i] != b->shape[i]) {
      fprintf(stderr, "Arrays must have the same shape for comparison\n");
      exit(EXIT_FAILURE);
    }
  }
  // converting both Arrays to float32 for computation
  float *a_float = convert_to_float32(a->data, a->dtype, a->size), *b_float = convert_to_float32(b->data, b->dtype, b->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  // perform the equality comparison
  equal_array_ops(a_float, b_float, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  return result;
}

Array* equal_scalar(Array* a, float b) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  // converting both Arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  if (a_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    exit(EXIT_FAILURE);
  }
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    exit(EXIT_FAILURE);
  }
  equal_scalar_ops(a_float, b, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(out);
  return result;
}

Array* not_equal_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != b->ndim) {
    fprintf(stderr, "Arrays must have same dimensions %d and %d for equal\n", a->ndim, b->ndim);
    exit(EXIT_FAILURE);
  }

  // checking if shapes match
  for (size_t i = 0; i < a->ndim; i++) {
    if (a->shape[i] != b->shape[i]) {
      fprintf(stderr, "Arrays must have the same shape for comparison\n");
      exit(EXIT_FAILURE);
    }
  }
  // converting both Arrays to float32 for computation
  float *a_float = convert_to_float32(a->data, a->dtype, a->size), *b_float = convert_to_float32(b->data, b->dtype, b->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  
  // perform the equality comparison
  not_equal_array_ops(a_float, b_float, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  return result;
}

Array* not_equal_scalar(Array* a, float b) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  // converting both Arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  if (a_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    exit(EXIT_FAILURE);
  }
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    exit(EXIT_FAILURE);
  }
  not_equal_scalar_ops(a_float, b, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(out);
  return result;
}

Array* greater_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != b->ndim) {
    fprintf(stderr, "Arrays must have same dimensions %d and %d for equal\n", a->ndim, b->ndim);
    exit(EXIT_FAILURE);
  }

  // checking if shapes match
  for (size_t i = 0; i < a->ndim; i++) {
    if (a->shape[i] != b->shape[i]) {
      fprintf(stderr, "Arrays must have the same shape for comparison\n");
      exit(EXIT_FAILURE);
    }
  }
  // converting both Arrays to float32 for computation
  float *a_float = convert_to_float32(a->data, a->dtype, a->size), *b_float = convert_to_float32(b->data, b->dtype, b->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  
  // perform the equality comparison
  greater_array_ops(a_float, b_float, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  return result;
}

Array* greater_scalar(Array* a, float b) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  // converting both Arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  if (a_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    exit(EXIT_FAILURE);
  }
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    exit(EXIT_FAILURE);
  }
  greater_scalar_ops(a_float, b, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(out);
  return result;
}

Array* greater_equal_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != b->ndim) {
    fprintf(stderr, "Arrays must have same dimensions %d and %d for equal\n", a->ndim, b->ndim);
    exit(EXIT_FAILURE);
  }

  // checking if shapes match
  for (size_t i = 0; i < a->ndim; i++) {
    if (a->shape[i] != b->shape[i]) {
      fprintf(stderr, "Arrays must have the same shape for comparison\n");
      exit(EXIT_FAILURE);
    }
  }
  // converting both Arrays to float32 for computation
  float *a_float = convert_to_float32(a->data, a->dtype, a->size), *b_float = convert_to_float32(b->data, b->dtype, b->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  
  // perform the equality comparison
  greater_equal_array_ops(a_float, b_float, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  return result;
}

Array* greater_equal_scalar(Array* a, float b) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  // converting both Arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  if (a_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    exit(EXIT_FAILURE);
  }
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    exit(EXIT_FAILURE);
  }
  greater_equal_scalar_ops(a_float, b, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(out);
  return result;
}

Array* smaller_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != b->ndim) {
    fprintf(stderr, "Arrays must have same dimensions %d and %d for equal\n", a->ndim, b->ndim);
    exit(EXIT_FAILURE);
  }

  // checking if shapes match
  for (size_t i = 0; i < a->ndim; i++) {
    if (a->shape[i] != b->shape[i]) {
      fprintf(stderr, "Arrays must have the same shape for comparison\n");
      exit(EXIT_FAILURE);
    }
  }
  // converting both Arrays to float32 for computation
  float *a_float = convert_to_float32(a->data, a->dtype, a->size), *b_float = convert_to_float32(b->data, b->dtype, b->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  
  // perform the equality comparison
  smaller_array_ops(a_float, b_float, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  return result;
}

Array* smaller_scalar(Array* a, float b) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  // converting both Arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  if (a_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    exit(EXIT_FAILURE);
  }
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    exit(EXIT_FAILURE);
  }
  smaller_scalar_ops(a_float, b, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(out);
  return result;
}

Array* smaller_equal_array(Array* a, Array* b) {
  if (a == NULL || b == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  if (a->ndim != b->ndim) {
    fprintf(stderr, "Arrays must have same dimensions %d and %d for equal\n", a->ndim, b->ndim);
    exit(EXIT_FAILURE);
  }

  // checking if shapes match
  for (size_t i = 0; i < a->ndim; i++) {
    if (a->shape[i] != b->shape[i]) {
      fprintf(stderr, "Arrays must have the same shape for comparison\n");
      exit(EXIT_FAILURE);
    }
  }
  // converting both Arrays to float32 for computation
  float *a_float = convert_to_float32(a->data, a->dtype, a->size), *b_float = convert_to_float32(b->data, b->dtype, b->size);
  float* out = (float*)malloc(a->size * sizeof(float));
  
  // perform the equality comparison
  smaller_equal_array_ops(a_float, b_float, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(b_float);
  free(out);
  return result;
}

Array* smaller_equal_scalar(Array* a, float b) {
  if (a == NULL) {
    fprintf(stderr, "Array value pointers are null!\n");
    exit(EXIT_FAILURE);
  }
  // converting both Arrays to float32 for computation
  float* a_float = convert_to_float32(a->data, a->dtype, a->size);
  if (a_float == NULL) {
    fprintf(stderr, "Memory allocation failed during dtype conversion\n");
    if (a_float) free(a_float);
    exit(EXIT_FAILURE);
  }
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    free(a_float);
    exit(EXIT_FAILURE);
  }
  smaller_equal_scalar_ops(a_float, b, out, a->size);
  // comparison operations always return boolean type
  dtype_t result_dtype = DTYPE_BOOL;
  Array* result = create_array(out, a->ndim, a->shape, a->size, result_dtype);
  free(a_float);
  free(out);
  return result;
}