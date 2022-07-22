import pandas as pd
import tabula

OLD_PDF = "Faculty-approved-HSS-list-as-of-January-19-2022.pdf"
NEW_PDF = "Faculty-approved-HSS-list-as-of-July-7-2022.pdf"

def extract_pdf_approved_courses(pdf):
    approved_courses_df_list = [df.iloc[:,0] for df in tabula.read_pdf(pdf, area=(0.75 * 72, 0.25 * 72, 10.25 * 72, 1.6 * 72), pages="all")]

    approved_courses_df = pd.concat(approved_courses_df_list, axis=0)

    return list(approved_courses_df[approved_courses_df.apply(lambda text: str(text)[0:3].isalpha() and str(text)[3:6].isnumeric())])

old = extract_pdf_approved_courses(OLD_PDF)
new = extract_pdf_approved_courses(NEW_PDF)

print("Courses in Jan 19th PDF but not in July 7th PDF")
for course in old:
    if course not in new:
        print(course)

print("Courses in July 7th PDF but not in Jan 19th PDF")
for course in new:
    if course not in old:
        print(course)