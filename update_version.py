import re

def update_version():
    with open('setup.py', 'r') as file:
        setup_content = file.read()

    # 使用正则表达式查找版本号
    version_match = re.search(r"version='(\d+\.\d+\.\d+)'", setup_content)
    if not version_match:
        raise ValueError("Version number not found in setup.py")

    # 获取当前版本号
    current_version = version_match.group(1)
    major, minor, patch = map(int, current_version.split('.'))

    # 递增版本号
    patch += 1
    new_version = f"{major}.{minor}.{patch}"

    # 替换版本号
    updated_content = setup_content.replace(f"version='{current_version}'", f"version='{new_version}'")

    with open('setup.py', 'w') as file:
        file.write(updated_content)

    print(f"Version updated from {current_version} to {new_version}")

if __name__ == "__main__":
    update_version()