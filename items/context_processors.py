from .models import User

def user_info(request):
    return {'user_info' : User.objects.filter(user_username=request.session['logged_user'])}