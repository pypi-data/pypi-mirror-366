#!/usr/bin/env python3

"""
make a full roundtrip test.yaml for SAML based SSO
"""

import argparse
import http.cookiejar
import http.server
import json
import logging
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from enum import Enum
from http.client import HTTPResponse
from typing import Dict, Any, List
from urllib.parse import urlparse

from flask import Flask, Response, request
from idpyoidc.client.oauth2.stand_alone_client import StandAloneClient

CALLBACK_ENDPOINT_CALLED = threading.Event()


class ClientConfigData:
    def __init__(
        self, client_id: str, client_secret: str, issuer: str, scopes: List[str]
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.issuer = issuer
        self.scopes = scopes


class Status(Enum):
    OK = 0, "OK"
    WARNING = 1, "WARNING"
    CRITICAL = 2, "CRITICAL"
    UNKNOWN = 3, "UNKNOWN"


class Evaluator:
    def __init__(self):
        self.start_time = None

    def start_test(self):
        self.start_time = time.time()

    def finish_test(self, message: str, status: Status = Status.OK):
        if not self.start_time:
            raise ValueError("Test has not been started.")

        auth_time = None
        if status == Status.OK:
            auth_time = round(time.time() - self.start_time, 2)

        message = f"{message}|authtime={auth_time or ''};"
        status_code, status_name = status.value

        print(f"{status_name} - {message}")
        os._exit(status_code)


def silence_flask_logs(app: Flask) -> None:
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    app.logger.disabled = True
    log.disabled = True


def get_flask_app(
    client: StandAloneClient, evaluator: Evaluator, callback_path: str, verbose: int
) -> Flask:
    app = Flask(__name__)
    app.config["client"] = client
    app.config["evaluator"] = evaluator
    silence_flask_logs(app)

    @app.route(callback_path)
    def signin_oidc():
        CALLBACK_ENDPOINT_CALLED.set()
        client: StandAloneClient = app.config["client"]
        query_params = request.args.to_dict()

        if verbose >= 3:
            print(f"Parameters returned to callback after OIDC auth '{query_params}'")

        auth_response = client.finalize(query_params)

        if verbose >= 3:
            print(
                f"Final authentication response after exchange of code for token '"
                f"{auth_response}'"
            )

        response = Response(status=200, headers={"Content-type": "text/plain"})

        @response.call_on_close
        def trigger_evaluation():
            # trigger auth response evaluation after the flask response has been sent
            if not auth_response.get("id_token"):
                evaluator.finish_test(
                    "ID token was not found in OP's response.", Status.CRITICAL
                )

            if not auth_response.get("userinfo"):
                evaluator.finish_test(
                    "User info was not found in OP's response.", Status.CRITICAL
                )

            evaluator.finish_test("Authentication was successful.", Status.OK)

        return response

    return app


def start_flask_app(
    client: StandAloneClient, evaluator: Evaluator, redirect_uri: str, verbose: int
):
    parsed_redirect_uri = urlparse(redirect_uri)
    app = get_flask_app(client, evaluator, parsed_redirect_uri.path, verbose)

    app.run(host=parsed_redirect_uri.hostname, port=parsed_redirect_uri.port)


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="SAML authentication check")
    parser._optionals.title = "Options"
    parser.add_argument(
        "--redirect-uri",
        "-r",
        required=True,
        help="URI where OIDC callback will be redirected",
    )
    parser.add_argument(
        "--client-id",
        "-cid",
        required=True,
        help="ID of OIDC client registered with OP",
    )
    parser.add_argument(
        "--client-secret",
        "-cs",
        required=True,
        help="secret of OIDC client registered with OP",
    )
    parser.add_argument(
        "--issuer",
        "-i",
        required=True,
        help="Issuer used for OIDC auth",
    )
    parser.add_argument(
        "--scopes",
        "-s",
        nargs="+",
        help="List of scopes client will ask to access",
        default=["openid", "email", "profile"],
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="verbose mode (for debugging)",
    )
    parser.add_argument(
        "--remember-me",
        action="store_true",
        help="check the Remember me option when logging in",
    )
    parser.add_argument(
        "--use-pkce",
        "-pkce",
        action="store_true",
        help="use pkce method for logging in",
    )

    return parser.parse_args()


