from django.shortcuts import render
from django.contrib import messages
from core.utils import call_procedure, execute_query
from core.decorators import login_required, role_required

@login_required
@role_required('Branch Manager', 'System Admin')
def province_report(request):
    employee = request.session['employee']
    branch_id = employee['branch_id']

    # 1. Check if HQ and get province info
    branch_info = execute_query(
        "SELECT b.is_headquarter, p.id AS province_id, p.name AS province_name "
        "FROM branch b "
        "JOIN city c ON b.city_id = c.id "
        "JOIN province p ON c.province_id = p.id "
        "WHERE b.id = %s",
        [branch_id]
    )
    if not branch_info:
        messages.error(request, 'Branch information not found.')
        return render(request, 'core/province_report.html', {'report': None})

    info = branch_info[0]
    if not info['is_headquarter']:
        messages.error(request, 'Province reports are only available for headquarters branches.')
        return render(request, 'core/province_report.html', {'report': None})

    province_id = info['province_id']

    # 2. Fetch province summary
    report = None
    try:
        rows = call_procedure('sp_get_province_report', province_id)
        report = rows[0] if rows else None
    except Exception as e:
        messages.error(request, str(e))

    # 3. Fetch per‑branch performance for the table
    branches = []
    try:
        branches = call_procedure('sp_get_branch_performance_by_province', province_id)
    except Exception as e:
        messages.error(request, str(e))

    return render(request, 'core/province_report.html', {
        'report': report,
        'province_name': info['province_name'],
        'branches': branches,
    })