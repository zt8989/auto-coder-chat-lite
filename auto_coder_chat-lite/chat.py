def coding(query):
    project_root = os.getcwd()
    files = "\n".join(get_all_file_names_in_project())
    files_code = "\n".join(
        [f"##File: {file}\n{open(file).read()}" for file in memory['current_files']['files'] if os.path.exists(file)]
    )

    with open("template.txt", "r") as template_file:
        template = template_file.read()

    replaced_template = template.format(
        project_root=project_root,
        files=files,
        files_code=files_code,
        query=query
    )

    with open("output.txt", "w") as output_file:
        output_file.write(replaced_template)

    try:
        import pyperclip
        pyperclip.copy(replaced_template)
    except ImportError:
        print("pyperclip not installed, unable to copy to clipboard.")

    print("Coding request processed and output saved to output.txt.")