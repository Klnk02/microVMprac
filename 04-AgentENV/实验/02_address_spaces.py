#!/usr/bin/env python3
"""Two ordinary Linux processes: pointer interpretation and remote copying.

No VM, AgentENV service, root access, or persistent output file is used by
the experiment itself. The memfd is an anonymous in-memory file, not a disk.
"""

import ctypes
import json
import mmap
import os
import platform
import struct
import sys


class IOVec(ctypes.Structure):
    _fields_ = [("base", ctypes.c_void_p), ("length", ctypes.c_size_t)]


def checked(value, operation):
    if value < 0:
        code = ctypes.get_errno()
        raise OSError(code, operation + ": " + os.strerror(code))
    return value


def read_exact(fd, size):
    data = b""
    while len(data) < size:
        part = os.read(fd, size - len(data))
        if not part:
            raise RuntimeError("child ended before sending its address")
        data += part
    return data


def main():
    if sys.platform != "linux" or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("This exercise needs 64-bit Linux; use local WSL")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.process_vm_readv.argtypes = [
        ctypes.c_int, ctypes.POINTER(IOVec), ctypes.c_ulong,
        ctypes.POINTER(IOVec), ctypes.c_ulong, ctypes.c_ulong,
    ]
    libc.process_vm_readv.restype = ctypes.c_ssize_t
    libc.pwrite.argtypes = [
        ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_longlong,
    ]
    libc.pwrite.restype = ctypes.c_ssize_t

    # fork preserves this VA in both processes; MAP_PRIVATE permits divergence.
    memory = mmap.mmap(-1, mmap.PAGESIZE,
                       flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS,
                       prot=mmap.PROT_READ | mmap.PROT_WRITE)
    source = (ctypes.c_char * mmap.PAGESIZE).from_buffer(memory)
    address = ctypes.addressof(source)
    ctypes.memmove(address, b"SERVER_PARENT\0", 14)
    count = 64
    file_fd = os.memfd_create("agentenv-lesson02", os.MFD_CLOEXEC)
    ready_r, ready_w = os.pipe()
    stop_r, stop_w = os.pipe()
    child_pid = os.fork()
    if child_pid == 0:
        os.close(ready_r)
        os.close(stop_w)
        try:
            ctypes.memmove(address, b"CHILD_GUEST_DATA\0", 17)
            written = checked(libc.pwrite(file_fd, address, count, 128),
                              "child pwrite")
            if written != count:
                raise RuntimeError("short child pwrite")
            os.write(ready_w, struct.pack("Q", address))
            os.close(ready_w)
            os.read(stop_r, 1)
        except BaseException as error:
            os.write(2, (str(error) + "\n").encode())
            os._exit(1)
        os._exit(0)

    os.close(ready_w)
    os.close(stop_r)
    try:
        remote_address = struct.unpack("Q", read_exact(ready_r, 8))[0]
        assert remote_address == address

        # Using the remote VA number in an ordinary local pwrite reads LOCAL data.
        assert checked(libc.pwrite(file_fd, remote_address, count, 0),
                       "parent pwrite") == count

        destination = ctypes.create_string_buffer(count)
        local = IOVec(ctypes.addressof(destination), count)
        remote = IOVec(remote_address, count)
        copied = checked(libc.process_vm_readv(
            child_pid, ctypes.byref(local), 1, ctypes.byref(remote), 1, 0),
            "process_vm_readv")
        assert copied == count
        assert checked(libc.pwrite(file_fd, ctypes.addressof(destination),
                                  count, 64), "parent write copied data") == count

        text = lambda offset: os.pread(file_fd, count, offset).split(b"\0", 1)[0].decode()
        actual = [text(0), text(64), text(128)]
        assert actual == ["SERVER_PARENT", "CHILD_GUEST_DATA", "CHILD_GUEST_DATA"], actual
        assert bytes(source[:count]).startswith(b"SERVER_PARENT\0")
        print(json.dumps({
            "experiment": "lesson02_two_ordinary_processes_not_real_agentenv",
            "environment": {"os": platform.system(), "kernel": platform.release()},
            "parent_pid": os.getpid(), "child_pid": child_pid,
            "parent_virtual_address": hex(address),
            "child_virtual_address": hex(remote_address),
            "copy_bytes": copied,
            "parent_pwrite_using_same_va_number": actual[0],
            "parent_pvm_then_pwrite": actual[1],
            "child_pwrite_using_its_own_va": actual[2],
            "file_backend": "anonymous memfd; no physical disk result",
            "result": "PASS",
        }, indent=2))
    finally:
        os.close(stop_w)  # EOF releases the child, even when a check fails.
        os.close(ready_r)
        _, status = os.waitpid(child_pid, 0)
        os.close(file_fd)
        del source
        memory.close()
        if status:
            raise RuntimeError("child failed with wait status " + str(status))


if __name__ == "__main__":
    main()
