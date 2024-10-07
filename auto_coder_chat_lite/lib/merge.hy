(import re)
(import hy [eval])
(import functools [reduce])
(import toolz [partition take-nth cons drop])

(defn even? [n]
  "Check if a number is even."
  (= (% n 2) 0))

(defn search-replace-merge [path search-code replace-code #* args]
  "Perform a search and replace operation on the given file. If search-code is empty, create a new file with replace-code.

  :param path: The path to the file to be modified.
  :param search-code: The code to search for in the file.
  :param replace-code: The code to replace the search-code with.
  :param args: Additional pairs of search-code and replace-code."
  (when (not (even? (len args)))
    (raise (ValueError "args must be of even length")))
  (if (not search-code)
    (with [file (open path "w" :encoding "utf-8")]
      (file.write replace-code))
    (with [file (open path "r" :encoding "utf-8")]
      (let [content (file.read)]
        (with [file (open path "w" :encoding "utf-8")]
          (file.write (reduce (fn [content next] (setv #(s r) next) (content.replace s r))
                              (zip (cons search-code (take-nth 2 args))
                                   (cons replace-code (take-nth 2 (drop 1 args))))
                                   content)))))))

(defn extract-hylang-code [text]
  "Extract HyLang code blocks from the given text by analyzing it line by line."
  (setv code-blocks []
        in-code-block False
        current-block [])
  (for [line (text.splitlines)]
    (cond
      (or (line.startswith "```hy") (line.startswith "```hylang"))
      (do
        (if in-code-block
          (do
            (code-blocks.append (.join "\n" current-block))
            (setv current-block []))
          (setv in-code-block True)))
      (and in-code-block (line.startswith "```"))
      (do
        (code-blocks.append (.join "\n" current-block))
        (setv current-block []
          in-code-block False))
      True
      (when in-code-block
        (current-block.append line))))
  (when current-block
    (code-blocks.append (.join "\n" current-block)))
  code-blocks)

(defn eval-hylang-code [code]
  "Evaluate the given HyLang code."
  (eval (hy.read-many code)))

(defn parse-and-eval-hylang [answer]
  "Parse and evaluate HyLang code from the given answer.

  :param answer: The answer containing HyLang code to be parsed and evaluated."
  (for [code (extract-hylang-code answer)]
    (eval-hylang-code code)))