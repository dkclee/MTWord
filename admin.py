from app import current_user, redirect, url_for, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView


class MTWordModelView(ModelView):
    def is_accessible(self):
        if current_user.is_anonymous:
            return False

        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_anonymous:
            return False

        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))
