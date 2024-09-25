(import os)
(import os [path])
(import tempfile [NamedTemporaryFile])
(import auto_coder_chat_lite.lib.merge [search_replace_merge])

(defn test_search_replace_merge []
  "Test the search_replace_merge function."
  (with [temp_file (NamedTemporaryFile :mode "w" :delete False)]
    (let [file_path temp_file.name
          original_content "This is a test file."
          search_code "test"
          replace_code "example"]
      (temp_file.write original_content)
      (temp_file.close)
      (search_replace_merge file_path search_code replace_code)
      (with [file (open file_path "r" :encoding "utf-8")]
        (let [new_content (file.read)]
          (assert (= new_content "This is a example file."))))
      (os.remove file_path))))