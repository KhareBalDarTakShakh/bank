from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one
from core.decorators import login_required, role_required

@login_required
@role_required('System Admin')
def loan_type_list(request):
    rows = call_procedure('sp_get_all_loan_types')
    return render(request, 'core/loan_type_list.html', {'loan_types': rows})

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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
