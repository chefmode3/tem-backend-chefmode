def with_app_context(task_function):
    def wrapper(*args, **kwargs):
        from app import create_app
        app = create_app()
        with app.app_context():
            return task_function(*args, **kwargs)
    return wrapper
