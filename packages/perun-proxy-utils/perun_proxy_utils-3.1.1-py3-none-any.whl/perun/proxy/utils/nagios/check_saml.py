#!/usr/bin/env python3

"""
make a full roundtrip test for SAML based SSO
"""

import argparse
import base64
import hmac
import http.cookiejar
import os
import re
import ssl
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

STATUS = {"OK": 0, "WARNING": 1, "CRITICAL": 2, "UNKNOWN": 3}

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,"
    + "application/xml;q=0.9,image/webp,*/*;q=0.8",
}

CACHE_REGEX = ".*_(OK|WARNING|CRITICAL|UNKNOWN)_.*"


# https://github.com/susam/mintotp/blob/master/mintotp.py
def hotp(key, counter, digits=6, digest="sha1"):
    key = base64.b32decode(key.upper() + "=" * ((8 - len(key)) % 8))
    counter = struct.pack(">Q", counter)
    mac = hmac.new(key, counter, digest).digest()
    offset = mac[-1] & 0x0F
    endoffset = offset + 4
    binary = struct.unpack(">L", mac[offset:endoffset])[0] & 0x7FFFFFFF
    return str(binary)[-digits:].zfill(digits)


def totp(key, time_step=30, digits=6, digest="sha1"):
    return hotp(key, int(time.time() / time_step), digits, digest)


class FormParser(HTMLParser):
    form_action = None
    form_data = {}
    _form_in_progress = False

    def __init__(self, *args, **kwargs):
        self.form_action = None
        self.form_data = {}
        self._form_in_progress = False
        super(FormParser, self).__init__(*args, **kwargs)

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "form":
            self._form_in_progress = True
            for name, value in attrs:
                if name.lower() == "action" and self.form_action is None:
                    self.form_action = value
        elif tag.lower() == "input":
            input_name = None
            input_value = None
            for name, value in attrs:
                if name.lower() == "name":
                    input_name = value
                elif name.lower() == "value":
                    input_value = value
            if input_name and input_value:
                self.form_data[input_name] = input_value

    def handle_endtag(self, tag):
        if tag.lower() == "form":
            self._form_in_progress = False


def parse_form(html):
    parser = FormParser()
    parser.feed(html)
    return parser.form_action, parser.form_data


def get_host_from_url(url):
    return urllib.parse.urlparse(url).hostname


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="SAML authentication check")
    parser._optionals.title = "Options"
    parser.add_argument(
        "--username",
        required=True,
        help="username for IdP",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="password for IdP",
    )
    parser.add_argument(
        "--url",
        help="URL that starts authentication",
        default="https://inet.muni.cz/sys/servertest",
    )
    parser.add_argument(
        "--string",
        help="string to expect after successful authentication",
        default="OSCIS",
    )
    parser.add_argument(
        "--logout-url",
        help="URL to trigger logout",
        default="https://inet.muni.cz/pub/appctl/logout",
    )
    parser.add_argument(
        "--postlogout-string",
        help="String to expect after successful logout",
        default="successfully signed out",
    )
    parser.add_argument(
        "--skip-logout-check",
        action="store_true",
        help="skip logout check",
    )
    parser.add_argument("--idp-host", help="hostname of IdP", default="id.muni.cz")
    parser.add_argument(
        "--hosts",
        nargs="*",
        default=[],
        help="space separated list of hostname:ip or hostname:hostname pairs "
        + "for replacing in all URLs",
    )
    parser.add_argument(
        "--warn-time",
        type=int,
        help="warning threshold in seconds",
        default=5,
    )
    parser.add_argument(
        "--critical-time",
        type=int,
        help="critical threshold in seconds",
        default=15,
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="ignore server name in SSL/TLS certificates",
    )
    parser.add_argument(
        "--username-field",
        help="name of the username field on the login page",
        default="username",
    )
    parser.add_argument(
        "--password-field",
        help="name of the password field on the login page",
        default="password",
    )
    parser.add_argument(
        "--totp",
        help="secret key (seed) for TOTP in Base32 encoding",
        default="ZYTYYE5FOAGW5ML7LRWUL4WTZLNJAMZS",
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
        "--security-text-check",
        action="store_true",
        help="perform security text check (implies --remember-me)",
    )
    parser.add_argument(
        "--cache-timeout",
        type=int,
        help="specify the time after which the cache will be wiped",
        default=0,
    )
    parser.add_argument(
        "--cache-file",
        default="check_saml_cache",
        help="name of the file used for the cache",
    )
    parser.add_argument(
        "--basic-oidc-check",
        action="store_true",
        help="check for presence of state and code parameters in the result",
    )

    args = parser.parse_args()
    if args.security_text_check:
        args.remember_me = True

    return args


