from rest_framework.authtoken.models import Token

def get_or_create(user):
    token = Token.objects.get_or_create(user=user)
    key = str(token[0])
    return {"key":key}