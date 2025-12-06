import subprocess
import shutil
from typing import Optional, Tuple

class DisasmCollector:
    def __init__(self):
        self.objdump_path = shutil.which("objdump")
        if not self.objdump_path:
            # Try arm-none-eabi-objdump as fallback or just fail if strict
            self.objdump_path = shutil.which("arm-none-eabi-objdump")
            
    def is_available(self) -> bool:
        return self.objdump_path is not None

    def get_tool_version(self) -> str:
        if not self.objdump_path:
            return "unknown"
        try:
            result = subprocess.run([self.objdump_path, "--version"], capture_output=True, text=True, check=True)
            return result.stdout.splitlines()[0]
        except subprocess.Error:
            return "unknown"

    def disassemble(self, file_path: str) -> Tuple[str, str]:
        """
        Run objdump on the file.
        Returns (disassembly_text, tool_version).
        """
        if not self.objdump_path:
            raise RuntimeError("objdump not found in PATH")

        try:
            # objdump -d -S artifact.elf
            result = subprocess.run(
                [self.objdump_path, "-d", "-S", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout, self.get_tool_version()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"objdump failed: {e.stderr}")
