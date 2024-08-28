# from fastapi import APIRouter, Depends
# from .services_auth import authenticate_user, get_current_user, User
# from fastapi import APIRouter
# from .services_auth import sign_up_user, UserSignUp

# router_auth = APIRouter(prefix="/auth", tags=["Authentication"])

# @router_auth.post("/signup")
# async def sign_up(user: UserSignUp):
#     return await sign_up_user(user)

# @router_auth.post("/token")
# async def login(user: User):
#     return await authenticate_user(user)

# @router_auth.get("/users/me")
# async def read_users_me(current_user: str = Depends(get_current_user)):
#     return current_user