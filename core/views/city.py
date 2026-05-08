from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one

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
