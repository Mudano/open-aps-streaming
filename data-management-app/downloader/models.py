
from flask_login import UserMixin
from downloader import db


class User(db.Model, UserMixin):
    __tablename__ = "app_users"
    __table_args__ = ({"schema": "openaps"})

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    hashed_pw = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean)
    verification_code = db.Column(db.String)
    admin = db.Column(db.Boolean)
    last_signin = db.Column(db.Date)
    login_count = db.Column(db.Integer)
    num_downloads = db.Column(db.Integer)
    total_download_size_mb = db.Column(db.Float)
    created_ts = db.Column(db.Date)

    def __repr__(self):
        return f"Users('{self.email}')"
