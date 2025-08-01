import argparse
from .core import upload_to_pypi
from .utils import get_files_from_dist

def main():
    parser = argparse.ArgumentParser(description="Hanifx PyPI Uploader without Twine")
    parser.add_argument("--token", required=True, help="Your PyPI API Token")
    parser.add_argument("--files", nargs="*", help="Files to upload (default: all in dist/)")
    args = parser.parse_args()

    files = args.files if args.files else get_files_from_dist()
    if not files:
        print("[X] No files found to upload in dist/")
        return
    
    success, failed = upload_to_pypi(args.token, files)
    print(f"\nSummary: {len(success)} success, {len(failed)} failed")

if __name__ == "__main__":
    main()
