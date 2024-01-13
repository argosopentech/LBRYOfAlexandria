import sys
import pathlib
import lbrytools as lbryt
from lbrytools import list_trending_claims

if __name__ == "__main__":
    vv = lbryt.print_blobs_ratio(plot_hst=True)
    print(vv)
