from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import call_procedure, fetch_one   # fetch_one optional if you need it

# ------------------------------------------------------------
# EMPLOYEE MANAGEMENT
# ------------------------------------------------------------

def employee_list(request):
    """Display all employees with branch and role names."""
    rows = call_procedure('sp_get_all_employees')
    return render(request, 'core/employee_list.html', {'employees': rows})

def employee_add(request):
    """Insert a new employee."""
    if request.method == 'POST':
        # Collect data from POST
        full_name = request.POST.get('full_name')
        national_code = request.POST.get('national_code')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', '')
        branch_id = request.POST.get('branch_id')
        role_id = request.POST.get('role_id')
        username = request.POST.get('username')
        password = request.POST.get('password')            # plain text
        acount_status = request.POST.get('acount_status', 1)

        try:
            call_procedure('sp_insert_employee', [
                full_name,
                national_code,
                phone_number,
                email,
                branch_id,
                role_id,
                username,
                password,               # procedure will hash it
                acount_status
            ])
            messages.success(request, 'Employee added successfully.')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error adding employee: {e}')

    # GET: show empty form
    branches = call_procedure('sp_get_all_branches')
    roles    = call_procedure('sp_get_all_roles')
    return render(request, 'core/employee_form.html', {
        'branches': branches,
        'roles': roles,
    })

