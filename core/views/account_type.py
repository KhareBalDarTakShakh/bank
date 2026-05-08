from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one
from core.decorators import login_required, role_required

@login_required
@role_required('System Admin')
def account_type_list(request):
    rows = call_procedure('sp_get_all_account_types')
    return render(request, 'core/account_type_list.html', {'account_types': rows})

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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
