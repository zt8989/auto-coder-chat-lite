import unittest
from auto_coder_chat_lite.common.code_auto_merge_editblock import CodeAutoMergeEditBlock, PathAndCode
from auto_coder_chat_lite.common import AutoCoderArgs
import os
import tempfile
import shutil

class TestCodeAutoMergeEditBlock(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_name = "test_file.py"
        self.file_path = os.path.join(self.temp_dir, self.file_name)
        
        self.args = AutoCoderArgs(file=self.file_path, source_dir=self.temp_dir, editblock_similarity=0.8)        
        self.code_auto_merge_editblock = CodeAutoMergeEditBlock(self.args)

    def generate_search_replace(self, file_path, search, replace):
        replace_header = ">>>>>>> REPLACE"
        search_header = "<<<<<<< SEARCH"
        return f"""
{search_header}
##File: {file_path}
{search}
=======
{replace}
{replace_header}
"""

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_merge_code_no_changes(self):
        # Create a test file
        with open(self.file_path, "w") as f:
            f.write("")
        new_file_path = self.file_path
        content = self.generate_search_replace(self.file_path, "", "")
        self.code_auto_merge_editblock.merge_code(content, force_skip_git=True)
        # Add assertions here to check if no changes were made
        self.assertTrue(os.path.exists(new_file_path))
        with open(new_file_path, "r") as f:
            self.assertEqual(f.read(), "")
        os.remove(new_file_path)

    def test_merge_code_with_changes(self):
        # Create a test file
        with open(self.file_path, "w") as f:
            f.write("existing_content\n")
        new_file_path = self.file_path
        content = self.generate_search_replace(self.file_path, "existing_content", "new_content")
        self.code_auto_merge_editblock.merge_code(content, force_skip_git=True)
        # Add assertions here to check if the new file was created
        self.assertTrue(os.path.exists(new_file_path))
        with open(new_file_path, "r") as f:
            self.assertEqual(f.read(), "new_file_content\n")
        os.remove(new_file_path)

if __name__ == '__main__':
    unittest.main()