(import os shutil)
(import argparse)
(import openai [Client])
(import auto-coder-chat-lite.common.config-manager [ConfigManager])
(import auto-coder-chat-lite.constants [PROJECT-DIR-NAME SOURCE_DIR PROJECT_DIR TEMPLATES])
(require hyrule *)

(defn get-client-from-config [config]
  "Create and return an OpenAI client using the provided configuration.
  
  :param config: A dictionary containing 'api-key', 'base-url', and 'model'.
  :return: An OpenAI client instance."
  (Client :api-key (get config "api-key") :base-url (get config "base-url")))

(defn initialize-config-manager []
  "Initialize and return a ConfigManager instance.
  
  :return: A ConfigManager instance."
  (setv home-dir (os.path.expanduser "~"))
  (setv config-dir (os.path.join home-dir PROJECT-DIR-NAME))
  (os.makedirs config-dir :exist-ok True)

  (setv config-file-path (os.path.join config-dir "config.json"))
  (ConfigManager config-file-path))

(defn create-chat-completion [client model messages [max-tokens None] [stream False]]
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
  (setv config-manager (initialize-config-manager))
  (setv config (config-manager.load))
  (setv client (get-client-from-config config))
  (try
    (setv response (create-chat-completion client (get config "model") messages max-tokens stream))
    response
    (except [e Exception]
      (print f"OpenAI API call failed: {e}")
      None)))

(defn main []
  "agent function to handle command-line arguments and perform actions."
  (setv parser (argparse.ArgumentParser :description "Agent script for auto-coder-chat-lite"))
  (parser.add-argument "action" :nargs "?" :default "setup" :help "Action to perform (default: setup)")
  (parser.add-argument "--base-url" :default "https://api.deepseek.com" :help "Base URL for OpenAI API")
  (parser.add-argument "--api-key" :help "API key for OpenAI")
  (parser.add-argument "--model" :default "deepseek-chat" :help "Model to use for OpenAI API")

  (setv args (parser.parse-args))

  (setv config-manager (initialize-config-manager))

  (when (= args.action "setup")
    (do
      (unless args.api-key
        (parser.error "--api-key is required when action is 'setup'"))
      
      (setv config {"base-url" args.base-url "api-key" args.api-key "model" args.model})

      (config-manager.save config)

      (setv client (get-client-from-config config))
      (try
        (setv response (create-chat-completion client (get config "model") [{"role" "user" "content" "Test prompt"}] :max-tokens 5))
        (print "OpenAI API test successful!")
        (print response)
        (except [e Exception]
          (print f"OpenAI API test failed: {e}")))))

  (when (= args.action "test")
    (do
      (setv config (config-manager.load))
      (setv client (get-client-from-config config))
      (try
        (setv response (create-chat-completion client (get config "model") [{"role" "user" "content" "Test prompt"}]))
        (print "OpenAI API test successful!")
        (print response)
        (except [e Exception]
          (print f"OpenAI API test failed: {e}")))))

  (when (= args.action "dump")
    (let
     [project-dir (os.path.join PROJECT_DIR TEMPLATES)
      source-dir (os.path.join SOURCE_DIR TEMPLATES)]
      (os.makedirs project-dir :exist-ok True)
      (for [template (os.listdir source-dir)]
        (let [source-file (os.path.join source-dir template)
              dest-file (os.path.join project-dir template)]
        (when (os.path.isfile source-file)
          (shutil.copy source-file dest-file))
        (print f"Templates dumped successfully! Copied {template} to {dest-file}")))))

  (unless(in args.action ["setup" "test" "dump"])
    (print f"Unknown action: {args.action}")))

(defmain []
  (main))