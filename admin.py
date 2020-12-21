from app import current_user
from flask_admin.contrib.sqla import ModelView


class MTWordModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))