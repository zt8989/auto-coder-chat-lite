import os
import argparse
from openai import Client
from auto_coder_chat_lite.common.config_manager import ConfigManager

def get_client_from_config(config):
    return Client(api_key=config['api_key'], base_url=config['base_url'])

def initialize_config_manager():
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, '.auto_coder_chat_lite')
    os.makedirs(config_dir, exist_ok=True)

    config_file_path = os.path.join(config_dir, 'config.json')
    config_manager = ConfigManager(config_file_path)
    return config_manager

def create_chat_completion(client, model, messages, max_tokens=5):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens
    )

def main():
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
            response = create_chat_completion(client, config['model'], [{"role": "user", "content": "Test prompt"}])
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