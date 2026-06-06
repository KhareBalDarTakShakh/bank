from django.urls import path
from .views import (
    account_type,
    auth,
    branch,
    city,
    country,
    employee,
    loan_type,
    province,
    role,
    teller,
    accounts,
    transactions,
    loans,
    reports,
)

urlpatterns = [
    path('', branch.branch_list, name='home'),

    # Employees
    path('employees/', employee.employee_list, name='employee_list'),
    path('employees/add/', employee.employee_add, name='employee_add'),
    path('employees/edit/<int:pk>/', employee.employee_edit, name='employee_edit'),
    path('employees/delete/<int:pk>/', employee.employee_delete, name='employee_delete'),
    # Branches
    path('branches/', branch.branch_list, name='branch_list'),
    path('branches/add/', branch.branch_add, name='branch_add'),
    path('branches/edit/<int:pk>/', branch.branch_edit, name='branch_edit'),
    path('branches/delete/<int:pk>/', branch.branch_delete, name='branch_delete'),
    # Roles
    path('roles/', role.role_list, name='role_list'),
    path('roles/add/', role.role_add, name='role_add'),
    path('roles/edit/<int:pk>/', role.role_edit, name='role_edit'),
    path('roles/delete/<int:pk>/', role.role_delete, name='role_delete'),
    # Account Types
    path('account-types/', account_type.account_type_list, name='account_type_list'),
    path('account-types/add/', account_type.account_type_add, name='account_type_add'),
    path('account-types/edit/<int:pk>/', account_type.account_type_edit, name='account_type_edit'),
    path('account-types/delete/<int:pk>/', account_type.account_type_delete, name='account_type_delete'),
    # Loan Types
    path('loan-types/', loan_type.loan_type_list, name='loan_type_list'),
    path('loan-types/add/', loan_type.loan_type_add, name='loan_type_add'),
    path('loan-types/edit/<int:pk>/', loan_type.loan_type_edit, name='loan_type_edit'),
    path('loan-types/delete/<int:pk>/', loan_type.loan_type_delete, name='loan_type_delete'),
    # Geographic
    path('countries/', country.country_list, name='country_list'),
    path('countries/add/', country.country_add, name='country_add'),
    path('countries/edit/<int:pk>/', country.country_edit, name='country_edit'),
    path('countries/delete/<int:pk>/', country.country_delete, name='country_delete'),

    path('provinces/', province.province_list, name='province_list'),
    path('provinces/add/', province.province_add, name='province_add'),
    path('provinces/edit/<int:pk>/', province.province_edit, name='province_edit'),
    path('provinces/delete/<int:pk>/', province.province_delete, name='province_delete'),

    path('cities/', city.city_list, name='city_list'),
    path('cities/add/', city.city_add, name='city_add'),
    path('cities/edit/<int:pk>/', city.city_edit, name='city_edit'),
    path('cities/delete/<int:pk>/', city.city_delete, name='city_delete'),

    # Auth
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    path('dashboard/', auth.dashboard_redirect, name='dashboard'),
    path('dashboard/admin/', auth.dashboard_admin, name='dashboard_admin'),
    path('dashboard/manager/', auth.dashboard_manager, name='dashboard_manager'),
    path('dashboard/teller/', auth.dashboard_teller, name='dashboard_teller'),
    path('dashboard/home/', auth.dashboard_home, name='dashboard_home'),

    # Customer management (teller/manager/admin)
    path('customers/', teller.customer_search, name='customer_search'),
    path('customers/add/', teller.customer_add, name='customer_add'),
    path('customers/<int:pk>/', teller.customer_profile, name='customer_profile'),
    path('customers/<int:pk>/edit/', teller.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/toggle-active/', teller.customer_toggle_active, name='customer_toggle_active'),

    # Account / card operations
    path('accounts/open/<int:customer_id>/', accounts.account_open, name='account_open'),
    path('accounts/issue-card/<int:account_id>/', accounts.issue_card, name='issue_card'),
    path('cards/<int:card_id>/toggle-status/', accounts.toggle_card_status, name='toggle_card_status'),

    # Transactions
    path('transactions/transfer/', transactions.transfer_view, name='transfer'),
    path('transactions/deposit/', transactions.deposit_view, name='deposit'),
    path('transactions/withdrawal/', transactions.withdrawal_view, name='withdrawal'),
    path('accounts/<int:account_id>/transactions/', transactions.transaction_history, name='transaction_history'),
    path('branch/report/', transactions.branch_report, name='branch_report'),
    path('audit-logs/', transactions.audit_log_list, name='audit_log_list'),
    path('vaults/', transactions.vault_list, name='vault_list'),

    # ===== PHASE 6 – Loans =====
    path('loans/request/', loans.loan_request, name='loan_request'),
    path('loans/queue/', loans.loan_approval_queue, name='loan_approval_queue'),
    path('loans/approve/<int:loan_id>/', loans.loan_approve, name='loan_approve'),
    path('loans/reject/<int:loan_id>/', loans.loan_reject, name='loan_reject'),
    path('customers/<int:customer_id>/loans/', loans.customer_loans, name='customer_loans'),
    path('loans/<int:loan_id>/installments/', loans.loan_installments, name='loan_installments'),
    path('installments/pay/<int:installment_id>/', loans.pay_installment, name='pay_installment'),

    path('province/report/', reports.province_report, name='province_report'),
]