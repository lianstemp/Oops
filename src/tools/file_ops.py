import os

def write_file(filename: str, content: str) -> str:
    """
    Writes content to a file in the output directory.

    Args:
        filename: The name of the file to write (e.g., 'scope.md').
        content: The content to write to the file.
    
    Returns:
        A success message with the full path of the written file.
    """
    output_dir = os.path.join(os.getcwd(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

def read_file(filename: str) -> str:
    """
    Reads content from a file in the output directory.

    Args:
        filename: The name of the file to read (e.g., 'scope.md').
    
    Returns:
        The content of the file, or an error message if the file doesn't exist.
    """
    output_dir = os.path.join(os.getcwd(), 'output')
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path):
        return f"File {filename} does not exist."
    
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
