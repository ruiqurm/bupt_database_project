
from fastapi import Request,Depends
from .user_token import oauth2_scheme,ALGORITHM,SECRET_KEY,TokenData
from .user import user_get_by_name,UserInDB
from .exceptions import Unauthorization,PermissionDenied
from jose import JWTError, jwt
from typing import List

async def get_current_user(request: Request,token: str = Depends(oauth2_scheme))->UserInDB:
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise Unauthorization()
		token_data = TokenData(username=username)
	except JWTError:
		raise Unauthorization()
	user = await user_get_by_name(token_data.username)
	if user is None:
		raise Unauthorization()
	if not user.is_active:
		raise InactiveUser()
	request.state.user = user
	return user
async def check_admin(user:UserInDB  = Depends(get_current_user)):
	if not user.is_admin:
		raise PermissionDenied()