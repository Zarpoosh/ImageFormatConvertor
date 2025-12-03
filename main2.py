import os
from PIL import Image

# مسیر پوشه‌ای که عکس‌ها داخلش هستند
input_folder = "images"
output_folder = "output_webp"

# اگر پوشه وجود نداشت، می‌سازه
os.makedirs(output_folder, exist_ok=True)

# فرمت‌هایی که می‌خوای تبدیل بشن
valid_extensions = [".jpg", ".jpeg", ".png"]

for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    file_name, ext = os.path.splitext(filename)

    if ext.lower() in valid_extensions:
        img = Image.open(file_path).convert("RGB")
        output_path = os.path.join(output_folder, f"{file_name}.webp")

        img.save(output_path, "webp", quality=85)
        print(f"Converted: {filename} → {file_name}.webp")

print("\n all of your images converted to webp :)")
