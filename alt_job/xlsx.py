import xlsxwriter
import tempfile

from alt_job.jobs import Job

def get_xlsx_file(items: list):
    """
        Return excel file encoded as Bytes
    """
    with tempfile.NamedTemporaryFile() as excel_file:
        with xlsxwriter.Workbook(excel_file.name) as workbook:
            headers={ key:key.title() for key in Job.fields }
            worksheet = workbook.add_worksheet()
            worksheet.write_row(row=0, col=0, data=headers.values())
            header_keys = list(headers.keys())
            for index, item in enumerate(items):
                row = map(lambda field_id: str(item.get(field_id, '')), header_keys)
                worksheet.write_row(row=index + 1, col=0, data=row)
        
        with open(excel_file.name, 'rb') as file:
            return file.read()