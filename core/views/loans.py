from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, execute_query
from core.decorators import login_required, role_required
from datetime import date


@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def loan_request(request):
    """Employee submits a loan request on behalf of a customer."""
    # Fetch dropdown data
    customers = call_procedure('sp_search_customers', '')  # recent customers
    loan_types = call_procedure('sp_get_all_loan_types')

    # Pre‑select customer if coming from profile (optional)
    preselected_customer_id = request.GET.get('customer_id')

    if request.method == 'POST':
        customer_id = int(request.POST.get('customer_id'))
        loan_type_id = int(request.POST.get('loan_type_id'))
        amount = request.POST.get('amount')
        installments = int(request.POST.get('installments'))
        employee_id = request.session['employee']['id']

        try:
            rows = call_procedure('sp_submit_loan_request',
                customer_id,
                loan_type_id,
                amount,
                installments,
                employee_id
            )
            loan_id = rows[0]['loan_request_id'] if rows else None
            messages.success(request, f'Loan request submitted. ID: {loan_id}')
            return redirect('loan_request')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'core/loan_request_form.html', {
        'customers': customers,
        'loan_types': loan_types,
        'preselected_customer_id': preselected_customer_id,
    })


@login_required
@role_required('Branch Manager', 'System Admin')
def loan_approval_queue(request):
    """Manager views pending loan requests."""
    rows = call_procedure('sp_get_pending_loans')
    return render(request, 'core/loan_approval_queue.html', {
        'pending_loans': rows
    })


@login_required
@role_required('Branch Manager', 'System Admin')
def loan_approve(request, loan_id):
    """Manager approves a loan request (generates installments)."""
    employee_id = request.session['employee']['id']
    try:
        result = call_procedure('sp_approve_loan', loan_id, employee_id)
        info = result[0] if result else {}
        messages.success(request,
            f'Loan approved. Monthly payment: {info.get("monthly_payment")}, '
            f'Total installments: {info.get("total_installments")}')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('loan_approval_queue')


@login_required
@role_required('Branch Manager', 'System Admin')
def loan_reject(request, loan_id):
    """Manager rejects a loan request."""
    employee_id = request.session['employee']['id']
    try:
        call_procedure('sp_reject_loan', loan_id, employee_id)
        messages.success(request, 'Loan rejected.')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('loan_approval_queue')


@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def customer_loans(request, customer_id):
    """View all loans for a specific customer."""
    # Fetch customer details
    cust_rows = call_procedure('sp_get_customer_by_id', customer_id)
    customer = cust_rows[0] if cust_rows else None
    if not customer:
        messages.error(request, 'Customer not found.')
        return redirect('customer_search')

    # Fetch loans
    loan_rows = call_procedure('sp_get_customer_loans', customer_id)

    return render(request, 'core/customer_loans.html', {
        'customer': customer,
        'loans': loan_rows,
    })


@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def loan_installments(request, loan_id):
    """View installments for a specific loan request."""
    # Quick query to get loan and customer info (avoid extra procedures)
    loan_info = execute_query(
        """SELECT lr.id, lr.amount, lr.installments, lr.status,
                  lt.name AS loan_type_name, lt.annual_interest_rate,
                  c.full_name AS customer_name, c.id AS customer_id
           FROM loan_request lr
           JOIN loan_type lt ON lr.loan_type_id = lt.id
           JOIN customer c ON lr.customer_id = c.id
           WHERE lr.id = %s""",
        [loan_id]
    )
    if not loan_info:
        messages.error(request, 'Loan not found.')
        return redirect('home')
    loan = loan_info[0]

    installments = call_procedure('sp_get_loan_installments', loan_id)

    return render(request, 'core/loan_installments.html', {
        'loan': loan,
        'installments': installments,
        'today': date.today(),
    })


@login_required
@role_required('Teller', 'Branch Manager', 'System Admin')
def pay_installment(request, installment_id):
    """Employee marks an installment as paid."""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            call_procedure('sp_pay_installment', installment_id, amount)
            messages.success(request, 'Installment paid.')
        except Exception as e:
            messages.error(request, str(e))
        # Redirect back to the loan installments page
        loan_id = request.POST.get('loan_id')
        if loan_id:
            return redirect('loan_installments', loan_id=loan_id)
    return redirect('home')
