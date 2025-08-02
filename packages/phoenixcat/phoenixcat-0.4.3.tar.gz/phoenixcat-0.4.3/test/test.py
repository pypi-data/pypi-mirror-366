import torch
import torch.version

print(torch.version.cuda)

import torch
import my_cuda_add

# 使用 CUDA 张量
x = torch.randn(1024, device="cuda")
y = torch.randn(1024, device="cuda")
out = torch.empty_like(x)

# 调用扩展函数
my_cuda_add.add(x, y, out)

print("x + y = ", out)

import latexify
