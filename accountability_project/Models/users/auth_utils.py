from knox.auth import TokenAuthentication

# The following class is used to override the TokenAuthentication class from django.knox which validates the authentication
# by defaut from a token passed in the Authorization header, and validates from the request cookies.
class TokenAuthSupportCookie(TokenAuthentication):
    """
    Extend the TokenAuthentication class to support cookie based authentication
    """
    def authenticate(self, request):
        # Check if 'auth_token' is in the request cookies.
        # Give precedence to 'Authorization' header.
        if 'auth_token' in request.COOKIES and 'HTTP_AUTHORIZATION' not in request.META:
            return self.authenticate_credentials(
                request.COOKIES.get('auth_token').encode("utf-8")
            )
        return super().authenticate(request)