from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_oauth.authentication import OAuth2Authentication

from .serializers import PaymentNotificationSerializer


class PaymentNotificationAPIView(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)

    def post(self, request, format=None):
        serializer = PaymentNotificationSerializer(data=request.DATA)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


payment_notification = PaymentNotificationAPIView.as_view()
