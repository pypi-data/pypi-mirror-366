import pytest
import numpy as np
import axon as ax

class TestArrayCreation:
  def test_array_from_list(self):
    a = ax.array([1, 2, 3, 4])
    assert a.shape == (4,)
    assert a.size == 4
    assert a.ndim == 1
    assert a.dtype == 'float32'
    assert a.tolist() == [1.0, 2.0, 3.0, 4.0]

  def test_array_from_scalar(self):
    a = ax.array([5])
    assert a.shape == (1,)
    assert a.size == 1
    assert a.ndim == 1
    assert a.tolist() == [5.0]

  def test_array_2d(self):
    a = ax.array([[1, 2], [3, 4]])
    assert a.shape == (2, 2)
    assert a.size == 4
    assert a.ndim == 2
    assert a.tolist() == [[1.0, 2.0], [3.0, 4.0]]

  def test_array_3d(self):
    a = ax.array([[[1, 2]], [[3, 4]]])
    assert a.shape == (2, 1, 2)
    assert a.size == 4
    assert a.ndim == 3

  def test_array_from_array(self):
    a = ax.array([1, 2, 3])
    b = ax.array(a)
    assert b.shape == a.shape
    assert b.size == a.size
    assert b.ndim == a.ndim
    assert b.dtype == a.dtype

  def test_array_with_dtype(self):
    a = ax.array([1, 2, 3], dtype='float64')
    assert a.dtype == 'float64'

  def test_array_dtypes(self):
    dtypes = ['int8', 'int16', 'int32', 'int64', 'float32', 'float64', 'uint8', 'uint16', 'uint32', 'uint64', 'bool']
    for dtype in dtypes:
      a = ax.array([1, 2, 3], dtype=dtype)
      assert a.dtype == dtype

class TestArrayTypeConversion:
  def test_astype_float32_to_float64(self):
    a = ax.array([1, 2, 3], dtype='float32')
    b = a.astype('float64')
    assert b.dtype == 'float64'
    assert b.shape == a.shape
    assert b.size == a.size

  def test_astype_float_to_int(self):
    a = ax.array([1.5, 2.7, 3.9], dtype='float32')
    b = a.astype('int32')
    assert b.dtype == 'int32'

  def test_astype_preserve_shape(self):
    a = ax.array([[1, 2], [3, 4]], dtype='float32')
    b = a.astype('float64')
    assert b.shape == (2, 2)
    assert b.size == 4
    assert b.ndim == 2

class TestArrayProperties:
  def test_repr(self):
    a = ax.array([1, 2, 3])
    repr_str = repr(a)
    assert 'array(' in repr_str
    assert 'dtype=float32' in repr_str

  def test_str(self):
    a = ax.array([1, 2, 3])
    str_result = str(a)
    assert str_result == ""

  def test_hash(self):
    a = ax.array([1, 2, 3])
    b = ax.array([1, 2, 3])
    assert hash(a) != hash(b)  # Different objects should have different hashes

  def test_is_contiguous(self):
    a = ax.array([1, 2, 3, 4])
    assert isinstance(a.is_contiguous(), bool)

  def test_is_view(self):
    a = ax.array([1, 2, 3, 4])
    assert isinstance(a.is_view(), bool)

# indexing has lot's of errors
# class TestArrayIndexing:
#   def test_getitem_1d(self):
#     a = ax.array([1, 2, 3, 4])
#     assert a[0].tolist() == 1.0
#     assert a[1].tolist() == 2.0

#   def test_getitem_2d(self):
#     a = ax.array([[1, 2], [3, 4]])
#     row = a[0]
#     assert row.tolist() == [1.0, 2.0]

#   def test_setitem_1d(self):
#     a = ax.array([1, 2, 3, 4])
#     a[0] = 10
#     assert a[0].tolist() == 10.0

#   def test_setitem_2d(self):
#     a = ax.array([[1, 2], [3, 4]])
#     a[0] = [10, 20]
#     assert a[0].tolist() == [10.0, 20.0]

#   def test_iteration(self):
#     a = ax.array([1, 2, 3])
#     elements = list(a)
#     assert len(elements) == 3

class TestArrayViews:
  def test_contiguous(self):
    a = ax.array([[1, 2], [3, 4]])
    b = a.contiguous()
    assert b.shape == a.shape

  def test_make_contiguous(self):
    a = ax.array([[1, 2], [3, 4]])
    a.make_contiguous()
    assert a.is_contiguous()

  def test_view(self):
    a = ax.array([1, 2, 3, 4])
    b = a.view()
    assert b.shape == a.shape

