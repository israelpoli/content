import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401

from pathlib import Path
import shutil
import shlex
import subprocess
from tempfile import mkdtemp
from subprocess import Popen, PIPE
import zipfile

def installLibrary(dir_path: Path, library_name: str) -> type(fileResult):
    # Install the package using pip     
    cmd = f'python3 -m pip install --target {dir_path} {library_name}'
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
       raise DemistoException(f"Failed to install the {library_name} library: {stderr.decode('utf-8')}")

    # Create a zip file with maximum compression level
    zip_path = dir_path / (library_name + '.zip')
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / file
                # Ensure the folder inside the ZIP file is named 'python'
                arcname = Path('python') / file_path.relative_to(dir_path)
                zip_file.write(file_path, arcname=arcname)

    # Read the zip file contents
    with open(zip_path, 'rb') as zip_file:
        zip_content = zip_file.read()

    return fileResult(library_name+'.zip', zip_content)

def main():
    args = demisto.args()
    library_name = args.get('library_name')
    try:
       dir_path = Path(mkdtemp(prefix='python'))
       result = installLibrary(dir_path, library_name)
       return_results(result)

    except Exception as e:
        return_error(f"An error occurred: {str(e)}")
        

if __name__ in ('__builtin__', 'builtins'):
    main()
