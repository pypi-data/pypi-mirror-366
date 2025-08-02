from axon import array, randn
import numpy as np
import time

# setting matrix size
shape1 = (256, 512)
shape2 = (512, 100)

# generate random matrices for axon
a1_axon = randn(shape1, dtype=array.float32)
a2_axon = randn(shape2, dtype=array.float32)

# generate random matrices for numpy
a1_np = np.astype(np.array(a1_axon.to_list()),np.float32)
a2_np = np.astype(np.array(a2_axon.to_list()),np.float32)

# warm-up (optional, for fairer timing)
_ = a1_axon @ a2_axon
_ = a1_np @ a2_np

# time axon
start = time.time()
result_axon = a1_axon @ a2_axon
axon_time = time.time() - start
print(f"Axon matmul time: {axon_time:.6f} seconds")

# time numpy
start = time.time()
result_np = a1_np @ a2_np
numpy_time = time.time() - start
print(f"Numpy matmul time: {numpy_time:.6f} seconds")

print(result_axon)
print(result_np)