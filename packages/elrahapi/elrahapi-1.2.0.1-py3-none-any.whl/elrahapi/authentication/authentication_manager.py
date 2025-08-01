from datetime import datetime, timedelta
from typing import Any
from elrahapi.database.session_manager import SessionManager
from elrahapi.utility.types import ElrahSession
from elrahapi.authentication.authentication_namespace import (
    ACCESS_TOKEN_EXPIRATION,
    OAUTH2_SCHEME,
    REFRESH_TOKEN_EXPIRATION,
)
from elrahapi.authentication.token import AccessToken, RefreshToken, TokenType
from elrahapi.crud.crud_models import CrudModels
from elrahapi.exception.auth_exception import (
    INACTIVE_USER_CUSTOM_HTTP_EXCEPTION,
    INVALID_CREDENTIALS_CUSTOM_HTTP_EXCEPTION,
)
from elrahapi.exception.exceptions_utils import raise_custom_http_exception
from elrahapi.security.secret import define_algorithm_and_key
from elrahapi.utility.utils import exec_stmt
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import  select
from sqlalchemy.sql import or_
from fastapi import Depends, status

from elrahapi.exception.custom_http_exception import CustomHttpException
from dotenv import load_dotenv
import os
load_dotenv(".env")

ISSUER = os.getenv("ISSUER")
AUDIENCE = os.getenv("AUDIENCE")

