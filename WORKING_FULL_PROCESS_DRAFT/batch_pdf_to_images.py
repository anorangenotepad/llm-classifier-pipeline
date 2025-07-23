from pdf2image import convert_from_path
import os

PDF_DIR = "pdf_files"
OUTPUT_DIR = "ocr_images"
DPI = 300

def convert_all_pdfs(pdf_dir, output_dir, dpi=300):
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            pdf_name = os.path.splitext(filename)[0]
            pdf_output_dir = os.path.join(output_dir, pdf_name)
            os.makedirs(pdf_output_dir, exist_ok=True)

            print(f"📄 Converting: {filename}")
            images = convert_from_path(pdf_path, dpi=dpi)

            for i, image in enumerate(images):
                image_filename = os.path.join(pdf_output_dir, f"page_{i+1}.png")
                image.save(image_filename, "PNG")
                print(f"  ✅ Saved: {image_filename}")

if __name__ == "__main__":
    convert_all_pdfs(PDF_DIR, OUTPUT_DIR, DPI)

