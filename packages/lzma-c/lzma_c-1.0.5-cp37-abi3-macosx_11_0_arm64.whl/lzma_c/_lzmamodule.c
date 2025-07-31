#define Py_LIMITED_API 0x03070000 // Python 3.11
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "LzmaLib.h"
#include "LzmaEnc.h"
#include "LzmaDec.h"
#include "Alloc.h"
#include "7zTypes.h"

static PyObject* lzma_compress_py(PyObject* self, PyObject* args) {
    PyObject* src_obj; // 接收通用的 Python 对象
    int level = 5, numThreads = 1;
    unsigned dictSize = 1 << 23;
    int lc = 3, lp = 0, pb = 2, fb = 128;

    // 1. 不再使用 "y*", 改用 "O" 接收一个通用对象
    if (!PyArg_ParseTuple(args, "O|Iiiiii", &src_obj, &level, &dictSize, &lc, &lp, &pb, &fb, &numThreads)) {
        return NULL;
    }

    // 2. 检查对象是否是 bytes 类型
    if (!PyBytes_Check(src_obj)) {
        PyErr_SetString(PyExc_TypeError, "Input must be a bytes object.");
        return NULL;
    }

    // 3. 手动获取指向内存的指针和长度
    const char* src_buf = PyBytes_AsString(src_obj);
    Py_ssize_t src_len = PyBytes_Size(src_obj);
    if (src_buf == NULL) {
        return NULL; // PyBytes_AsString 失败会设置异常
    }

    size_t propsSize = LZMA_PROPS_SIZE;
    unsigned char props[LZMA_PROPS_SIZE];
    // 注意: 这里 src_len 是 Py_ssize_t, 需要转换为 size_t
    size_t destLen = (size_t)src_len + (size_t)src_len / 3 + 128;
    unsigned char* dest = (unsigned char*)PyMem_Malloc(destLen);
    if (!dest) return PyErr_NoMemory();

    int res = LzmaCompress(dest, &destLen, (const unsigned char*)src_buf, (size_t)src_len,
                        props, &propsSize, level, dictSize, lc, lp, pb, fb, numThreads);

    // 4. 不再需要 PyBuffer_Release

    if (res != SZ_OK) {
        PyMem_Free(dest);
        PyErr_SetString(PyExc_RuntimeError, "LZMA compression failed");
        return NULL;
    }

    PyObject* result = Py_BuildValue("(y#y#)", dest, destLen, props, propsSize);
    PyMem_Free(dest);
    return result;
}
static PyObject* lzma_uncompress_py(PyObject* self, PyObject* args) {
    PyObject *src_obj, *props_obj;
    unsigned long long uncompressed_size_ull; // "K" 格式对应 unsigned long long

    // 1. 改用 "OOK" 格式接收通用对象
    if (!PyArg_ParseTuple(args, "OOK", &src_obj, &props_obj, &uncompressed_size_ull)) {
        return NULL;
    }

    // 2. 检查对象是否是 bytes 类型
    if (!PyBytes_Check(src_obj) || !PyBytes_Check(props_obj)) {
        PyErr_SetString(PyExc_TypeError, "Input and properties must be bytes objects.");
        return NULL;
    }

    // 3. 手动获取 props 的指针和长度
    const char* props_buf = PyBytes_AsString(props_obj);
    Py_ssize_t props_len = PyBytes_Size(props_obj);
    if (props_buf == NULL) {
        return NULL; // PyBytes_AsString 失败会设置异常
    }

    if (props_len != LZMA_PROPS_SIZE) {
        PyErr_SetString(PyExc_ValueError, "LZMA properties must be 5 bytes");
        return NULL;
    }

    // 4. 手动获取 src 的指针和长度
    const char* src_buf = PyBytes_AsString(src_obj);
    Py_ssize_t src_len_py = PyBytes_Size(src_obj);
    if (src_buf == NULL) {
        return NULL; // PyBytes_AsString 失败会设置异常
    }

    size_t destLen = (size_t)uncompressed_size_ull;
    unsigned char* dest = (unsigned char*)PyMem_Malloc(destLen);
    if (!dest) return PyErr_NoMemory();

    size_t srcLen = (size_t)src_len_py;
    int res = LzmaUncompress(dest, &destLen, (const unsigned char*)src_buf, &srcLen,
                             (const unsigned char*)props_buf, (size_t)props_len);

    // 5. 不再需要 PyBuffer_Release

    if (res != SZ_OK) {
        PyMem_Free(dest);
        PyErr_SetString(PyExc_RuntimeError, "LZMA uncompression failed");
        return NULL;
    }

    PyObject* result = Py_BuildValue("y#", dest, destLen);
    PyMem_Free(dest);
    return result;
}


static PyMethodDef LzmaMethods[] = {
    {"compress", lzma_compress_py, METH_VARARGS, "Compress data using LZMA."},
    {"uncompress", lzma_uncompress_py, METH_VARARGS, "Decompress data using LZMA."},
    {NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef lzmamodule = {
    PyModuleDef_HEAD_INIT,
    "_lzma", 
    "A Python interface to the 7-Zip LZMA C library.", 
    -1,
    LzmaMethods
};

PyMODINIT_FUNC PyInit__lzma(void) {
    return PyModule_Create(&lzmamodule);
}