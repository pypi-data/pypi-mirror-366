import subprocess
import tempfile
import os

class LocalSandboxService:
    def run_code(self, code: str):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode('utf-8'))
            temp_path = f.name
        try:
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True, text=True, timeout=30
            )
            return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
        finally:
            os.remove(temp_path)




