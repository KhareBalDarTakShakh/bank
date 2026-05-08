from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one

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
