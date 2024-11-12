from app.services import UserService

def test_create_user(app):
    with app.app_context():
        user = UserService.create_user('testuser', 'test@example.com')
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'