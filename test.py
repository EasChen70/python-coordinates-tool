import os
from PIL import Image
import pillow_heif

local_heic_folder = r"C:\Users\Eason\Dropbox\Jamestown Potential Spots"
local_jpeg_destination_folder = r"C:\Users\Eason\Downloads\python-coordinates\location_files"

# Conversion function
def convert_heic_to_jpeg(source_path, destination_path):
    try: 
        heif_file = pillow_heif.read_heif(source_path)
        image = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data, 
            "raw", 
            heif_file.mode, 
            heif_file.stride,
        )
        image.save(destination_path, "JPEG")
        return True
    except Exception as e:
        print(f"Error converting {source_path} to JPEG: {e}")
        return False

# Iterate over HEIC files
for filename in os.listdir(local_heic_folder):
    if filename.lower().endswith('.heic'):
        heic_path = os.path.join(local_heic_folder, filename)
        jpeg_filename = filename[:-5] + '.jpg'  # Change extension to .jpg
        jpeg_path = os.path.join(local_jpeg_destination_folder, jpeg_filename)

        if convert_heic_to_jpeg(heic_path, jpeg_path):
            print(f"Converted {filename} to JPEG successfully.")
        else:
            print(f"Error converting {filename}.")

print("Conversion process complete.")


#Extract geolocation and put coordinates in coordinates.csv