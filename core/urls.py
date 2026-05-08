from django.urls import path
from .views import account_type, auth, branch, city, country, employee, loan_type, province, role

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
]