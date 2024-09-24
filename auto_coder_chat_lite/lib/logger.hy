(import os
        logging
        logging.handlers
        auto_coder_chat_lite.constants [PROJECT_DIR_NAME])

(defn setup-logger [name]
  "Set up a logger with the given name."
  (setv logger (logging.getLogger name))
  (setv formatter (logging.Formatter "%(message)s"))
  (setv logger.level logging.INFO)
  (setv log-dir (os.path.join (os.getcwd) PROJECT_DIR_NAME))
  (os.makedirs log-dir :exist-ok True)
  (setv log-file (os.path.join log-dir "auto-coder-chat-lite.log"))
  (setv file-handler (logging.handlers.TimedRotatingFileHandler log-file :when "midnight"))
  (setv file-handler.formatter formatter)
  (setv file-handler.level logging.INFO)
  (.addHandler logger file-handler)

  logger)