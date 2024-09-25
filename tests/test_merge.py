import os
import tempfile
from io import StringIO
from contextlib import redirect_stdout
from auto_coder_chat_lite.lib.merge import search_replace_merge, parse_and_eval_hylang, extract_hylang_code, eval_hylang_code

def test_search_replace_merge():
    """Test the search_replace_merge function."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        file_path = temp_file.name
        original_content = "This is a test file."
        search_code = "test"
        replace_code = "example"
        temp_file.write(original_content)
        temp_file.close()
        search_replace_merge(file_path, search_code, replace_code)
        with open(file_path, "r", encoding="utf-8") as file:
            new_content = file.read()
            assert new_content == "This is a example file."
        os.remove(file_path)

def test_parse_and_eval_hylang():
    """Test the parse_and_eval_hylang function."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        file_path = temp_file.name
        original_content = "This is a test file."
        search_code = "test"
        replace_code = "example"
        escaped_file_path = os.path.normpath(file_path).replace('\\', '\\\\')
        answer = f'```hylang\n(search_replace_merge "{escaped_file_path}" "{search_code}" "{replace_code}")\n```\n'
        temp_file.write(original_content)
        temp_file.close()
        parse_and_eval_hylang(answer)
        with open(file_path, "r", encoding="utf-8") as file:
            new_content = file.read()
            assert new_content == "This is a example file."
        os.remove(file_path)

def test_extract_hylang_code():
    """Test the extract_hylang_code function."""
    text = '```hylang\n(print "Hello, World!")\n```\nSome other text\n```hylang\n(defn add [a b]\n  (+ a b))\n```'
    code_blocks = extract_hylang_code(text)
    assert code_blocks == ['(print "Hello, World!")\n', '(defn add [a b]\n  (+ a b))\n']

def test_eval_hylang_code():
    """Test the eval_hylang_code function."""
    code = '(print "Hello, World!")'
    with StringIO() as captured_output:
        with redirect_stdout(captured_output):
            eval_hylang_code(code)
        output = captured_output.getvalue()
        assert output == "Hello, World!\n"