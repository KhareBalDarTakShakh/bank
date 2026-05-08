from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one
from core.decorators import login_required, role_required

@login_required
@role_required('System Admin')
def branch_list(request):
    rows = call_procedure('sp_get_all_branches')
    return render(request, 'core/branch_list.html', {'branches': rows})

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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
