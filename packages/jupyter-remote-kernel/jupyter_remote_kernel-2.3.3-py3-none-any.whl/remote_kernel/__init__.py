#!/usr/bin/env python3
import os, time

__version__ = '2.3.3'

# Global variables for configuration
PID_FILE = "/tmp/remote_kernel.pid"
LOG_FILE = "/tmp/remote_kernel.log"
KERNELS_DIR_DEFAULT = os.path.expanduser("~/.local/share/jupyter/kernels")

PYTHON_BIN = os.environ.get("REMOTE_KERNEL_PYTHON", "python")
REMOTE_CONN_DIR = os.environ.get("REMOTE_CONN_DIR", "/tmp")
KERNELS_DIR = os.environ.get("LOCAL_KERNELS_DIR", KERNELS_DIR_DEFAULT)

def usage():
    print("Usage:")
    print("  remote_kernel --endpoint <user@host[:port]> [-J user@host:port] -f <connection_file>")
    print("  remote_kernel add --endpoint <user@host[:port]> [-J user@host:port] --name <Display Name>")
    print("  remote_kernel list")
    print("  remote_kernel delete <slug-or-name>")
    print("  remote_kernel connect [<slug-or-name>]")
    print("  remote_kernel sync [<slug-or-name>] [src_file]")
    print("  remote_kernel -v (show version)")

def version():
    print(f"version {__version__}")
    print(f"ENV: LOCAL_KERNELS_DIR = {KERNELS_DIR}")
    print(f"ENV: REMOTE_KERNEL_PYTHON = {PYTHON_BIN}")
    print(f"ENV: REMOTE_CONN_DIR = {REMOTE_CONN_DIR}")
    print(f"PID file: {PID_FILE}")
    print(f"Log file: {LOG_FILE}")

def log(msg, k=None):
    prefix = f"[{k}] " if k else ""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {prefix}{msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")