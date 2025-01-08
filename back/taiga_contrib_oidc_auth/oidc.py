# Copyright (C) 2018 Aurelien Bompard <aurelien@bompard.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import unicodedata

from django.apps import apps
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from taiga.auth.services import send_register_email
from taiga.auth.signals import user_registered as user_registered_signal
from taiga.base import exceptions as exc
from taiga.base.utils.slug import slugify


# TODO: check groups? https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#advanced-user-verification-based-on-their-claims


class TaigaOIDCAuthenticationBackend(OIDCAuthenticationBackend):

    AUTHDATA_KEY = os.getenv("OIDC_AUTHDATA_KEY", "oidc")
    AUTHDATA_CLAIM = os.getenv("OIDC_CLAIM_AUTHDATA", "sub")
    EMAIL_CLAIM = os.getenv("OIDC_CLAIM_EMAIL", "email")
    FULLNAME_CLAIM = os.getenv("OIDC_CLAIM_FULLNAME", "name")
    USERNAME_CLAIM = os.getenv("OIDC_CLAIM_USERNAME", "nickname")

    def filter_users_by_claims(self, claims):
        auth_id = claims.get(self.AUTHDATA_CLAIM, self.get_username(claims))

        AuthData = apps.get_model("users", "AuthData")
        try:
            auth_data = AuthData.objects.filter(
                key=self.AUTHDATA_KEY, value=auth_id
            )
            return [ad.user for ad in auth_data]

        except AuthData.DoesNotExist:
            return self.UserModel.objects.none()

    def get_username(self, claims):
        username = claims.get(self.USERNAME_CLAIM)
        if not username:
            return super(TaigaOIDCAuthenticationBackend, self).get_username(claims)

        if os.getenv("OIDC_SLUGGIFY_USERNAME", "False") == "True":
            username = slugify(username)

        return unicodedata.normalize("NFKC", username)[:150]

    def create_user(self, claims):
        email = claims.get(self.EMAIL_CLAIM)
        if not email:
            return None

        username = self.get_username(claims)
        full_name = claims.get(self.FULLNAME_CLAIM, username)
        auth_id = claims.get(self.AUTHDATA_CLAIM, username)

        AuthData = apps.get_model("users", "AuthData")
        try:
            # User association exist?
            auth_data = AuthData.objects.get(key=self.AUTHDATA_KEY, value=auth_id)
            user = auth_data.user
        except AuthData.DoesNotExist:
            try:
                # Is a user with the same email?
                user = self.UserModel.objects.get(email=email)
                AuthData.objects.create(
                    user=user, key=self.AUTHDATA_KEY, value=auth_id, extra={}
                )
            except self.UserModel.DoesNotExist:
                if os.getenv("PUBLIC_REGISTER_ENABLED", False) == "True":
                    # Create a new user
                    user = self.UserModel.objects.create(
                        email=email, username=username, full_name=full_name
                    )
                    AuthData.objects.create(
                        user=user, key=self.AUTHDATA_KEY, value=auth_id, extra={}
                    )

                    send_register_email(user)
                    user_registered_signal.send(sender=self.UserModel, user=user)
                else:
                    raise exc.IntegrityError("Sorry, was unable to locate user and registrations have been disabled by the Administrator")

        return user

    def update_user(self, user, claims):
        try:
            user.full_name = claims[self.FULLNAME_CLAIM]
        except KeyError:
            pass
        else:
            user.save()
        return user
