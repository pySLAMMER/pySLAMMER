from livereload import Server, shell
import os

def preprocess():
    # Add any preprocessing steps here
    pass

if __name__ == "__main__":
    # Run preprocessing steps
    preprocess()
    
    # Build the initial HTML files
    os.system('make html')
    
    # Check if the build directory and index.html exist
    build_dir = "_build/html"
    # if not os.path.exists(build_dir) or not os.path.exists(os.path.join(build_dir, "index.html")):
    #     raise FileNotFoundError("The build directory or index.html was not found. Ensure 'make html' is building the site correctly.")
    
    server = Server()
    server.watch("*.rst", shell('make html'), delay=1)
    server.watch("*.md", shell('make html'), delay=1)
    server.watch("*.py", shell('make html'), delay=1)
    server.watch("_static/*", shell('make html'), delay=1)
    server.watch("_templates/*", shell('make html'), delay=1)
    server.serve(root=build_dir)