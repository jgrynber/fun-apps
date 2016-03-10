from django.conf.urls import patterns, url


urlpatterns = patterns('payment_api.views',
    url(r'^payment-notification/$', 'payment_notification', name='payment-notification'),
)
