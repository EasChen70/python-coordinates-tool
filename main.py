import os
import dropbox
import exifread

# Read Dropbox token
with open("token.txt", "r") as f:
    token = f.read().strip()

dbx = dropbox.Dropbox(token)

# Download files from Dropbox
def download_from_dbx(dropbox_folder, destination_folder):
    try:
        files = dbx.files_list_folder(dropbox_folder).entries
        for file in files:
            if isinstance(file, dropbox.files.FileMetadata):
                local_path = os.path.join(destination_folder, file.name)
                with open(local_path, "wb") as f:
                    metadata, res = dbx.files_download(path=file.path_lower)
                    f.write(res.content)
        print("Photos downloaded successfully.")
    except Exception as e:
        print(f"Error downloading photos: {e}")

# Extract EXIF data
def get_exif_data(image_path):
    with open(image_path, 'rb') as img_file:
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
        if file_name.lower().endswith(('jpg', 'jpeg', 'png')):
            image_path = os.path.join(local_folder, file_name)
            exif_data = get_exif_data(image_path)
            geolocation = get_geolocation(exif_data)
            if geolocation:
                coordinates.append((file_name, geolocation))
    
    return coordinates

def generate_coordinate_file(coordinates, output_file):
    with open(output_file, 'w') as f:
        f.write("Image Name, Latitude, Longitude\n")
        for file_name, (lat, lon) in coordinates:
            f.write(f"{file_name}, {lat}, {lon}\n")

# Paths and constants
dropbox_folder = "/Jamestown Potential Spots"
local_download_path = r"C:\Users\Eason\Downloads\python-coordinates\location_files"
output_file = 'coordinates.csv'

# Execute the functions
download_from_dbx(dropbox_folder, local_download_path)
coordinates = extract_coordinates_from_photos(local_download_path)
generate_coordinate_file(coordinates, output_file)

print(f"Coordinates have been written to {output_file}")