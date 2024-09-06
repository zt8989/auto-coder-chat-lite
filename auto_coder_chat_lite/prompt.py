import argparse
import os
import pyperclip
from jinja2 import Environment, FileSystemLoader

def main():
    parser = argparse.ArgumentParser(description="Render a template using Jinja2")
    parser.add_argument("template_path", help="Path to the template file")
    parser.add_argument("text_path", help="Path to the text file to be used as content")
    parser.add_argument("-o", "--output_path", default="output.txt", help="Path to the output file (default: output.txt)")

    args = parser.parse_args()

    with open(args.text_path, 'r', encoding='utf-8') as f:
        content = f.read()

    env = Environment(loader=FileSystemLoader(os.path.dirname(args.template_path)))
    template = env.get_template(os.path.basename(args.template_path))
    rendered_content = template.render(content=content)

    with open(args.output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)

    try:
        pyperclip.copy(rendered_content)
        print(f"Rendered content saved to {args.output_path} and copied to clipboard.")
    except pyperclip.PyperclipException as e:
        print(f"Rendered content saved to {args.output_path}, but failed to copy to clipboard: {e}")

if __name__ == "__main__":
    main()