class AuthenticationManager:

    def __init__(
        self,
        session_manager:SessionManager ,
        secret_key: str | None = None,
        algorithm: str | None = None,
        refresh_token_expiration: int | None = None,
        access_token_expiration: int | None = None,

    ):
        self.__authentication_models: CrudModels = None
        self.__refresh_token_expiration = (
            refresh_token_expiration
            if refresh_token_expiration
            else REFRESH_TOKEN_EXPIRATION
        )
        self.__access_token_expiration = (
            access_token_expiration
            if access_token_expiration
            else ACCESS_TOKEN_EXPIRATION
        )
        self.__algorithm, self.__secret_key = define_algorithm_and_key(
            secret_key,
            algorithm,
        )
        self.__session_manager: SessionManager = session_manager

    @property
    def session_manager(self) -> SessionManager:
        return self.__session_manager

    @session_manager.setter
    def session_manager(self, session_manager: SessionManager):
        self.__session_manager = session_manager

    @property
    def authentication_models(self):
        return self.__authentication_models

    @authentication_models.setter
    def authentication_models(self, authentication_models: CrudModels):
        self.__authentication_models = authentication_models

    @property
    def algorithm(self):
        return self.__algorithm

    @algorithm.setter
    def algorithms(self, algorithm: str):
        self.__algorithm = algorithm

    @property
    def access_token_expiration(self):
        return self.__access_token_expiration

    @access_token_expiration.setter
    def access_token_expiration(self, access_token_expiration: int):
        self.__access_token_expiration = access_token_expiration

    @property
    def refresh_token_expiration(self):
        return self.__refresh_token_expiration

    @refresh_token_expiration.setter
    def refresh_token_expiration(self, refresh_token_expiration: int):
        self.__refresh_token_expiration = refresh_token_expiration

    def create_token(self,
        data: dict,
        token_type: TokenType,
        expires_delta: timedelta = None
        )->AccessToken | RefreshToken :
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            milliseconds = self.__access_token_expiration if token_type == TokenType.ACCESS_TOKEN else self.__refresh_token_expiration
            expire = datetime.now() + timedelta(
                milliseconds=milliseconds
            )
        iat = datetime.now()
        to_encode.update({"exp": expire, "iat": iat})
        if ISSUER :
            to_encode.update({"iss": ISSUER})
        if AUDIENCE :
            to_encode.update({"aud": AUDIENCE})
        encode_jwt = jwt.encode(
            to_encode, self.__secret_key, algorithm=self.__algorithm
        )
        return {token_type.value: encode_jwt, "token_type": "bearer"}

    def get_access_token(self, token=Depends(OAUTH2_SCHEME)):
        self.validate_token(token)
        return token

    def validate_token(self, token: str):
        try:
            payload = jwt.decode(token, self.__secret_key, algorithms=self.__algorithm)
            return payload
        except ExpiredSignatureError as e:
            raise_custom_http_exception(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token has expired : {str(e)}"
            )
        except JWTError as e:
            raise_custom_http_exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token : {str(e)}",
            )

    async def change_user_state(self, pk: Any, session: ElrahSession):
        try:
            pk_attr = self.__authentication_models.get_pk()
            stmt = select(self.__authentication_models.sqlalchemy_model).where(
                pk_attr == pk
            )
            result = await exec_stmt(stmt=stmt, session=session)
            user = result.scalar_one_or_none()
            if user:
                user.change_user_state()
                await self.session_manager.commit_and_refresh(
                    session=session,
                    object=user
                )
            else:
                detail = "User Not Found"
                raise_custom_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND, detail=detail
                )
        except CustomHttpException as che :
            await self.session_manager.rollback_session(session=session)
            raise che
        except Exception as e:
            await self.session_manager.rollback_session(session=session)
            detail=f"Error while changing user state: {str(e)}"
            raise_custom_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
            )

    async def get_user_by_sub(self, sub: str,session: ElrahSession):
        try:
            # if sub.isdigit():
            #     sub = int(sub)
            pk_attr = self.__authentication_models.get_pk()
            email_attr = self.__authentication_models.sqlalchemy_model.email
            username_attr = self.__authentication_models.sqlalchemy_model.username
            stmt = select(self.__authentication_models.sqlalchemy_model).where(
                or_(
                    pk_attr == sub,
                    email_attr == sub,
                    username_attr == sub)
            )
            result = await exec_stmt(
                stmt=stmt,
                session=session
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise INVALID_CREDENTIALS_CUSTOM_HTTP_EXCEPTION
            return user
        except CustomHttpException as che:
            await self.session_manager.rollback_session(session=session)
            raise che
        except Exception as e:
            await self.session_manager.rollback_session(session=session)
            detail = f"Error while getting user by sub: {str(e)}"
            raise_custom_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
            )

    async def is_authorized(
        self,
        sub: str,
        privilege_name: str | None = None,
        role_name: str | None = None,
        ) -> bool:
        try:
            session: ElrahSession = await self.session_manager.get_session()
            user = await self.get_user_by_sub(sub=sub,session=session)
            if role_name:
                return user.has_role(role_name=role_name)
            elif privilege_name:
                return user.has_privilege(privilege_name)
        except CustomHttpException as che:
            await self.session_manager.rollback_session(session=session)
            raise che
        except Exception as e:
            await self.session_manager.rollback_session(session=session)
            detail="Error while checking authorization: " + str(e)
            raise_custom_http_exception(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=detail
                )
        finally:
            await self.session_manager.close_session(session=session)

    def get_sub_from_token(self, token: str) -> str:
        payload = self.validate_token(token)
        sub: str = payload.get("sub")
        if sub.isdigit():
            sub = int(sub)
        return sub

    def check_authorization(
        self,
        privilege_name: str | None = None,
        role_name: str | None = None,
    ) -> callable:
        async def auth_result(token: str = Depends(self.get_access_token)):
            sub=self.get_sub_from_token(token=token)
            if role_name and sub:
                return await self.is_authorized(
                    sub=sub,
                    role_name=role_name,
                )
            elif privilege_name and sub :
                return await self.is_authorized(
                    sub=sub,
                    privilege_name=privilege_name,
                )
            elif (role_name and privilege_name) or (not role_name and not privilege_name):
                raise_custom_http_exception(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Either role or privilege must be provided, not both"
                )
            else:
                raise_custom_http_exception(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Sub must be provided , Maybe User is not authenticated"
                )
        return auth_result

    def check_authorizations(
        self,
        privileges_name: list[str] | None = None,
        roles_name: list[str] | None = None,
    ) ->list[callable]:
        authorizations = []
        for privilege_name in privileges_name:
            authorizations.append(
                self.check_authorization(
                    privilege_name=privilege_name
                    )
            )
        for role_name in roles_name:
            authorizations.append(
                self.check_authorization(role_name=role_name)
            )
        return authorizations

    async def authenticate_user(
        self,
        password: str,
        session: ElrahSession,
        sub: str | None = None,
    ):
        try :
            if sub is None:
                raise INVALID_CREDENTIALS_CUSTOM_HTTP_EXCEPTION
            user = await self.get_user_by_sub(session=session, sub=sub)
            if user:
                if not user.check_password(password):
                    user.try_login(False)
                    await  self.session_manager.commit_and_refresh(
                        session=session,
                        object=user
                    )
                    raise INVALID_CREDENTIALS_CUSTOM_HTTP_EXCEPTION
                if not user.is_active:
                    raise INACTIVE_USER_CUSTOM_HTTP_EXCEPTION
            user.try_login(True)
            await self.session_manager.commit_and_refresh(
                session=session,
                object=user
            )
            return user
        except CustomHttpException as che:
            await self.session_manager.rollback_session(session=session)
            raise che
        except Exception as e:
            await self.session_manager.rollback_session(session=session)
            detail = f"Error while authenticating user: {str(e)}"
            raise_custom_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
            )

    def get_current_user_sub(
        self,
        token: str = Depends(OAUTH2_SCHEME),
    ):
        payload =  self.validate_token(token)
        sub: str = payload.get("sub")
        if sub is None:
            raise INVALID_CREDENTIALS_CUSTOM_HTTP_EXCEPTION
        return sub

    async def refresh_token(
        self, session: ElrahSession, refresh_token_data: RefreshToken
    ):
        try :
            # payload =  self.validate_token(refresh_token_data.refresh_token)
            # sub = payload.get("sub")
            sub = self.get_sub_from_token(token=refresh_token_data.refresh_token)
            if sub is None:
                raise INVALID_CREDENTIALS_CUSTOM_HTTP_EXCEPTION
            user = await self.get_user_by_sub(sub=sub, session=session)
            access_token_expiration = timedelta(milliseconds=self.__access_token_expiration)
            data = user.build_access_token_data(pk_name=self.__authentication_models.primary_key_name)
            access_token = self.create_token(
                data=data, expires_delta=access_token_expiration,token_type=TokenType.ACCESS_TOKEN
            )
            return access_token
        except CustomHttpException as che:
            await self.session_manager.rollback_session(session=session)
            raise che
        except Exception as e:
            await self.session_manager.rollback_session(session=session)
            detail = f"Error while refreshing token: {str(e)}"
            raise_custom_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
            )

    async def is_existing_user(self,session:ElrahSession, sub: str):
        user= await self.get_user_by_sub(sub=sub,session=session)
        return user is not None

    async def read_one_user(self,session:ElrahSession,sub: str):
        try:
            user= await self.get_user_by_sub(sub=sub,session=session)
            return user
        except CustomHttpException as che:
            await self.session_manager.rollback_session(session=session)
            raise che
        except Exception as e:
            await self.session_manager.rollback_session(session=session)
            detail = f"Error while reading user with sub {sub} , details : {str(e)}"
            raise_custom_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
            )

    async def change_password(
        self,session:ElrahSession, sub: str, current_password: str, new_password: str
    ):
        current_user = await self.authenticate_user(
            password=current_password,
            sub=sub,
            session=session,
        )
        current_user.password = new_password
        await self.session_manager.commit_and_refresh(
            session=session,
            object=current_user
        )
