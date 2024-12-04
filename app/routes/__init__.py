from app.routes.login_ressource import LoginResource
from app.routes.main_routes import (
    SignupResource,
    LoginResource,
    LogoutResource,
    PasswordResetRequestResource,
    ResetPasswordResource,
    UpdateUserResource,
)
from app.routes.usecase_route import (
    GetRecipeResource,
    GetAllRecipesResource,
    GetMyRecipesResource,
    FlagRecipeResource,
    IsRecipeFlaggedResource,
    SearchRecipesResource
)
from app.routes.maillist_route import SaveMailResource
