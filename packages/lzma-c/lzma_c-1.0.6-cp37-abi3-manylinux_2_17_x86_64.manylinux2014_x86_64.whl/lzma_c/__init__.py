# src/lzma_c/__init__.py

# _lzma 是由 C 代码编译成的 .pyd/.so 文件
# 直接导入 C 扩展模块，避免循环导入问题
import os

version = os.environ.get("LZMA_VERSION", "0.0.0.dev0")
# 如果版本号以 "v" 开头，就去掉它
if version.startswith('v'):
    version = version[1:]
__version__ = version
def compress(data: bytes) -> bytes:
    """
    Compresses data and returns a stream with a standard LZMA header.
    Header format: [5 bytes props][8 bytes uncompressed size][compressed data]
    """
    if not isinstance(data, bytes):
        raise TypeError("Input must be bytes.")
    
    from . import _lzma
    compressed_data, props = _lzma.compress(data)
    
    original_size_bytes = len(data).to_bytes(8, 'little')
    
    return props + original_size_bytes + compressed_data

def decompress(stream: bytes) -> bytes:
    """
    Decompresses a stream with a standard LZMA header.
    """
    if not isinstance(stream, bytes):
        raise TypeError("Input must be bytes.")
    
    if len(stream) < 13:
        raise ValueError("Invalid LZMA stream: header is too short.")
        
    props = stream[:5]
    original_size = int.from_bytes(stream[5:13], 'little')
    compressed_data = stream[13:]
    from . import _lzma
    return _lzma.uncompress(compressed_data, props, original_size)

# 导出公共 API
__all__ = ['compress', 'decompress']