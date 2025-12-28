from docxtpl import DocxTemplate, InlineImage
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import os

def create_vacation_form(context):
    """
    Generates a vacation form from a template and returns it as a byte stream.
    
    Args:
        context (dict): A dictionary containing the data to be rendered in the template.
        
    Returns:
        BytesIO: A memory stream containing the generated DOCX document.
    """
    doc = DocxTemplate("backend/templates/vacation_template.docx")
    
    # Handle Signatures
    if context.get('employee_signature_path') and os.path.exists(context.get('employee_signature_path')):
        context['employee_signature'] = InlineImage(doc, context['employee_signature_path'], width=Cm(3.5))
    else:
        context['employee_signature'] = ''

    if context.get('manager_signature_path') and os.path.exists(context.get('manager_signature_path')):
        context['manager_signature'] = InlineImage(doc, context['manager_signature_path'], width=Cm(3.5))
    else:
        context['manager_signature'] = ''

    doc.render(context)
    
    # Save the document to a memory stream
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)  # Go to the beginning of the stream
    
    return file_stream

def create_dashboard_report(data):
    """
    Generates a comprehensive dashboard report.
    data: dict containing user, balance, contract, attendance info.
    """
    doc = Document()
    
    # Title
    heading = doc.add_heading('Employee Dashboard Report', 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Employee Info
    doc.add_heading('Employee Profile', level=1)
    p = doc.add_paragraph()
    p.add_run('Name (EN): ').bold = True
    p.add_run(f"{data['name_en']}\n")
    p.add_run('Name (AR): ').bold = True
    p.add_run(f"{data['name_ar']}\n")
    p.add_run('Position: ').bold = True
    p.add_run(f"{data['position_en']} / {data['position_ar']}\n")
    p.add_run('Email: ').bold = True
    p.add_run(f"{data['email']}\n")
    p.add_run('Unit: ').bold = True
    p.add_run(f"{data['unit_en']} / {data['unit_ar']}")

    # Vacation Balance
    doc.add_heading('Vacation Balance', level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Earned'
    hdr_cells[1].text = 'Used'
    hdr_cells[2].text = 'Available'
    
    row_cells = table.add_row().cells
    row_cells[0].text = str(data['balance_earned'])
    row_cells[1].text = str(data['balance_used'])
    row_cells[2].text = str(data['balance_available'])

    # Contract Status
    doc.add_heading('Contract Status', level=1)
    p = doc.add_paragraph()
    p.add_run('Contract End Date: ').bold = True
    p.add_run(f"{data['contract_end_date']}\n")
    p.add_run('Days Remaining: ').bold = True
    
    days_run = p.add_run(f"{data['days_remaining']}")
    if data['days_remaining'] <= 40:
        days_run.font.color.rgb = RGBColor(255, 0, 0)
        p.add_run(' (Expiring Soon)').font.color.rgb = RGBColor(255, 0, 0)

    # Attendance
    doc.add_heading('Today\'s Attendance', level=1)
    p = doc.add_paragraph()
    p.add_run('Status: ').bold = True
    p.add_run(f"{data['attendance_status']}")

    # Recent Requests
    doc.add_heading('Recent Leave Requests', level=1)
    if data['requests']:
        req_table = doc.add_table(rows=1, cols=4)
        req_table.style = 'Table Grid'
        hdr = req_table.rows[0].cells
        hdr[0].text = 'Type'
        hdr[1].text = 'Start Date'
        hdr[2].text = 'End Date'
        hdr[3].text = 'Status'
        
        for req in data['requests']:
            row = req_table.add_row().cells
            row[0].text = req['vacation_type']
            row[1].text = req['start_date']
            row[2].text = req['end_date']
            row[3].text = req['status']
    else:
        doc.add_paragraph("No recent leave requests.")

    # Team Overview (For Managers/Admins)
    if 'team_data' in data and data['team_data']:
        doc.add_page_break()
        doc.add_heading('Team Overview', level=1)
        
        team_table = doc.add_table(rows=1, cols=3)
        team_table.style = 'Table Grid'
        hdr = team_table.rows[0].cells
        hdr[0].text = 'Employee Name'
        hdr[1].text = 'Position'
        hdr[2].text = 'Available Balance'
        
        for member in data['team_data']:
            row = team_table.add_row().cells
            row[0].text = f"{member['name_en']} / {member['name_ar']}"
            row[1].text = member['position_en']
            row[2].text = str(member['vacation_balance'])

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

