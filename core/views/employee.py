from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one

def employee_list(request):
    """Display all employees with branch and role names."""
    rows = call_procedure('sp_get_all_employees')
    return render(request, 'core/employee_list.html', {'employees': rows})

def employee_add(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        national_code = request.POST.get('national_code')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', '')
        branch_id = request.POST.get('branch_id')
        role_id = request.POST.get('role_id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        acount_status = request.POST.get('acount_status', 1)

        try:
            call_procedure('sp_insert_employee',
                full_name,
                national_code,
                phone_number,
                email,
                int(branch_id),
                int(role_id),
                username,
                password,
                int(acount_status)
            )
            messages.success(request, 'Employee added.')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    branches = call_procedure('sp_get_all_branches')
    roles    = call_procedure('sp_get_all_roles')
    return render(request, 'core/employee_form.html', {
        'branches': branches,
        'roles': roles,
    })

def employee_edit(request, pk):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        national_code = request.POST.get('national_code')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', '')
        branch_id = request.POST.get('branch_id')
        role_id = request.POST.get('role_id')
        username = request.POST.get('username')
        password = request.POST.get('password') or None
        acount_status = request.POST.get('acount_status', 1)

        try:
            call_procedure('sp_update_employee',
                pk,
                full_name,
                national_code,
                phone_number,
                email,
                int(branch_id),
                int(role_id),
                username,
                password,
                int(acount_status)
            )
            messages.success(request, 'Employee updated.')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_employee_by_id', pk)
        employee = rows[0] if rows else None
        if not employee:
            messages.error(request, 'Employee not found.')
            return redirect('employee_list')
        branches = call_procedure('sp_get_all_branches')
        roles    = call_procedure('sp_get_all_roles')
        return render(request, 'core/employee_form.html', {
            'employee': employee,
            'branches': branches,
            'roles': roles,
        })

def employee_delete(request, pk):
    # Use sp_get_all_employees to get branch_name/role_name
    all_emps = call_procedure('sp_get_all_employees')
    employee = next((e for e in all_emps if e['id'] == pk), None)

    if not employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_list')

    if request.method == 'POST':
        try:
            call_procedure('sp_delete_employee', [pk])
            messages.success(request, 'Employee deleted.')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error deleting employee: {e}')
            return redirect('employee_list')

    return render(request, 'core/employee_confirm_delete.html', {'employee': employee})
