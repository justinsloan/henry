import re
import subprocess
import sys, os
import shutil
from pathlib import Path

def get_recent_markdown_files(directory, recursive=True):
    file_list = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.lower().endswith(('.md', '.markdown')):
                path = os.path.join(root, file_name)
                file_list.append((os.path.getmtime(path), path))
        if not recursive:
            break

    # Keep only the six most recent files
    file_list.sort(reverse=True, key=lambda x: x[0])
    recent_files = [p for _, p in file_list[:24]]

    return recent_files

def count_words_outside_header(text=""):
    """Return a word count that does not include words that are in the Jekyll headers."""
    lines = text.split('\n')
    in_header = False
    word_count = 0

    for line in lines:
        stripped_line = line.strip()
        if stripped_line == "---":
            in_header = not in_header
            continue
        if not in_header and stripped_line:
            words = stripped_line.split()
            word_count += len(words)

    return word_count


def get_jekyll_version(jekyll_path="jekyll"):
    """
    Get the Jekyll version from `jekyll --version`.
    """
    cmd = [
        jekyll_path,
        "--version"
    ]

    try:
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("`jekyll` command not found – make sure Ruby & the Jekyll gem are installed.") from exc

    return result.returncode, result.stdout, result.stderr


def new_jekyll_site(jekyll_path="jekyll", dir_name="my_jekyll_site", cwd=None):
    """
    Execute `jekyll new <dir_name>`.
    """
    cmd = [jekyll_path, "new", dir_name]
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,          # we will inspect `returncode`
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "`jekyll` command not found. "
            "Make sure Ruby and Jekyll are installed."
        ) from e

    return result.returncode, result.stdout, result.stderr


def build_jekyll_site(jekyll_path="jekyll", site_dir="my_jekyll_site", destination_dir=""):
    """
    Build the Jekyll site in `destination_dir`.
    """
    if not destination_dir:
        destination_dir = site_dir  + "/_site"

    cmd = [
        jekyll_path,
        "build",
        "--source",
        str(site_dir),
        "--destination",
        str(destination_dir),
    ] # Command: jekyll build --source {site_dir} --destination {destination_dir}

    result = subprocess.run(
        cmd,
        cwd=site_dir,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def get_app_paths():
    """Check PATH to find Ruby and Jekyll install."""
    # check if .gem path exists; the Ruby binary is located here on Mac systems
    gem_path = ""
    gem_user_path = Path(os.path.expanduser('~') + "/.gem/ruby")
    if not gem_user_path.is_dir():
        # .gem dir does not exist
        gem_path = ""
    else:
        # there is a .gem path, so we need to find the ruby version number so we can get the /bin path
        version_pattern = re.compile(r"^\d+\.\d+\.\d+$")
        for entry in gem_user_path.iterdir():
            if entry.is_dir() and version_pattern.match(entry.name):
                gem_path = str(gem_user_path) + "/" + entry.name + "/bin"
                break

    system_path = os.pathsep.join([p for p in os.environ['PATH'].split(os.pathsep)])
    user_path = os.path.expanduser('~') + "/bin"
    search_path = user_path + gem_path + ":" + system_path
    jekyll_path = shutil.which('jekyll', path=search_path)
    ruby_path = shutil.which('ruby', path=search_path)

    print("System :::" + str(system_path))
    print("User   :::" + str(user_path))
    print("Search :::" + str(search_path))
    print("")
    print("FOUND")
    print("Ruby   :::" + str(ruby_path))
    print("Jekyll :::" + str(jekyll_path))

    return search_path, ruby_path, jekyll_path


def create_directory(directory_path):
    """Checks if a directory exists and creates it if it doesn't."""
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)  # Create the directory and any parent directories
            print(f"Directory '{directory_path}' created successfully.")
            return False
        else:
            print(f"Directory '{directory_path}' already exists.")
            return True
    except Exception as e:
        print(f"An error occurred: {e}")