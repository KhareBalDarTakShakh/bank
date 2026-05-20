from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure
from core.decorators import login_required, role_required

@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def customer_search(request):
    """Search customers by name or national code."""
    query = request.GET.get('q', '').strip()
    rows = call_procedure('sp_search_customers', query)
    return render(request, 'core/customer_search.html', {
        'customers': rows,
        'query': query
    })

@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def customer_add(request):
    """Register a new customer."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        national_code = request.POST.get('national_code', '')
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        registered_by = request.session['employee']['id']

        try:
            # sp_register_customer returns the new ID in a result set
            rows = call_procedure('sp_register_customer',
                full_name, national_code, phone_number, address, registered_by
            )
            new_id = rows[0]['new_customer_id'] if rows else None
            messages.success(request, f'Customer registered with ID {new_id}.')
            return redirect('customer_profile', pk=new_id)
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/customer_form.html')

@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def customer_profile(request, pk):
    """Show customer details, accounts, and cards."""
    # Fetch customer info
    cust_rows = call_procedure('sp_get_customer_by_id', pk)
    customer = cust_rows[0] if cust_rows else None
    if not customer:
        messages.error(request, 'Customer not found.')
        return redirect('customer_search')

    # Fetch accounts for this customer
    account_rows = call_procedure('sp_get_accounts_by_customer', pk)

    # For each account, fetch cards (we’ll do this in a loop – could be a dedicated procedure later)
    accounts = []
    for acc in account_rows:
        card_rows = call_procedure('sp_get_cards_by_account', acc['id'])
        accounts.append({
            'id': acc['id'],
            'account_number': acc['account_number'],
            'account_type_name': acc['account_type_name'],
            'balance': acc['balance'],
            'status': acc['status'],
            'opening_date': acc['opening_date'],
            'cards': card_rows
        })

    account_types = call_procedure('sp_get_all_account_types')

    return render(request, 'core/customer_profile.html', {
        'customer': customer,
        'accounts': accounts,
        'account_types': account_types,
    })

@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def customer_edit(request, pk):
    """Edit customer details and toggle active status."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        is_active = int(request.POST.get('is_active', 1))

        try:
            call_procedure('sp_update_customer', pk, full_name, phone_number, address, is_active)
            messages.success(request, 'Customer updated.')
            return redirect('customer_profile', pk=pk)
        except Exception as e:
            messages.error(request, str(e))
    else:
        cust_rows = call_procedure('sp_get_customer_by_id', pk)
        customer = cust_rows[0] if cust_rows else None
        if not customer:
            messages.error(request, 'Customer not found.')
            return redirect('customer_search')

        return render(request, 'core/customer_form.html', {'customer': customer})

@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def customer_toggle_active(request, pk):
    """Toggle customer active status from profile page."""
    if request.method == 'POST':
        cust_rows = call_procedure('sp_get_customer_by_id', pk)
        customer = cust_rows[0] if cust_rows else None
        if not customer:
            messages.error(request, 'Customer not found.')
            return redirect('customer_search')

        new_status = 0 if customer['is_active'] == 1 else 1
        try:
            call_procedure('sp_update_customer', pk, customer['full_name'],
                           customer['phone_number'], customer['address'], new_status)
            messages.success(request, f'Customer {"activated" if new_status else "deactivated"}.')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('customer_profile', pk=pk)
