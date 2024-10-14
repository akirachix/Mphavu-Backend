import json
import logging
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.contrib.auth import authenticate, login as django_login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
# Set up OAuth
oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"http://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)
# Set up logger
logger = logging.getLogger(__name__)
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        logger.info(f"Login attempt for email: {email}")
        user = authenticate(email=email, password=password)
        if user is not None and user.is_active:
            django_login(request, user)
            logger.info(f"User {email} logged in successfully.")
            return JsonResponse({'status': 'success', 'message': 'Logged in successfully!'}, status=200)
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)
@csrf_exempt
def loginSSO(request):
    """Redirect to the Auth0 login page for SSO."""
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )
@csrf_exempt
def callback(request):
    """Handle the callback from Auth0 and return a JSON response with user details."""
    try:
        token = oauth.auth0.authorize_access_token(request)
        request.session["user"] = token
        logger.info("OAuth callback successful.")
        # Return user information as JSON
        return JsonResponse({
            'status': 'success',
            'token': token,
        }, status=200)
    except Exception as e:
        logger.error(f"Error during OAuth callback: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to authorize'}, status=400)
@csrf_exempt
def logout(request):
    """Log out the user and clear the session."""
    request.session.clear()
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'User logged out successfully'}, status=200)
    else:
        return redirect(
            f"http://{settings.AUTH0_DOMAIN}/v2/logout?"
            + urlencode(
                {
                    "returnTo": request.build_absolute_uri(reverse("index")),
                    "client_id": settings.AUTH0_CLIENT_ID,
                },
                quote_via=quote_plus,
            ),
        )
def index(request):
    """Return user authentication details as JSON."""
    return JsonResponse({
        "user_authenticated": request.user.is_authenticated,
        "session": request.session.get("user"),
    })