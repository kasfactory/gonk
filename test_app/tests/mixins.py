from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()


class CreateUserMixin:
    def create_user(self, email, password, is_superuser: bool = False) -> User:
        user = User.objects.create(
            username=email,
            email=email,
            is_superuser=is_superuser,
        )
        user.set_password(password)

        return user

    def add_permission(self, user: User, name: str) -> User:
        permission = Permission.objects.get(codename=name)
        user.user_permissions.add(permission)
        return user
