#ifndef __NORM__H__
#define __NORM__H__

#include "../core/core.h"
#include "../core/dtype.h"

extern "C" {
  Array* clip_array(Array* a, float max_val);
  Array* clamp_array(Array* a, float min_val, float max_val);
  Array* mm_norm_array(Array* a);
  Array* std_norm_array(Array* a);
  Array* rms_norm_array(Array* a);
  Array* l1_norm_array(Array* a);
  Array* l2_norm_array(Array* a);
  Array* unit_norm_array(Array* a);
  Array* robust_norm_array(Array* a);
}

#endif  //!__NORM__H__