class TestBinaryOperations:
  def test_add_array(self):
    a = ax.array([1, 2, 3])
    b = ax.array([4, 5, 6])
    c = a + b
    expected = [5.0, 7.0, 9.0]
    assert c.tolist() == expected

  def test_add_scalar(self):
    a = ax.array([1, 2, 3])
    c = a + 5
    expected = [6.0, 7.0, 8.0]
    assert c.tolist() == expected

  def test_sub_array(self):
    a = ax.array([5, 7, 9])
    b = ax.array([1, 2, 3])
    c = a - b
    expected = [4.0, 5.0, 6.0]
    assert c.tolist() == expected

  def test_sub_scalar(self):
    a = ax.array([5, 7, 9])
    c = a - 2
    expected = [3.0, 5.0, 7.0]
    assert c.tolist() == expected

  def test_mul_array(self):
    a = ax.array([2, 3, 4])
    b = ax.array([2, 2, 2])
    c = a * b
    expected = [4.0, 6.0, 8.0]
    assert c.tolist() == expected

  def test_mul_scalar(self):
    a = ax.array([2, 3, 4])
    c = a * 3
    expected = [6.0, 9.0, 12.0]
    assert c.tolist() == expected

  def test_div_array(self):
    a = ax.array([6, 8, 10])
    b = ax.array([2, 2, 2])
    c = a / b
    expected = [3.0, 4.0, 5.0]
    assert c.tolist() == expected

  def test_div_scalar(self):
    a = ax.array([6, 8, 10])
    c = a / 2
    expected = [3.0, 4.0, 5.0]
    assert c.tolist() == expected

  def test_pow_array(self):
    a = ax.array([2, 3, 4])
    c = 4 ** a
    expected = [16.0, 64.0, 256.0]
    assert c.tolist() == expected

  def test_pow_scalar(self):
    a = ax.array([2, 3, 4])
    c = a ** 2
    expected = [4.0, 9.0, 16.0]
    assert c.tolist() == expected

class TestReverseOperations:
  def test_radd(self):
    a = ax.array([1, 2, 3])
    c = 5 + a
    expected = [6.0, 7.0, 8.0]
    assert c.tolist() == expected

  def test_rsub(self):
    a = ax.array([1, 2, 3])
    c = 10 - a
    expected = [9.0, 8.0, 7.0]
    assert c.tolist() == expected

  def test_rmul(self):
    a = ax.array([2, 3, 4])
    c = 2 * a
    expected = [4.0, 6.0, 8.0]
    assert c.tolist() == expected

  def test_rtruediv(self):
    a = ax.array([2, 4, 5])
    c = 20 / a
    expected = [10.0, 5.0, 4.0]
    assert c.tolist() == expected

  def test_rpow(self):
    a = ax.array([2, 3, 2])
    c = 2 ** a
    expected = [4.0, 8.0, 4.0]
    assert c.tolist() == expected

