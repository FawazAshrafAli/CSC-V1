from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, View
from django.conf import settings
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse, HttpResponse
import razorpay
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.templatetags.static import static
from django.utils import timezone

from .models import PaymentHistory, Payment, Price
from csc_center.models import CscCenter



class PaymentView(CreateView):
    model = Payment
    fields = "__all__"
    template_name = 'payment.html'
    redirect_url = reverse_lazy('payment:payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        price_obj = Price.objects.all().first()
        amount = price_obj.price

        today = timezone.now().date()

        if today >= price_obj.from_date and today <= price_obj.to_date:
            amount = price_obj.offer_price
            
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
            "currency": currency,
            "csc_center": csc_center
        })

        return context
    
    def get(self, request, *args, **kwargs):
        try:
            csc_center = get_object_or_404(CscCenter, slug = self.kwargs.get('slug'))
            if csc_center.is_active == True:
                return redirect(reverse_lazy('home:error404'))
        except Http404:
            return redirect(self.redirect_url)
        return super().get(request, *args, **kwargs)


class PaymentSuccessView(View):
    success_url = reverse_lazy('users:home')

    def html_to_pdf(self, template_src, context_dict={}):
        template = get_template(template_src)
        html = template.render(context_dict)
        result = HttpResponse(content_type="application/pdf")
        pdf = pisa.CreatePDF(html, dest=result)
        if not pdf.err:
            return result
        return None

    def send_payment_success_email(self, request, payment):
        subject = "Payment Successfull and CSC Center Account Activated"

        service_charge = 50
        total = payment.amount + service_charge
        relative_image_url = static('images/logo.png')
        full_image_url = request.build_absolute_uri(relative_image_url)

        pdf_data = {
            "payment": payment,
            "image": full_image_url,
            "service_charge": service_charge,
            "total": total
        }

        pdf = self.html_to_pdf("invoice/invoice.html", pdf_data)

        email_context = {
            "csc_center_name": payment.csc_center.name,
            "owner": payment.csc_center.owner,
            "amount": payment.amount
        }

        email_body = render_to_string('payment_email_templates/payment_successful.html', email_context)

        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[payment.csc_center.email]
        )

        email.content_subtype = 'html'

        if pdf:
            email.attach('invoice.pdf', pdf.content, 'application/pdf')

        email.send()
        
        return "Email sent successfully"
    
    def post(self, request, *args, **kwargs):
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        csc_center = request.POST.get('csc_center')
        
        try:
            csc_center = get_object_or_404(CscCenter, slug = csc_center)
        except Http404:
            pass
            

        if not razorpay_payment_id or not razorpay_order_id or not csc_center:
            return JsonResponse({"status": "Payment failed!", "message": "Missing payment or order ID"}, status=400)    

        try:
            payment = get_object_or_404(Payment, order_id = razorpay_order_id)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment_details = client.payment.fetch(razorpay_payment_id)

            payment_method = payment_details['method']
            card_last4 = payment_details.get('card', {}).get('last4', None)     

            if razorpay_payment_id:
                payment.payment_id = razorpay_payment_id
                payment.status = "Completed"
                payment.payment_method = str(payment_method).capitalize()
                if card_last4:
                    payment.card_last4 = card_last4
                payment.save()

                csc_center.is_active = True
                csc_center.status = "Paid"
                csc_center.save()

                self.send_payment_success_email(request, payment)
                messages.success(request, "Payment Completed. Your account is now activated.")
                return redirect(self.success_url)
            else:
                return JsonResponse({"status": "Payment failed!"})        
            
        except Http404:
            return JsonResponse({"status": "Invalid order!"})


def get_price(request):
    price = Price.objects.all().first()
    if price:
        data = {"price": price.price}
        if price.offer_price:
            today = timezone.now().date()
            if today >= price.from_date and today <= price.to_date:
                data = {
                "price": price.offer_price,
                "from_date": price.from_date if price.from_date else None,
                "to_date": price.to_date if price.to_date else None,
                "description": price.description if price.description else None,
            }
    else:
        data = {"error": "No price found!"}

    return JsonResponse(data)