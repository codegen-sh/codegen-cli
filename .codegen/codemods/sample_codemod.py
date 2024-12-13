# grab codebase content
file = codebase.files[0]  # or .get_file("test.py")
function = codebase.functions[0]  # or .get_symbol("my_func")

# print logs
print(f"# of files: {len(codebase.files)}")
print(f"# of functions: {len(codebase.functions)}")

# make edits
file.edit("🌈" + file.content)  # edit contents
function.rename("new_name")  # rename
function.set_docstring("new docstring")  # set docstring

# ... etc.
