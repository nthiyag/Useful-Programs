from PyPDF2 import PdfFileMerger
import pathlib

read_dir = "C:\\Users\\nikhi\\Desktop\\Useful Programs\\PDFs"

merger = PdfFileMerger()

for filename in pathlib.Path(read_dir).iterdir():
    print("Processing", str(filename) +"...")
    merger.append(str(filename))

merger.write("C:\\Users\\nikhi\\Desktop\\Useful Programs\\PDFs\\result.pdf")
merger.close()