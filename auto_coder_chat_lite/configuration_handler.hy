(import os)
(import auto_coder_chat_lite.constants 
        [CONF_AUTO_COMPLETE
         SHOW_FILE_TREE 
         EDITBLOCK_SIMILARITY 
         MERGE_TYPE MERGE_CONFIRM 
         HUMAN_AS_MODEL 
         MERGE_TYPE_SEARCH_REPLACE 
         MERGE_TYPE_GIT_DIFF 
         LANGUAGE])
; (import hy.pyops *)
(require hyrule *)
(import hyrule [assoc])

(defn print-config [memory key]
  (let [conf (get memory "conf" key)]
    (print f"Updated configuration: {key} = {conf}")))

(defn print-config-keys [memory]
  (print "Current configuration:")
  (lfor key (get memory "conf") (let [conf (get memory "conf" key)]
    (print f"  {key} = {conf}"))))

(defn handle-configuration [user-input memory save-memory]
  (let [conf-args (-> user-input
                      (cut (len "/conf") None)
                      .strip
                      .split)]
    (let [conf-args-len (len conf-args)]
      (cond 
        (= conf-args-len 2)
          (let [[key value] conf-args]
            (cond
              (= key SHOW_FILE_TREE)
                (if (in value ["true" "false"])
                  (do
                    (assoc (get memory "conf") key (= (.lower value) "true"))
                    (print-config memory key)
                    (save-memory))
                  (print "Invalid value. Please provide 'true' or 'false'."))
              (= key EDITBLOCK_SIMILARITY)
                (try
                  (let [value (float value)]
                    (if (and (<= 0 value) (<= value 1))
                      (do
                        (assoc (get memory "conf") key value)
                        (print-config memory key)
                        (save-memory))
                      (print "Invalid value. Please provide a number between 0 and 1.")))
                  (except [ValueError]
                    (print "Invalid value. Please provide a valid number.")))
              (= key MERGE_TYPE)
                (let [values (get CONF_AUTO_COMPLETE key)]
                  (if (in value values)
                    (do
                      (assoc (get memory "conf") key value)
                      (print-config memory key)
                      (save-memory))
                    (print f"Invalid value. Please provide {values}.")))
              (= key MERGE_CONFIRM)
                (if (in (.lower value) ["true" "false"])
                  (do
                    (assoc (get memory "conf") MERGE_CONFIRM (= (.lower value) "true"))
                    (print-config memory key)
                    (save-memory))
                  (print "Invalid value. Please provide 'true' or 'false'."))
              (= key HUMAN_AS_MODEL)
                (if (in (.lower value) ["true" "false"])
                  (do
                    (assoc (get memory "conf") HUMAN_AS_MODEL (= (.lower value) "true"))
                    (print-config memory key)
                    (save-memory))
                  (print "Invalid value. Please provide 'true' or 'false'."))
              (= key LANGUAGE)
                (if (in value ["zh" "en"])
                  (do
                    (assoc (get memory "conf") LANGUAGE value)
                    (print-config memory key)
                    (save-memory))
                  (print "Invalid value. Please provide 'zh' or 'en'."))
              True
                (try
                  (let [value (float value)]
                    (assoc (get memory "conf") key value)
                    (print-config memory key)
                    (save-memory))
                  (except [ValueError]
                    (print "Invalid value. Please provide a valid number.")))))
        (= conf-args-len 1)
          (let [[key] conf-args]
            (if (in key (get memory "conf"))
              (print-config memory key)
              (print f"Configuration key '{key}' not found.")))
        (= conf-args-len 0)
          (if (get memory "conf")
            (do
              (print-config-keys memory))
            (print "No configuration values set."))
        True
         (print "Usage: /conf [<key> [<value>]]")))))