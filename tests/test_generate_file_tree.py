import os
import pytest
from auto_coder_chat_lite.chat import generate_file_tree

@pytest.fixture
def temp_dir(tmpdir):
    """Create a temporary directory with some files and directories."""
    temp_dir = tmpdir.mkdir("test_dir")
    temp_dir.join("file1.txt").write("")
    temp_dir.mkdir("subdir").join("file2.txt").write("")
    return temp_dir

def test_generate_file_tree(temp_dir):
    """Test the generate_file_tree function."""
    expected_output = str(temp_dir) +(
        "/\n"
        "    file1.txt\n"
        "    subdir/\n"
        "        file2.txt"
    )
    result = generate_file_tree(str(temp_dir))
    assert result == expected_output

def test_generate_file_tree_with_git_and_gitignore(temp_dir):
    """Test the generate_file_tree function with .git folder and .gitignore file."""
    git_dir = temp_dir.mkdir(".git")
    a = git_dir.join("a")
    a.write("")
    gitignore_file = temp_dir.join(".gitignore")
    gitignore_file.write("file1.txt\n")

    expected_output = str(temp_dir) +(
        "/\n"
        "    .gitignore\n"
        "    subdir/\n"
        "        file2.txt"
    )
    result = generate_file_tree(str(temp_dir))
    assert result == expected_output