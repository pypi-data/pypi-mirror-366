#ifndef __DECOMPOSE__H__
#define __DECOMPOSE__H__

#include "../core/core.h"
#include "../core/dtype.h"

extern "C" {
  Array** svd_array(Array* a);
  Array* cholesky_array(Array* a);
  Array* eig_array(Array* a);        // eigen values
  Array* eigv_array(Array* a);        // eigen vectors
  Array* eigh_array(Array* a);        // eigen hermitian values
  Array* eighv_array(Array* a);         // eigen hermitian vectors
  Array* batched_eig_array(Array* a);    // batched eigen values
  Array* batched_eigv_array(Array* a);    // batched eigen vectors
  Array* batched_eigh_array(Array* a);      // batched eigen hermitian values
  Array* batched_eighv_array(Array* a);      // batched eigen hermitian vectors
  Array** batched_qr_array(Array* a);
  Array** qr_array(Array* a);
  Array** batched_qr_array(Array* a);
  Array** lu_array(Array* a);
  Array** batched_lu_array(Array* a);
}

#endif  //!__DECOMPOSE__H__