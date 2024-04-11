from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            
            authorized_groups = ['restaurant', 'frontdesk']  
            if user.groups.filter(name__in=authorized_groups).exists():
                login(request, user)
                # Redirect based on group membership (optional)
                if user.groups.filter(name='restaurant').exists():
                    return redirect('restaurant:dashboard') 
                elif user.groups.filter(name='frontdesk').exists():
                    return redirect('booking:dashboard')  

                else:
                    
                    message = 'Welcome! (Choose specific section)'
                    return render(request, 'authentication/login.html', {'message': message})
            else:
                
                error_message = 'Eengkk!! You are not authorized to access this application.'
                return render(request, 'authentication/login.html', {'error': error_message})
        else:
           
            error_message = 'Invalid username or password.'
            return render(request, 'authentication/login.html', {'error': error_message})

   
    return render(request, 'authentication/login.html')

def logout_view(request):
    """Logs out the user and redirects to the login page."""
    logout(request)
    return redirect('authentication:login')

