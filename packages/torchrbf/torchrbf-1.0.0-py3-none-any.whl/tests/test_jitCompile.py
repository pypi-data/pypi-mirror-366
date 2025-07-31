import torch
from torchrbf import RBFInterpolator
from time import perf_counter


def run():
    y = torch.randn(100, 3)
    d = torch.randn(100, 3)

    interp = RBFInterpolator(y, d, smoothing=0.0, kernel="thin_plate_spline").cuda()
    
    default_time = 0
    jit_time = 0

    for _ in range(100):
        x = torch.randn(100, 3).cuda()
        t0 = perf_counter()
        out = interp(x)
        t1 = perf_counter()
        out._coeffs.shape # dummy operation to force computation
        default_time += t1 - t0

    traced = torch.jit.trace(interp, x)
    for _ in range(100):
        x = torch.randn(100, 3).cuda()
        t0 = perf_counter()
        out = traced(x)
        t1 = perf_counter()
        out._coeffs.shape
        jit_time += t1 - t0
    
    print(f"Default time: {default_time / 100:.4f} seconds")
    print(f"JIT time: {jit_time / 100:.4f} seconds")
    

if __name__ == '__main__':
    run()
