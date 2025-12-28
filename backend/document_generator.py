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
    data: dict containing user, balance, contract, attendance info, and period filters.
    """
    doc = Document()

    # Title
    heading = doc.add_heading('Employee Dashboard Report', 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Period Information (if provided)
    if 'filter_type' in data and 'period_start' in data and 'period_end' in data:
        doc.add_heading('Report Period', level=1)
        p = doc.add_paragraph()
        filter_type_display = data['filter_type'].replace('_', ' ').upper()
        p.add_run('Period: ').bold = True
        p.add_run(f"{filter_type_display}\n")
        p.add_run('Date Range: ').bold = True
        p.add_run(f"{data['period_start']} to {data['period_end']}")

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

    # Vacation Balance (Total)
    doc.add_heading('Total Vacation Balance', level=1)
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

    # Period Statistics (if provided)
    if 'period_leaves_taken' in data:
        doc.add_heading('Period Statistics', level=1)
        p = doc.add_paragraph()
        p.add_run('Leaves Taken in Period: ').bold = True
        p.add_run(f"{data['period_leaves_taken']} days\n")
        p.add_run('Requests in Period: ').bold = True
        p.add_run(f"{data['period_requests_count']}")

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

    # Requests in Period
    requests_heading = 'Leave Requests in Period' if 'filter_type' in data else 'Recent Leave Requests'
    doc.add_heading(requests_heading, level=1)
    if data['requests']:
        req_table = doc.add_table(rows=1, cols=5)
        req_table.style = 'Table Grid'
        hdr = req_table.rows[0].cells
        hdr[0].text = 'Type'
        hdr[1].text = 'Start Date'
        hdr[2].text = 'End Date'
        hdr[3].text = 'Duration'
        hdr[4].text = 'Status'

        for req in data['requests']:
            row = req_table.add_row().cells
            row[0].text = req['vacation_type']
            row[1].text = req['start_date']
            row[2].text = req['end_date']
            row[3].text = f"{req['duration']} days"
            row[4].text = req['status']
    else:
        doc.add_paragraph("No leave requests in this period.")

    # Team Overview (For Managers/Admins)
    if 'team_data' in data and data['team_data']:
        doc.add_page_break()
        doc.add_heading('Team Overview', level=1)

        # Summary statistics
        if data['team_data']:
            total_team_leaves = sum(m.get('total_leaves_taken', 0) for m in data['team_data'])
            avg_balance = sum(m.get('vacation_balance', 0) for m in data['team_data']) / len(data['team_data'])
            on_leave_count = sum(1 for m in data['team_data'] if m.get('current_status') == 'On Leave')

            p = doc.add_paragraph()
            p.add_run('Team Summary:\n').bold = True
            p.add_run(f"Total Members: {len(data['team_data'])}\n")
            p.add_run(f"Currently On Leave: {on_leave_count}\n")
            if 'filter_type' in data:
                p.add_run(f"Total Leaves Taken in Period: {total_team_leaves} days\n")
            p.add_run(f"Average Available Balance: {avg_balance:.1f} days")

            doc.add_paragraph()  # Spacing

        # Individual team members table
        team_table = doc.add_table(rows=1, cols=5)
        team_table.style = 'Table Grid'
        hdr = team_table.rows[0].cells
        hdr[0].text = 'Employee Name'
        hdr[1].text = 'Position'
        hdr[2].text = 'Available Balance'
        hdr[3].text = 'Leaves in Period'
        hdr[4].text = 'Current Status'

        for member in data['team_data']:
            row = team_table.add_row().cells
            row[0].text = f"{member['name_en']} / {member['name_ar']}"
            row[1].text = member.get('position_en', 'N/A')
            row[2].text = f"{member.get('vacation_balance', 0)} days"
            row[3].text = f"{member.get('total_leaves_taken', 0)} days"
            row[4].text = member.get('current_status', 'Present')

        # Leave type breakdown (if available)
        has_leave_types = any(member.get('leaves_by_type') for member in data['team_data'])
        if has_leave_types:
            doc.add_paragraph()
            doc.add_heading('Leave Types Breakdown', level=2)
            for member in data['team_data']:
                if member.get('leaves_by_type'):
                    p = doc.add_paragraph()
                    p.add_run(f"{member['name_en']}: ").bold = True
                    leave_types_str = ", ".join([f"{type_}: {days} days" for type_, days in member['leaves_by_type'].items()])
                    p.add_run(leave_types_str)

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

