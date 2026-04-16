import os, subprocess

def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

        if os.path.commonpath([target_file, working_dir_abs]) != working_dir_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not target_file.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_file]
        if args:
            command.extend(args)
        process = subprocess.run(
            command, capture_output=True, cwd=working_dir_abs, timeout=30, text=True
            )
        
        output = []
        if process.returncode != 0:
            output.append(f"Process exited with code {process.returncode}")
        if not (process.stdout or process.stderr):
            output.append("No output produced")
        if process.stdout:
            output.append(f"STDOUT:\n{process.stdout}")
        if process.stderr:
            output.append(f"STDERR:\n{process.stderr}")
        return "\n".join(output)
        
    except Exception as e:
        return f"Error: executing Python file: {e}"