import unittest
from src.auto_coder_chat_lite.code_auto_merge_editblock import CodeAutoMergeEditBlock, PathAndCode
from autocoder.common import AutoCoderArgs
import os

class TestCodeAutoMergeEditBlock(unittest.TestCase):
    def setUp(self):
        self.args = AutoCoderArgs(file="test_file", source_dir="test_source_dir", editblock_similarity=0.8)
        self.code_auto_merge_editblock = CodeAutoMergeEditBlock(self.args)

    def test_merge_code_no_changes(self):
        content = """
##File: test_file
new_content
new_file_content