def replace_host_in_url(hosts, url, headers):
    host = get_host_from_url(url)
    headers["Host"] = host
    if host in hosts:
        parsed = urllib.parse.urlparse(url)
        url = parsed._replace(netloc=hosts[host]).geturl()
        headers["Host"] = host
    return url, headers


class ResolvingHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts, verbose=0):
        self.hosts = hosts
        self.verbose = verbose

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Check whether the host should be replaced with an IP"""
        referrer = req.headers["Referer"] if "Referer" in req.headers else None
        newurl, newheaders = replace_host_in_url(self.hosts, newurl, DEFAULT_HEADERS)
        req.headers = newheaders
        if referrer:
            req.headers["Referer"] = referrer
        if self.verbose >= 1:
            print("Redirecting to {}".format(newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)

    def http_error_308(self, req, fp, code, msg, hdrs):
        return self.http_error_301(req, fp, 301, msg, hdrs)


class SAMLChecker:
    def curl(self, url, data=None, referrer=None):
        url, headers = replace_host_in_url(self.hosts, url, DEFAULT_HEADERS)

        if referrer:
            headers["Referer"], _ = replace_host_in_url(
                dict(map(reversed, self.hosts.items())),
                urllib.parse.urlparse(referrer)
                ._replace(fragment="")
                ._replace(query="")
                .geturl(),
                {},
            )
        if self.args.verbose >= 1:
            print("curl: {}".format(url))
            if "Referer" in headers:
                print("Referrer: {}".format(headers["Referer"]))
        req = urllib.request.Request(
            url=url,
            data=urllib.parse.urlencode(data).encode("ascii") if data else None,
            headers=headers,
        )
        if self.args.verbose >= 1:
            print("")
        response = None
        try:
            response = self.opener.open(req)
            return response
        except urllib.error.URLError as e:
            if self.args.verbose >= 1:
                print(e)
            if self.args.verbose >= 2:
                print(response)
            self.finish(e.reason, "CRITICAL")

    def js_form_redirect(self, html, url, force=False):
        if (
            force
            or "document.getElementsByTagName('input')[0].click();" in html
            or "document.forms[0].submit()" in html
            or "javascript:DoSubmit();" in html
        ):
            form_action, form_data = parse_form(html)
            return self.send_form(url, form_action, form_data)
        return None, None

    def initial_request(self, url):
        response = self.curl(url)
        response_html = response.read().decode("utf-8")
        response_url = response.url

        try_response_html, try_response_url = self.js_form_redirect(
            response_html, response_url
        )
        if try_response_html is None:
            if self.args.verbose >= 1:
                print("JS redirect not found on initial page")
        else:
            if self.args.verbose >= 1:
                print("JS redirect found on initial page")
            response_html = try_response_html
            response_url = try_response_url
        return response_html, response_url

    def send_form(self, url, action, data):
        target_url = urllib.parse.urljoin(url, action)
        response = self.curl(target_url, data, url)
        return response.read().decode("utf-8"), response.url

    def send_credentials(self, login_form_url, login_form_action, login_form_data):
        login_form_data[self.args.username_field] = self.args.username
        login_form_data[self.args.password_field] = self.args.password
        if self.args.remember_me:
            login_form_data["remember_me"] = "Yes"
        response_html, response_url = self.send_form(
            login_form_url, login_form_action, login_form_data
        )

        if self.args.verbose >= 1:
            print(response_url)
        if self.args.verbose >= 3:
            print(response_html)

        # MFA
        if "totp" in response_html.lower() or "privacyidea" in response_html.lower():
            if self.args.verbose >= 1:
                print("MFA is required")
            totp_form_action, totp_form_data = parse_form(response_html)
            totp_code = totp(self.args.totp)
            totp_form_data["code"] = totp_code
            totp_form_data["otp"] = totp_code
            response_html, response_url = self.send_form(
                response_url, totp_form_action, totp_form_data
            )
            if self.args.verbose >= 1:
                print(response_url)
            if "TOTP" in response_html or "privacyIDEA" in response_html:
                if self.args.verbose >= 2:
                    print(response_html)
                self.finish("TOTP MFA failed", "CRITICAL")
            if self.args.verbose >= 3:
                print(response_html)

        if "consent" in response_html:
            self.finish("Consent is required", "UNKNOWN")
        elif "Wrong UČO or password" in response_html:
            self.finish(
                "Login was not successful, invalid username or password", "CRITICAL"
            )
        elif "Unhandled exception" in response_html:
            self.finish(
                "Login was not successful, unhandled exception occured", "CRITICAL"
            )
        elif "SAMLResponse" not in response_html:
            self.finish("Login was not successful, unknown error", "CRITICAL")

        form_action, form_data = parse_form(response_html)
        if "SAMLResponse" not in form_data:
            self.finish("Login was not successful, unknown error", "CRITICAL")
        saml_response = base64.b64decode(form_data["SAMLResponse"]).decode("utf-8")

        if (
            'StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"'
            not in saml_response
        ):
            self.finish("Login was not successful, non-success response", "CRITICAL")

        return self.js_form_redirect(response_html, response_url, True)

    def js_form_redirect_all(self, html, url):
        for _ in range(10):
            try_html, try_url = self.js_form_redirect(html, url)
            if try_html is not None and try_url is not None:
                html = try_html
                url = try_url
            else:
                return (html, url)
        return (html, url)

    def finish(
        self,
        message,
        status="OK",
        cache_time=time.time(),
        from_cache=False,
        auth_time=None,
    ):
        if auth_time is not None and isinstance(auth_time, float):
            message = "{}|authtime={:.2f};{};{};;".format(
                message, auth_time, self.args.warn_time, self.args.critical_time
            )
        if auth_time is None and from_cache is False:
            message = "{}|authtime=;{};{};;".format(
                message, self.args.warn_time, self.args.critical_time
            )
        if self.args.cache_timeout > 0:
            try:
                file_path = tempfile.gettempdir() + "/" + self.args.cache_file
                f = open(file_path, "w")
                f.write("{}_{}_{}".format(cache_time, status, message))
                f.close()
            except (OSError, ValueError):
                pass
        if from_cache:
            message = "Cached: " + message
        print("{} - {}".format(status, message))
        sys.exit(STATUS[status])

    def check_cache(self):
        try:
            tempdir = tempfile.gettempdir()
            file_path = tempdir + "/" + self.args.cache_file
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    res_b = f.read()
                    if not re.match(CACHE_REGEX, res_b):
                        raise ValueError("Bad cache content!")
                    res = res_b.split("_")
                cached_time = float(res[0])
                status = res[1]
                message = res[2]
                actual_time = time.time()
                time_diff = actual_time - float(cached_time)
                if time_diff < self.args.cache_timeout:
                    self.finish(
                        message=message,
                        status=status,
                        cache_time=cached_time,
                        from_cache=True,
                    )
        except (OSError, ValueError):
            pass

    def main(self):
        """
        CMD Line tool
        """

        if self.args.cache_timeout > 0:
            self.check_cache()

        start_time = time.time()

        # 1. start authentication
        login_form_html, login_form_url = self.initial_request(self.args.url)
        if self.args.verbose >= 3:
            print(login_form_html)

        # 2. log in and post response back
        login_form_action, login_form_data = parse_form(login_form_html)
        html, response_url = self.send_credentials(
            login_form_url, login_form_action, login_form_data
        )

        # 3. follow all JS redirects
        html, response_url = self.js_form_redirect_all(html, response_url)

        if self.args.string not in html:
            if self.args.verbose >= 2:
                print(html)
            self.finish(
                "Missing the testing string {} in the response.".format(
                    self.args.string
                ),
                "CRITICAL",
            )

        if self.args.verbose >= 3:
            print(html)

        elapsed_seconds = time.time() - start_time
        status = "OK"
        if elapsed_seconds >= self.args.critical_time:
            status = "CRITICAL"
        if elapsed_seconds >= self.args.warn_time:
            status = "WARNING"

        if self.args.remember_me:
            # logout from SP and IdP but keep username cookie
            self.cookiejar.clear_session_cookies()
            self.cookiejar.clear(get_host_from_url(self.args.url))
            self.cookiejar.clear(
                (
                    self.hosts[self.args.idp_host]
                    if self.args.idp_host in self.hosts
                    else self.args.idp_host
                ),
                "/",
                "SimpleSAMLAuthToken",
            )
            self.cookiejar.clear(
                (
                    self.hosts[self.args.idp_host]
                    if self.args.idp_host in self.hosts
                    else self.args.idp_host
                ),
                "/",
                "SimpleSAMLSessionID",
            )
            login_form_html, login_form_url = self.initial_request(self.args.url)
            if self.args.verbose >= 3:
                print(login_form_html)
            if (
                self.args.security_text_check
                and 'class="security-text"' not in login_form_html
            ):
                self.finish(
                    "Missing security text on the login page.",
                    "CRITICAL",
                )

            if self.args.username not in login_form_html:
                self.finish(
                    "Missing remembered username on the login page.",
                    "WARNING",
                )

        if self.args.basic_oidc_check:
            mandatory_parameters = ["code=", "state="]
            for param in mandatory_parameters:
                if param not in response_url:
                    if self.args.verbose >= 3:
                        print(response_url)
                    self.finish(
                        f"Missing mandatory parameter '{param}' in response url.",
                        "CRITICAL",
                    )

        if not self.args.skip_logout_check:
            # test logout
            logout_html, logout_url = self.initial_request(self.args.logout_url)
            if self.args.verbose >= 3:
                print(logout_html)
            if self.args.postlogout_string not in logout_html:
                self.finish(
                    "Missing the testing string {} in the logout response.".format(
                        self.args.postlogout_string
                    ),
                    "CRITICAL",
                )

        self.finish(
            "Authentication took {:.2f} seconds".format(elapsed_seconds),
            status,
            auth_time=elapsed_seconds,
        )

    def __init__(self, args):
        self.args = args
        self.hosts = {
            host.split(":", 1)[0]: host.split(":", 1)[1]
            for host in (
                self.args.hosts[0].strip("\"'").split(" ")
                if self.args.hosts and " " in self.args.hosts[0]
                else self.args.hosts
            )
        }
        self.cookiejar = http.cookiejar.CookieJar()
        if self.args.insecure:
            self.opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(self.cookiejar),
                ResolvingHTTPRedirectHandler(self.hosts, self.args.verbose),
                urllib.request.HTTPSHandler(context=ssl.SSLContext()),
            )
        else:
            self.opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(self.cookiejar),
                ResolvingHTTPRedirectHandler(self.hosts, self.args.verbose),
            )


def main():
    checker = SAMLChecker(get_args())
    checker.main()


if __name__ == "__main__":
    main()
