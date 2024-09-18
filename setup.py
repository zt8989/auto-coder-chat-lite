from setuptools import setup, find_packages

setup(
    name='auto_coder_chat_lite',
    version='0.1.10',
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    include_package_data=True,
    package_data={'auto_coder_chat_lite': ['template/code.txt', 'template/commit_message.txt']},
    install_requires=[
        'colorama==0.4.6',
        'pathspec==0.12.1',
        'prompt_toolkit==3.0.47',
        'pydantic==2.8.2',
        'Pygments==2.18.0',
        'pyperclip==1.9.0',
        'rich==13.7.1',
        'GitPython==3.1.43',
        'Jinja2==3.1.4',
        'pylint==3.2.7',
        'openai==1.44.1',
    ],
    entry_points='''
        [console_scripts]
        chat.code=auto_coder_chat_lite.chat:main
        chat.prompt=auto_coder_chat_lite.prompt:main
        chat.agent=auto_coder_chat_lite.agent:main
    ''',
    author='cowboy',
    author_email='251027705@qq.com',
    description='a simple code chat tool inspired by auto coder',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zt8989/auto-coder-chat-lite',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)