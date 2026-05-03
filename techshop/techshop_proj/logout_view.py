from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import RedirectView

class LogoutGetView(RedirectView):
    """Custom logout view that accepts GET requests"""
    permanent = False
    
    def get_redirect_url(self):
        logout(self.request)
        return '/'
    
# Also create a URL-friendly function-based view
def logout_view(request):
    """Simple logout view that accepts GET"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('store:home')
