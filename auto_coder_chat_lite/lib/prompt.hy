(import argparse os pyperclip jinja2 [Environment FileSystemLoader])

(defn main []
  (setv parser (argparse.ArgumentParser :description "Render a template using Jinja2"))
  (parser.add_argument "template_path" :help "Path to the template file")
  (parser.add_argument "text_path" :help "Path to the text file to be used as content")
  (parser.add_argument "-o" "--output_path" :default "output.txt" :help "Path to the output file (default: output.txt)")

  (setv args (parser.parse_args))

  (with [f (open args.text_path "r" :encoding "utf-8")]
    (setv content (f.read)))

  (setv env (Environment :loader (FileSystemLoader (os.path.dirname args.template_path))))
  (setv template (env.get_template (os.path.basename args.template_path)))
  (print args.text_path content)
  (setv rendered_content (template.render :content content))

  (with [f (open args.output_path "w" :encoding "utf-8")]
    (f.write rendered_content))

  (try
    (do
      (pyperclip.copy rendered_content)
      (print f"Rendered content saved to {args.output_path} and copied to clipboard."))
    (except [e pyperclip.PyperclipException]
      (print f"Rendered content saved to {args.output_path}, but failed to copy to clipboard: {e}"))))