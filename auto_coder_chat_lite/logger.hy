(import logging)

(defn setup-logger [name]
  "Set up a logger with the given name."
  (setv logger (logging.getLogger name))
  (setv console-handler (logging.StreamHandler))
  (setv formatter (logging.Formatter "%(message)s"))
  (setv console-handler.formatter formatter)
  (setv logger.level logging.INFO)
  (setv console-handler.level logging.INFO)
  (.addHandler logger console-handler)
  logger)