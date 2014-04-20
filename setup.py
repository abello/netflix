from distutils.core import setup 
from distutils.extension import Extension 
from Cython.Distutils import build_ext


ext = Extension(
    "ht", # name of extension
    ["ht.pyx"], # filename of our Pyrex/Cython source
    language="c++", # this causes Pyrex/Cython to create C++ source
#     include_dirs=[...], # usual stuff
#     libraries=[...], # ditto
#     extra_link_args=[...], # if needed
    cmdclass = {'build_ext': build_ext}
    )


setup(cmdclass = {'build_ext': build_ext}, ext_modules = ext)
