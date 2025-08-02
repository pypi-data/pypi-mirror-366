import pytest
import numpy as np
import axon as ax

class TestDecompose:
  def test_det_2d(self):
    a = ax.array([[1, 2], [3, 4]], dtype='float32')
    result = ax.linalg.det(a)
    expected = np.linalg.det(np.array([[1, 2], [3, 4]]))
    assert abs(result.tolist() - expected) < 1e-6

  def test_det_3d_batch(self):
    a = ax.array([[[1, 2], [3, 4]], [[2, 1], [1, 3]]], dtype='float32')
    result = ax.linalg.det(a)
    expected = np.array([np.linalg.det([[1, 2], [3, 4]]), np.linalg.det([[2, 1], [1, 3]])])
    assert result.shape == (2,)
    assert np.allclose([float(x) for x in result.tolist()], expected, atol=1e-5)

  def test_lu_2d(self):
    a = ax.array([[2, 1], [1, 1]], dtype='float32')
    l, u = ax.linalg.lu(a)
    assert l.shape == (2, 2)
    assert u.shape == (2, 2)

  def test_lu_3d_batch(self):
    a = ax.array([[[2, 1], [1, 1]], [[3, 2], [1, 2]]], dtype='float32')
    l, u = ax.linalg.lu(a)
    assert l.shape == (2, 2, 2)
    assert u.shape == (2, 2, 2)

  def test_qr_2d(self):
    a = ax.array([[1, 1], [1, 0], [0, 1]], dtype='float32')
    q, r = ax.linalg.qr(a)
    assert q.shape == (3, 3)
    assert r.shape == (3, 2)
    product = np.dot(np.array(q.tolist()), np.array(r.tolist()))
    assert np.allclose(product.tolist(), np.array(a.tolist()), atol=1e-4)

  def test_svd_2d(self):
    a = ax.array([[1, 2], [3, 4], [5, 6]], dtype='float32')
    u, s, vt = ax.linalg.svd(a)
    assert u.shape == (3, 3)
    assert s.shape == (2,)
    assert vt.shape == (2, 2)
    u_np, s_np, vt_np = np.linalg.svd(np.array(a.tolist()))
    assert np.allclose(np.array(s.tolist()), s_np, atol=1e-3)

  def test_cholesky(self):
    a = ax.array([[4, 12, -16], [12, 37, -43], [-16, -43, 98]], dtype='float32')
    result = ax.linalg.cholesky(a)
    expected = np.linalg.cholesky(np.array(a.tolist()))
    assert np.allclose(np.array(result.tolist()), expected, atol=1e-4)

  def test_eign_2d(self):
    a = ax.array([[1, 2], [2, 3]], dtype='float32')
    result = ax.linalg.eign(a)
    expected = np.linalg.eigvals(np.array(a.tolist()))
    result_sorted = np.sort([float(x) for x in result.tolist()])
    expected_sorted = np.sort(expected)
    assert np.allclose(result_sorted, expected_sorted, atol=1e-3)

  def test_eignv_2d(self):
    a = ax.array([[1, 2], [2, 3]], dtype='float32')
    result = ax.linalg.eignv(a)
    assert result.shape == (2, 2)

  def test_eignh_hermitian(self):
    a = ax.array([[2, 1], [1, 2]], dtype='float32')
    result = ax.linalg.eignh(a)
    expected = np.linalg.eigvalsh(np.array(a.tolist()))
    result_sorted = np.sort([float(x) for x in result.tolist()])
    expected_sorted = np.sort(expected)
    assert np.allclose(result_sorted, expected_sorted, atol=1e-3)

  def test_eignhv_hermitian(self):
    a = ax.array([[2, 1], [1, 2]], dtype='float32')
    result = ax.linalg.eignhv(a)
    assert result.shape == (2, 2)

