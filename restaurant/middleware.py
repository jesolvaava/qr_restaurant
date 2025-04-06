from django.shortcuts import redirect

class KitchenAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that require staff access
        staff_paths = ['/kitchen/', '/stocks/']
        
        if any(request.path.startswith(path) for path in staff_paths):
            # Check both authentication methods
            if not (request.user.is_authenticated and request.user.is_staff) and \
               not request.session.get('staff_authenticated'):
                return redirect('staff_login')
        
        response = self.get_response(request)
        return response
