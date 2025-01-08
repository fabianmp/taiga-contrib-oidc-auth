ENABLE_OIDC_AUTH = os.getenv('ENABLE_OIDC_AUTH', 'False') == 'True'
if ENABLE_OIDC_AUTH:
    INSTALLED_APPS += [
        "mozilla_django_oidc",
        "taiga_contrib_oidc_auth",
    ]

    AUTHENTICATION_BACKENDS = list(AUTHENTICATION_BACKENDS) + [
        "taiga_contrib_oidc_auth.oidc.TaigaOIDCAuthenticationBackend",
    ]

    # Add the OIDC urls
    ROOT_URLCONF = "settings.urls"

    # OIDC Settings
    import os
    OIDC_CALLBACK_CLASS = "taiga_contrib_oidc_auth.views.TaigaOIDCAuthenticationCallbackView"
    OIDC_RP_SCOPES = os.getenv("OIDC_SCOPES", "openid profile email")
    OIDC_RP_SIGN_ALGO = "RS256"
    OIDC_BASE_URL = os.getenv("OIDC_ISSUER")
    OIDC_OP_JWKS_ENDPOINT = os.getenv("OIDC_JWKS_ENDPOINT", OIDC_BASE_URL + "/protocol/openid-connect/certs")
    OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv("OIDC_AUTHORIZATION_ENDPOINT", OIDC_BASE_URL + "/protocol/openid-connect/auth")
    OIDC_OP_TOKEN_ENDPOINT = os.getenv("OIDC_TOKEN_ENDPOINT", OIDC_BASE_URL + "/protocol/openid-connect/token")
    OIDC_OP_USER_ENDPOINT = os.getenv("OIDC_USERINFO_ENDPOINT", OIDC_BASE_URL + "/protocol/openid-connect/userinfo")
    OIDC_RP_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
    OIDC_RP_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET")

USE_FORWARDED_HOST = os.getenv('USE_X_FORWARDED_HOST', 'False') == 'True'
if USE_FORWARDED_HOST:
    USE_X_FORWARDED_HOST = USE_FORWARDED_HOST
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
