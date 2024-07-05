import os
from PIL import Image
import pillow_heif
import exifread

with open('heic_folder.txt', 'r') as f:
    local_heic_folder = f.read().strip()

with open('jpg_folder.txt', 'r') as f:
    local_jpeg_destination_folder = f.read().strip()
    
output_file = 'coordinates.csv'

# Ensure the destination folder exists
os.makedirs(local_jpeg_destination_folder, exist_ok=True)

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

# Extract geolocation and put coordinates in coordinates.csv
def get_exif(jpg_path):
    with open(jpg_path, 'rb') as img_file:
        tags = exifread.process_file(img_file)
    return tags

def get_geolocation(exif_data):
    gps_latitude = exif_data.get('GPS GPSLatitude')
    gps_latitude_ref = exif_data.get('GPS GPSLatitudeRef')
    gps_longitude = exif_data.get('GPS GPSLongitude')
    gps_longitude_ref = exif_data.get('GPS GPSLongitudeRef')
    
    if gps_latitude and gps_longitude:
        lat = [float(x.num) / float(x.den) for x in gps_latitude.values]
        lon = [float(x.num) / float(x.den) for x in gps_longitude.values]
        
        lat_ref = gps_latitude_ref.values[0]
        lon_ref = gps_longitude_ref.values[0]
        
        lat = lat[0] + lat[1] / 60 + lat[2] / 3600
        lon = lon[0] + lon[1] / 60 + lon[2] / 3600
        
        if lat_ref != 'N':
            lat = -lat
        if lon_ref != 'E':
            lon = -lon
        
        return lat, lon
    return None

def extract_coordinates_from_photos(local_folder):
    coordinates = []
    
    for file_name in os.listdir(local_folder):
        if file_name.lower().endswith(('jpg', 'jpeg')):
            image_path = os.path.join(local_folder, file_name)
            exif_data = get_exif(image_path)
            geolocation = get_geolocation(exif_data)
            if geolocation:
                print(f"File: {file_name}, Geolocation: {geolocation}")  # Debug info
                coordinates.append((file_name, geolocation))
            else:
                print(f"File: {file_name} does not contain GPS data.")  # Debug info
    
    return coordinates

def generate_coordinate_file(coordinates, output_file):
    with open(output_file, 'w') as f:
        f.write("Image Name, Latitude, Longitude\n")
        for file_name, (lat, lon) in coordinates:
            f.write(f"{file_name}, {lat}, {lon}\n")

# Execute the functions
coordinates = extract_coordinates_from_photos(local_jpeg_destination_folder)
generate_coordinate_file(coordinates, output_file)

print(f"Coordinates have been written to {output_file}")
