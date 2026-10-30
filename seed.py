from app import create_app
from app.models import db, User

app = create_app()
with app.app_context():
    if User.query.count() == 0:
        users = [
            ("Reporter One", "rep@dits.test", "pass123", "reporter"),
            ("Developer One", "dev@dits.test", "pass123", "developer"),
            ("Team Leader", "lead@dits.test", "pass123", "leader"),
            ("Tester One", "tester@dits.test", "pass123", "reporter"),
        ]
        for name, email, pw, role in users:
            u = User(name=name, email=email, role=role)
            u.set_password(pw)
            db.session.add(u)
        db.session.commit()
        print("Seeded 4 users.")
    else:
        print("Users already exist - skipping.")
