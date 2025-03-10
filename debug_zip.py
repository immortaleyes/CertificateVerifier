import zipfile
import os

# Path to the ZIP file
ZIP_FILE_PATH = 'attached_assets/OJT Student\'s Certificate_2025.zip'

def debug_zip_contents():
    """Print all file names in the ZIP archive"""
    try:
        # Check if ZIP file exists
        if not os.path.exists(ZIP_FILE_PATH):
            print(f"ERROR: ZIP file not found: {ZIP_FILE_PATH}")
            return
        
        # Open the zip file
        with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
            # List all files in the zip
            file_list = zip_ref.namelist()
            print(f"Found {len(file_list)} files in archive")
            
            # Print all file names
            print("\nALL FILES IN ARCHIVE:")
            for i, file_name in enumerate(file_list, 1):
                print(f"{i}. {file_name}")
            
            # Look for files containing "328"
            print("\nFILES CONTAINING '328':")
            found_any = False
            for file_name in file_list:
                if "328" in file_name:
                    print(f"MATCH: {file_name}")
                    found_any = True
            
            if not found_any:
                print("No files containing '328' found")
            
            # Show specific file containing "Shamal"
            print("\nFILES CONTAINING 'Shamal':")
            found_any = False
            for file_name in file_list:
                if "shamal" in file_name.lower():
                    print(f"MATCH: {file_name}")
                    found_any = True
            
            if not found_any:
                print("No files containing 'Shamal' found")

    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    debug_zip_contents()