from django.urls import path
from . import views

urlpatterns = [
    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/edit/<int:pk>/', views.employee_edit, name='employee_edit'),
    path('employees/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    # Branches
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/add/', views.branch_add, name='branch_add'),
    path('branches/edit/<int:pk>/', views.branch_edit, name='branch_edit'),
    path('branches/delete/<int:pk>/', views.branch_delete, name='branch_delete'),
    # Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/add/', views.role_add, name='role_add'),
    path('roles/edit/<int:pk>/', views.role_edit, name='role_edit'),
    path('roles/delete/<int:pk>/', views.role_delete, name='role_delete'),
    # Account Types
    path('account-types/', views.account_type_list, name='account_type_list'),
    path('account-types/add/', views.account_type_add, name='account_type_add'),
    path('account-types/edit/<int:pk>/', views.account_type_edit, name='account_type_edit'),
    path('account-types/delete/<int:pk>/', views.account_type_delete, name='account_type_delete'),
    # Loan Types
    path('loan-types/', views.loan_type_list, name='loan_type_list'),
    path('loan-types/add/', views.loan_type_add, name='loan_type_add'),
    path('loan-types/edit/<int:pk>/', views.loan_type_edit, name='loan_type_edit'),
    path('loan-types/delete/<int:pk>/', views.loan_type_delete, name='loan_type_delete'),
    # Geographic
    path('countries/', views.country_list, name='country_list'),
    path('countries/add/', views.country_add, name='country_add'),
    path('countries/edit/<int:pk>/', views.country_edit, name='country_edit'),
    path('countries/delete/<int:pk>/', views.country_delete, name='country_delete'),

    path('provinces/', views.province_list, name='province_list'),
    path('provinces/add/', views.province_add, name='province_add'),
    path('provinces/edit/<int:pk>/', views.province_edit, name='province_edit'),
    path('provinces/delete/<int:pk>/', views.province_delete, name='province_delete'),

    path('cities/', views.city_list, name='city_list'),
    path('cities/add/', views.city_add, name='city_add'),
    path('cities/edit/<int:pk>/', views.city_edit, name='city_edit'),
    path('cities/delete/<int:pk>/', views.city_delete, name='city_delete'),
]