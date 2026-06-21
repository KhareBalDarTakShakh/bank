from django.shortcuts import render, redirect
from django.contrib import messages
from ..utils import call_procedure, execute_query
from ..decorators import customer_login_required


# ---------- Authentication ----------
def customer_login_view(request):
    """Authenticate a bank customer."""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        try:
            rows = call_procedure('sp_authenticate_customer', username, password)
            if rows:
                user = rows[0]
                request.session['customer'] = {
                    'id': user['id'],
                    'full_name': user['full_name'],
                    'national_code': user['national_code'],
                    'username': user['username'],
                }
                messages.success(request, f'Welcome, {user["full_name"]}!')
                return redirect('customer_dashboard')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/customer_login.html')


def customer_logout_view(request):
    """Logout customer and clear session."""
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('customer_login')


# ---------- Dashboard & Accounts ----------
@customer_login_required
def customer_dashboard(request):
    """Customer home page with summary."""
    customer = request.session['customer']
    # Get total balance
    rows = call_procedure('sp_get_accounts_by_customer', customer['id'])
    total_balance = sum(float(acc['balance']) for acc in rows) if rows else 0
    return render(request, 'core/customer_dashboard.html', {
        'customer': customer,
        'accounts': rows,
        'total_balance': total_balance,
    })


@customer_login_required
def my_accounts(request):
    """List all accounts of the logged-in customer."""
    customer = request.session['customer']
    rows = call_procedure('sp_get_accounts_by_customer', customer['id'])
    return render(request, 'core/my_accounts.html', {
        'accounts': rows,
    })


# ---------- Transactions ----------
@customer_login_required
def my_transactions(request, account_id):
    """View transactions for a specific account (must belong to the customer)."""
    customer = request.session['customer']

    # Ownership check
    acc_rows = execute_query(
        "SELECT id, account_number FROM account WHERE id = %s AND customer_id = %s",
        [account_id, customer['id']]
    )
    if not acc_rows:
        messages.error(request, 'Account not found or access denied.')
        return redirect('customer_dashboard')

    account = acc_rows[0]
    page = int(request.GET.get('page', 1))
    limit = 20
    offset = (page - 1) * limit

    transactions = call_procedure('sp_get_transactions', account_id, limit, offset)
    return render(request, 'core/my_transactions.html', {
        'account': account,
        'transactions': transactions,
        'page': page,
    })


# ---------- Transfer ----------
@customer_login_required
def my_transfer(request):
    """Transfer money from one of the customer's accounts to another account."""
    customer = request.session['customer']
    my_accounts = call_procedure('sp_get_accounts_by_customer', customer['id'])

    if request.method == 'POST':
        from_account_id = int(request.POST.get('from_account_id'))
        to_account_number = request.POST.get('to_account_number', '').strip()
        amount = request.POST.get('amount')

        # Verify that the from_account belongs to the customer
        owner_check = execute_query(
            "SELECT id FROM account WHERE id = %s AND customer_id = %s",
            [from_account_id, customer['id']]
        )
        if not owner_check:
            messages.error(request, 'Invalid source account.')
            return redirect('my_transfer')

        # Lookup destination account
        to_account = execute_query(
            "SELECT id FROM account WHERE account_number = %s",
            [to_account_number]
        )
        if not to_account:
            messages.error(request, f'Account number "{to_account_number}" not found.')
            return redirect('my_transfer')

        to_account_id = to_account[0]['id']

        try:
            call_procedure('sp_transfer',
                from_account_id, to_account_id, amount,
                'Customer transfer', 1, 'transfer'  # created_by = 1 (system or treasury)
            )
            messages.success(request, 'Transfer completed.')
            return redirect('my_transfer')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/my_transfer.html', {
        'accounts': my_accounts,
    })


# ---------- Loans ----------
@customer_login_required
def my_loans(request):
    """View all loans of the customer."""
    customer = request.session['customer']
    loans = call_procedure('sp_get_customer_loans', customer['id'])
    return render(request, 'core/my_loans.html', {
        'loans': loans,
    })


@customer_login_required
def request_loan(request):
    """Customer submits a loan request directly."""
    customer = request.session['customer']
    loan_types = call_procedure('sp_get_all_loan_types')

    if request.method == 'POST':
        loan_type_id = int(request.POST.get('loan_type_id'))
        amount = request.POST.get('amount')
        installments = int(request.POST.get('installments'))

        try:
            call_procedure('sp_submit_loan_request',
                customer['id'], loan_type_id, amount, installments,
                1  # system operator id (could be fixed as system)
            )
            messages.success(request, 'Loan request submitted.')
            return redirect('my_loans')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/request_loan.html', {
        'loan_types': loan_types,
    })

@customer_login_required
def my_loan_installments(request, loan_id):
    """View installments for a specific loan that belongs to the customer."""
    customer = request.session['customer']

    # Verify loan exists and belongs to this customer
    loan_info = execute_query(
        """SELECT lr.id, lr.amount, lr.installments, lr.status,
                  lt.name AS loan_type_name, lt.annual_interest_rate
           FROM loan_request lr
           JOIN loan_type lt ON lr.loan_type_id = lt.id
           WHERE lr.id = %s AND lr.customer_id = %s""",
        [loan_id, customer['id']]
    )
    if not loan_info:
        messages.error(request, 'Loan not found or access denied.')
        return redirect('my_loans')

    loan = loan_info[0]
    installments = call_procedure('sp_get_loan_installments', loan_id)

    return render(request, 'core/my_loan_installments.html', {
        'loan': loan,
        'installments': installments,
    })


@customer_login_required
def customer_pay_installment(request, installment_id):
    """Pay a specific installment (mark as paid)."""
    if request.method == 'POST':
        customer = request.session['customer']
        amount = request.POST.get('amount')
        loan_id = request.POST.get('loan_id')

        # Verify that the installment belongs to a loan that belongs to this customer
        owner_check = execute_query(
            """SELECT i.id FROM installment i
               JOIN loan_request lr ON i.loan_request_id = lr.id
               WHERE i.id = %s AND lr.customer_id = %s""",
            [installment_id, customer['id']]
        )
        if not owner_check:
            messages.error(request, 'Installment not found or access denied.')
            return redirect('my_loans')

        try:
            call_procedure('sp_pay_installment', installment_id, amount)
            messages.success(request, 'Installment paid successfully.')
        except Exception as e:
            messages.error(request, str(e))

        if loan_id:
            return redirect('my_loan_installments', loan_id=loan_id)
    return redirect('my_loans')