from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, execute_query
from core.decorators import login_required, role_required


# ---------- helper ----------
def _get_account_by_number(account_number):
    """
    Returns a dict with id, balance, status for the given account_number,
    or raises an error message to be shown to the user.
    """
    rows = execute_query(
        "SELECT id, balance, status FROM account WHERE account_number = %s",
        [account_number]
    )
    if not rows:
        raise ValueError(f"Account number '{account_number}' not found.")
    return rows[0]


# ------------------------------------------------------------
# TRANSFER
# ------------------------------------------------------------
@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def transfer_view(request):
    """Transfer money between two customer accounts."""
    if request.method == 'POST':
        from_number = request.POST.get('from_account', '').strip()
        to_number = request.POST.get('to_account', '').strip()
        amount = request.POST.get('amount', '')
        description = request.POST.get('description', '')
        employee_id = request.session['employee']['id']

        try:
            from_account = _get_account_by_number(from_number)
            to_account   = _get_account_by_number(to_number)

            rows = call_procedure('sp_transfer',
                from_account['id'],
                to_account['id'],
                amount,
                description,
                employee_id,
                'transfer'
            )
            txn = rows[0] if rows else {}
            messages.success(request,
                f"Transfer completed. Transaction ID: {txn.get('transaction_id')}, "
                f"Amount: {txn.get('amount')}")
            return redirect('transfer')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/transaction_form.html', {
        'type': 'transfer',
        'title': 'Transfer Money'
    })


# ------------------------------------------------------------
# DEPOSIT
# ------------------------------------------------------------
@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def deposit_view(request):
    """Deposit cash into a customer account from the branch vault."""
    if request.method == 'POST':
        to_number = request.POST.get('to_account', '').strip()
        amount = request.POST.get('amount', '')
        description = request.POST.get('description', '')
        employee = request.session['employee']
        employee_id = employee['id']
        branch_id = employee['branch_id']

        try:
            to_account = _get_account_by_number(to_number)

            call_procedure('sp_deposit',
                to_account['id'],
                amount,
                branch_id,
                employee_id,
                description
            )
            messages.success(request, f"Deposit completed. Amount: {amount}")
            return redirect('deposit')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/transaction_form.html', {
        'type': 'deposit',
        'title': 'Cash Deposit'
    })


# ------------------------------------------------------------
# WITHDRAWAL
# ------------------------------------------------------------
@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def withdrawal_view(request):
    """Withdraw cash from a customer account to the branch vault."""
    if request.method == 'POST':
        from_number = request.POST.get('from_account', '').strip()
        amount = request.POST.get('amount', '')
        description = request.POST.get('description', '')
        employee = request.session['employee']
        employee_id = employee['id']
        branch_id = employee['branch_id']

        try:
            from_account = _get_account_by_number(from_number)

            call_procedure('sp_withdrawal',
                from_account['id'],
                amount,
                branch_id,
                employee_id,
                description
            )
            messages.success(request, f"Withdrawal completed. Amount: {amount}")
            return redirect('withdrawal')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/transaction_form.html', {
        'type': 'withdrawal',
        'title': 'Cash Withdrawal'
    })


# ------------------------------------------------------------
# TRANSACTION HISTORY
# ------------------------------------------------------------
@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def transaction_history(request, account_id):
    """View transaction history for a specific account."""
    # Optional: get customer info for breadcrumbs
    acc_rows = execute_query(
        "SELECT a.*, c.full_name FROM account a JOIN customer c ON a.customer_id = c.id WHERE a.id = %s",
        [account_id]
    )
    if not acc_rows:
        messages.error(request, 'Account not found.')
        return redirect('home')

    account = acc_rows[0]

    # Get pagination parameters (optional)
    page = int(request.GET.get('page', 1))
    limit = 20
    offset = (page - 1) * limit

    rows = call_procedure('sp_get_transactions', account_id, limit, offset)
    return render(request, 'core/transaction_history.html', {
        'account': account,
        'transactions': rows,
        'page': page
    })


# ------------------------------------------------------------
# BRANCH REPORT
# ------------------------------------------------------------
@login_required
@role_required('Branch Manager', 'System Admin')
def branch_report(request):
    employee = request.session['employee']
    branch_id = employee['branch_id']

    # Fetch branch name
    branch_rows = execute_query("SELECT name FROM branch WHERE id = %s", [branch_id])
    branch_name = branch_rows[0]['name'] if branch_rows else 'Unknown'

    try:
        rows = call_procedure('sp_get_branch_report', branch_id)
        report = rows[0] if rows else {}
    except Exception as e:
        messages.error(request, str(e))
        report = {}

    return render(request, 'core/branch_report.html', {
        'report': report,
        'branch_id': branch_id,
        'branch_name': branch_name,
    })
