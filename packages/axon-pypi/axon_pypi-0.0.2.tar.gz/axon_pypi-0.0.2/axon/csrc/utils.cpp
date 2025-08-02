#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "cpu/helpers.h"
#include "inc/random.h"

Array* zeros_like_array(Array* a) {
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  zeros_like_array_ops(out, a->size);
  Array* result = create_array(out, a->ndim, a->shape, a->size, a->dtype);
  free(out);
  return result;
}

Array* zeros_array(int* shape, size_t size, size_t ndim, dtype_t dtype) {
  float* out = (float*)malloc(size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  zeros_array_ops(out, size);
  Array* result = create_array(out, ndim, shape, size, dtype);
  free(out);
  return result;
}

Array* ones_like_array(Array* a) {
  float* out = (float*)malloc(a->size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  ones_like_array_ops(out, a->size);
  Array* result = create_array(out, a->ndim, a->shape, a->size, a->dtype);
  free(out);
  return result;
}

Array* ones_array(int* shape, size_t size, size_t ndim, dtype_t dtype) {
  float* out = (float*)malloc(size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  ones_array_ops(out, size);
  Array* result = create_array(out, ndim, shape, size, dtype);
  free(out);
  return result;
}

Array* randn_array(int* shape, size_t size, size_t ndim, dtype_t dtype) {
  float* out = (float*)malloc(size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  fill_randn(out, size);
  Array* result = create_array(out, ndim, shape, size, dtype);
  free(out);
  return result;
}

Array* randint_array(int low, int high, int* shape, size_t size, size_t ndim, dtype_t dtype) {
  float* out = (float*)malloc(size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  fill_randint(out, low, high, size);
  Array* result = create_array(out, ndim, shape, size, dtype);
  free(out);
  return result;
}

Array* uniform_array(int low, int high, int* shape, size_t size, size_t ndim, dtype_t dtype) {
  float* out = (float*)malloc(size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  fill_uniform(out, low, high, size);
  Array* result = create_array(out, ndim, shape, size, dtype);
  free(out);
  return result;
}

Array* fill_array(float fill_val, int* shape, size_t size, size_t ndim, dtype_t dtype) {
  float* out = (float*)malloc(size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  fill_array_ops(out, fill_val, size);
  Array* result = create_array(out, ndim, shape, size, dtype);
  free(out);
  return result;
}

Array* linspace_array(float start, float step, float end, int* shape, size_t size, size_t ndim, dtype_t dtype) {
  float* out = (float*)malloc(size * sizeof(float));
  if (out == NULL) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  // float step_size = (step > 1) ? (end - start) / (step - 1) : 0.0f;
  float step_size = (size > 1) ? (end - start) / (size - 1) : 0.0f;
  linspace_array_ops(out, start, step_size, size);
  Array* result = create_array(out, ndim, shape, size, dtype);
  free(out);
  return result;
}

Array* arange_array(float start, float stop, float step, dtype_t dtype) {
  if (step == 0.0f) {
    fprintf(stderr, "Step cannot be zero\n");
    exit(EXIT_FAILURE);
  }
  size_t size = arange_size(start, stop, step);
  if (size == 0) {
    fprintf(stderr, "Invalid arange parameters\n");
    exit(EXIT_FAILURE);
  }
  float* out = (float*)malloc(size * sizeof(float));
  if (!out) {
    fprintf(stderr, "Memory allocation failed\n");
    exit(EXIT_FAILURE);
  }
  arange_array_ops(out, start, stop, step, size);
  int* shape = (int*)malloc(sizeof(int));
  if (!shape) {
    fprintf(stderr, "Memory allocation failed\n");
    free(out);
    exit(EXIT_FAILURE);
  }
  shape[0] = (int)size;
  Array* result = create_array(out, 1, shape, size, dtype);
  free(out);
  free(shape);
  return result;
}