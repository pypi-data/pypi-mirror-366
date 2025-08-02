import pytest
import numpy as np
import axon as ax

class TestUtils:
  def test_zeros_1d(self):
    result = ax.zeros(5)
    expected = np.zeros(5, dtype='float32')
    assert result.shape == (5,)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_zeros_2d(self):
    result = ax.zeros(3, 4)
    expected = np.zeros((3, 4), dtype='float32')
    assert result.shape == (3, 4)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_zeros_3d(self):
    result = ax.zeros(2, 3, 4)
    expected = np.zeros((2, 3, 4), dtype='float32')
    assert result.shape == (2, 3, 4)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_zeros_int32(self):
    result = ax.zeros(3, 3, dtype='int32')
    expected = np.zeros((3, 3), dtype='int32')
    assert result.shape == (3, 3)
    assert result.dtype == 'int32'
    assert np.array_equal(result.tolist(), expected.tolist())

  def test_ones_1d(self):
    result = ax.ones(5)
    expected = np.ones(5, dtype='float32')
    assert result.shape == (5,)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_ones_2d(self):
    result = ax.ones(3, 4)
    expected = np.ones((3, 4), dtype='float32')
    assert result.shape == (3, 4)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_ones_3d(self):
    result = ax.ones(2, 3, 4)
    expected = np.ones((2, 3, 4), dtype='float32')
    assert result.shape == (2, 3, 4)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_ones_int32(self):
    result = ax.ones(3, 3, dtype='int32')
    expected = np.ones((3, 3), dtype='int32')
    assert result.shape == (3, 3)
    assert result.dtype == 'int32'
    assert np.array_equal(result.tolist(), expected.tolist())

  def test_zeros_like(self):
    a = ax.array([[1, 2, 3], [4, 5, 6]], dtype='float32')
    result = ax.zeros_like(a)
    expected = np.zeros_like(np.array(a.tolist()))
    assert result.shape == a.shape
    assert result.dtype == a.dtype
    assert np.allclose(result.tolist(), expected.tolist())

  def test_ones_like(self):
    a = ax.array([[1, 2, 3], [4, 5, 6]], dtype='float32')
    result = ax.ones_like(a)
    expected = np.ones_like(np.array(a.tolist()))
    assert result.shape == a.shape
    assert result.dtype == a.dtype
    assert np.allclose(result.tolist(), expected.tolist())

  def test_randn_1d(self):
    result = ax.randn(100)
    assert result.shape == (100,)
    assert result.dtype == 'float32'
    assert abs(np.mean(result.tolist())) < 0.2
    assert abs(np.std(result.tolist()) - 1.0) < 0.2

  def test_randn_2d(self):
    result = ax.randn(50, 50)
    assert result.shape == (50, 50)
    assert result.dtype == 'float32'
    assert abs(np.mean(result.tolist())) < 0.2
    assert abs(np.std(result.tolist()) - 1.0) < 0.2

  def test_randn_3d(self):
    result = ax.randn(10, 10, 10)
    assert result.shape == (10, 10, 10)
    assert result.dtype == 'float32'
    assert abs(np.mean(result.tolist())) < 0.2
    assert abs(np.std(result.tolist()) - 1.0) < 0.2

  def test_randint_1d(self):
    result = ax.randint(0, 10, 100)
    assert result.shape == (100,)
    assert result.dtype == 'int32'
    values = result.tolist()
    assert all(0 <= v < 10 for v in values)

  def test_randint_2d(self):
    result = ax.randint(5, 15, 10, 10)
    assert result.shape == (10, 10)
    assert result.dtype == 'int32'
    values = np.array(result.tolist()).flatten()
    assert all(5 <= v < 15 for v in values)

  def test_randint_3d(self):
    result = ax.randint(-5, 5, 5, 5, 5)
    assert result.shape == (5, 5, 5)
    assert result.dtype == 'int32'
    values = np.array(result.tolist()).flatten()
    assert all(-5 <= v < 5 for v in values)

  def test_uniform_1d(self):
    result = ax.uniform(0, 1, 100)
    assert result.shape == (100,)
    assert result.dtype == 'float32'
    values = result.tolist()
    assert all(0 <= v <= 1 for v in values)

  def test_uniform_2d(self):
    result = ax.uniform(2, 8, 10, 10)
    assert result.shape == (10, 10)
    assert result.dtype == 'float32'
    values = np.array(result.tolist()).flatten()
    assert all(2 <= v <= 8 for v in values)

  def test_uniform_3d(self):
    result = ax.uniform(-1, 1, 5, 5, 5)
    assert result.shape == (5, 5, 5)
    assert result.dtype == 'float32'
    values = np.array(result.tolist()).flatten()
    assert all(-1 <= v <= 1 for v in values)

  def test_fill_1d(self):
    result = ax.fill(3.14, 5)
    expected = np.full(5, 3.14, dtype='float32')
    assert result.shape == (5,)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_fill_2d(self):
    result = ax.fill(-2.5, 3, 4)
    expected = np.full((3, 4), -2.5, dtype='float32')
    assert result.shape == (3, 4)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_fill_3d(self):
    result = ax.fill(7.0, 2, 3, 4)
    expected = np.full((2, 3, 4), 7.0, dtype='float32')
    assert result.shape == (2, 3, 4)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_fill_int32(self):
    result = ax.fill(42, 3, 3, dtype='int32')
    expected = np.full((3, 3), 42, dtype='int32')
    assert result.shape == (3, 3)
    assert result.dtype == 'int32'
    assert np.array_equal(result.tolist(), expected.tolist())

  def test_linspace_1d(self):
    result = ax.linspace(0.0, 1.0, 10.0, 11)
    expected = np.linspace(0.0, 10.0, 11, dtype='float32')
    assert result.shape == (11,)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist(), atol=1e-3)

  def test_linspace_2d(self):
    result = ax.linspace(1.0, 0.5, 5.0, 2, 5)
    assert result.shape == (2, 5)
    assert result.dtype == 'float32'
    assert result.size == 10

  def test_linspace_3d(self):
    result = ax.linspace(-1.0, 0.1, 1.0, 2, 3, 4)
    assert result.shape == (2, 3, 4)
    assert result.dtype == 'float32'
    assert result.size == 24

  def test_arange_positive_step(self):
    result = ax.arange(0.0, 10.0, 2.0)
    expected = np.arange(0.0, 10.0, 2.0, dtype='float32')
    assert result.shape == (5,)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_arange_negative_step(self):
    result = ax.arange(10.0, 0.0, -2.0)
    expected = np.arange(10.0, 0.0, -2.0, dtype='float32')
    assert result.shape == (5,)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist())

  def test_arange_float_step(self):
    result = ax.arange(0.0, 1.0, 0.1)
    expected = np.arange(0.0, 1.0, 0.1, dtype='float32')
    assert result.shape == (10,)
    assert result.dtype == 'float32'
    assert np.allclose(result.tolist(), expected.tolist(), atol=1e-6)

  def test_arange_int32(self):
    result = ax.arange(0.0, 5.0, 1.0, dtype='int32')
    expected = np.arange(0, 5, 1, dtype='int32')
    assert result.shape == (5,)
    assert result.dtype == 'int32'
    assert np.array_equal(result.tolist(), expected.tolist())

  def test_arange_zero_step_error(self):
    with pytest.raises(ValueError, match="Step cannot be zero"):
      ax.arange(0.0, 10.0, 0.0)

  def test_arange_invalid_range_error(self):
    with pytest.raises(ValueError, match="Invalid arange parameters"):
      ax.arange(10.0, 0.0, 1.0)
    with pytest.raises(ValueError, match="Invalid arange parameters"):
      ax.arange(0.0, 10.0, -1.0)

if __name__ == "__main__":
  pytest.main([__file__, "-v"])