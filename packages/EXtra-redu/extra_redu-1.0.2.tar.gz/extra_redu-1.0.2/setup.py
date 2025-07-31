import numpy as np
from setuptools import Extension, setup


extensions = [
    Extension(
        "extra_redu.lossy.rounding",
        [
            "src/extra_redu/lossy/rounding.pyx",
            "src/extra_redu/lossy/rounding_impl.c"
        ],
        include_dirs=[np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    ),
]

setup(
    ext_modules=extensions,
)
