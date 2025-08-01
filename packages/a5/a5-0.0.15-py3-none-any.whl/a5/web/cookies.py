import http.cookies
from datetime import datetime, timezone
from email.utils import formatdate


def now():
    return datetime.now(timezone.utc)


def http_date(dt=None):
    """
    Format the datetime for HTTP cookies
    """
    if not dt:
        dt = now()
    return formatdate(dt.timestamp(), usegmt=True)


def create_cookie(cookie_name, cookie_domain, token, expiry):
    cookie = http.cookies.Morsel()
    cookie.set(cookie_name, token, token)
    # tell the browser when to stop sending the cookie
    cookie["expires"] = http_date(expiry)
    # restrict to our domain, note if there's no domain, it won't include subdomains
    cookie["domain"] = cookie_domain
    # path so that it's accessible for all API requests, otherwise defaults to not the whole site
    cookie["path"] = "/"
    if cookie_domain == "localhost":
        # send only on requests from first-party domains
        cookie["samesite"] = "Strict"
    else:
        # send on all requests, requires Secure
        cookie["samesite"] = "None"
        # only set cookie on HTTPS sites in production
        cookie["secure"] = True
    # not accessible from javascript
    cookie["httponly"] = True

    return cookie.OutputString()


def parse_cookie(cookie_name, http_cookie_str):
    cookie = http.cookies.SimpleCookie(http_cookie_str).get(cookie_name)

    if not cookie:
        return None

    return cookie.value
