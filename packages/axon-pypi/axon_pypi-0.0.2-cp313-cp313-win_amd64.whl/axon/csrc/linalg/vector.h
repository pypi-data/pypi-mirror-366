#ifndef __VECTOR__H__
#define __VECTOR__H__

#include "../core/core.h"
#include "../core/dtype.h"

extern "C" {
  Array* vector_dot(Array* a, Array* b);
  Array* vector_matrix_dot(Array* vec, Array* mat);
  Array* vector_inner(Array* a, Array* b);
  Array* vector_outer(Array* a, Array* b);
  Array* vector_cross(Array* a, Array* b);
  Array* vector_cross_axis(Array* a, Array* b, int axis);
}

#endif  //!__VECTOR__H__