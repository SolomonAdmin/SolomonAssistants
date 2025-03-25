import os

def get_app_directory_tree_with_content(root_dir):
    """Generate a tree-like directory structure for the 'app/' directory and include file content."""
    tree_str = []
    exclude_dirs = {'__pycache__', 'venv', '.git', 'bin', 'etc', 'include', 'lib', 'share'}
    code_extensions = {'.py', '.js', '.sh'}  # Include file types to read
    app_found = False

    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Check if we're in the 'app' directory or its subdirectories
        if app_found or os.path.basename(root) == 'app':
            app_found = True
            level = root.replace(root_dir, '').count(os.sep)
            indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
            tree_str.append(f'{indent}{os.path.basename(root)}')
            
            for file in files:
                if not file.endswith(('.pyc', '.pem')):  # Skip .pyc files and .pem files
                    indent = '│   ' * level + '├── '
                    tree_str.append(f'{indent}{file}')
                    
                    # Read and include file content if it matches code_extensions
                    if os.path.splitext(file)[1] in code_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                tree_str.append(f"\nFILE NAME {file_path}\n")
                                tree_str.append(content)
                                tree_str.append(f"\nFILE NAME {file_path}\n")
                        except Exception as e:
                            print(f"Error reading {file_path}: {str(e)}")
            # Skip processing directories outside of 'app'
            if os.path.basename(root) != 'app' and not root.startswith(os.path.join(root_dir, 'app')):
                break
    
    return '\n'.join(tree_str)

def aggregate_app_code(root_dir, output_file):
    """Save the directory structure and content for the 'app/' folder to a file."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write the initial description
        outfile.write('"""\n')
        outfile.write('Here is the application tree for the "app" directory:\n\n')
        
        # Generate and write the tree structure with file content
        tree = get_app_directory_tree_with_content(root_dir)
        outfile.write(tree)
        outfile.write('\n"""\n')

if __name__ == "__main__":
    # Get the current directory (where the script is run)
    current_dir = os.getcwd()
    output_file = "app_directory_tree_with_content.txt"
    
    aggregate_app_code(current_dir, output_file)
    print(f"Directory tree and file content for 'app/' saved to {output_file}")
