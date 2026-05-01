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

# ------------------------------------------------------------
# BRANCH MANAGEMENT
# ------------------------------------------------------------

def branch_list(request):
    rows = call_procedure('sp_get_all_branches')
    return render(request, 'core/branch_list.html', {'branches': rows})

def branch_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_branch',
                request.POST.get('name'),
                int(request.POST.get('is_headquarter', 0)),
                request.POST.get('email', ''),
                request.POST.get('phone_number', ''),
                request.POST.get('address', ''),
                int(request.POST.get('city_id')),
                int(request.POST.get('status', 1))
            )
            messages.success(request, 'Branch added.')
            return redirect('branch_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    cities = call_procedure('sp_get_all_cities')
    return render(request, 'core/branch_form.html', {'cities': cities})

def branch_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_branch',
                pk,
                request.POST.get('name'),
                int(request.POST.get('is_headquarter', 0)),
                request.POST.get('email', ''),
                request.POST.get('phone_number', ''),
                request.POST.get('address', ''),
                int(request.POST.get('city_id')),
                int(request.POST.get('status', 1))
            )
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
        cities = call_procedure('sp_get_all_cities')
        return render(request, 'core/branch_form.html', {
            'branch': branch,
            'cities': cities
        })

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
            call_procedure('sp_insert_role', request.POST.get('name'))
            messages.success(request, 'Role added.')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/role_form.html')

def role_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_role', pk, request.POST.get('name'))
            messages.success(request, 'Role updated.')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_all_roles')
        role = next((r for r in rows if r['id'] == pk), None)
        if not role:
            messages.error(request, 'Role not found.')
            return redirect('role_list')
        return render(request, 'core/role_form.html', {'role': role})

def role_delete(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_role', pk)
            messages.success(request, 'Role deleted.')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('role_list')
    else:
        rows = call_procedure('sp_get_all_roles')
        role = next((r for r in rows if r['id'] == pk), None)
        if not role:
            messages.error(request, 'Role not found.')
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
            call_procedure('sp_insert_account_type',
                request.POST.get('name'),
                request.POST.get('interest_rate')
            )
            messages.success(request, 'Account type added.')
            return redirect('account_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/account_type_form.html')

def account_type_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_account_type',
                pk,
                request.POST.get('name'),
                request.POST.get('interest_rate')
            )
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
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_account_type', pk)
            messages.success(request, 'Account type deleted.')
            return redirect('account_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('account_type_list')
    else:
        rows = call_procedure('sp_get_all_account_types')
        account_type = next((t for t in rows if t['id'] == pk), None)
        if not account_type:
            messages.error(request, 'Account type not found.')
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
            call_procedure('sp_insert_loan_type',
                request.POST.get('name'),
                request.POST.get('max_amount'),
                request.POST.get('annual_interest_rate'),
                request.POST.get('max_installments')
            )
            messages.success(request, 'Loan type added.')
            return redirect('loan_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/loan_type_form.html')

def loan_type_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_loan_type',
                pk,
                request.POST.get('name'),
                request.POST.get('max_amount'),
                request.POST.get('annual_interest_rate'),
                request.POST.get('max_installments')
            )
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
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_loan_type', pk)
            messages.success(request, 'Loan type deleted.')
            return redirect('loan_type_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('loan_type_list')
    else:
        rows = call_procedure('sp_get_all_loan_types')
        loan_type = next((t for t in rows if t['id'] == pk), None)
        if not loan_type:
            messages.error(request, 'Loan type not found.')
            return redirect('loan_type_list')
        return render(request, 'core/loan_type_confirm_delete.html', {'loan_type': loan_type})

# ------------------------------------------------------------
# GEOGRAPHIC MANAGEMENT
# ------------------------------------------------------------

# ---- Country ----
def country_list(request):
    rows = call_procedure('sp_get_all_countries')
    return render(request, 'core/country_list.html', {'countries': rows})

def country_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_country',
                request.POST.get('name'),
                request.POST.get('iso_code')
            )   # directly, no list
            messages.success(request, 'Country added.')
            return redirect('country_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'core/country_form.html')

def country_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_country',
                pk,
                request.POST.get('name'),
                request.POST.get('iso_code')
            )
            messages.success(request, 'Country updated.')
            return redirect('country_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_country_by_id', pk)
        country = rows[0] if rows else None
        if not country:
            messages.error(request, 'Country not found.')
            return redirect('country_list')
        return render(request, 'core/country_form.html', {'country': country})

def country_delete(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_country', pk)
            messages.success(request, 'Country deleted.')
            return redirect('country_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('country_list')
    else:
        rows = call_procedure('sp_get_country_by_id', pk)
        country = rows[0] if rows else None
        if not country:
            messages.error(request, 'Country not found.')
            return redirect('country_list')
        return render(request, 'core/country_confirm_delete.html', {'country': country})

# ---- Province ----
def province_list(request):
    rows = call_procedure('sp_get_all_provinces')
    return render(request, 'core/province_list.html', {'provinces': rows})

def province_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_province',
                request.POST.get('name'),
                int(request.POST.get('country_id'))
            )
            messages.success(request, 'Province added.')
            return redirect('province_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    countries = call_procedure('sp_get_all_countries')
    return render(request, 'core/province_form.html', {'countries': countries})


def province_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_province',
                pk,
                request.POST.get('name'),
                int(request.POST.get('country_id'))
            )
            messages.success(request, 'Province updated.')
            return redirect('province_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_province_by_id', pk)
        province = rows[0] if rows else None
        if not province:
            messages.error(request, 'Province not found.')
            return redirect('province_list')
        countries = call_procedure('sp_get_all_countries')
        return render(request, 'core/province_form.html', {
            'province': province,
            'countries': countries
        })

def province_delete(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_province', pk)
            messages.success(request, 'Province deleted.')
            return redirect('province_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('province_list')
    else:
        rows = call_procedure('sp_get_all_provinces')
        province = next((p for p in rows if p['id'] == pk), None)
        if not province:
            messages.error(request, 'Province not found.')
            return redirect('province_list')
        return render(request, 'core/province_confirm_delete.html', {'province': province})
    
# ---- City ----
def city_list(request):
    rows = call_procedure('sp_get_all_cities')
    return render(request, 'core/city_list.html', {'cities': rows})

def city_add(request):
    if request.method == 'POST':
        try:
            call_procedure('sp_insert_city',
                request.POST.get('name'),
                int(request.POST.get('province_id'))
            )
            messages.success(request, 'City added.')
            return redirect('city_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    provinces = call_procedure('sp_get_all_provinces')
    return render(request, 'core/city_form.html', {'provinces': provinces})

def city_edit(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_update_city',
                pk,
                request.POST.get('name'),
                int(request.POST.get('province_id'))
            )
            messages.success(request, 'City updated.')
            return redirect('city_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        rows = call_procedure('sp_get_city_by_id', pk)
        city = rows[0] if rows else None
        if not city:
            messages.error(request, 'City not found.')
            return redirect('city_list')
        provinces = call_procedure('sp_get_all_provinces')
        return render(request, 'core/city_form.html', {
            'city': city,
            'provinces': provinces
        })

def city_delete(request, pk):
    if request.method == 'POST':
        try:
            call_procedure('sp_delete_city', pk)
            messages.success(request, 'City deleted.')
            return redirect('city_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('city_list')
    else:
        rows = call_procedure('sp_get_all_cities')
        city = next((c for c in rows if c['id'] == pk), None)
        if not city:
            messages.error(request, 'City not found.')
            return redirect('city_list')
        return render(request, 'core/city_confirm_delete.html', {'city': city})
    