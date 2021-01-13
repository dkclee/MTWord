
from flask import Blueprint, render_template, request, url_for, \
    flash, redirect, abort

from flask_login import login_required, current_user

from ..sets import get_all_verses

from ..models import db, Set
from ..forms import SetForm

sets = Blueprint('sets', __name__)

####################################################################
# Set Routes


@sets.route("/sets/new", methods=["GET", "POST"])
@login_required
def create_new_set():
    """ Creates a new set
        - Validates that there is at least 1 valid verse reference
    """

    form = SetForm()

    if form.validate_on_submit():

        # Get all the verse instances with the references
        verses = get_all_verses(request.form.getlist('refs'))

        # If there are no valid references
        if not verses:
            form.name.errors = [
                "Please make sure to include at least 1 valid verse reference"
            ]
            return render_template("sets/add_edit_set.html",
                                   form=form,
                                   title="Add a new set",
                                   verb="Create")

        name = form.name.data

        description = form.description.data

        new_set = Set(name=name,
                      description=description,
                      user_id=current_user.id)

        db.session.add(new_set)
        db.session.commit()

        new_set.verses += verses

        db.session.commit()

        flash("Created new set!", "success")

        return redirect(url_for("show_set", set_id=new_set.id))

    return render_template("sets/add_edit_set.html",
                           form=form,
                           title="Add a new set",
                           verb="Create")


@sets.route("/sets/<int:set_id>/edit", methods=["GET", "POST"])
@login_required
def edit_set(set_id):
    """ Display the functionality to the set
        - Populate the form with data ahead of time
    """

    form = SetForm()

    current_set = Set.query.get(set_id)

    if current_set.user_id != current_user.id:
        abort(404)

    if form.validate_on_submit():

        # Get all the verse instances with the references
        verses = get_all_verses(request.form.getlist('refs'))

        if not verses:
            form.name.errors = [
                "Please make sure to include at least 1 valid verse reference"
            ]
            return render_template("sets/add_edit_set.html",
                                   form=form,
                                   title="Edit your set",
                                   verb="Edit",
                                   verses=current_set.verses)

        edited_set = Set.query.get(set_id)

        edited_set.name = form.name.data
        edited_set.description = form.description.data

        edited_set.verses = verses

        db.session.commit()

        flash("Updated your set!", "info")

        return redirect(url_for("show_set", set_id=set_id))

    form = SetForm(obj=current_set)
    return render_template("sets/add_edit_set.html",
                           form=form,
                           title="Edit your set",
                           verb="Edit",
                           verses=current_set.verses)


@sets.route("/sets/<int:set_id>/copy", methods=["GET", "POST"])
@login_required
def copy_set(set_id):
    """ Display the functionality to copy someone else's set
        - Populate the form with data ahead of time
    """

    form = SetForm()

    current_set = Set.query.get(set_id)

    if current_set.user_id == current_user.id:
        abort(404)

    if form.validate_on_submit():

        # Get all the verse instances with the references
        verses = get_all_verses(request.form.getlist('refs'))

        if not verses:
            form.name.errors = [
                "Please make sure to include at least 1 valid verse reference"
            ]
            return render_template("sets/add_edit_set.html",
                                   form=form,
                                   title="Copy someone else's set",
                                   verb="Copy",
                                   verses=current_set.verses)

        copied_set = Set(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id,
        )

        db.session.add(copied_set)
        db.session.commit()

        copied_set.verses = verses

        db.session.commit()

        flash("Copied the set!", "info")

        return redirect(url_for("show_set", set_id=copied_set.id))

    form = SetForm(obj=current_set)
    return render_template("sets/add_edit_set.html",
                           form=form,
                           title="Copy someone else's set",
                           verb="Copy",
                           verses=current_set.verses)


@sets.route("/sets/<int:set_id>")
def show_set(set_id):
    """ Display the set with:
        - Options to edit the set
        - Various studying means
    """

    current_set = Set.query.get_or_404(set_id)

    headers = ("Reference", "Verse")
    verses = current_set.verses

    is_favorite = current_set in current_user.favorite_sets

    return render_template("sets/show_set.html",
                           set=current_set,
                           headers=headers,
                           verses=verses,
                           is_favorite=is_favorite,)


@sets.route("/sets/<int:set_id>/cards")
def show_set_cards(set_id):
    """ """


@sets.route("/sets/<int:set_id>/practice")
def show_set_practice(set_id):
    """ """


@sets.route("/sets/<int:set_id>/test")
def show_set_test(set_id):
    """  """


@sets.route("/sets/<int:set_id>/delete", methods=["POST"])
@login_required
def delete_set(set_id):
    """ Delete the set, (if the set is not found, return 404) """

    current_set = Set.query.get_or_404(set_id)

    # Ensure only the owner can delete the set
    if current_set.user_id == current_user.id:
        db.session.delete(current_set)
        db.session.commit()

        flash("Your set has been successfully deleted", "success")

        return redirect(url_for("index"))

    flash("You cannot delete someone else's set!", "warning")
    return redirect(request.referrer)
