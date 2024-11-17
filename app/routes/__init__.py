from app.routes.login_ressource import LoginResource
from app.routes.protect_resource import ProtectedAreaResource
from app.routes.main_routes import (
    SignupResource,
    LoginResource,
    LogoutResource,
    PasswordResetRequestResource,
    ResetPasswordResource,

)
from app.routes.usecase_route import (
    GetRecipeResource,
    GetAllRecipesResource,
    GetMyRecipesResource,
    FlagRecipeResource,
    IsRecipeFlaggedResource
)