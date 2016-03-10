from rest_framework import serializers


class PaymentNotificationSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
