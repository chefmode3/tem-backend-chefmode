from PIL import Image
import os

def make_square_and_resize(image_path, output_path, target_size=(1024, 1024)):
    """Adjust the input image to a square by padding with white pixels and resize it."""
    with Image.open(image_path) as img:
        # Get the original image size
        width, height = img.size

        # Determine the size of the new square image
        new_size = max(width, height)

        # Create a new white square canvas
        new_img = Image.new('RGB', (new_size, new_size), (255, 255, 255))

        # Calculate the position to center the original image on the new canvas
        left = (new_size - width) // 2
        top = (new_size - height) // 2

        # Paste the original image onto the center of the new canvas
        new_img.paste(img, (left, top))

        # Resize the image to the target size (1024x1024) using LANCZOS filter
        resized_img = new_img.resize(target_size, Image.LANCZOS)

        # Save the resized image
        resized_img.save(output_path)

# Example usage:
input_folder = r'C:\Users\jordan.gibbs\Downloads\drive-download-20241014T181453Z-001'
output_folder = 'output_images'

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Process all images in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        make_square_and_resize(input_path, output_path)
        print(f'Processed: {filename}')
