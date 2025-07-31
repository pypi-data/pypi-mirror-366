import torch
import numpy as np
from PIL import Image
# from torchrbf.RBFInterpolator import RBFInterpolator
# from ..torchrbf.RBFInterpolator import RBFInterpolator
from RBFInterpolator import RBFInterpolator
from torchvision.utils import save_image

def test_opt():
    dev = 'cuda'

    num_x = 512
    smoothing = 0
    W = 128
    H = 128
    sW = 128
    sH = 128
    # pick random points from the image to keep as data
    # n_keep = 128
    # keep = np.random.choice(W * H, n_keep, replace=False)

    img = Image.open('/home/arman/Downloads/cat.jpg')
    img = img.resize((W, H))
    img = np.array(img).astype(np.float32) / 255
    img = torch.from_numpy(img).float().to(dev) # H x W x 3
    img = img.permute(2, 0, 1) # 3 x H x W
    print('img',img.shape)

    # make y a 2D grid of points using meshgrid
    y = np.meshgrid(np.linspace(-1, 1, sW), np.linspace(-1, 1, sH))
    y = np.stack(y, axis=-1).reshape(-1, 2)
    y = torch.from_numpy(y).float().to(dev) # N x 2
    print('y',y.shape)
    # query d at y using bilinear interpolation
    d = torch.nn.functional.grid_sample(img[None], y.view(1, sH, sW, 2), align_corners=True).view(-1, 3)
    print('d',d.shape)

    x = np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))
    x = np.stack(x, axis=-1).reshape(-1, 2)
    x = torch.from_numpy(x).float().to(dev) # N x 2
    print('x',x.shape)

    kernel = 'thin_plate_spline'
    kernel = 'linear'

    smoothing = torch.rand(y.shape[0], device=dev, requires_grad=True)
    optimizer = torch.optim.Adam([smoothing], lr=0.008)

    for i in range(100):
        optimizer.zero_grad()

        print(smoothing.shape)
        rbf_torch = RBFInterpolator(y, d, neighbors=None, smoothing=smoothing, kernel=kernel, device=dev)
        interp_img = rbf_torch(x, use_grad=True).view(3,H,W)
        loss = torch.mean((interp_img - img)**2)
        print(i, loss.item())
        loss.backward()
        optimizer.step()

        save_image(interp_img, 'interp_img.png')


if __name__ == '__main__':
    test_opt()