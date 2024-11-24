# app settings
APP_SETTINGS=app.config.ProductionConfig
TIME_ZONE='US/Pacific'
USE_TZ=True
DEBUG=False
SECRET_KEY=2LxIkVzktjameJFVqBZFGJPIAWDAP5Df

# OpenApi settings
OPENAI_API_KEY="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"
OPENAI_ORGANIZATION="org-xYVDxzYujg2ErOpXDcsttD83"

# Database settings
PROD_DATABASE_URL=postgresql://chefmode:chefmodedb@chef_mode_db:5432/chef_mode_backend
DATABASE_URL_DEV=postgresql://chefmode:chefmodedb@chef_mode_db:5432/chef_mode_backend
DATABASE_TEST_URL=sqlite:///test.db

# Google Settings
GOOGLE_CLIENT_ID=875921665781-kvapofau0re4k648u57a2qffrc159e75.apps.googleusercontent.com
GOOGLE_SCOPE=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
GOOGLE_REDIRECT_URI=http://localhost:5000/api/v1/auth/callback

# Mail Settings
MAIL_SERVER = 'pro.turbo-smtp.com'
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_SERVER = 'live.smtp.mailtrap.io'
MAIL_USERNAME = 'libert.noutcheu@gmail.com'
MAIL_PASSWORD = 'Noutvan2_1'
DEFAULT_FROM_EMAIL = 'libert.noutcheu@gmail.com'
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_PORT = 587
USE_TZ=True

# celery config
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TIMEZONE='US/Pacific'