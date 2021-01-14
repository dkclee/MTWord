from flask import Blueprint, render_template, request, abort, flash, \
    url_for, redirect

from flask_login import current_user, login_required

from ..models import User, Set, db
from ..forms import EditUserForm

users = Blueprint('users', __name__, template_folder="templates")

####################################################################
# User Routes


@users.route("/users/<int:user_id>")
def show_user_profile(user_id):
    """ Shows the user profile """

    user = User.query.get_or_404(user_id)

    page = request.args.get("page", 1, type=int)

    sets = Set.query.filter_by(user_id=user.id).paginate(page, 10)

    return render_template("users/user_profile.html",
                           user=user,
                           sets=sets.items,
                           set_paginate=sets,
                           )


@users.route("/users/<int:user_id>/favorites")
def show_user_favorites(user_id):
    """ Shows the user's favorited sets """

    user = User.query.get_or_404(user_id)

    page = request.args.get("page", 1, type=int)

    favorited_sets_id = set([fav_set.id for fav_set in user.favorite_sets])

    sets = Set.query.filter(Set.id.in_(favorited_sets_id)).paginate(page, 10)

    return render_template("users/user_favorites.html",
                           user=user,
                           sets=sets.items,
                           set_paginate=sets,
                           type="fav"
                           )


@users.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user_profile(user_id):
    """ Edit the user profile """

    if current_user.id != user_id:
        abort(404)

    form = EditUserForm()

    if form.validate_on_submit():
        # Check to see if there is already someone else with this username
        same_username_user = User.query.filter_by(
            username=form.username.data
        ).first()

        is_unique_username = same_username_user != current_user

        if same_username_user and is_unique_username:
            form.username.errors = ["Username is already taken"]
            return render_template("users/edit_user.html", form=form)

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.bio = form.bio.data

        db.session.commit()

        flash("Successfully edited your information!", "success")
        return redirect(url_for("users.show_user_profile",
                                user_id=current_user.id))

    form = EditUserForm(obj=current_user)

    return render_template("users/edit_user.html", form=form)
