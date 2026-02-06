from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        email = self.normalize_email(email)
        user = self.model(email=email)
        
        user.is_superuser = False
        user.is_verified = False

        user.set_password(password)
        user.save(using=self._db)

        return user
