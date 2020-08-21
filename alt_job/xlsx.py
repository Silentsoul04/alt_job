import xlsxwriter
import tempfile
from alt_job.jobs import Job

def get_xlsx_file(items: list):
    """
        Return excel file encoded as Bytes
    """
    print("Making Excel file...")
    with tempfile.NamedTemporaryFile() as excel_file:
        with xlsxwriter.Workbook(excel_file.name) as workbook:
            headers={ 
                key:key.title() for key in Job.fields 
            }
            worksheet = workbook.add_worksheet()
            worksheet.write_row(row=0, col=0, data=headers.values())
            header_keys = list(headers.keys())
            cell_format = workbook.add_format()
            for index, item in enumerate(items):
                row = map(lambda field_id: str(item.get(field_id, '')), header_keys)
                worksheet.write_row(row=index + 1, col=0, data=row)
                worksheet.set_row(row=index + 1, height=13, cell_format=cell_format)
            worksheet.autofilter(0, 0, len(items)-1, len(Job.fields)-1)
        
        with open(excel_file.name, 'rb') as file:
            return file.read()