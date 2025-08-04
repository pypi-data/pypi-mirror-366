from setuptools import setup, Extension, find_packages
import numpy as np
import os

__version__ = "0.1.1"


compile_args = []
if os.name == "nt":  # Windows (MSVC)
    # Use release flags for performance
    compile_args.extend(["/std:c++11", "/O2", "/Oi", "/Ot", "/Oy", "/GL", "/GR-", "/EHsc", "/DNDEBUG"])
    link_args = ["/LTCG"]
else:  # Linux/Mac (GCC/Clang)
    # Use release flags for performance
    compile_args.extend(["-std=c++11", "-O3", "-march=native", "-ffast-math", "-flto", "-DNDEBUG"])
    link_args = ["-flto"]
    # Add -fPIC for Linux/macOS if not already default (position independent code)
    if os.name != "nt":
        compile_args.append("-fPIC")

setup(
    name="pyscreeningfs",
    version=__version__,
    author="Mingyuan Wang",
    author_email="bruce.wmy.research@gmail.com",
    description="This is a Python implementation by the authors of the paper 'Online Feature Screening for Data Streams With Concept Drift' from Dr. Mingyuan Wang and Dr. Adrian Barbu. Contain various feature selection methods.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown', # If your README is Markdown
    url="https://github.com/tbonewmy/Online-Feature-Screening-for-Datastream-with-Sparsity-Concept-Drifting", # Link to your GitHub repo
    packages=find_packages(), # Automatically find all Python packages (e.g., 'fsonline' folder)
    python_requires='>=3.10', # Minimum Python version required
    install_requires=[
        "numpy>=2.2.4", # Specify the required numpy version
        # Add any other Python dependencies here
    ],
    license="Apache-2.0",
    keywords=[
        "feature selection",
        "feature screening",
        "variable screening",
        "online learning",
        "online feature selection",
        "concept drift",
        "data drift",
        "machine learning",
        "artificial intelligence",
        "statistics"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 3 - Alpha", # Or Beta, Production/Stable
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    ext_modules=[
        Extension(
            "pyscreeningfs.fsonline",
            sources=["pyscreeningfs/fsonline.cpp", "pyscreeningfs/ScsUtil.cpp"],  # Your converted C++ file
            include_dirs=[np.get_include()],  # NumPy headers
            extra_compile_args=compile_args,
            # libraries=["m"],  # Link math library if needed, for Linux/macOS
	        define_macros=[("PY_SSIZE_T_CLEAN", None),
                        ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),  # NumPy stability
                        ],  # For Python 3.7+
            extra_link_args=link_args
	        # define_macros=[("PYTHON3", None)] # For Python < 3.7
            # extra_link_args=['/DEBUG']
        )
    ],
)
