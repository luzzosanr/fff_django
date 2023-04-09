import logging
from accounts.models import verif_and_register, ShopperProfile
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view

logger = logging.getLogger("django")

@api_view(['GET'])
def is_logged(request):
    print(request.user)
    if not request.user.is_authenticated:
        return Response({'status': 'not logged'})
    
    return Response({'status': f"logged in as {request.user.role}"})

@api_view(['GET'])
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({'status': 'logged out'})
    else:
        return Response({'status': 'not logged'})

@api_view(['POST'])
def login_user(request):
    """
    :param request: username, password
    :return: login the user
    """
    if request.user.is_authenticated and request.user.role == request.data.get('user_type'):
        return Response({'status': 'already logged'})
    elif request.user.is_authenticated:
        logout(request)
        
    
    username = request.data.get('username')
    password = request.data.get('password')
    logger.debug(f"Authenticating {username}")
    user = authenticate(request, username = username, password = password)
    logger.debug(f"User {user} authenticated")
    
    if user and user.role == request.data.get('user_type'):
        logger.debug(f"Logging in {user} as {user.role}")
        login(request, user)
        logger.debug(f"User {user} logged in as {user.role}")
        return Response({'status': 'success'})
    else:
        return Response({'status': 'wrong credentials'})

@api_view(['POST'])
def register(request):
    if request.user.is_authenticated:
        return Response({'status': 'already logged'})
    
    created, res, user = verif_and_register(email = request.data.get('username'), password = request.data.get('password'), type = request.data.get('user_type'))
    
    if created:
        logger.debug(f"Logging in {user} as {user.role}")
        login(request, user)
        logger.debug(f"User {user} logged in as {user.role}")
    
    return Response(res)

@api_view(['GET'])
def get_payment_profile(request):
    if not request.user.is_authenticated or request.user.role != 'SHOPPER':
        return Response({'status': 'not logged'})
    
    return Response({'status': 'success', 'address': ShopperProfile.objects.get(user = request.user).address})

