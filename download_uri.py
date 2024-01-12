import sys
import pathlib
import lbrytools as lbryt
from lbrytools import download_single

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_uri.py <URI>")
        sys.exit(1)

    uri = sys.argv[1]
    ddir = str(pathlib.Path.home() / "Downloads")
    own_dir = True

    d = lbryt.download_single(uri, ddir, own_dir)
    print(d)
