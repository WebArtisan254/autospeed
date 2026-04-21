from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..domain.entries import create_entry_for_user, ValidationError

@bp.route("/entries/new", methods=["GET", "POST"])
@login_required
def new_entry():
    if request.method == "POST":
        try:
            create_entry_for_user(
                user_id=current_user.id,
                data=request.form,
            )
            flash("Entry created.")
            return redirect(url_for("web.entries"))
        except ValidationError as e:
            flash(e.message)

    return render_template("entries/new.html")