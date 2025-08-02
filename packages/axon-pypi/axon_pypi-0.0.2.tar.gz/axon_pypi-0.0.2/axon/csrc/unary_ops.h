#ifndef __UNARY_OPS__H__
#define __UNARY_OPS__H__

#include "core/core.h"
#include "core/dtype.h"

extern "C" {
  // unary ops
  Array* sin_array(Array* a);
  Array* sinh_array(Array* a);
  Array* cos_array(Array* a);
  Array* cosh_array(Array* a);
  Array* tan_array(Array* a);
  Array* tanh_array(Array* a);
  Array* log_array(Array* a);
  Array* exp_array(Array* a);
  Array* abs_array(Array* a);
  Array* neg_array(Array* a);
  Array* sqrt_array(Array* a);
  Array* sign_array(Array* a);
}

#endif  //!__UNARY_OPS__H__