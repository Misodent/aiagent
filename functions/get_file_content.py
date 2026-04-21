import os
from config import MAX_CHARS
from google import genai
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Provides the content of a file of a specified path relative to the working directory, up to 10000 characters",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to get content from, relative to the working directory (default is the working directory itself)",
            ),
        },
        required=["file_path"]
    ),
)

def get_file_content(working_directory, file_path):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

        if os.path.commonpath([working_dir_abs, target_file]) != working_dir_abs:
            return f'Error: Cannot read "{target_file}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: {target_file}'

        with open(target_file, "r") as f:
            file_content_string = f.read(MAX_CHARS)

            if f.read(1):
                file_content_string += f'[...File "{target_file}" truncated at {MAX_CHARS} characters]'

            return file_content_string
    except Exception as e:
        return f"Error: getting file content: {e}"