#ifndef __ARRAY__H__
#define __ARRAY__H__

#include "core/core.h"
#include "core/dtype.h"

extern "C" {
  Array* matmul_array(Array* a, Array* b);
  Array* batch_matmul_array(Array* a, Array* b);
  Array* broadcasted_matmul_array(Array* a, Array* b);
  Array* dot_array(Array* a, Array* b);
  Array* batch_dot_array(Array* a, Array* b);
}

#endif  //!__ARRAY__H__