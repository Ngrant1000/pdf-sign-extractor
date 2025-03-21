import os

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    return directory

def get_output_path(pdf_path, output_path=None, output_dir=None):
    """Determine the output path for extracted text"""
    if output_path:
        return output_path
    
    base_name = os.path.basename(pdf_path)
    file_name = os.path.splitext(base_name)[0] + ".txt"
    
    if output_dir:
        ensure_dir(output_dir)
        return os.path.join(output_dir, file_name)
    else:
        return file_name 