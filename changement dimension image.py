from PIL import Image
import os

input_dir = "images"
output_dir = "images_200"
os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir):
    if file.endswith(".gif"):
        img = Image.open(os.path.join(input_dir, file))
        img = img.resize((200, 200), Image.LANCZOS)
        img.save(os.path.join(output_dir, file))
