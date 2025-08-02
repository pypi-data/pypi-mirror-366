#ifndef __REDUX_OPS__H__
#define __REDUX_OPS__H__

#include "core/core.h"
#include "core/dtype.h"

extern "C" {
  // reduction ops
  Array* sum_array(Array* a, int axis, bool keepdims);
  Array* mean_array(Array* a, int axis, bool keepdims);
  Array* max_array(Array* a, int axis, bool keepdims);
  Array* min_array(Array* a, int axis, bool keepdims);
  Array* var_array(Array* a, int axis, int ddof);
  Array* std_array(Array* a, int axis, int ddof);
}

#endif  //!__REDUX_OPS__H__