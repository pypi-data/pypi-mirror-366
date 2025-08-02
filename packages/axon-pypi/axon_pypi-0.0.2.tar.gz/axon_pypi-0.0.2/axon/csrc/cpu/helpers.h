#ifndef __HELPER__H__
#define __HELPER__H__

#include <stddef.h>
#include <stdint.h>

extern "C" {
  // array initialization functions
  void zeros_like_array_ops(float* out, size_t size);
  void zeros_array_ops(float* out, size_t size);
  void ones_like_array_ops(float* out, size_t size);
  void ones_array_ops(float* out, size_t size);

  // array filling functions
  void fill_array_ops(float* out, float value, size_t size);
  void linspace_array_ops(float* out, float start, float step_size, size_t size);
  void arange_array_ops(float* out, float start, float stop, float step, size_t max_size);
  size_t arange_size(float start, float stop, float step);

  // random array generation functions
  void fill_randn(float* out, size_t size);
  void fill_uniform(float* out, float low, float high, size_t size);
  void fill_randint(float* out, int low, int high, size_t size);

  // RNG management functions
  void set_random_seed(uint64_t seed);
  void reset_random_state();
}

#endif  //!__HELPER__H__