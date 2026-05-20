import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.configs.extensions import db
from app.models.users import User

def create_admin():
    app = create_app()
    with app.app_context():
        u = User.query.filter_by(email='admin@example.com').first()
        if not u:
            u = User(email='admin@example.com', user_name='admin_test')
            u.is_verified = True
            if hasattr(u, 'isadmin'):
                u.isadmin = True
            u.password = 'Admin@1234'
            db.session.add(u)
        else:
            u.password = 'Admin@1234'
            u.is_verified = True
        
        db.session.commit()
        print('Created/Updated Email: admin@example.com, Password: Admin@1234')

if __name__ == '__main__':
    create_admin()
