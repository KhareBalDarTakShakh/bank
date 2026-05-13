from django.shortcuts import render, redirect
from django.contrib import messages
from ..utils import call_procedure, execute_query
from ..decorators import login_required, role_required

@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def account_open(request, customer_id):
    """
    Open a new account for a given customer.
    """
    if request.method == 'POST':
        account_type_id = int(request.POST.get('account_type_id'))
        initial_balance = request.POST.get('initial_balance', '0')
        opened_by = request.session['employee']['id']

        try:
            rows = call_procedure('sp_open_account',
                customer_id,
                account_type_id,
                initial_balance,
                opened_by
            )
            new_account = rows[0]
            messages.success(request, f"Account opened successfully. Account number: {new_account.get('new_account_id')}")
        except Exception as e:
            messages.error(request, str(e))

    return redirect('customer_profile', pk=customer_id)

@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def issue_card(request, account_id):
    """
    Issue a new card for the given account, then redirect back to the customer's profile.
    """
    if request.method == 'POST':
        # Retrieve customer_id from account table (or a hidden field in form)
        # We can use a simple query
        acc_rows = execute_query("SELECT customer_id FROM account WHERE id = %s", [account_id])
        if not acc_rows:
            messages.error(request, 'Account not found.')
            return redirect('customer_search')

        customer_id = acc_rows[0]['customer_id']

        try:
            rows = call_procedure('sp_issue_card', account_id)
            card_info = rows[0]
            messages.success(request,
                f"Card issued. Number: {card_info['card_number']}, CVV2: {card_info['cvv2']}")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('customer_profile', pk=customer_id)

    # If GET, just redirect to home (should be POST only)
    return redirect('home')
