import argparse
from .vulnscan import run_scan  # or however you start your scan


def main():
    parser = argparse.ArgumentParser(
        description="Run VulnScan on a target URL")
    parser.add_argument('--url', type=str, help='Target URL to scan')
    args = parser.parse_args()

    if args.url:
        run_scan(args.url)
    else:
        print("Please provide a target URL using --url")
