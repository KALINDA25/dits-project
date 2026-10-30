from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from app.models import db, Defect

dash_bp = Blueprint("dashboard", __name__)

@dash_bp.route("/dashboard")
@login_required
def dashboard():
    by_status = dict(db.session.query(Defect.status, func.count()).group_by(Defect.status).all())
    by_priority = dict(db.session.query(Defect.priority, func.count()).group_by(Defect.priority).all())
    total = Defect.query.count()
    return render_template("dashboard.html", by_status=by_status, by_priority=by_priority, total=total)