class OIDCChecker:
    def curl(self, url, data=None):
        if self.args.verbose >= 1:
            print("curl: {}".format(url))
        req = urllib.request.Request(
            url=url,
            data=urllib.parse.urlencode(data).encode("ascii") if data else None,
        )
        response = None
        try:
            response: HTTPResponse = self.opener.open(req)
            return response
        except urllib.error.URLError as e:
            if self.args.verbose >= 1:
                print(e)
            if self.args.verbose >= 2:
                print(response)
            self.evaluator.finish_test(e.reason, Status.CRITICAL)

    def perform_oidc_auth(self, url: str) -> None:
        # Reflector backend ensures that no additional information needs to be sent
        # to the oidc auth endpoint and the auth should pass successfully
        self.curl(url)

    def main(self):
        """
        CMD Line tool
        """

        self.evaluator.start_test()

        # 1. start the Flask endpoint which handles OIDC callback
        if self.args.verbose >= 3:
            print("STEP 1 - starting flask endpoint (callback)")

        thread = threading.Thread(
            target=start_flask_app,
            args=[
                self.client,
                self.evaluator,
                self.args.redirect_uri,
                self.args.verbose,
            ],
        )
        thread.start()

        # 2. initiate auth process
        if self.args.verbose >= 3:
            print("STEP 2 - initiating OIDC auth process")

        req_args = {"redirect_uri": self.args.redirect_uri}
        login_url = self.client.init_authorization(req_args=req_args)
        if self.args.verbose >= 3:
            print(f"OIDC initiating url: '{login_url}'")

        # 3. further proceed with auth
        if self.args.verbose >= 3:
            print("STEP 3 - proceeding with second OIDC auth step")

        self.perform_oidc_auth(login_url)

        # This point should not be reached if callback endpoint was called
        if not CALLBACK_ENDPOINT_CALLED.is_set():
            self.evaluator.finish_test(
                "Callback endpoint was not called.", Status.CRITICAL
            )

    def get_issuer_info(self, issuer):
        well_known_endpoint = f"{issuer}/.well-known/openid-configuration"
        urllib.request.Request(well_known_endpoint)
        response = self.curl(well_known_endpoint)
        return json.loads(response.read().decode("utf-8"))

    def get_non_pkce_client_cfg(
        self, client_config_data: ClientConfigData
    ) -> Dict[str, Any]:
        return {
            "provider_info": {
                "issuer": client_config_data.issuer,
            },
            "client_id": client_config_data.client_id,
            "client_secret": client_config_data.client_secret,
            "scopes_supported": client_config_data.scopes,
            "client_type": "oidc",
        }

    def get_pkce_client_cfg(
        self, client_config_data: ClientConfigData
    ) -> Dict[str, Any]:
        base_config = self.get_non_pkce_client_cfg(client_config_data)
        issuer_info = self.get_issuer_info(client_config_data.issuer)

        additional_provider_info = {
            "jwks_uri": issuer_info.get("jwks_uri"),
            "userinfo_endpoint": issuer_info.get("userinfo_endpoint"),
            "token_endpoint": issuer_info.get("token_endpoint"),
            "authorization_endpoint": issuer_info.get("authorization_endpoint"),
        }
        base_config["provider_info"].update(additional_provider_info)

        pkce_addon_info = {
            "add_ons": {
                "pkce": {
                    "function": "idpyoidc.client.oauth2.add_on.pkce.add_support",
                    "kwargs": {
                        "code_challenge_length": 64,
                        "code_challenge_method": "S256",
                    },
                },
            },
        }
        base_config.update(pkce_addon_info)

        return base_config

    def get_registered_client(
        self, client_config_data: ClientConfigData
    ) -> StandAloneClient:
        if self.is_using_pkce:
            client_cfg = self.get_pkce_client_cfg(client_config_data)
        else:
            client_cfg = self.get_non_pkce_client_cfg(client_config_data)

        client = StandAloneClient(config=client_cfg)
        client.do_provider_info()  # get provider info based on issuer in client's
        # config
        client.do_client_registration()  # client is configured statically if
        # client_id is provided in the config

        return client

    def __init__(self, args):
        self.args = args
        self.cookiejar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookiejar),
        )
        self.is_using_pkce = args.use_pkce
        client_config_data = ClientConfigData(
            args.client_id, args.client_secret, args.issuer, args.scopes
        )
        self.client = self.get_registered_client(client_config_data)
        self.evaluator = Evaluator()


def main():
    checker = OIDCChecker(get_args())
    checker.main()


if __name__ == "__main__":
    main()
