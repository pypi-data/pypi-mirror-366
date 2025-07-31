# setup.py
from setuptools import Extension, setup

# 当 setuptools 构建时，它会执行这个文件并查找 setup() 调用
# 来获取包括 C 扩展在内的所有配置。
setup(
    ext_modules=[
        Extension(
            name = "lzma_c._lzma",
            sources=[
                "src/lzma_c/_lzmamodule.c",
                "vendor/lzma/LzmaLib.c",
                "vendor/lzma/Alloc.c",
                "vendor/lzma/LzFind.c",
                "vendor/lzma/LzFindMt.c",
                "vendor/lzma/LzFindOpt.c",
                "vendor/lzma/LzmaDec.c",
                "vendor/lzma/LzmaEnc.c",
                "vendor/lzma/Threads.c",
                "vendor/lzma/CpuArch.c",
            ],
            include_dirs = ["vendor/lzma/include"],
            py_limited_api = True,  # 使用受限的 Python API
        )
    ],
    options= {
        'bdist_wheel': {
            'py_limited_api': 'cp37',  
        }
    }
        
)