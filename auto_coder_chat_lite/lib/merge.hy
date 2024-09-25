(import re)
(import hy [eval])

(defn search_replace_merge [path search_code replace_code]
  "Perform a search and replace operation on the given file. If search_code is empty, create a new file with replace_code.

  :param path: The path to the file to be modified.
  :param search_code: The code to search for in the file.
  :param replace_code: The code to replace the search_code with."
  (if (not search_code)
    (with [file (open path "w" :encoding "utf-8")]
      (file.write replace_code))
    (with [file (open path "r" :encoding "utf-8")]
      (let [content (file.read)]
        (with [file (open path "w" :encoding "utf-8")]
          (file.write (content.replace search_code replace_code)))))))

(defn extract_hylang_code [text]
  "Extract HyLang code blocks from the given text."
  (re.findall r"```hylang\n(.*?)```" text :flags re.DOTALL))

(defn eval_hylang_code [code]
  "Evaluate the given HyLang code."
  (eval (hy.read-many code)))

(defn parse_and_eval_hylang [answer]
  "Parse and evaluate HyLang code from the given answer.

  :param answer: The answer containing HyLang code to be parsed and evaluated."
  (for [code (extract_hylang_code answer)]
    (eval_hylang_code code)))