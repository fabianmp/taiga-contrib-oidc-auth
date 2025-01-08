# Taiga Contrib OIDC Auth

[![Docker Image Version](https://img.shields.io/docker/v/fabianmp/taiga-front?sort=semver&style=flat&logo=docker&label=taiga-front&cacheSeconds=3600)](https://hub.docker.com/repository/docker/fabianmp/taiga-front)
[![Docker Image Version](https://img.shields.io/docker/v/fabianmp/taiga-back?sort=semver&style=flat&logo=docker&label=taiga-back&cacheSeconds=3600)](https://hub.docker.com/repository/docker/fabianmp/taiga-back)

Forked from [kaleidos-ventures/taiga-contrib-oidc-auth](https://github.com/kaleidos-ventures/taiga-contrib-oidc-auth)
and patched to be compatible with [robrotheram/taiga-contrib-openid-auth](https://github.com/robrotheram/taiga-contrib-openid-auth).

This repository also provides Docker images built on top of the [official Taiga.io images](https://hub.docker.com/u/taigaio)
including the OIDC authentication provider.

## Configuration

### taiga-front

Configure the following environment variables for the container running `taiga-front`:

```sh
ENABLE_OIDC_AUTH="true"
OIDC_BUTTON_TEXT="OIDC"  # optionally configure login button
DEFAULT_LOGIN_ENABLED="false"  # optionally disable local user login
```

Enabling OIDC login is independent from setting `PUBLIC_REGISTER_ENABLED`.

### taiga-back

Configure the following environment variables for the container running `taiga-back`:

```sh
ENABLE_OIDC_AUTH="True"
OIDC_ISSUER="<url of your OIDC provider>"
OIDC_CLIENT_ID="<client id configured in OIDC provider"
OIDC_CLIENT_SECRET="<client secret configured in OIDC provider"
OIDC_SCOPES="openid profile email"  # optionally configure scopes

# optionally configure endpoints
OIDC_AUTHORIZATION_ENDPOINT="<url to authorization endpoint>"
OIDC_JWKS_ENDPOINT="<url to JWKS endpoint>"
OIDC_TOKEN_ENDPOINT="<url to token endpoint>"
OIDC_USERINFO_ENDPOINT="<url to user info endpoint>"

# if you run behind a reverse proxy with TLS termination
# activate this to use HTTPS in the redirect URI
USE_X_FORWARDED_HOST="True"
```

## Advanced Configuration / Migration

If you want to migrate from an existing installation using [robrotheram/taiga-contrib-openid-auth](https://github.com/robrotheram/taiga-contrib-openid-auth)
or if you need to configure the claims returned from your OIDC provider, you can set the following environment variables for the
container running `taiga-back`:

```sh
OIDC_AUTHDATA_KEY="openid"  # use existing connection from robrotheram/taiga-contrib-openid-auth
OIDC_SLUGGIFY_USERNAME="True"  # generate the same username as robrotheram/taiga-contrib-openid-auth
OIDC_CLAIM_USERNAME="preferred_username"  # use preferred username from OpenID
OIDC_CLAIM_AUTHDATA="sub"  # claim used to identify OAuth users
OIDC_CLAIM_EMAIL="email"  # claim containing user's e-mail address
OIDC_CLAIM_FULLNAME="name"  # claim containing user's full name
```


## Configuration for your IDP

This plugin uses [mozilla_django_oidc](https://github.com/mozilla/mozilla-django-oidc).
As such, the following attributes are important for your OAuth2.0 client:

 * post_login_redirect_uris: Should be `https://YOUR-TAIGA-INSTANCE/api/oidc/callback/` (note the trailing slash!)
 * token_endpoint_auth_method: Should be `client_secret_post` (not client_secret_basic) (unless you are using [`OIDC_TOKEN_USE_BASIC_AUTH=True`](https://github.com/mozilla/mozilla-django-oidc/blob/2c2334fdc9b2fc72a492b5f0e990b4c30de68363/mozilla_django_oidc/auth.py#L236C31-L236C56))
