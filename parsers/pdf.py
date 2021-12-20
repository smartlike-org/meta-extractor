import sys
import os
from PyPDF2 import PdfFileReader
import logging


def get_meta(host, url, page, header, meta, authors_meta, verbose, read_from_files):
    if read_from_files == False:
        os.system("wget -S --timeout=10 --tries=3 '%s' -O %s > %s 2>&1" %
                  (url, page, header))

    try:
        with open(page, 'rb') as f:
            pdf = PdfFileReader(f)
            info = pdf.getDocumentInfo()
            number_of_pages = pdf.getNumPages()

        if info.title != None:
            meta['title'] = info.title
        if len(meta['title']) == 0 and info.subject != None:
            meta['title'] = info.subject

        if info.author != None:
            meta['authors'].append(info.author)

        meta["image"] = "pdf.png"  # TODO: replace the image
        meta["status"] = "ok"
    except:
        logging.info("failed to parse pdf")
    return meta


def text_extractor(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        # get the first page
        page = pdf.getPage(1)
        print(page)
        print('Page type: {}'.format(str(type(page))))
        text = page.extractText()
        print(text)
