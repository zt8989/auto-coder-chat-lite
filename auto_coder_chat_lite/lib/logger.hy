(import os
        logging
        logging.handlers
        auto-coder-chat-lite.constants [PROJECT-DIR-NAME])

(setv log-dir (os.path.join (os.getcwd) PROJECT-DIR-NAME))
(os.makedirs log-dir :exist-ok True)
(setv log-file (os.path.join log-dir "auto-coder-chat-lite.log"))
(setv file-handler (logging.handlers.TimedRotatingFileHandler log-file :when "midnight"))
(setv formatter (logging.Formatter "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
(setv file-handler.formatter formatter)
(setv file-handler.level logging.INFO)

(defn setup-logger [name]
  "Set up a logger with the given name."
  (setv logger (logging.getLogger name))
  (setv logger.level logging.INFO)
  (.addHandler logger file-handler)

  logger)