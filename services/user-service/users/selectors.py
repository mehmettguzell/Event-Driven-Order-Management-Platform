from users.models import User

def get_user_by_email(email):
    return User.objects.filter(email=email).first()