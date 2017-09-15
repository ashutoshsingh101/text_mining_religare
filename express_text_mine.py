# -*- coding: utf-8 -*-

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import re



class text_extraction_and_page_division():
    
    def __init__(self,pdf_name):
        self.pdf_name = pdf_name

    def parse_layout_obj_page_wise(self,layout_objs,pages_list):    
        for obj in layout_objs:
            # if it's a textbox, print text and location
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                pages_list.extend(obj.get_text().split('\n'))

            # if it's a container,recurse
            elif isinstance(obj, pdfminer.layout.LTFigure):
                pages_list = self.parse_layout_obj_page_wise(obj._objs,pages_list)
        return pages_list

    def text_extraction(self):
        complete_report = []

        open_pdf_file = open(self.pdf_name, 'rb')
        pdf_parser = PDFParser(open_pdf_file)
        document = PDFDocument(pdf_parser)

        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        device = PDFDevice(rsrcmgr)

        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        for page in PDFPage.create_pages(document):
            pages_list = []
            interpreter.process_page(page)
            layout = device.get_result()

            pages_list = self.parse_layout_obj_page_wise(layout._objs,pages_list)
            complete_report.append(pages_list)

        return complete_report


class extract_information_of_report():
    def __init__(self,complete_report,dataset_dictonary):
        self.complete_report = complete_report
        self.dataset_dictionary = dataset_dictionary

    
    def value_of_test(self,line_number,page,first_value_of_page,line_number_of_previous_value):
        if first_value_of_page == False:
            start_index_for_value = line_number
        else:
            start_index_for_value = line_number_of_previous_value
        for line_number_for_value in range(start_index_for_value + 1,len(page)):
            if re.match(r'^\d+\.?\d*$',page[line_number_for_value]):
                print(page[line_number_for_value])
                first_value_of_page = True
                return first_value_of_page,line_number_for_value
                break
                
        return first_value_of_page,line_number_for_value

    def unit_of_test(self,line_number,page,first_unit_of_page,line_number_of_previous_unit):
        if first_unit_of_page == False:
            start_index_for_unit = line_number
        else:
            start_index_for_unit = line_number_of_previous_unit
        for line_number_for_unit in range(start_index_for_unit + 1,len(page)):
            if re.match(r'([a-z]{0,4}\s*/\s*[a-z]{2,4})|(x?10\^?\d+\s*/)',page[line_number_for_unit]):
                print(page[line_number_for_unit])
                first_unit_of_page = True
                return first_unit_of_page,line_number_for_unit
            elif 'pg' in page[line_number_for_unit] or 'fl' in page[line_number_for_unit]:
                if len(page[line_number_for_unit]) == 2:
                    print(page[line_number_for_unit])
                    first_unit_of_page = True
                    return first_unit_of_page,line_number_for_unit
            else:
                if '%' in page[line_number_for_unit] and len(page[line_number_for_unit]) == 1:
                    print(page[line_number_for_unit])
                    first_unit_of_page = True
                    return first_unit_of_page,line_number_for_unit
        return first_unit_of_page,line_number_for_unit

    def reference_range_of_test_for_simple_range_type(self,line_number,page,first_reference_range_of_page,line_number_of_previous_reference_range):
        if first_reference_range_of_page == False:
            start_index_for_simple_range = line_number
        else:
            start_index_for_simple_range = line_number_of_previous_reference_range
        for line_number_for_simple_range in range(start_index_for_simple_range + 1,len(page)):
            if re.match(r'(\d+\.?\d*\s*\-\s*\d+\.?\d*)|((<|>)\s*\d+)',page[line_number_for_simple_range]):
                print(page[line_number_for_simple_range])
                print('\n')
                print('\n')
                first_reference_range_of_page = True
                return first_reference_range_of_page,line_number_for_simple_range
        return first_reference_range_of_page,line_number_for_simple_range

    def when_multiple_lines_of_reference_range_found(self,page,start_line_number_of_commplex_range,complex_range_list):
        if re.search(r'\d+',page[start_line_number_of_commplex_range]):
            if 'up to' in page[start_line_number_of_commplex_range ].lower() or 'less than' in page[start_line_number_of_commplex_range ].lower() or 'greater than' in page[start_line_number_of_commplex_range ].lower() or '<' in page[start_line_number_of_commplex_range ].lower() or '>' in page[start_line_number_of_commplex_range ].lower():
                complex_range_list.append(page[start_line_number_of_commplex_range ])
                return complex_range_list, start_line_number_of_commplex_range

            
            if (page[start_line_number_of_commplex_range].strip()).endswith('to') or (page[start_line_number_of_commplex_range ].strip()).endswith('-'):
                if re.match(r'\d+',page[start_line_number_of_commplex_range +1]):
                    complex_range_list.append(page[start_line_number_of_commplex_range ]+' '+page[start_line_number_of_commplex_range +1])
                    return complex_range_list, start_line_number_of_commplex_range
            else:
                if (page[start_line_number_of_commplex_range  +1].strip()).startswith('to') or (page[start_line_number_of_commplex_range  +1].strip()).startswith('-') or re.search(r'\d+',page[start_line_number_of_commplex_range +1]):
                    complex_range_list.append(page[start_line_number_of_commplex_range ]+' '+page[start_line_number_of_commplex_range +1])
                    start_line_number_of_commplex_range = start_line_number_of_commplex_range +1
                    return complex_range_list, start_line_number_of_commplex_range
                else:
                    complex_range_list.append(page[start_line_number_of_commplex_range ])
                    return complex_range_list, start_line_number_of_commplex_range

        else:
            if re.search(r'\d+',page[start_line_number_of_commplex_range +1]):
                complex_range_list.append(page[start_line_number_of_commplex_range ]+' '+page[start_line_number_of_commplex_range +1])
                start_line_number_of_commplex_range = start_line_number_of_commplex_range +1
                return complex_range_list, start_line_number_of_commplex_range
        return complex_range_list, start_line_number_of_commplex_range


    def reference_range_of_test_for_compex_range_type(self,line_number,page,first_reference_range_of_page,line_number_of_previous_reference_range):
        list_denoting_complex_range_keyword = ['Desirable','less than','Borderline','High','Normal','Up to',
        'Hypertriglyceidemic','Very High','risk factor']
        complex_range_list = []
        identifier_for_deciding_range_function = ''
        if first_reference_range_of_page == False:
            start_index_for_simple_range = line_number
        else:
            start_index_for_simple_range = line_number_of_previous_reference_range
        start_line_number_of_commplex_range = start_index_for_simple_range
        while start_line_number_of_commplex_range in range(len(page)):
            for key_word in list_denoting_complex_range_keyword:
                if key_word.lower() in page[start_line_number_of_commplex_range ].lower():
                    complex_range_list, start_line_number_of_commplex_range = self.when_multiple_lines_of_reference_range_found(page,start_line_number_of_commplex_range,complex_range_list)
                    break
                   
            start_line_number_of_commplex_range = start_line_number_of_commplex_range + 1
            if len(complex_range_list) == 3:
                print(complex_range_list)
                first_reference_range_of_page = True
                print('\n')
                return first_reference_range_of_page,start_line_number_of_commplex_range
        return first_reference_range_of_page,start_line_number_of_commplex_range




    def test_information_extraction(self,profile_dictionary,page):
        first_value_of_page = False
        first_unit_of_page = False
        first_reference_range_of_page = False
        line_number_of_previous_value = 0
        line_number_of_previous_unit = 0
        line_number_of_previous_reference_range = 0
        line_number_for_searching_testnames = -1
        for line_number in range(line_number_for_searching_testnames+1,len(page)):
            for test_name in profile_dictionary['tests']:
                if test_name in page[line_number]:
                    line_number_for_searching_testnames = line_number
                    print(page[line_number])
                    first_value_of_page,line_number_of_previous_value = self.value_of_test(line_number,page,first_value_of_page,line_number_of_previous_value)
                    first_unit_of_page,line_number_of_previous_unit = self.unit_of_test(line_number,page,first_unit_of_page,line_number_of_previous_unit)
                    if profile_dictionary['profile_name'] == 'TOTAL LIPID PROFILE':
                        if page[line_number] == 'CHOLESTEROL' or page[line_number] == 'TRIGLYCERIDES' or page[line_number] == 'SR. HDL':
                        # first_reference_range_of_page,line_number_of_previous_reference_range = self.reference_range_of_test_for_simple_range_type(line_number,page,first_reference_range_of_page,line_number_of_previous_reference_range)
                            first_reference_range_of_page,line_number_of_previous_reference_range= self.reference_range_of_test_for_compex_range_type(line_number,page,first_reference_range_of_page,line_number_of_previous_reference_range)
                    # else:
                    #     self.reference_range_of_test_for_compex_range_type(line_number,page,first_reference_range_of_page,line_number_of_previous_reference_range)
                    break

    def profile_identifier(self):
        for profile_dictionary in self.dataset_dictionary:
            for page in complete_report:
                for line_number in range(len(page)):
                    if profile_dictionary['profile_name'] in page[line_number]:
                        if profile_dictionary['profile_name'] == "TOTAL LIPID PROFILE":
                            print('yes')
                            self.test_information_extraction(profile_dictionary,page)












dataset_dictionary = [{"profile_name":"TOTAL LIPID PROFILE","tests":["CHOLESTEROL","TRIGLYCERIDES","SR. HDL","SR.LDL","SR.VLDL","T.C / HDL","LDL / HDL"]}
,{"profile_name":"Plasma Glucose - Fasting - (GOD-POD method)","tests":["Plasma Glucose - Fasting - (GOD-POD method)"]}
,{"profile_name":"RENAL FUNCTION TEST","tests":["BLOOD UREA LEVEL","CREATININE","URIC ACID"]}
,{"profile_name":"COMPLETE BLOOD COUNT (CBC) REPORT","tests":["TOTAL LEUCOCYTE","RBC COUNT","HEMOGLOBIN","HAEMATOCRIT","MCV","MCH","MCHC","RDW" ,"NEUTROPHILS", "LYMPHOCYTES", "MONOCYTES","EOSINOPHILS","PLATELETS","MPV","BASOPHILS","E.S.R."]}]




extract_text_and_divide_pages = text_extraction_and_page_division('express_religare.pdf')
complete_report = extract_text_and_divide_pages.text_extraction()


extract_information = extract_information_of_report(complete_report,dataset_dictionary)
extract_information.profile_identifier()



