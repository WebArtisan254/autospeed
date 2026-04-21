
@bp.route("/email-outbox")
@admin_required
def email_outbox():
    msgs = db.session.scalars(
        select(EmailOutBox).order_by(EmailOutbox.created_at.desc()).limit(100)
    ).all()
    return render_template("admin/email_outbox.html", msgs=msgs)