class TestNorm:
  def test_normalize_mm(self):
    a = ax.array([1, 2, 3, 4, 5], dtype='float32')
    result = ax.linalg.normalize(a, mode="mm")
    assert result.shape == a.shape
    assert 0 <= float(min(result.tolist())) <= 1
    assert 0 <= float(max(result.tolist())) <= 1

  def test_normalize_std(self):
    a = ax.array([1, 2, 3, 4, 5], dtype='float32')
    result = ax.linalg.normalize(a, mode="std")
    assert result.shape == a.shape

  def test_normalize_rms(self):
    a = ax.array([1, 2, 3, 4, 5], dtype='float32')
    result = ax.linalg.normalize(a, mode="rms")
    assert result.shape == a.shape

  def test_l1_norm(self):
    a = ax.array([3, 4], dtype='float32')
    mag, result = ax.linalg.l1_norm(a, True)
    expected = np.linalg.norm(np.array(a.tolist()), ord=1)
    assert abs(mag.tolist() - expected) < 1e-5

  def test_l2_norm(self):
    a = ax.array([3, 4], dtype='float32')
    mag, result = ax.linalg.l2_norm(a, True)
    expected = np.linalg.norm(np.array(a.tolist()), ord=2)
    assert abs(mag.tolist() - expected) < 1e-5

  def test_unit_norm(self):
    a = ax.array([3, 4], dtype='float32')
    result = ax.linalg.unit_norm(a)
    norm = np.linalg.norm([float(x) for x in result.tolist()])
    assert abs(norm - 1.0) < 1e-5

  def test_robust_norm(self):
    a = ax.array([1, 2, 100, 3, 4], dtype='float32')
    result = ax.linalg.robust_norm(a)
    assert result.shape == a.shape

class TestVector:
  def test_dot(self):
    a = ax.array([1, 2, 3], dtype='float32')
    b = ax.array([4, 5, 6], dtype='float32')
    result = ax.linalg.dot(a, b)
    expected = np.dot(np.array(a.tolist()), np.array(b.tolist()))
    assert abs(result.tolist() - expected) < 1e-5

  def test_dot_mv(self):
    mat = ax.array([[1, 2], [3, 4], [5, 6]], dtype='float32')
    vec = ax.array([1, 2], dtype='float32')
    result = ax.linalg.dot_mv(mat, vec)
    expected = np.dot(np.array(mat.tolist()), np.array(vec.tolist()))
    assert np.allclose(result.tolist(), expected, atol=1e-5)

  def test_inner(self):
    a = ax.array([1, 2, 3], dtype='float32')
    b = ax.array([4, 5, 6], dtype='float32')
    result = ax.linalg.inner(a, b)
    expected = np.inner(np.array(a.tolist()), np.array(b.tolist()))
    assert abs(result.tolist() - expected) < 1e-5

  def test_outer(self):
    a = ax.array([1, 2, 3], dtype='float32')
    b = ax.array([4, 5], dtype='float32')
    result = ax.linalg.outer(a, b)
    expected = np.outer(np.array(a.tolist()), np.array(b.tolist()))
    assert np.allclose(result.tolist(), expected, atol=1e-5)

  def test_cross_1d(self):
    a = ax.array([1, 2, 3], dtype='float32')
    b = ax.array([4, 5, 6], dtype='float32')
    result = ax.linalg.cross(a, b)
    expected = np.cross(np.array(a.tolist()), np.array(b.tolist()))
    assert np.allclose(result.tolist(), expected, atol=1e-5)

  def test_cross_2d_with_axis(self):
    a = ax.array([[1, 2, 3], [4, 5, 6]], dtype='float32')
    b = ax.array([[7, 8, 9], [10, 11, 12]], dtype='float32')
    result = ax.linalg.cross(a, b, axis=1)
    assert result.shape == (2, 3)

  def test_inv(self):
    a = ax.array([[1, 2], [3, 4]], dtype='float32')
    result = ax.linalg.inv(a)
    expected = np.linalg.inv(np.array(a.tolist()))
    assert np.allclose(result.tolist(), expected, atol=1e-4)

  # def test_rank(self):
  #   a = ax.array([[1, 2], [3, 4]], dtype='float32')
  #   result = ax.linalg.rank(a)
  #   expected = np.linalg.matrix_rank(np.array(a.tolist()))
  #   assert abs(result.tolist() - expected) < 1e-5

  def test_solve(self):
    a = ax.array([[2, 1], [1, 1]], dtype='float32')
    b = ax.array([3, 2], dtype='float32')
    result = ax.linalg.solve(a, b)
    expected = np.linalg.solve(np.array(a.tolist()), np.array(b.tolist()))
    assert np.allclose(result.tolist(), expected, atol=1e-4)

  def test_solve_2d(self):
    a = ax.array([[2, 1], [1, 1]], dtype='float32')
    b = ax.array([[3, 1], [2, 1]], dtype='float32')
    result = ax.linalg.solve(a, b)
    expected = np.linalg.solve(np.array(a.tolist()), np.array(b.tolist()))
    assert np.allclose(result.tolist(), expected, atol=1e-4)

  def test_lstsq(self):
    a = ax.array([[1, 1], [1, 2], [1, 3]], dtype='float32')
    b = ax.array([6, 8, 10], dtype='float32')
    result = ax.linalg.lstsq(a, b)
    expected, _, _, _ = np.linalg.lstsq(np.array(a.tolist()), np.array(b.tolist()), rcond=None)
    assert np.allclose(result.tolist(), expected, atol=1e-3)

  def test_lstsq_2d(self):
    a = ax.array([[1, 1], [1, 2], [1, 3]], dtype='float32')
    b = ax.array([[6, 1], [8, 2], [10, 3]], dtype='float32')
    result = ax.linalg.lstsq(a, b)
    expected, _, _, _ = np.linalg.lstsq(np.array(a.tolist()), np.array(b.tolist()), rcond=None)
    assert np.allclose(result.tolist(), expected, atol=1e-3)

