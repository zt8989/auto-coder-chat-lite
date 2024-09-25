(import os)
(import argparse)
(import openai [Client])
(import auto_coder_chat_lite.common.config_manager [ConfigManager])
(require hyrule *)

(defn get_client_from_config [config]
  "Create and return an OpenAI client using the provided configuration.
  
  :param config: A dictionary containing 'api_key', 'base_url', and 'model'.
  :return: An OpenAI client instance."
  (Client :api_key (get config "api_key") :base_url (get config "base_url")))

(defn initialize_config_manager []
  "Initialize and return a ConfigManager instance.
  
  :return: A ConfigManager instance."
  (setv home-dir (os.path.expanduser "~"))
  (setv config-dir (os.path.join home-dir ".auto_coder_chat_lite"))
  (os.makedirs config-dir :exist-ok True)

  (setv config-file-path (os.path.join config-dir "config.json"))
  (ConfigManager config-file-path))

(defn create_chat_completion [client model messages [max-tokens None] [stream False]]
  "Create a chat completion using the OpenAI API.
  
  :param client: An OpenAI client instance.
  :param model: The model to use for the chat completion.
  :param messages: A list of message objects.
  :param max-tokens: The maximum number of tokens to generate. If None, no limit is applied.
  :param stream: Whether to stream the response.
  :return: The response from the OpenAI API."
  (client.chat.completions.create
    :model model
    :messages messages
    :max-tokens max-tokens
    :stream stream))

(defn external-chat-completion [messages [max-tokens None] [stream False]]
  "Create a chat completion using the OpenAI API from an external system.
  
  :param messages: A list of message objects.
  :param max-tokens: The maximum number of tokens to generate.
  :param stream: Whether to stream the response.
  :return: The response from the OpenAI API or None if the call fails."
  (setv config-manager (initialize_config_manager))
  (setv config (config-manager.load))
  (setv client (get_client_from_config config))
  (try
    (setv response (create_chat_completion client (get config "model") messages max-tokens stream))
    response
    (except [e Exception]
      (print f"OpenAI API call failed: {e}")
      None)))

(defn main []
  "agent function to handle command-line arguments and perform actions."
  (setv parser (argparse.ArgumentParser :description "Agent script for auto_coder_chat_lite"))
  (parser.add-argument "action" :nargs "?" :default "setup" :help "Action to perform (default: setup)")
  (parser.add-argument "--base_url" :default "https://api.deepseek.com" :help "Base URL for OpenAI API")
  (parser.add-argument "--api_key" :help "API key for OpenAI")
  (parser.add-argument "--model" :default "deepseek-chat" :help "Model to use for OpenAI API")

  (setv args (parser.parse-args))

  (setv config-manager (initialize_config_manager))

  (when (= args.action "setup")
    (do
      (unless args.api_key
        (parser.error "--api_key is required when action is 'setup'"))
      
      (setv config {"base_url" args.base_url "api_key" args.api_key "model" args.model})

      (config-manager.save config)

      (setv client (get_client_from_config config))
      (try
        (setv response (create_chat_completion client (get config "model") [{"role" "user" "content" "Test prompt"}] :max-tokens 5))
        (print "OpenAI API test successful!")
        (print response)
        (except [e Exception]
          (print f"OpenAI API test failed: {e}")))))

  (when (= args.action "test")
    (do
      (setv config (config-manager.load))
      (setv client (get_client_from_config config))
      (try
        (setv response (create_chat_completion client (get config "model") [{"role" "user" "content" "Test prompt"}]))
        (print "OpenAI API test successful!")
        (print response)
        (except [e Exception]
          (print f"OpenAI API test failed: {e}")))))

  (unless(in args.action ["setup" "test"])
    (print f"Unknown action: {args.action}")))

(when (= __name__ "__main__")
    (main))