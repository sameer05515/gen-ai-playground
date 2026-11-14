import os
import zipfile

def create_zip(source_folder, output_zip):

    excluded_dirs = {".git", ".venv", "__pycache__", "node_modules","chroma_db"}

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:

        for root, dirs, files in os.walk(source_folder):

            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_folder)

                zipf.write(file_path, arcname)

    print("ZIP created:", output_zip)


create_zip(
    r"D:\GIT\gen-ai-playground\example-base-04\chatgpt-intelligence-rag-v1",
    r"D:\GIT\gen-ai-playground\example-base-04\chatgpt-intelligence-rag-v1.zip"
)