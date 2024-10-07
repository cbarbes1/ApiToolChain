
# from pdfminer.high_level import extract_text
# from pdfminer.layout import LAParams


# # Extract text from the PDF
# def extract_text_from_pdf(pdf_path):
#     laparams = LAParams(word_margin=2.0)
#     return extract_text(pdf_path, laparams=laparams)

# # Example usage
# pdf_path = 'directory.pdf'
# extracted_text = extract_text_from_pdf(pdf_path)
# with open('test.txt', 'w') as f:
#     print(extracted_text, file=f)

from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import PDFPageAggregator

from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

def extract_lines_from_pdf(pdf_path):
    lines = []

    # Open the PDF file
    with open(pdf_path, 'rb') as fp:
        # Create a PDF resource manager
        rsrcmgr = PDFResourceManager()
        # Set parameters for analysis
        laparams = LAParams()
        # Create a PDF device with aggregator
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Extract text from each page
        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            # Get the layout object
            layout = device.get_result()

            # Loop through layout objects
            for element in layout:
                if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
                    lines.append(element.get_text())

    return lines

# Example usage
pdf_path = 'directory.pdf'
extracted_lines = extract_lines_from_pdf(pdf_path)

# Process the extracted lines
for line in extracted_lines:
    if "Department" in line:
        print(line)  # Process lines after department names