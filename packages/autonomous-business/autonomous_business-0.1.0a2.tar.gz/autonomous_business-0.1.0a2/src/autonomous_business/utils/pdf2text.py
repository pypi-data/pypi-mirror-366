import os
import pymupdf

def convert_pdf_to_text(pdf_path, txt_path):
    """Converts a single PDF to a text file."""
    try:
        doc = pymupdf.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Converted: {pdf_path} -> {txt_path}")
    except Exception as e:
        print(f"Failed to convert {pdf_path}: {e}")

def convert_all_pdfs_in_directory(input_dir, output_dir):
    """Converts all PDF files in input_dir to text files in output_dir."""
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(output_dir, txt_filename)
            convert_pdf_to_text(pdf_path, txt_path)

if __name__ == "__main__":
    # Set your input and output directory paths here
    input_directory = "./data/some_input_dir"     # Change to your actual PDF directory
    output_directory = "./data/some_output_dir"   # Change to your desired output directory

    convert_all_pdfs_in_directory(input_directory, output_directory)
