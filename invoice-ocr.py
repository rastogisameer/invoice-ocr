"""This application demonstrates how to perform basic operations with the
Google Cloud Vision API.

Example Usage:
python detect.py text ./resources/wakeupcat.jpg
python detect.py labels ./resources/landmark.jpg
python detect.py web ./resources/landmark.jpg
python detect.py web-uri http://wheresgus.com/dog.JPG
python detect.py web-geo ./resources/city.jpg
python detect.py faces-uri gs://your-bucket/file.jpg
python detect_pdf.py ocr-uri gs://python-docs-samples-tests/HodgeConj.pdf \
gs://BUCKET_NAME/PREFIX/

For more information, the documentation at
https://cloud.google.com/vision/docs.
"""


import io

from google.cloud import vision
from google.protobuf import json_format



# [START def_detect_text]
def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    # [START migration_text_detection]
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))
    # [END migration_text_detection]
# [END def_detect_text]



# [START def_detect_document]
def detect_blocks(path):
    """Detects document features in an image."""
    client = vision.ImageAnnotatorClient()

    # [START migration_document_text_detection]
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock({})'.format(block.confidence))
            
            for paragraph in block.paragraphs:

                word_list = []
                print('  Para({})'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    '''print('    Word: {} ({})'.format(word_text, word.confidence))'''
                    word_list.append(word_text)
                    '''for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))'''
                para_str = ' '.join([w for w in word_list])
                print('    ' + para_str)
    # [END migration_document_text_detection]
# [END def_detect_document]



if __name__ == '__main__':
    detect_blocks('/home/sameer/data/invoices/pages/png/Invoice_4.png')