from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Defect, User, Comment, StatusHistory

defects_bp = Blueprint("defects", __name__)

VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}

ALLOWED = {
    "Open":        {"Assigned"},
    "Assigned":    {"In Progress"},
    "In Progress": {"Resolved"},
    "Resolved":    {"Verified", "In Progress"},
    "Verified":    {"Closed"},
    "Closed":      set(),
}

def _change_status(defect, new_status):
    if new_status not in ALLOWED.get(defect.status, set()):
        raise ValueError(f"Invalid transition {defect.status} -> {new_status}")
    db.session.add(StatusHistory(
        defect_id=defect.id, old_status=defect.status,
        new_status=new_status, changed_by=current_user.id,
    ))
    defect.status = new_status
    db.session.commit()

@defects_bp.route("/defects")
@login_required
def list_defects():
    defects = Defect.query.order_by(Defect.report_date.desc()).all()
    return render_template("defects.html", defects=defects)

@defects_bp.route("/defects/new", methods=["GET", "POST"])
@login_required
def report_defect():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")

        if not title:
            flash("Title is required.", "error")
            return render_template("report_defect.html"), 400
        if priority not in VALID_PRIORITIES:
            flash("Invalid priority.", "error")
            return render_template("report_defect.html"), 400

        d = Defect(title=title, description=description,
                   priority=priority, reporter_id=current_user.id)
        db.session.add(d)
        db.session.commit()
        flash("Defect reported successfully.", "success")
        return redirect(url_for("defects.view_defect", defect_id=d.id))
    return render_template("report_defect.html")

@defects_bp.route("/defects/<int:defect_id>")
@login_required
def view_defect(defect_id):
    d = Defect.query.get_or_404(defect_id)
    developers = User.query.filter_by(role="developer").all()
    comments = Comment.query.filter_by(defect_id=defect_id).order_by(Comment.created_at).all()
    history = StatusHistory.query.filter_by(defect_id=defect_id).order_by(StatusHistory.changed_at).all()
    return render_template("view_defect.html",
                           d=d, developers=developers, comments=comments, history=history)

@defects_bp.route("/defects/<int:defect_id>/assign", methods=["POST"])
@login_required
def assign_defect(defect_id):
    if current_user.role not in ("leader", "admin"):
        return "Forbidden", 403
    d = Defect.query.get_or_404(defect_id)
    try:
        assignee_id = int(request.form["assignee_id"])
    except (KeyError, ValueError):
        return "Invalid assignee", 400
    if not User.query.get(assignee_id):
        return "Invalid assignee", 400
    d.assignee_id = assignee_id
    _change_status(d, "Assigned")
    return redirect(url_for("defects.view_defect", defect_id=d.id))

@defects_bp.route("/defects/<int:defect_id>/status", methods=["POST"])
@login_required
def change_status(defect_id):
    d = Defect.query.get_or_404(defect_id)
    new_status = request.form.get("status")
    try:
        _change_status(d, new_status)
    except ValueError:
        flash("Invalid status transition.", "error")
    return redirect(url_for("defects.view_defect", defect_id=d.id))

@defects_bp.route("/defects/<int:defect_id>/comment", methods=["POST"])
@login_required
def add_comment(defect_id):
    d = Defect.query.get_or_404(defect_id)
    body = request.form.get("body", "").strip()
    if body:
        db.session.add(Comment(defect_id=d.id, author_id=current_user.id, body=body))
        db.session.commit()
    return redirect(url_for("defects.view_defect", defect_id=d.id))

# ==========================================
# NEW UNIQUE FEATURES BELOW
# ==========================================

@defects_bp.route("/my-workspace")
@login_required
def my_workspace():
    if current_user.role == "developer":
        my_defects = Defect.query.filter_by(assignee_id=current_user.id).all()
    else:
        my_defects = Defect.query.filter_by(reporter_id=current_user.id).all()
    return render_template("defects.html", defects=my_defects)

@defects_bp.route("/board")
@login_required
def board():
    defects = Defect.query.all()
    return render_template("board.html", defects=defects)