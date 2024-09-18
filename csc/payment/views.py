from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, View
from django.conf import settings
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse
import razorpay

from .models import PaymentHistory, Payment
from csc_center.models import CscCenter

class PaymentView(CreateView):
    model = Payment
    fields = "__all__"
    template_name = 'payment.html'
    redirect_url = reverse_lazy('payment:payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        amount = 100
        currency = "INR"

        payment_data = {
            "amount": amount * 100,
            "currency": "INR",
            "payment_capture": "1"
        }        

        order = client.order.create(data=payment_data)

        try:
            csc_center = get_object_or_404(CscCenter, slug = self.kwargs.get('slug'))
        except Http404:
            return redirect(self.redirect_url)

        self.model.objects.create(csc_center = csc_center, order_id = order['id'], amount = amount, status = "Created")

        context.update({
            "razorpay_order_id": order['id'],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "amount": amount,
            "currency": currency
        })

        return context
    

class PaymentSuccessView(View):
    def post(self, request, *args, **kwargs):
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        
        # try:
        #     csc_center = get_object_or_404(CscCenter, slug = self.kwargs.get('slug'))
        # except Http404

        if not razorpay_payment_id or not razorpay_order_id:
            return JsonResponse({"status": "Payment failed!", "message": "Missing payment or order ID"}, status=400)    

        try:
            payment = get_object_or_404(Payment, order_id = razorpay_order_id)

            if razorpay_payment_id:
                payment.payment_id = razorpay_payment_id
                payment.status = "Completed"
                payment.save()



                return JsonResponse({"status": "Payment successfull", "payment_id": razorpay_payment_id})
            else:
                return JsonResponse({"status": "Payment failed!"})        
            
        except Http404:
            return JsonResponse({"status": "Invalid order!"})
