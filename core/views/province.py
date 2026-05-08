from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one
from core.decorators import login_required, role_required

@login_required
@role_required('System Admin')
def province_list(request):
    rows = call_procedure('sp_get_all_provinces')
    return render(request, 'core/province_list.html', {'provinces': rows})

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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

@login_required
@role_required('System Admin')
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
