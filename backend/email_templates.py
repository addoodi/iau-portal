"""
HTML Email Templates for IAU Portal
Bilingual templates (Arabic RTL + English LTR) with borderless 2-column table layout
"""

from typing import Dict, Any


def get_base_email_template() -> str:
    """
    Base HTML structure for all emails with IAU Portal branding

    Returns:
        str: HTML template string with {content} placeholder
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #0f5132 0%, #1e7e4f 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .info-table td {{
            padding: 15px;
            vertical-align: top;
        }}
        .info-table .ar-col {{
            direction: rtl;
            text-align: right;
            border-left: 1px solid #e0e0e0;
            width: 50%;
            font-family: 'Arial', sans-serif;
        }}
        .info-table .en-col {{
            direction: ltr;
            text-align: left;
            width: 50%;
        }}
        .label {{
            font-weight: bold;
            color: #0f5132;
            margin-bottom: 5px;
        }}
        .value {{
            color: #333;
            margin-bottom: 15px;
        }}
        .footer {{
            background-color: #f9f9f9;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .critical {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""


def render_leave_request_created_email(data: Dict[str, Any]) -> str:
    """
    Email to manager when employee creates leave request

    Args:
        data: Dict containing:
            - employee_name_ar: str
            - employee_name_en: str
            - employee_id: str
            - vacation_type: str (e.g., 'Annual', 'Sick')
            - start_date: str
            - end_date: str
            - duration: int
            - manager_name_ar: str
            - manager_name_en: str

    Returns:
        str: Complete HTML email
    """
    vacation_types = {
        'Annual': {'ar': 'إجازة سنوية', 'en': 'Annual Vacation'},
        'Sick': {'ar': 'إجازة مرضية', 'en': 'Sick Leave'},
        'Unpaid': {'ar': 'إجازة بدون أجر', 'en': 'Unpaid Leave'},
        'Emergency': {'ar': 'إجازة طارئة', 'en': 'Emergency Leave'}
    }

    vac_type = vacation_types.get(data['vacation_type'], {'ar': data['vacation_type'], 'en': data['vacation_type']})

    content = f"""
    <div class="container">
        <div class="header">
            <h1>New Leave Request / طلب إجازة جديد</h1>
        </div>
        <div class="content">
            <table class="info-table">
                <tr>
                    <td class="ar-col">
                        <div class="label">عزيزي/عزيزتي {data['manager_name_ar']}</div>
                        <p class="value">تم تقديم طلب إجازة جديد ويحتاج إلى موافقتك.</p>
                    </td>
                    <td class="en-col">
                        <div class="label">Dear {data['manager_name_en']}</div>
                        <p class="value">A new leave request has been submitted and requires your approval.</p>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">اسم الموظف:</div>
                        <div class="value">{data['employee_name_ar']} ({data['employee_id']})</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Employee Name:</div>
                        <div class="value">{data['employee_name_en']} ({data['employee_id']})</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">نوع الإجازة:</div>
                        <div class="value">{vac_type['ar']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Vacation Type:</div>
                        <div class="value">{vac_type['en']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">تاريخ البدء:</div>
                        <div class="value">{data['start_date']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Start Date:</div>
                        <div class="value">{data['start_date']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">تاريخ الانتهاء:</div>
                        <div class="value">{data['end_date']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">End Date:</div>
                        <div class="value">{data['end_date']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">المدة:</div>
                        <div class="value">{data['duration']} يوم/أيام</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Duration:</div>
                        <div class="value">{data['duration']} day(s)</div>
                    </td>
                </tr>
            </table>
        </div>
        <div class="footer">
            <p>IAU Portal - Vacation Management System</p>
            <p>نظام إدارة الإجازات - بوابة جامعة الإمام عبدالرحمن بن فيصل</p>
        </div>
    </div>
    """

    return get_base_email_template().format(content=content)


def render_leave_request_approved_email(data: Dict[str, Any]) -> str:
    """
    Email to employee when request is approved

    Args:
        data: Dict containing:
            - employee_name_ar: str
            - employee_name_en: str
            - vacation_type: str
            - start_date: str
            - end_date: str
            - duration: int
            - balance_deducted: int
            - remaining_balance: float

    Returns:
        str: Complete HTML email
    """
    vacation_types = {
        'Annual': {'ar': 'إجازة سنوية', 'en': 'Annual Vacation'},
        'Sick': {'ar': 'إجازة مرضية', 'en': 'Sick Leave'},
        'Unpaid': {'ar': 'إجازة بدون أجر', 'en': 'Unpaid Leave'},
        'Emergency': {'ar': 'إجازة طارئة', 'en': 'Emergency Leave'}
    }

    vac_type = vacation_types.get(data['vacation_type'], {'ar': data['vacation_type'], 'en': data['vacation_type']})

    content = f"""
    <div class="container">
        <div class="header">
            <h1>Request Approved / تمت الموافقة على الطلب</h1>
        </div>
        <div class="content">
            <table class="info-table">
                <tr>
                    <td class="ar-col">
                        <div class="label">عزيزي/عزيزتي {data['employee_name_ar']}</div>
                        <p class="value">تمت الموافقة على طلب إجازتك!</p>
                    </td>
                    <td class="en-col">
                        <div class="label">Dear {data['employee_name_en']}</div>
                        <p class="value">Your leave request has been approved!</p>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">نوع الإجازة:</div>
                        <div class="value">{vac_type['ar']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Vacation Type:</div>
                        <div class="value">{vac_type['en']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">من:</div>
                        <div class="value">{data['start_date']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">From:</div>
                        <div class="value">{data['start_date']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">إلى:</div>
                        <div class="value">{data['end_date']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">To:</div>
                        <div class="value">{data['end_date']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">عدد الأيام المستخدمة:</div>
                        <div class="value">{data['balance_deducted']} يوم/أيام</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Days Used:</div>
                        <div class="value">{data['balance_deducted']} day(s)</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">الرصيد المتبقي:</div>
                        <div class="value">{data['remaining_balance']:.1f} يوم/أيام</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Remaining Balance:</div>
                        <div class="value">{data['remaining_balance']:.1f} day(s)</div>
                    </td>
                </tr>
            </table>
        </div>
        <div class="footer">
            <p>IAU Portal - Vacation Management System</p>
            <p>نظام إدارة الإجازات - بوابة جامعة الإمام عبدالرحمن بن فيصل</p>
        </div>
    </div>
    """

    return get_base_email_template().format(content=content)


def render_contract_reminder_40_days_email(data: Dict[str, Any]) -> str:
    """
    Email 40 days before contract end

    Args:
        data: Dict containing:
            - employee_name_ar: str
            - employee_name_en: str
            - contract_end_date: str
            - days_remaining: int
            - vacation_balance: float

    Returns:
        str: Complete HTML email
    """
    content = f"""
    <div class="container">
        <div class="header">
            <h1>Contract End Reminder / تذكير بانتهاء العقد</h1>
        </div>
        <div class="content">
            <div class="warning">
                <table class="info-table" style="margin: 0;">
                    <tr>
                        <td class="ar-col" style="border: none;">
                            <strong>تنبيه: عقدك سينتهي قريباً</strong>
                        </td>
                        <td class="en-col" style="border: none;">
                            <strong>Notice: Your contract is ending soon</strong>
                        </td>
                    </tr>
                </table>
            </div>
            <table class="info-table">
                <tr>
                    <td class="ar-col">
                        <div class="label">عزيزي/عزيزتي {data['employee_name_ar']}</div>
                        <p class="value">نود تذكيرك بأن عقدك الحالي سينتهي قريباً.</p>
                    </td>
                    <td class="en-col">
                        <div class="label">Dear {data['employee_name_en']}</div>
                        <p class="value">We would like to remind you that your current contract is ending soon.</p>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">تاريخ انتهاء العقد:</div>
                        <div class="value">{data['contract_end_date']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Contract End Date:</div>
                        <div class="value">{data['contract_end_date']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">الأيام المتبقية:</div>
                        <div class="value">{data['days_remaining']} يوم/أيام</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Days Remaining:</div>
                        <div class="value">{data['days_remaining']} day(s)</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">رصيد الإجازات المتبقي:</div>
                        <div class="value">{data['vacation_balance']:.1f} يوم/أيام</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Remaining Vacation Balance:</div>
                        <div class="value">{data['vacation_balance']:.1f} day(s)</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <p class="value">يرجى التخطيط وفقاً لذلك واستخدام رصيد إجازاتك قبل انتهاء العقد.</p>
                    </td>
                    <td class="en-col">
                        <p class="value">Please plan accordingly and use your vacation balance before the contract ends.</p>
                    </td>
                </tr>
            </table>
        </div>
        <div class="footer">
            <p>IAU Portal - Vacation Management System</p>
            <p>نظام إدارة الإجازات - بوابة جامعة الإمام عبدالرحمن بن فيصل</p>
        </div>
    </div>
    """

    return get_base_email_template().format(content=content)


def render_contract_critical_warning_email(data: Dict[str, Any]) -> str:
    """
    Critical email when balance equals remaining days (1 day before)

    Args:
        data: Dict containing:
            - employee_name_ar: str
            - employee_name_en: str
            - contract_end_date: str
            - days_remaining: int
            - vacation_balance: float

    Returns:
        str: Complete HTML email
    """
    content = f"""
    <div class="container">
        <div class="header" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
            <h1>CRITICAL: Contract Ending / تحذير حرج: انتهاء العقد</h1>
        </div>
        <div class="content">
            <div class="critical">
                <table class="info-table" style="margin: 0;">
                    <tr>
                        <td class="ar-col" style="border: none;">
                            <strong>⚠️ تحذير حرج: رصيد إجازتك يساوي الأيام المتبقية في عقدك!</strong>
                        </td>
                        <td class="en-col" style="border: none;">
                            <strong>⚠️ CRITICAL WARNING: Your vacation balance equals your remaining contract days!</strong>
                        </td>
                    </tr>
                </table>
            </div>
            <table class="info-table">
                <tr>
                    <td class="ar-col">
                        <div class="label">عزيزي/عزيزتي {data['employee_name_ar']}</div>
                        <p class="value">هذا تنبيه عاجل بشأن عقدك ورصيد إجازاتك.</p>
                    </td>
                    <td class="en-col">
                        <div class="label">Dear {data['employee_name_en']}</div>
                        <p class="value">This is an urgent notification regarding your contract and vacation balance.</p>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">تاريخ انتهاء العقد:</div>
                        <div class="value">{data['contract_end_date']}</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Contract End Date:</div>
                        <div class="value">{data['contract_end_date']}</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">الأيام المتبقية في العقد:</div>
                        <div class="value">{data['days_remaining']} يوم/أيام</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Days Remaining in Contract:</div>
                        <div class="value">{data['days_remaining']} day(s)</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <div class="label">رصيد الإجازات:</div>
                        <div class="value">{data['vacation_balance']:.1f} يوم/أيام</div>
                    </td>
                    <td class="en-col">
                        <div class="label">Vacation Balance:</div>
                        <div class="value">{data['vacation_balance']:.1f} day(s)</div>
                    </td>
                </tr>
                <tr>
                    <td class="ar-col">
                        <p class="value" style="color: #dc3545; font-weight: bold;">
                            يرجى اتخاذ إجراء فوري! قد تفقد رصيد إجازاتك غير المستخدم عند انتهاء العقد.
                        </p>
                    </td>
                    <td class="en-col">
                        <p class="value" style="color: #dc3545; font-weight: bold;">
                            Please take immediate action! You may lose your unused vacation balance when the contract ends.
                        </p>
                    </td>
                </tr>
            </table>
        </div>
        <div class="footer">
            <p>IAU Portal - Vacation Management System</p>
            <p>نظام إدارة الإجازات - بوابة جامعة الإمام عبدالرحمن بن فيصل</p>
        </div>
    </div>
    """

    return get_base_email_template().format(content=content)
