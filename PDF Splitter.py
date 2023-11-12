from PyPDF2 import PdfReader, PdfWriter
import pathlib

read_dir = "PDFs"

for filename in pathlib.Path(read_dir).iterdir():
    print("Processing", str(filename) +"...")
    file = PdfReader(open(filename, "rb"))
    for i in range(len(file.pages)):
        writer = PdfWriter()
        writer.add_page(file.pages[i])
        writer.write(open(str(filename) + "_" + str(i) +".pdf", "wb"))
        writer.close()