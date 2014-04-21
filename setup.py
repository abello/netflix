from distutils.core import setup 
from distutils.extension import Extension 
from Cython.Distutils import build_ext


ext = [Extension(
    "ht", # name of extension
    ["ht.pyx"], # filename of our Pyrex/Cython source
    language="c++", # this causes Pyrex/Cython to create C++ source
    extra_compile_args=["-std=c++11"],
#     include_dirs=[...], # usual stuff
#     libraries=[...], # ditto
#     extra_link_args=[...], # if needed
    ),
    Extension(
        "train", # name of extension
        ["train.pyx"], # filename of our Pyrex/Cython source
        language="c++", # this causes Pyrex/Cython to create C++ source
    extra_compile_args=["-std=c++11"],
#         extra_compile_args=["-std=c++11"],
    #     include_dirs=[...], # usual stuff
    #     libraries=[...], # ditto
    #     extra_link_args=[...], # if needed
        ),
    Extension(
        "test", # name of extension
        ["test.pyx"], # filename of our Pyrex/Cython source
        language="c", # this causes Pyrex/Cython to create C++ source
#         extra_compile_args=["-std=c++11"],
    #     include_dirs=[...], # usual stuff
    #     libraries=[...], # ditto
    #     extra_link_args=[...], # if needed
        )
    ]


setup(cmdclass = {'build_ext': build_ext}, ext_modules = ext)
