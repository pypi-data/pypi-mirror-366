import matplotlib.pyplot as plt
import numpy as np


class AGIPDGeometry:
    def __init__(self, gap=8, downsample=1):
        """Makes an example of AGIPD geometry

        Pixel size 200 um, module shape 512 by 128 pixels
        Quadrant layout:
                 y
          Q4  Q1 ^
          Q3  Q2 |
          x <----+

        Parameters
        ----------
        gap: float
            The gap between modules in pixels

        """
        self.nmod = 16
        self.nfs, self.nss = 512 // downsample, 128 // downsample
        self.px_size = 200e-6 * downsample
        self.shape = (self.nmod, self.nfs, self.nss)

        self.fs, self.ss = np.mgrid[: self.nfs, : self.nss]

        self.corners = (
            np.array(
                [
                    [-512, 512 + gap * 6],  # Q1
                    [-512 - 3 * gap, 0],  # Q2
                    [512, -512 - gap * 6],  # Q3
                    [512 + 3 * gap, 0],  # Q1
                ],
                np.float32,
            )
            // downsample
        )

        g = gap // downsample
        self.x = x = np.zeros(self.shape, np.float32)
        self.y = y = np.zeros(self.shape, np.float32)
        for modno in range(16):
            k = 1 - 2 * (modno >= 8)
            fsx, fsy = k, 0
            ssx, ssy = 0, -k
            xc, yc = self.corners[modno // 4]
            yc += -k * (modno % 4) * (self.nss + g)
            x[modno] = (self.fs * fsx + self.ss * ssx + xc) * self.px_size
            y[modno] = (self.fs * fsy + self.ss * ssy + yc) * self.px_size

        self.r = np.sqrt(x * x + y * y)

        self.i = i = np.round(x / self.px_size).astype(int)
        self.j = j = np.round(y / self.px_size).astype(int)
        self.ni = ni = max(abs(np.min(i)), abs(np.max(i))) + 1
        self.nj = nj = max(abs(np.min(j)), abs(np.max(j))) + 1
        self.i += ni
        self.j += nj

    def random_mask(
        self, num_cells, num_trains=1, bad_pixel_fraction=0.01, dtype=np.uint16
    ):
        shape = (num_cells,) + self.shape
        p = [bad_pixel_fraction, 1.0 - bad_pixel_fraction]
        mask = np.random.choice(np.array([0, 1], dtype), size=shape, p=p)
        return np.tile(mask, [num_trains, 1, 1, 1])

    def assemble(self, data, fill_value=np.nan):
        image = np.full((2 * self.nj, 2 * self.ni),
                        fill_value, np.result_type(data, fill_value))
        image[self.j, self.i] = data
        return image

    def draw(self, data, mask=None, ax=None, **kwargs):
        im = self.assemble(data)
        if ax is None:
            fig, ax = plt.subplots(1, 1, **kwargs)
        ax.matshow(im)