def employee_edit(request, pk):
    """Edit an existing employee."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        national_code = request.POST.get('national_code')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', '')
        branch_id = request.POST.get('branch_id')
        role_id = request.POST.get('role_id')
        username = request.POST.get('username')
        password = request.POST.get('password') or None   # keep old if blank
        acount_status = request.POST.get('acount_status', 1)

        try:
            call_procedure('sp_update_employee', [
                pk,
                full_name,
                national_code,
                phone_number,
                email,
                branch_id,
                role_id,
                username,
                password,    # None → keep old password
                acount_status
            ])
            messages.success(request, 'Employee updated.')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error updating employee: {e}')

    # GET: fetch existing data and pre‑fill form
    rows = call_procedure('sp_get_employee_by_id', pk)
    employee = rows[0] if rows else None
    if not employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_list')
    else:
        rows = call_procedure('sp_get_employee_by_id', pk)
        employee = rows[0] if rows else None
        if not employee:
            messages.error(request, 'Employee not found.')
            return redirect('employee_list')

        # ADD THESE TWO LINES
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

# ------------------------------------------------------------
# BRANCH MANAGEMENT
# ------------------------------------------------------------

def branch_list(request):
    rows = call_procedure('sp_get_all_branches')
    return render(request, 'core/branch_list.html', {'branches': rows})

def branch_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_branch', [
                request.POST.get('name'),
                int(request.POST.get('is_headquarter', 0)),
                request.POST.get('email', ''),
                request.POST.get('phone_number', ''),
                request.POST.get('address', ''),
                int(request.POST.get('city_id')),
                int(request.POST.get('status', 1))
            ])
            messages.success(request, 'Branch added.')
            return redirect('branch_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/branch_form.html')

def branch_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_branch', [
                pk,
                request.POST.get('name'),
                int(request.POST.get('is_headquarter', 0)),
                request.POST.get('email', ''),
                request.POST.get('phone_number', ''),
                request.POST.get('address', ''),
                int(request.POST.get('city_id')),
                int(request.POST.get('status', 1))
            ])
            messages.success(request, 'Branch updated.')
            return redirect('branch_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_branch_by_id', pk)
        branch = rows[0] if rows else None
        if not branch:
            messages.error(request, 'Branch not found.')
            return redirect('branch_list')
        return render(request, 'core/branch_form.html', {'branch': branch})

def branch_delete(request, pk):
    rows = call_procedure('sp_get_branch_by_id', pk)
    branch = rows[0] if rows else None
    if not branch:
        messages.error(request, 'Branch not found.')
        return redirect('branch_list')
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_branch', [pk])
            messages.success(request, 'Branch deleted.')
            return redirect('branch_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('branch_list')
    return render(request, 'core/branch_confirm_delete.html', {'branch': branch})

# ------------------------------------------------------------
# ROLE MANAGEMENT
# ------------------------------------------------------------

def role_list(request):
    rows = call_procedure('sp_get_all_roles')
    return render(request, 'core/role_list.html', {'roles': rows})

def role_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_role', [request.POST.get('name')])
            messages.success(request, 'Role added.')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/role_form.html')

def role_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_role', [pk, request.POST.get('name')])
            messages.success(request, 'Role updated.')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_all_roles')
        role = next((r for r in rows if r['id'] == pk), None)  # since we don't have a sp_get_role_by_id
        if not role:
            messages.error(request, 'Role not found.')
            return redirect('role_list')
        return render(request, 'core/role_form.html', {'role': role})

def role_delete(request, pk):
    rows = call_procedure('sp_get_all_roles')
    role = next((r for r in rows if r['id'] == pk), None)
    if not role:
        messages.error(request, 'Role not found.')
        return redirect('role_list')
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_role', [pk])
            messages.success(request, 'Role deleted.')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('role_list')
    return render(request, 'core/role_confirm_delete.html', {'role': role})

# ------------------------------------------------------------
# ACCOUNT TYPE MANAGEMENT
# ------------------------------------------------------------

def account_type_list(request):
    rows = call_procedure('sp_get_all_account_types')
    return render(request, 'core/account_type_list.html', {'account_types': rows})

def account_type_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_account_type', [
                request.POST.get('name'),
                request.POST.get('interest_rate')
            ])
            messages.success(request, 'Account type added.')
            return redirect('account_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/account_type_form.html')

def account_type_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_account_type', [
                pk,
                request.POST.get('name'),
                request.POST.get('interest_rate')
            ])
            messages.success(request, 'Account type updated.')
            return redirect('account_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_all_account_types')
        account_type = next((t for t in rows if t['id'] == pk), None)
        if not account_type:
            messages.error(request, 'Account type not found.')
            return redirect('account_type_list')
        return render(request, 'core/account_type_form.html', {'account_type': account_type})

def account_type_delete(request, pk):
    rows = call_procedure('sp_get_all_account_types')
    account_type = next((t for t in rows if t['id'] == pk), None)
    if not account_type:
        messages.error(request, 'Account type not found.')
        return redirect('account_type_list')
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_account_type', [pk])
            messages.success(request, 'Account type deleted.')
            return redirect('account_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('account_type_list')
    return render(request, 'core/account_type_confirm_delete.html', {'account_type': account_type})

# ------------------------------------------------------------
# LOAN TYPE MANAGEMENT
# ------------------------------------------------------------

def loan_type_list(request):
    rows = call_procedure('sp_get_all_loan_types')
    return render(request, 'core/loan_type_list.html', {'loan_types': rows})

def loan_type_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_loan_type', [
                request.POST.get('name'),
                request.POST.get('max_amount'),
                request.POST.get('annual_interest_rate'),
                request.POST.get('max_installments')
            ])
            messages.success(request, 'Loan type added.')
            return redirect('loan_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/loan_type_form.html')

def loan_type_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_loan_type', [
                pk,
                request.POST.get('name'),
                request.POST.get('max_amount'),
                request.POST.get('annual_interest_rate'),
                request.POST.get('max_installments')
            ])
            messages.success(request, 'Loan type updated.')
            return redirect('loan_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_all_loan_types')
        loan_type = next((t for t in rows if t['id'] == pk), None)
        if not loan_type:
            messages.error(request, 'Loan type not found.')
            return redirect('loan_type_list')
        return render(request, 'core/loan_type_form.html', {'loan_type': loan_type})

def loan_type_delete(request, pk):
    rows = call_procedure('sp_get_all_loan_types')
    loan_type = next((t for t in rows if t['id'] == pk), None)
    if not loan_type:
        messages.error(request, 'Loan type not found.')
        return redirect('loan_type_list')
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_loan_type', [pk])
            messages.success(request, 'Loan type deleted.')
            return redirect('loan_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('loan_type_list')
    return render(request, 'core/loan_type_confirm_delete.html', {'loan_type': loan_type})