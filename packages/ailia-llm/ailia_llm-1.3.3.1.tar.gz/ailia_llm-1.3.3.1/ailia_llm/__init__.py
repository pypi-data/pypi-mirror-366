import ctypes
import os
import sys

import numpy
import ailia

import os
import platform

#### dependency check
if sys.platform == "win32":
    import ctypes
    try:
        for library in ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"]:
            ctypes.windll.LoadLibrary(library)
    except:
        print("  WARNING Please install MSVC 2015-2019 runtime from https://docs.microsoft.com/ja-jp/cpp/windows/latest-supported-vc-redist")


#### loading DLL / DYLIB / SO  ####
if sys.platform == "win32":
    dll_platform = "windows/x64"
    dll_name = "ailia_llm.dll"
    dll_name_fallback = "ailia_llm_fallback.dll"
    load_fn = ctypes.WinDLL
elif sys.platform == "darwin":
    dll_platform = "mac"
    dll_name = "libailia_llm.dylib"
    dll_name_fallback = None
    load_fn = ctypes.CDLL
else:
    is_arm = "arm" in platform.machine() or platform.machine() == "aarch64"
    if is_arm:
        if platform.architecture()[0] == "32bit":
            dll_platform = "linux/armeabi-v7a"
        else:
            dll_platform = "linux/arm64-v8a"
    else:
        dll_platform = "linux/x64"
    dll_name = "libailia_llm.so"
    dll_name_fallback = None
    load_fn = ctypes.CDLL

dll_found = False
candidate = ["", str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep), str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep) + dll_platform + str(os.sep)]

for dir in candidate:
    try:
        dll = load_fn(dir + dll_name) # Load gpu library first
        dll_found = True
    except:
        pass

if not dll_found:
    for dir in candidate:
        try:
            dll = load_fn(dir + dll_name_fallback) # Fallback cpu library second
            dll_found = True
        except:
            pass

if not dll_found:
    msg = "DLL load failed : \'" + dll_name + "\' is not found"
    raise ImportError(msg)

# ==============================================================================

from ctypes import *

AILIA_LLM_STATUS_SUCCESS = ( 0 )
AILIA_LLM_STATUS_CONTEXT_FULL = ( -8 )

class AILIALLMChatMessage(ctypes.Structure):
    _fields_ = [
        ("role", ctypes.c_char_p),
        ("content", ctypes.c_char_p)
    ]

# ==============================================================================

dll.ailiaLLMCreate.restype = c_int
dll.ailiaLLMCreate.argtypes = (POINTER(c_void_p), )

dll.ailiaLLMDestroy.restype = None
dll.ailiaLLMDestroy.argtypes = (c_void_p, )

dll.ailiaLLMOpenModelFileA.restype = c_int
dll.ailiaLLMOpenModelFileA.argtypes = (c_void_p, c_char_p, c_uint32)

dll.ailiaLLMOpenModelFileW.restype = c_int
dll.ailiaLLMOpenModelFileW.argtypes = (c_void_p, c_wchar_p, c_uint32)

dll.ailiaLLMGetDeltaTextSize.restype = c_int
dll.ailiaLLMGetDeltaTextSize.argtypes = (c_void_p, POINTER(c_uint32))

dll.ailiaLLMGetDeltaText.restype = c_int
dll.ailiaLLMGetDeltaText.argtypes = (c_void_p, numpy.ctypeslib.ndpointer(
                dtype=numpy.uint8, flags='CONTIGUOUS'
            ),                               # text
            ctypes.c_uint)

dll.ailiaLLMSetSamplingParams.restype = c_int
dll.ailiaLLMSetSamplingParams.argtypes = (c_void_p, ctypes.c_uint, ctypes.c_float, ctypes.c_float, ctypes.c_uint)

dll.ailiaLLMSetPrompt.restype = c_int
dll.ailiaLLMSetPrompt.argtypes = (c_void_p, ctypes.POINTER(AILIALLMChatMessage), ctypes.c_uint)

dll.ailiaLLMGenerate.restype = c_int
dll.ailiaLLMGenerate.argtypes = (c_void_p, POINTER(c_uint32))

dll.ailiaLLMGetTokenCount.restype = c_int
dll.ailiaLLMGetTokenCount.argtypes = (c_void_p, POINTER(c_uint32), c_char_p)

