
(defn search_replace_merge [path search_code replace_code]
  "Perform a search and replace operation on the given file."
  (with [file (open path "r" :encoding "utf-8")]
    (let [content (file.read)]
      (with [file (open path "w" :encoding "utf-8")]
        (file.write (content.replace search_code replace_code))))))