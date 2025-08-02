#ifndef __MATRIX__H__
#define __MATRIX__H__

#include "../core/core.h"
#include "../core/dtype.h"

extern "C" {
  Array* det_array(Array* a);
  Array* batched_det_array(Array* a);
  Array* inv_array(Array* a);
  Array* solve_array(Array* a, Array* b);
  Array* lstsq_array(Array* a, Array* b);
}

#endif  //!__MATRIX__H__