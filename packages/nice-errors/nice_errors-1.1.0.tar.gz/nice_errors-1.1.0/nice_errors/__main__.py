import argparse
from importlib.metadata import version, PackageNotFoundError


def get_package_version():
    try:
        return version("nice_errors")
    except PackageNotFoundError:
        return "unknown"
parser = argparse.ArgumentParser(prog='python -m nice_errors', usage='%(prog)s [options]')

parser.add_argument('--version', action='version', version='%(prog)s ' + get_package_version(),help='show program\'s version and exit')

parser.parse_args()