import firebase_admin
from firebase_admin import credentials, storage, firestore
import urllib.request
import os
import uuid
from datetime import datetime
from google.api_core.exceptions import NotFound
import google.api_core.exceptions


firebase_admin_sdk = "firebase_key\sphere-6ee2b-firebase-adminsdk-pag88-6502a061c3.json"
storage_bucket = "sphere-6ee2b.appspot.com"
database_parent_node = 'images'
database_bucket = 'pictures/'


# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_admin_sdk)  # Update with your service account key path


try:
    # Initialize Firebase Admin SDK
    firebase_admin.initialize_app(cred,{'storageBucket': storage_bucket})
    print("Firebase Admin SDK initialized successfully!")

    # Initialize Firestore client
    db = firestore.client()

    print("Firestore initialized successfully!")

except Exception as e:
    print(f"Failed to initialize Firebase: {e}")




# Reference to Firebase Storage bucket
bucket = storage.bucket()




def upload_image_to_storage(image_path, destination_name):
    # Check if image_path exists
    if not os.path.isfile(image_path):
        print(f"Error: Image file '{image_path}' does not exist.")
        return None

    # Check if file is JPEG or PNG
    if not (image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg') or image_path.lower().endswith('.png')):
        print(f"Error: Unsupported image format. Only JPEG and PNG formats are supported.")
        return None

    # Upload image to Firebase Storage under 'pictures' folder
    blob = bucket.blob(database_bucket + destination_name)
    blob.upload_from_filename(image_path)

    # Get download URL
    blob.make_public()
    image_url = blob.public_url

    return image_url



def save_image_url_to_database(image_url, image_name):

    # Generate a unique ID for the document
    unique_id = str(uuid.uuid4())
  
    # Save image metadata to Firestore
    image_ref = db.collection(database_parent_node).document(unique_id)
    image_ref.set({
        'image_url': image_url,
        'image_name': image_name,
        'favourite': False,
        'timestamp': datetime.now()
    })

    return unique_id




def save_image_url_to_txt(image_url):
   
    # This is an extra function
    # Save image URL to a text file (append mode)
    
    # This function will save links of all images that you have upload to firebase.
    # You can view that images by copy pasting that link into your web browser
    
    with open('uploaded_image_url.txt', 'a') as f:
        f.write(image_url + '\n') 




def fetch_all_images():

    try:
        blobs = bucket.list_blobs(prefix=database_bucket)
        for blob in blobs:
            image_url = blob.public_url
            image_name = blob.name.split('/')[-1]
            
            print(f"Image Name: {image_name}, Image URL: {image_url}")
            
            # Download image and save locally with image_name
            download_image(image_url, image_name+".jpeg")
            print(image_name)

    except Exception as e:
        print(f"Failed to fetch images from Firebase Storage: {e}")



def download_image(image_url, image_name):
    try:
        # Ensure 'images' folder exists
        if not os.path.exists('saved_image_folder'):
            os.makedirs('saved_image_folder')

        # Download image from URL
        image_path = os.path.join('saved_image_folder', image_name)
        urllib.request.urlretrieve(image_url, image_path)
        print(f"Downloaded image '{image_name}' successfully.")

    except Exception as e:
        print(f"Failed to download image '{image_name}': {e}")





def main():
    # Example image path
    image_path = 'sample_images\image1.jpeg'  # Update with your image file path
    image_name = '1st image'  # Update with desired image name that you want to save in Firebase Storage
    
    image_url = upload_image_to_storage(image_path, image_name)
    
    if image_url:
        print(f"Image uploaded to Firebase Storage. URL: {image_url}")
        
        # Save image URL to Realtime Database
        unique_id = save_image_url_to_database(image_url, image_name)
        print(f"Image URL saved to Realtime Database with unique ID: {unique_id}")

        
        # Save image URL to a text file
        save_image_url_to_txt(image_url)
        print("Image URL saved to image_url.txt.")
    else:
        print("Failed to upload image to Firebase Storage. Check error messages above.")

    # fetch_all_images() 


if __name__ == "__main__":
    main()