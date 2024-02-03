"""

Utility functions used in test.py (pytest loads this file automatically).

"""

import pytest
import os
import subprocess
import shlex
import struct
import tempfile
import re
import sys

# To avoid building WasmOS every time, use placefolder and replace this with the specified script. 
AUTORUN_PLACEHOLDER = "__REPLACE_ME_AUTORUN__" + "a" * 512
ANSI_ESCAPE_SEQ_REGEX = re.compile(r'\x1B\[[^m]+m')

runner = None

# Build WasmOS and create a runner.
@pytest.fixture
def run_wasmos(request):
    # Build WasmOS if not built.
    global runner
    if runner is None:
        build_argv = [
            "make",
            "build",
            f"AUTORUN={AUTORUN_PLACEHOLDER}",
            f"-j{os.cpu_count()}"
        ]
        subprocess.run(build_argv, check=True)
    
    # Create Runner.
    runner = Runner(
        request.config.getoption("--qemu"),
        shlex.split(os.environ["QEMUFLAGS"]),
        "build/wasmos.elf"
    )

    return do_run_wasmos

def do_run_wasmos(script, qemu_net0_options=None):
    return runner.run(script + "; shutdown", qemu_net0_options)

class Result:
    def __init__(self, log, raw_log):
        self.log = log
        self.raw_log = raw_log
    
class Runner:
    def __init__(self, qemu, default_qemu_flags, image_path):
        self.qemu = qemu
        self.default_qemu_flags = default_qemu_flags
        self.image = open(image_path, "rb").read()
        self.placeholder_bytes = AUTORUN_PLACEHOLDER.encode("ascii")
    
    def run(self, script, qemu_net0_options):
        if len(script.encode("ascii")) > len(self.placeholder_bytes):
            raise ValueError("script is too long")
        
        qemu_args = []

        for arg in self.default_qemu_flags:
            if qemu_net0_options is not None and "-netdev user, id=net0" in arg:
                qemu_args.append(arg + "," + ",".join(qemu_net0_options))
            else:
                qemu_args.append(arg)
        
        script_bytes = struct.pack(
            f"{len(AUTORUN_PLACEHOLDER)}s", 
            script.encode("ascii")
        )

        with tempfile.NamedTemporaryFile(mode="wb+", delete=False) as f:
            # Replace the placefolder with the specified script.
            f.write(self.image.replace(self.placeholder_bytes, script_bytes))
            f.close()

            # Execute the specified script on Qemu.
            qemu_argv = [self.qemu, "-kernel", f.name, "-snapshot"] + qemu_args

            try:
                raw_log = subprocess.check_output(qemu_argv)
            finally:
                os.remove(f.name)
            
            # Write outputs to stdout (for debugging).
            sys.stdout.buffer.write(raw_log)

            log = raw_log.decode('utf-8', errors='backslashreplace')
            # Remove color.
            log = re.sub(ANSI_ESCAPE_SEQ_REGEX, '', log)
        
        return Result(log, raw_log)

# Define command line options
def pytest_addoption(parser):
    parser.addoption("--qemu", required=True)