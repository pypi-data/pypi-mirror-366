import os
import sys

def is_package_installed_in_site_packages(site_packages_path, package_name):
    # Check for both: package folders (e.g., pandas/) or .dist-info directories
    candidates = os.listdir(site_packages_path)
    package_name = package_name.lower()
    for item in candidates:
        if item.lower() == package_name or item.lower().startswith(package_name + "-") and item.endswith(".dist-info"):
            return True
    return False

def search_package(package_name):
    base_dirs = [
        os.path.expanduser("~"),
        os.path.join(os.environ.get("USERPROFILE", ""), ".virtualenvs"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Envs"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "projects"),
    ]

    print(f"\nSearching for package '{package_name}'...\n")
    found_envs = set()

    for base in base_dirs:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            if "site-packages" in root:
                if is_package_installed_in_site_packages(root, package_name):
                    parts = root.split(os.sep)
                    if "Lib" in parts:
                        lib_index = parts.index("Lib")
                    elif "lib" in parts:
                        lib_index = parts.index("lib")
                    else:
                        continue
                    env_path = os.sep.join(parts[:lib_index])
                    found_envs.add(env_path)

    if found_envs:
        print(f"Package '{package_name}' found in the following location(s):\n")
        for env in sorted(found_envs):
            print(f"→ {env}")
    else:
        print(f"Package '{package_name}' not found in known virtual environments.")



def main():
    if len(sys.argv) < 2:
        print("Usage:\nfindpkg <package_name>")
    else:
        search_package(sys.argv[1])
