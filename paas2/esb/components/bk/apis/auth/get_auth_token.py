# -*- coding: utf-8 -*-
import datetime

from django.utils import timezone

from common.base_utils import generate_token
from common.constants import API_TYPE_Q
from esb.bkcore.models import UserAuthToken
from components.component import Component
from .toolkit import configs


class GetAuthToken(Component):
    """
    apiLabel 获取AuthToken
    apiMethod GET

    ### 功能描述

    获取AuthToken

    ### 请求参数

    {{ common_args_desc }}

    ### 请求参数示例

    ```python
    {
        "app_code": "esb_test",
        "app_secret": "xxx",
        "bk_token": "xxx",
    }
    ```

    ### 返回结果示例

    ```python
    {
        "result": true,
        "code": "00",
        "message": "",
        "data": {
            "username": "alex",
            "auth_token": "1V8E8MMybNq5S8WDU4pO5hImxk5ldO",
            "expires_in": 15551578
        }
    }
    ```
    """

    sys_name = configs.SYSTEM_NAME
    api_type = API_TYPE_Q

    def get_auth_token(self, app_code, username):
        token = UserAuthToken.objects.filter(app_code=app_code, username=username).first()
        return token

    def create_auth_token(self, app_code, username):
        token = UserAuthToken.objects.create(
            app_code=app_code,
            username=username,
            auth_token=generate_token(),
            expires=timezone.now() + datetime.timedelta(days=180),
        )
        return token

    def handle(self):
        app_code = self.request.app_code
        username = self.current_user.username

        token = self.get_auth_token(app_code, username)
        if token:
            # 判断如果token已经过期，生成一个新的token
            if token.has_expired():
                token.auth_token = generate_token()
                token.expires = timezone.now() + datetime.timedelta(days=180)

            token.touch()
            token.save()
        else:
            token = self.create_auth_token(app_code=app_code, username=username)
        self.response.payload = {
            "result": True,
            "data": token.get_info(),
        }