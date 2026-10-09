
from django.contrib.auth.decorators import user_passes_test


def store_admin_required(view_func):
    def check_admin(user):
        return (
            user.is_authenticated
            and (
                user.is_superuser
                or user.groups.filter(name="Store Admin").exists()
            )
        )

    return user_passes_test(
        check_admin,
        login_url="login",
    )(view_func)