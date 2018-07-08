#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  8 11:13:24 2018

@author: sameer
"""

import sys
   

import os, shutil
from PyPDF2 import PdfFileReader, PdfFileWriter
from wand.image import Image
import cv2
import numpy as np
import pytesseract

RESOLUTION = 200
COMPRESSION = 80

def split_pdf(path):
        
    pdf = PdfFileReader(path)
    
    fname = os.path.splitext(os.path.basename(path))[0]
    parent_dir = os.path.dirname(path) + os.path.sep + 'pages'
    
    if os.path.exists(parent_dir):
        shutil.rmtree(parent_dir)
        print("Deleted: {}".format(parent_dir))
        
    os.makedirs(parent_dir)
    
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
        
        output_filename = parent_dir + os.path.sep + '{}_{}.pdf'.format(fname, page+1)
        
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
            
        print('Created: {}'.format(output_filename))
        
    return parent_dir
        
def pdf_to_jpg(pages_dir, filename):
    
    filepath = pages_dir + os.path.sep + filename
    parent_dir = pages_dir + os.path.sep + 'jpeg'
    try:        
        with Image(filename = filepath, resolution=RESOLUTION) as img:
                              
            if not os.path.exists(parent_dir):                
                os.makedirs(parent_dir)
                print("Created: {}".format(parent_dir))
               
            output_filename = parent_dir + os.path.sep + '{}.jpg'.format(os.path.splitext(filename)[0])
            
            if os.path.exists(output_filename):
                os.remove(output_filename)
                print("Deleted: {}".format(output_filename))
            
            img.compression_quality = COMPRESSION
            img.save(filename = output_filename)
            print('Converted: {}'.format(output_filename))
    except Exception:
        print("Exception occurred")
    
    return parent_dir
    
def pdffolder_to_jpg(path):
    
    files = os.listdir(path)
    jpg_dir = ''
    
    for fl in files:
        
        if os.path.isfile(path + os.path.sep + fl):
            jpg_dir = pdf_to_jpg(path, fl)
        
    return jpg_dir
    
def read_image(path):
    img = cv2.imread(path)
    print("Imaging: {}".format(path))
    return img
   
def save_image(img, parent_dir, fname):
    output_filepath = parent_dir + os.path.sep + fname
    if os.path.exists(output_filepath):
        os.remove(output_filepath)
        
    cv2.imwrite(output_filepath, img)
    print("Created: {}".format(output_filepath))

def rescale(img, invoice_path):
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
       
    save_image(img, invoice_path, 'rescaled.jpg')
    
    return img


def grayscale(img, invoice_path):
    
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
 
    save_image(img, invoice_path, 'gray.jpg')

    return img
    

def binarisation(img, invoice_path):
    # with otsu - t becomes l
    #img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    #img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)[1]
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 215, 1)

    save_image(img, invoice_path, 'bin.jpg')
    
    return img


def denoise(img, invoice_path):
    #img = cv2.fastNlMeansDenoising(img, None, 9, 13)
    img = cv2.medianBlur(img, 3)
    
    kernel = np.ones((1, 1), np.uint8)
    #img = cv2.dilate(img, kernel, iterations=1)
    #img = cv2.erode(img, kernel, iterations=1)
    #img = cv2.GaussianBlur(img, (5, 5), 0)
       
    save_image(img, invoice_path, 'denoise.jpg')
        
    return img


def deskew(img, invoice_path):

    coords = np.column_stack(np.where(img > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        	angle = -(90 + angle)

    else:
        	angle = -angle
    
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    save_image(img, invoice_path, 'deskew.jpg')
    
    return img
 

def ocr(img, invoice_path):
    
    text = pytesseract.image_to_string(img)
    output_filepath = invoice_path + os.path.sep + 'text.txt'
    with open(output_filepath, 'w') as fw:
        fw.write(text)
    
    print("Created: {}".format(output_filepath))

def invoice_dir(filepath):
    parent_dir = os.path.dirname(filepath)
    invoice_dir = parent_dir + os.path.sep + os.path.splitext(os.path.basename(filepath))[0]
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)
        print("Created: {}".format(invoice_dir))
 
    return invoice_dir

def readfolder_image(path):        
    files = os.listdir(path)
        
    for fl in files:
        filepath = path + os.path.sep + fl
        if os.path.isfile(filepath):
            img = read_image(filepath)
      
            invoice_path = invoice_dir(filepath)
            
            img = rescale(img, invoice_path)
            img = grayscale(img, invoice_path)
            
            img = binarisation(img, invoice_path)   
            img = denoise(img, invoice_path)
            #img = deskew(img, invoice_path)
            ocr(img, invoice_path)
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: readInvoice.py <filepath>")
        sys.exit(1)

    split_dir = split_pdf(sys.argv[1])
    
    jpg_dir = pdffolder_to_jpg(split_dir)
    
    readfolder_image(jpg_dir)
    
  