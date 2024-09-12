import os
import argparse
from openai import Client
from auto_coder_chat_lite.common.config_manager import ConfigManager

def get_client_from_config(config):
    """
    Create and return an OpenAI client using the provided configuration.
    
    :param config: A dictionary containing 'api_key' and 'base_url'.
    :return: An OpenAI client instance.
    """
    return Client(api_key=config['api_key'], base_url=config['base_url'])

def initialize_config_manager():
    """
    Initialize and return a ConfigManager instance.
    
    :return: A ConfigManager instance.
    """
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, '.auto_coder_chat_lite')
    os.makedirs(config_dir, exist_ok=True)

    config_file_path = os.path.join(config_dir, 'config.json')
    config_manager = ConfigManager(config_file_path)
    return config_manager

def create_chat_completion(client, model, messages, max_tokens=None):
    """
    Create a chat completion using the OpenAI API.
    
    :param client: An OpenAI client instance.
    :param model: The model to use for the chat completion.
    :param messages: A list of message objects.
    :param max_tokens: The maximum number of tokens to generate. If None, no limit is applied.
    :return: The response from the OpenAI API.
    """
    return client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens
    )

def external_chat_completion(messages, max_tokens=None):
    """
    Create a chat completion using the OpenAI API from an external system.
    
    :param messages: A list of message objects.
    :param max_tokens: The maximum number of tokens to generate.
    :return: The response from the OpenAI API or None if the call fails.
    """
    config_manager = initialize_config_manager()
    config = config_manager.load()
    client = get_client_from_config(config)
    try:
        response = create_chat_completion(client, config['model'], messages, max_tokens)
        return response
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return None

def main():
    """
    Main function to handle command-line arguments and perform actions.
    """
    parser = argparse.ArgumentParser(description="Agent script for auto_coder_chat_lite")
    parser.add_argument('action', nargs='?', default='setup', help='Action to perform (default: setup)')
    parser.add_argument('--base_url', default='https://api.deepseek.com', help='Base URL for OpenAI API')
    parser.add_argument('--api_key', help='API key for OpenAI')
    parser.add_argument('--model', default='deepseek-chat', help='Model to use for OpenAI API')

    args = parser.parse_args()

    config_manager = initialize_config_manager()

    if args.action == 'setup':
        if not args.api_key:
            parser.error("--api_key is required when action is 'setup'")
        
        config = {
            'base_url': args.base_url,
            'api_key': args.api_key,
            'model': args.model
        }

        config_manager.save(config)

        client = get_client_from_config(config)
        try:
            response = create_chat_completion(client, config['model'], [{"role": "user", "content": "Test prompt"}], max_tokens=5)
            print("OpenAI API test successful!")
            print(response)
        except Exception as e:
            print(f"OpenAI API test failed: {e}")
    elif args.action == 'test':
        config = config_manager.load()
        client = get_client_from_config(config)
        try:
            response = create_chat_completion(client, config['model'], [{"role": "user", "content": "Test prompt"}])
            print("OpenAI API test successful!")
            print(response)
        except Exception as e:
            print(f"OpenAI API test failed: {e}")
    else:
        print(f"Unknown action: {args.action}")

if __name__ == "__main__":
    main()