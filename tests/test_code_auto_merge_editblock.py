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
```python
##File: {file_path}
{search_header}
{search}
=======
{replace}
{replace_header}
```
"""

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_parse_whole_text(self):
        file_path = "test_file.py"
        search_content = "existing_content"
        replace_content = "new_content"
        content = self.generate_search_replace(file_path, search_content, replace_content)
        expected_result = [
            PathAndCode(path="test_file.py", content="<<<<<<< SEARCH\nexisting_content\n=======\nnew_content\n>>>>>>> REPLACE")
        ]
        result = self.code_auto_merge_editblock.parse_whole_text(content)
        self.assertEqual(result, expected_result)

    def test_get_edits(self):
        file_path = "test_file.py"
        search_content = "existing_content"
        replace_content = "new_content"
        content = self.generate_search_replace(file_path, search_content, replace_content)
        expected_result = [
            ("test_file.py", "existing_content", "new_content")
        ]
        result = self.code_auto_merge_editblock.get_edits(content)
        self.assertEqual(result, expected_result)

    def test_merge_code(self):
        search_content = "existing_content"
        replace_content = "new_content"
        content = self.generate_search_replace(self.file_path, search_content, replace_content)
        
        # Create a temporary file with the initial content
        initial_content = "existing_content"
        with open(self.file_path, "w") as f:
            f.write(initial_content)
        
        # Run the merge_code function
        self.code_auto_merge_editblock.merge_code(content)
        
        # Verify the file content has been updated
        with open(self.file_path, "r") as f:
            updated_content = f.read()
        
        self.assertEqual(updated_content, "new_content")

if __name__ == '__main__':
    unittest.main()