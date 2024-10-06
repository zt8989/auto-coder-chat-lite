import pytest
from hy import eval
from auto_coder_chat_lite.configuration_handler import handle_configuration
from auto_coder_chat_lite.constants import SHOW_FILE_TREE, EDITBLOCK_SIMILARITY, MERGE_TYPE, MERGE_CONFIRM, HUMAN_AS_MODEL, LANGUAGE

@pytest.fixture
def memory():
    return {"conf": {}}

@pytest.fixture
def save_memory():
    return lambda: None

def test_handle_configuration_set_show_file_tree(memory, save_memory):
    user_input = f"/conf {SHOW_FILE_TREE} true"
    handle_configuration(user_input, memory, save_memory)
    assert memory["conf"][SHOW_FILE_TREE] == True

def test_handle_configuration_set_editblock_similarity(memory, save_memory):
    user_input = f"/conf {EDITBLOCK_SIMILARITY} 0.5"
    handle_configuration(user_input, memory, save_memory)
    assert memory["conf"][EDITBLOCK_SIMILARITY] == 0.5

def test_handle_configuration_set_merge_type(memory, save_memory):
    user_input = f"/conf {MERGE_TYPE} search_replace"
    handle_configuration(user_input, memory, save_memory)
    assert memory["conf"][MERGE_TYPE] == "search_replace"

def test_handle_configuration_set_merge_confirm(memory, save_memory):
    user_input = f"/conf {MERGE_CONFIRM} true"
    handle_configuration(user_input, memory, save_memory)
    assert memory["conf"][MERGE_CONFIRM] == True

def test_handle_configuration_set_human_as_model(memory, save_memory):
    user_input = f"/conf {HUMAN_AS_MODEL} true"
    handle_configuration(user_input, memory, save_memory)
    assert memory["conf"][HUMAN_AS_MODEL] == True

def test_handle_configuration_set_language(memory, save_memory):
    user_input = f"/conf {LANGUAGE} zh"
    handle_configuration(user_input, memory, save_memory)
    assert memory["conf"][LANGUAGE] == "zh"

def test_handle_configuration_get_single_key(memory, save_memory):
    memory["conf"] = {SHOW_FILE_TREE: True, EDITBLOCK_SIMILARITY: 0.5}
    user_input = f"/conf {SHOW_FILE_TREE}"
    handle_configuration(user_input, memory, save_memory)
    # No assertion needed, just checking if it prints the correct key

def test_handle_configuration_get_all_keys(memory, save_memory):
    memory["conf"] = {SHOW_FILE_TREE: True, EDITBLOCK_SIMILARITY: 0.5}
    user_input = "/conf"
    handle_configuration(user_input, memory, save_memory)
    # No assertion needed, just checking if it prints all keys