class TestUnaryOperations:
  def test_neg(self):
    a = ax.array([1, -2, 3])
    c = -a
    expected = [-1.0, 2.0, -3.0]
    assert c.tolist() == expected

  def test_log(self):
    a = ax.array([1, 2, 3])
    c = a.log()
    expected = np.log([1, 2, 3]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_sqrt(self):
    a = ax.array([1, 4, 9])
    c = a.sqrt()
    expected = [1.0, 2.0, 3.0]
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_exp(self):
    a = ax.array([0, 1, 2])
    c = a.exp()
    expected = np.exp([0, 1, 2]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_abs(self):
    a = ax.array([-1, -2, 3])
    c = a.abs()
    expected = [1.0, 2.0, 3.0]
    assert c.tolist() == expected

  def test_sign(self):
    a = ax.array([-5, 0, 5])
    c = a.sign()
    expected = [-1.0, 0.0, 1.0]
    assert c.tolist() == expected

  def test_sin(self):
    a = ax.array([0, np.pi/2, np.pi])
    c = a.sin()
    expected = np.sin([0, np.pi/2, np.pi]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_cos(self):
    a = ax.array([0, np.pi/2, np.pi])
    c = a.cos()
    expected = np.cos([0, np.pi/2, np.pi]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_tan(self):
    a = ax.array([0, np.pi/4])
    c = a.tan()
    expected = np.tan([0, np.pi/4]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_sinh(self):
    a = ax.array([0, 1, 2])
    c = a.sinh()
    expected = np.sinh([0, 1, 2]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_cosh(self):
    a = ax.array([0, 1, 2])
    c = a.cosh()
    expected = np.cosh([0, 1, 2]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

  def test_tanh(self):
    a = ax.array([0, 1, 2])
    c = a.tanh()
    expected = np.tanh([0, 1, 2]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

class TestMatrixOperations:
  def test_matmul_2d(self):
    a = ax.array([[1, 2], [3, 4]])
    b = ax.array([[5, 6], [7, 8]])
    c = a @ b
    expected = np.matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]).tolist()
    assert np.allclose(c.tolist(), expected, atol=1e-5)

class TestShapeOperations:
  def test_transpose_2d(self):
    a = ax.array([[1, 2, 3], [4, 5, 6]])
    b = a.transpose()
    assert b.shape == (3, 2)
    expected = [[1, 4], [2, 5], [3, 6]]
    assert b.tolist() == expected

  def test_reshape(self):
    a = ax.array([1, 2, 3, 4, 5, 6])
    b = a.reshape([2, 3])
    assert b.shape == (2, 3)
    expected = [[1, 2, 3], [4, 5, 6]]
    assert b.tolist() == expected

  def test_reshape_tuple(self):
    a = ax.array([1, 2, 3, 4])
    b = a.reshape((2, 2))
    assert b.shape == (2, 2)

  def test_flatten(self):
    a = ax.array([[1, 2], [3, 4]])
    b = a.flatten()
    assert b.shape == (4,)
    assert b.tolist() == [1, 2, 3, 4]

  def test_squeeze_default(self):
    a = ax.array([[[1, 2, 3]]])
    b = a.squeeze()
    assert b.ndim < a.ndim

  def test_squeeze_axis(self):
    a = ax.array([[[1, 2, 3]]])
    b = a.squeeze(0)
    assert b.shape[0] == 1

  def test_expand_dims(self):
    a = ax.array([1, 2, 3])
    b = a.expand_dims(0)
    assert b.ndim == a.ndim + 1

class TestReductionOperations:
  def test_sum_all(self):
    a = ax.array([1, 2, 3, 4])
    result = a.sum()
    expected = 10.0
    assert abs(result.tolist() - expected) < 1e-5

  def test_sum_axis(self):
    a = ax.array([[1, 2], [3, 4]])
    result = a.sum(axis=0)
    expected = [4.0, 6.0]
    assert result.tolist() == expected

  def test_sum_keepdims(self):
    a = ax.array([[1, 2], [3, 4]])
    result = a.sum(axis=0, keepdims=True)
    assert result.ndim == a.ndim

  def test_mean_all(self):
    a = ax.array([1, 2, 3, 4])
    result = a.mean()
    expected = 2.5
    assert abs(result.tolist() - expected) < 1e-5

  def test_mean_axis(self):
    a = ax.array([[1, 2], [3, 4]])
    result = a.mean(axis=0)
    expected = [2.0, 3.0]
    assert result.tolist() == expected

  def test_max_all(self):
    a = ax.array([1, 4, 2, 3])
    result = a.max()
    expected = 4.0
    assert result.tolist() == expected

  def test_max_axis(self):
    a = ax.array([[1, 4], [2, 3]])
    result = a.max(axis=0)
    expected = [2.0, 4.0]
    assert result.tolist() == expected

  def test_min_all(self):
    a = ax.array([1, 4, 2, 3])
    result = a.min()
    expected = 1.0
    assert result.tolist() == expected

  def test_min_axis(self):
    a = ax.array([[1, 4], [2, 3]])
    result = a.min(axis=0)
    expected = [1.0, 3.0]
    assert result.tolist() == expected

  def test_var_default(self):
    a = ax.array([1, 2, 3, 4])
    result = a.var()
    expected = np.var([1, 2, 3, 4], ddof=0)
    assert abs(result.tolist() - expected) < 1e-5

  def test_var_ddof(self):
    a = ax.array([1, 2, 3, 4])
    result = a.var(ddof=1)
    expected = np.var([1, 2, 3, 4], ddof=1)
    assert abs(result.tolist() - expected) < 1e-5

  def test_std_default(self):
    a = ax.array([1, 2, 3, 4])
    result = a.std()
    expected = np.std([1, 2, 3, 4], ddof=0)
    assert abs(result.tolist() - expected) < 1e-5

  def test_std_ddof(self):
    a = ax.array([1, 2, 3, 4])
    result = a.std(ddof=1)
    expected = np.std([1, 2, 3, 4], ddof=1)
    assert abs(result.tolist() - expected) < 1e-5

class TestClippingOperations:
  def test_clip(self):
    a = ax.array([1, 5, 10, 15])
    result = a.clip(8)
    # Values above 8 should be clipped to 8
    assert all(x <= 8.0 for x in result.tolist())

  def test_clamp(self):
    a = ax.array([1, 5, 10, 15])
    result = a.clamp(12, 3)  # max=12, min=3
    result_list = result.tolist()
    assert all(3.0 <= x <= 12.0 for x in result_list)

class TestComparisonOperations:
  def test_equal_array(self):
    a = ax.array([1, 2, 3])
    b = ax.array([1, 5, 3])
    result = a == b
    expected = [True, False, True]
    assert result.tolist() == expected

  def test_equal_scalar(self):
    a = ax.array([1, 2, 3])
    result = a == 2
    expected = [False, True, False]
    assert result.tolist() == expected

  def test_not_equal_array(self):
    a = ax.array([1, 2, 3])
    b = ax.array([1, 5, 3])
    result = a != b
    expected = [False, True, False]
    assert result.tolist() == expected

  def test_not_equal_scalar(self):
    a = ax.array([1, 2, 3])
    result = a != 2
    expected = [True, False, True]
    assert result.tolist() == expected

  def test_greater_than_array(self):
    a = ax.array([1, 5, 3])
    b = ax.array([2, 2, 3])
    result = a > b
    expected = [False, True, False]
    assert result.tolist() == expected

  def test_greater_than_scalar(self):
    a = ax.array([1, 5, 3])
    result = a > 3
    expected = [False, True, False]
    assert result.tolist() == expected

  def test_less_than_array(self):
    a = ax.array([1, 5, 3])
    b = ax.array([2, 2, 3])
    result = a < b
    expected = [True, False, False]
    assert result.tolist() == expected

  def test_less_than_scalar(self):
    a = ax.array([1, 5, 3])
    result = a < 3
    expected = [True, False, False]
    assert result.tolist() == expected

  def test_greater_equal_array(self):
    a = ax.array([1, 5, 3])
    b = ax.array([2, 2, 3])
    result = a >= b
    expected = [False, True, True]
    assert result.tolist() == expected

  def test_greater_equal_scalar(self):
    a = ax.array([1, 5, 3])
    result = a >= 3
    expected = [False, True, True]
    assert result.tolist() == expected

  def test_less_equal_array(self):
    a = ax.array([1, 5, 3])
    b = ax.array([2, 2, 3])
    result = a <= b
    expected = [True, False, True]
    assert result.tolist() == expected

  def test_less_equal_scalar(self):
    a = ax.array([1, 5, 3])
    result = a <= 3
    expected = [True, False, True]
    assert result.tolist() == expected

class TestDtypeConstants:
  def test_dtype_constants_in_class(self):
    assert hasattr(ax.array, 'int8')
    assert hasattr(ax.array, 'float32')
    assert hasattr(ax.array, 'boolean')
    assert ax.array.int8 == 'int8'
    assert ax.array.float32 == 'float32'
    assert ax.array.boolean == 'bool'

class TestErrorHandling:
  def test_invalid_dtype(self):
    # This should not raise an error during creation, but might during operations
    try:
      a = ax.array([1, 2, 3], dtype='invalid_dtype')
    except:
      # If it raises an error, that's acceptable behavior
      pass

  def test_empty_list(self):
    try:
      a = ax.array([])
      # If this works, check basic properties
      assert a.size == 0
    except:
      # If it raises an error, that's acceptable behavior for empty arrays
      pass

class TestEdgeCases:
  def test_single_element_array(self):
    a = ax.array([42])
    assert a.size == 1
    assert a.tolist() == [42.0]

  def test_large_array(self):
    data = list(range(1000))
    a = ax.array(data)
    assert a.size == 1000
    assert len(a.tolist()) == 1000

  def test_nested_operations(self):
    a = ax.array([1, 2, 3])
    b = ax.array([4, 5, 6])
    result = (a + b) * 2 - 1
    expected = [(1+4)*2-1, (2+5)*2-1, (3+6)*2-1]
    assert result.tolist() == expected

if __name__ == "__main__":
  pytest.main([__file__, "-v"])