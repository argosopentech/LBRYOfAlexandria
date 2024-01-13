import sys
import pathlib
import lbrytools as lbryt
from lbrytools import list_trending_claims

if __name__ == "__main__":
    g = lbryt.list_trending_claims()  # all types, 1000 claims
    print(g)