class TestErrorHandling:
  def test_det_invalid_ndim(self):
    a = ax.array([1, 2, 3], dtype='float32')
    with pytest.raises(ValueError, match="Can't compute determinant"):
      ax.linalg.det(a)

  def test_eign_invalid_ndim(self):
    a = ax.array([[[[1, 2], [3, 4]], [[1, 2], [3, 4]]], [[[1, 2], [3, 4]], [[1, 2], [3, 4]]]], dtype='float32')
    with pytest.raises(ValueError, match="Can't compute eigenvalues"):
      ax.linalg.eign(a)

  def test_cross_invalid_axis(self):
    a = ax.array([[1, 2, 3], [4, 5, 6]], dtype='float32')
    b = ax.array([[7, 8, 9], [10, 11, 12]], dtype='float32')
    with pytest.raises(ValueError, match="Axis value can't be NULL"):
      ax.linalg.cross(a, b)

  def test_cross_axis_out_of_bounds(self):
    a = ax.array([[1, 2, 3], [4, 5, 6]], dtype='float32')
    b = ax.array([[7, 8, 9], [10, 11, 12]], dtype='float32')
    with pytest.raises(IndexError, match="Can't exceed the ndim"):
      ax.linalg.cross(a, b, axis=5)

  def test_normalize_invalid_mode(self):
    a = ax.array([1, 2, 3], dtype='float32')
    with pytest.raises(AssertionError, match="only supports"):
      ax.linalg.normalize(a, mode="invalid")

class TestDtypeHandling:
  def test_float64_operations(self):
    a = ax.array([[1, 2], [3, 4]], dtype='float64')
    det_result = ax.linalg.det(a, dtype='float64')
    inv_result = ax.linalg.inv(a, dtype='float64')
    assert det_result.dtype == 'float64'
    assert inv_result.dtype == 'float64'

  def test_dtype_preservation(self):
    a = ax.array([1, 2, 3], dtype='float32')
    result = ax.linalg.l2_norm(a)
    assert result.dtype == a.dtype

if __name__ == "__main__":
  pytest.main([__file__, "-v"])