#ifndef __BINARY_OPS__H__
#define __BINARY_OPS__H__

#include "core/core.h"
#include "core/dtype.h"

extern "C" {
  // binary ops
  Array* add_array(Array* a, Array* b);
  Array* add_scalar_array(Array* a, float b);
  Array* add_broadcasted_array(Array* a, Array* b);
  Array* sub_array(Array* a, Array* b);
  Array* sub_scalar_array(Array* a, float b);
  Array* sub_broadcasted_array(Array* a, Array* b);
  Array* mul_array(Array* a, Array* b);
  Array* mul_scalar_array(Array* a, float b);
  Array* mul_broadcasted_array(Array* a, Array* b);
  Array* div_array(Array* a, Array* b);
  Array* div_scalar_array(Array* a, float b);
  Array* div_broadcasted_array(Array* a, Array* b);
  Array* pow_array(Array* a, float exp);
  Array* pow_scalar(float a, Array* exp);
}

#endif  //!__BINARY_OPS__H__