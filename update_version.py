import re
import subprocess

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

    try:
        # 创建新的 git tag
        subprocess.run(['git', 'tag', f'v{new_version}'], check=True)
        print(f"Git tag v{new_version} 已创建")

        # 推送新的 tag 到远程仓库
        subprocess.run(['git', 'push', 'origin', f'v{new_version}'], check=True)
        print(f"Git tag v{new_version} 已推送到远程仓库")
    except subprocess.CalledProcessError as e:
        print(f"创建或推送 Git tag 时出错: {e}")

    print(f"Version updated from {current_version} to {new_version}")

if __name__ == "__main__":
    update_version()