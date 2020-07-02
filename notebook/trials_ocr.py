import ocrmypdf
import pandas as pd
input_pdf = "../output_image/Syndicat_Interdepartemental__De_lEau_Seine_Aval/5e42c807634f4125899acbd1--2eafac55-e07a-4f72-985f-ec63746efbfe.pdf"
output_pdf = "../output_image/Syndicat_Interdepartemental__De_lEau_Seine_Aval/5e42c807634f4125899acbd1--2eafac55-e07a-4f72-985f-ec63746efbfe_ocr.pdf"
a = ocrmypdf.ocr(input_pdf, output_pdf, output_file='txt')
ocrmypdf.ocr()

