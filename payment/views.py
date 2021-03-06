# -*- coding: utf-8 -*-

import logging

import requests
from requests.exceptions import ConnectionError

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponseBadRequest, Http404
from django.views.decorators.csrf import csrf_exempt

import slumber.exceptions

from edxmako.shortcuts import render_to_response

from commerce import ecommerce_api_client

from .utils import get_order, get_course, get_basket, get_order_context

logger = logging.getLogger(__name__)


def get_order_or_404(user, order_id):
    try:
        return get_order(user, order_id)
    except (slumber.exceptions.HttpNotFoundError, slumber.exceptions.HttpClientError):
        raise Http404()


def get_basket_or_404(user, order_id):
    try:
        return get_basket(user, order_id)
    except (slumber.exceptions.HttpNotFoundError, slumber.exceptions.HttpClientError):
        raise Http404()


def get_course_or_404(order_or_basket):
    """Retrieve course corresponding to order or basket.

    If the course does not exist, this will raise a 404 error.
    """
    try:
        course = get_course(order_or_basket)
    except (KeyError, IndexError, ObjectDoesNotExist):
        raise Http404
    return course


@csrf_exempt
@login_required
def paybox_success(request):
    """Called at the end of a successful payment.

    E.g arguments: amount=10000&reference-fun=EDX-100056&autorisation=XXXXXX&reponse-paybox=00000&appel-paybox=16047443&transaction-paybox=7558206
    """
    # TODO: find a smart way to factorize the control logic upon the 3 views

    if request.GET.get('reponse-paybox') != '00000' or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    if settings.FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION:
        # TODO what should we do with the response?
        _response = requests.post(settings.ECOMMERCE_NOTIFICATION_URL, request.GET)

    order = get_order_or_404(request.user, request.GET['reference-fun'])
    course = get_course_or_404(order)

    return render_to_response('payment/success.html', {
        'order': order,
        'ordered_course': course,
    })


@csrf_exempt
@login_required
def paybox_error(request):
    """Called on transaction error."""
    errorcode = request.GET.get('reponse-paybox')

    if errorcode is None or errorcode in ('00000', '00001') or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    order_number = request.GET['reference-fun']
    basket = get_basket_or_404(request.user, order_number)
    course = get_course_or_404(basket)
    total_excl_tax = basket['lines'][0]['price_excl_tax']

    return render_to_response('payment/error.html', {
        'errorcode': errorcode,
        'total_excl_tax': total_excl_tax,
        'basket_course': course,
        'order_number': order_number,
    })


@csrf_exempt
@login_required
def paybox_cancel(request):
    """User clicked on 'Cancel' before entering card information."""
    if request.GET.get('reponse-paybox') not in ('00001', '00004') or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    order_number = request.GET['reference-fun']
    basket = get_basket_or_404(request.user, order_number)
    course = get_course_or_404(basket)
    total_excl_tax = basket['lines'][0]['price_excl_tax']

    return render_to_response('payment/cancel.html', {
        'total_excl_tax': total_excl_tax,
        'basket_course': course,
        'order_number': order_number,
    })


@login_required
def detail_receipt(request, order_id):
    order = get_order_or_404(request.user, order_id)
    if not order:
        return render_to_response("payment/order.html", {"order": None, 'order_id': order_id})
    course = get_course_or_404(order)
    context = get_order_context(request.user, order, course)
    return render_to_response('payment/order.html', context)


@login_required
def list_receipts(request):
    api = ecommerce_api_client(request.user)
    try:
        order_history = api.orders().get()
    except ConnectionError as e:
        logger.exception(e)
        order_history = []

    return render_to_response('payment/list_orders.html', {"order_history": order_history})

