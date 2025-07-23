import os
from PIL import Image
import pytesseract

IMAGE_DIR = "ocr_images"
TEXT_OUTPUT_DIR = "ocr_text"

def ocr_images_to_text(image_dir, text_output_dir):
    for root, _, files in os.walk(image_dir):
        for filename in files:
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(root, filename)
                rel_path = os.path.relpath(image_path, image_dir)
                text_path = os.path.join(text_output_dir, os.path.splitext(rel_path)[0] + ".txt")

                os.makedirs(os.path.dirname(text_path), exist_ok=True)

                print(f"OCR: {rel_path}")
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image)

                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f" ✅Saved: {text_path}")

if __name__ == "__main__":
    os.makedirs(TEXT_OUTPUT_DIR, exist_ok=True)
    ocr_images_to_text(IMAGE_DIR, TEXT_OUTPUT_DIR)

