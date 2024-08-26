from setuptools import setup, find_packages

setup(
    name='auto-coder-chat-lite',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        code.chat=auto_coder_chat_lite.cli:create_project
    ''',
    author='cowboy',
    author_email='251027705@qq.com',
    description='a simple code chat tool inspired by auto coder',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zt8989/auto-coder-chat-lite',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
