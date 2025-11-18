"""
Dependency Checker for Skripsi Downloader
Checks if all required packages are installed
"""
import sys


def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False


def main():
    """Check all required dependencies"""
    print("=" * 60)
    print("Skripsi Downloader - Dependency Checker")
    print("=" * 60)
    print()

    packages = [
        ("requests", "requests"),
        ("Pillow", "PIL"),
        ("img2pdf", "img2pdf"),
        ("pytesseract", "pytesseract"),
        ("numpy", "numpy"),
        ("python-docx", "docx"),
        ("rich", "rich"),
        ("questionary", "questionary")
    ]

    missing = []
    installed = []

    for package_name, import_name in packages:
        if check_package(package_name, import_name):
            installed.append(package_name)
        else:
            missing.append(package_name)

    print()
    print("=" * 60)
    print(f"Summary: {len(installed)}/{len(packages)} packages installed")
    print("=" * 60)

    if missing:
        print()
        print("Missing packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print()
        print("To install missing packages, run:")
        print(f"  pip install {' '.join(missing)}")
        print()
        return False
    else:
        print()
        print("✓ All dependencies are installed!")
        print("You can now run: python main.py")
        print()
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
