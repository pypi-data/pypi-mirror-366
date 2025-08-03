import urllib
import os

def is_remote_url(path: str) -> bool:
    parsed = urllib.parse.urlparse(path)

    # Rule 1: Has a remote scheme like http or https
    if parsed.scheme in ("http", "https"):
        return True
    if parsed.scheme in ("file", "relative"):
        return False

    # Rule 2: If it's a local file path (relative or absolute), resolve and check existence
    local_path = os.path.abspath(os.path.expanduser(parsed.path))
    if os.path.exists(local_path):
        return False        

    # Rule 3: Default to remote
    return True
