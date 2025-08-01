import ctypes
import os
import re
import threading


class _Opaque(ctypes.Structure):
    """:meta private:"""
    pass

LIBRARY_NAME_PATTERN = re.compile("chemaxon-lib\\.(so|dylib|dll)")
""":meta private:"""

# Idea: use one thread for MainThread and create and tear down IsolateThreads for each other threads.
# Isolate threads enable separate memory space for each thread. So static fields on the java side will become separate
# memory space for the different threads in the generated native code.
class _IsolateHandler:
    """:meta private:"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            library_path = os.path.join(os.path.dirname(__file__), "libs")

            # This is needed because the native shared library extension is differ based on the operation system
            files = os.listdir(library_path)
            cls._instance.cxn = None
            for f in files:
                if LIBRARY_NAME_PATTERN.fullmatch(f):
                    cls._instance.cxn = ctypes.cdll.LoadLibrary(os.path.join(str(library_path), f))
                    break

            if 'awt.dll' in files:
                ctypes.cdll.LoadLibrary(os.path.join(str(library_path), 'awt.dll'))
            if 'libawt_xawt.so' in files:
                ctypes.cdll.LoadLibrary(os.path.join(str(library_path), 'libawt_xawt.so'))

            if cls._instance.cxn is None:
                raise Exception("Could not find chemaxon-lib!")

            cls._instance.main_thread = None
        return cls._instance

    def __del__(self):
        if self._instance.main_thread is not None:
            self.cxn.graal_tear_down_isolate(self.main_thread)

    def get_isolate_thread(self):
        if threading.current_thread() is threading.main_thread():
            if self._instance.main_thread is None:
                self._instance.main_thread = _create_new_thread()
            return self._instance.main_thread
        else:
            return _create_new_thread()

    def cleanup_isolate_thread(self, thread):
        if not threading.current_thread() is threading.main_thread():
            self.cxn.graal_tear_down_isolate(thread)

    def get_lib(self):
        return self.cxn


def _create_new_thread():
    """:meta private:"""
    isolate = ctypes.pointer(_Opaque())
    thread = ctypes.pointer(_Opaque())
    # start native environment
    _cxn.graal_create_isolate(None, ctypes.pointer(isolate), ctypes.pointer(thread))
    return thread

_isolate_handler = _IsolateHandler()
""":meta private:"""
_cxn = _isolate_handler.get_lib()
""":meta private:"""
