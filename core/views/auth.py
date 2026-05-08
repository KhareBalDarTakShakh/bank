from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import call_procedure, fetch_one

def login_view(request):
    """Authenticate employee using the database procedure."""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        try:
            rows = call_procedure('sp_authenticate_employee', username, password)
            if rows:
                user = rows[0]   # dict with id, full_name, branch_id, role_id, role_name, username
                # Store essential data in session
                request.session['employee'] = {
                    'id': user['id'],
                    'full_name': user['full_name'],
                    'branch_id': user['branch_id'],
                    'role_id': user['role_id'],
                    'role_name': user['role_name'],
                    'username': user['username'],
                }
                messages.success(request, f'Welcome, {user["full_name"]}!')
                # Redirect to correct dashboard based on role
                role = user['role_name']
                if role == 'System Admin':
                    return redirect('dashboard_admin')
                elif role == 'Branch Manager':
                    return redirect('dashboard_manager')
                elif role == 'Teller':
                    return redirect('dashboard_teller')
                else:   # HelpDesk or any other
                    return redirect('dashboard_home')   # fallback
            else:
                # Should not happen because procedure raises error on failure
                messages.error(request, 'Invalid username or password.')
        except Exception as e:
            # The procedure will have thrown an SQL exception with the message
            messages.error(request, str(e))

    return render(request, 'core/login.html')

def logout_view(request):
    """Clear session and log out."""
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('login')

# ---- Role-based dashboards (placeholder - will be expanded later) ----
def dashboard_admin(request):
    """System Admin dashboard – redirects to branch list for now."""
    return redirect('branch_list')   # existing God-mode panel

def dashboard_manager(request):
    """Branch Manager dashboard – placeholder."""
    return render(request, 'core/dashboard_manager.html')

def dashboard_teller(request):
    """Teller dashboard – placeholder."""
    return render(request, 'core/dashboard_teller.html')

def dashboard_home(request):
    """Fallback dashboard for other roles."""
    return render(request, 'core/dashboard_home.html')

def dashboard_redirect(request):
    """Redirect to the appropriate dashboard based on role."""
    employee = request.session.get('employee')
    if not employee:
        return redirect('login')
    role = employee.get('role_name')
    if role == 'System Admin':
        return redirect('dashboard_admin')
    elif role == 'Branch Manager':
        return redirect('dashboard_manager')
    elif role == 'Teller':
        return redirect('dashboard_teller')
    else:
        return redirect('dashboard_home')
