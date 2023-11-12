import pdf2image
import PIL
import pathlib

read_dir = "PDFs"

processed_img_list = []

skip_filename_keywords = ("L01", "L02", "L03")

for filename in pathlib.Path(read_dir).iterdir():
    print("Processing", str(filename) +"...")
    img_list = pdf2image.convert_from_path(str(filename), poppler_path="C:\\Program Files\\poppler-0.68.0_x86\\poppler-0.68.0\\bin")
    if any([keyword in str(filename) for keyword in skip_filename_keywords]):
        processed_img_list.extend([img.convert('L') for img in img_list])
    else:
        processed_img_list.extend([PIL.ImageChops.invert(img).convert('L') for img in img_list])
    
processed_img_list[0].save(read_dir + "\\Formatted.pdf", "PDF", save_all=True, append_images=processed_img_list[1:])