from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one
from core.decorators import login_required, role_required

@login_required
@role_required('System Admin')
def country_list(request):
    rows = call_procedure('sp_get_all_countries')
    return render(request, 'core/country_list.html', {'countries': rows})

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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
