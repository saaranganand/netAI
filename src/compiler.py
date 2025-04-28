import os
import subprocess

class P4Compiler:
    """
    Runs the p4c compiler inside Docker
    """

    def compile(self, p4_file: str) -> (bool, str):
        file_name = os.path.basename(p4_file)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"out:/mnt",
            "p4lang/p4c:latest",
            "p4c", f"/mnt/{file_name}"
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        success = proc.returncode == 0
        feedback = proc.stderr if not success else ""
        return success, feedback