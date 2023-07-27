from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate

from .models import Task
from .serializers import TodoSerializer
from django.core.exceptions import ValidationError

import json
import datetime

class GetTokenView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token = AccessToken.for_user(user)
            token_exp_second = token.get("exp")
            token_exp_date = datetime.datetime.fromtimestamp(token_exp_second)
            formatted_token_exp_date = token_exp_date.strftime("%Y-%m-%d %H:%M:%S")
            json_response = {
                                "access_token": str(token),
                                "token_expiration": str(formatted_token_exp_date)
                            }
            return Response(json_response, status=status.HTTP_200_OK)
        else:
            json_response = {"error": "Invalid credentials."}
            return Response(json_response, status=status.HTTP_401_UNAUTHORIZED)



class TaskListApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.all()
        serializer = TodoSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            request_body = json.loads(request.body.decode())
            task_fields = [field.name for field in Task._meta.fields]
            if set(request_body.keys()) <= set(task_fields):
                try:
                    title = request_body["title"]
                    done = request_body["done"]
                except KeyError:
                    # for example the request has title but does not have done.
                    return Response({"error": "some necessary field not found in your request."}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    Task.objects.create(title=title, done=done)
                    return Response({"detail" : "task created successfully."}, status=status.HTTP_200_OK)
                except ValidationError:
                    # for example title is integer or done does not have boolean value.
                    return Response({"error": "some thing were wrong in your request."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # for example the request has some parameters that they are not defined in Task model.
                return Response({"error": "your request format is not correct."}, status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError:
            # when json format is not correct.
            return Response({"error": "your request body is not correct."}, status=status.HTTP_400_BAD_REQUEST)