dll.ailiaLLMGetPromptTokenCount.restype = c_int
dll.ailiaLLMGetPromptTokenCount.argtypes = (c_void_p, POINTER(c_uint32))

dll.ailiaLLMGetGeneratedTokenCount.restype = c_int
dll.ailiaLLMGetGeneratedTokenCount.argtypes = (c_void_p, POINTER(c_uint32))


# ==============================================================================
# base model class
# ==============================================================================

class AiliaLLMError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(f"{message} code:{code}")
        self.code = code

class AiliaLLM():
    _instance = None
    _context_full = False

    def _check(self, status):
        if status != AILIA_LLM_STATUS_SUCCESS:
            raise AiliaLLMError(f"ailia LLM error", status)

    def _string_buffer_aw(self, path):
        if sys.platform == "win32":
            return ctypes.create_unicode_buffer(path)
        else:
            return ctypes.create_string_buffer(path.encode("utf-8"))

    def _string_buffer(self, path):
        return ctypes.create_string_buffer(path.encode("utf-8"))

    def _string_to_c_char_p(self, s):
        return ctypes.c_char_p(s.encode('utf-8'))

    def __init__(self):
        self._instance = ctypes.c_void_p(None)
        self._check(dll.ailiaLLMCreate(cast(pointer(self._instance), POINTER(c_void_p))))

    def open(self, model_path, n_ctx = 0):
        if "time_license" in ailia.get_version():
            ailia.check_and_download_license()
        p1 = self._string_buffer_aw(model_path)

        if sys.platform == "win32":
            self._check(dll.ailiaLLMOpenModelFileW(self._instance, p1, ctypes.c_uint32(n_ctx)))
        else:
            self._check(dll.ailiaLLMOpenModelFileA(self._instance, p1, ctypes.c_uint32(n_ctx)))

    def generate(self, prompts, top_k = 40, top_p = 0.9, temp = 0.4, dist = 1234):
        messages = (AILIALLMChatMessage * len(prompts))()
        for i in range(len(prompts)):
            messages[i].role = self._string_to_c_char_p(prompts[i]["role"])
            messages[i].content = self._string_to_c_char_p(prompts[i]["content"])

        status = dll.ailiaLLMSetSamplingParams(self._instance, top_k, top_p, temp, dist)
        self._check(status)

        self._context_full = False
        status = dll.ailiaLLMSetPrompt(self._instance, messages, ctypes.c_uint32(len(prompts)))
        if status == AILIA_LLM_STATUS_CONTEXT_FULL:
            self._context_full = True
            return
        self._check(status)

        buf = numpy.zeros((0), dtype=numpy.uint8, order='C')
        before_text = ""

        while True:
            done = ctypes.c_uint(0)
            status = dll.ailiaLLMGenerate(self._instance, ctypes.byref(done))
            self._check(status)

            if status == AILIA_LLM_STATUS_CONTEXT_FULL:
                self._context_full = True
                break

            if done.value == 1:
                break

            count = ctypes.c_uint(0)
            self._check(dll.ailiaLLMGetDeltaTextSize(self._instance, ctypes.byref(count)))

            new_buf = numpy.zeros((count.value), dtype=numpy.uint8, order='C')

            self._check(dll.ailiaLLMGetDeltaText(self._instance, new_buf, count))

            buf = numpy.concatenate([buf[:-1], new_buf])

            text = bytes(buf[:- 1]).decode("utf-8", errors="ignore")
            delta_text = text[len(before_text):]

            yield delta_text
            before_text = text

    def context_full(self):
        return self._context_full

    def token_count(self, text):
        count = ctypes.c_uint(0)
        text = self._string_to_c_char_p(text)
        self._check(dll.ailiaLLMGetTokenCount(self._instance, ctypes.byref(count), text))
        return count.value

    def prompt_token_count(self):
        count = ctypes.c_uint(0)
        self._check(dll.ailiaLLMGetPromptTokenCount(self._instance, ctypes.byref(count)))
        return count.value

    def generated_token_count(self):
        count = ctypes.c_uint(0)
        self._check(dll.ailiaLLMGetGeneratedTokenCount(self._instance, ctypes.byref(count)))
        return count.value

    def __del__(self):
        if self._instance:
            dll.ailiaLLMDestroy(cast(self._instance, c_void_p))

