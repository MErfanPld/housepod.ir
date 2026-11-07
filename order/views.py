from decimal import Decimal
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView

from products.models import Product

from .forms import CheckoutForm, ReceiptUploadForm
from .models import BankAccount, Order, PaymentReceipt
from .services import (
    add_to_cart,
    create_order_from_cart,
    get_or_create_cart,
    remove_from_cart,
    update_cart_item,
)


class CartDetailView(TemplateView):
    """نمایش سبد خرید"""
    template_name = "order/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        items = list(cart.items.select_related("product"))
        context["cart"] = cart
        context["items"] = items
        context["total"] = sum((i.line_total for i in items), Decimal("0"))
        return context


class AddToCartView(View):
    """افزودن محصول به سبد (POST)"""

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs["slug"], is_active=True)
        try:
            qty = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1
        if not product.is_in_stock:
            messages.error(request, "این محصول موجود نیست.")
            return redirect(product.get_absolute_url())

        _, limited = add_to_cart(request, product, qty)
        if limited:
            messages.warning(
                request,
                f"از «{product.name}» فقط {product.stock} عدد موجود است؛ تعداد سبد اصلاح شد.",
            )
        else:
            messages.success(request, f"«{product.name}» به سبد اضافه شد.")

        next_url = request.POST.get("next")
        if not (next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        )):
            next_url = reverse("order:cart")
        return redirect(next_url)


class UpdateCartItemView(View):
    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1
        limited = update_cart_item(cart, kwargs["product_id"], quantity)
        if limited:
            messages.warning(request, "تعداد درخواستی بیش از موجودی بود و اصلاح شد.")
        else:
            messages.success(request, "سبد به‌روز شد.")
        return redirect("order:cart")


class RemoveCartItemView(View):
    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        remove_from_cart(cart, kwargs["product_id"])
        messages.success(request, "از سبد حذف شد.")
        return redirect("order:cart")


class CheckoutView(LoginRequiredMixin, FormView):
    """ثبت سفارش از روی سبد + آدرس ارسال"""
    template_name = "order/checkout.html"
    form_class = CheckoutForm
    login_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if not request.user.check_profile_complete():
            messages.warning(request, "لطفاً ابتدا اطلاعات پروفایل و آدرس را تکمیل کنید.")
            # next تا بعد از تکمیل پروفایل، کاربر به چک‌اوت برگردد
            query = urlencode({"next": reverse("order:checkout")})
            return redirect(f"{reverse('accounts:profile_complete')}?{query}")

        self.cart = get_or_create_cart(request)
        self.cart_items = list(self.cart.items.select_related("product"))
        if not self.cart_items:
            messages.warning(request, "سبد خرید خالی است.")
            return redirect("order:cart")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        user = self.request.user
        return {
            "receiver_name": user.get_shipping_receiver(),
            "receiver_phone": user.get_shipping_phone(),
            "province": user.province,
            "city": user.city,
            "postal_code": user.postal_code,
            "address": user.address,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subtotal = sum((i.line_total for i in self.cart_items), Decimal("0"))
        shipping_cost = Decimal("0")  # بعداً قابل تنظیم
        context.update(
            cart=self.cart,
            items=self.cart_items,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=subtotal + shipping_cost,
        )
        return context

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم را بررسی کنید.")
        return super().form_invalid(form)

    def form_valid(self, form):
        try:
            order = create_order_from_cart(
                user=self.request.user,
                cart=self.cart,
                shipping_cost=Decimal("0"),
                **form.cleaned_data,
            )
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return redirect("order:cart")
        messages.success(
            self.request,
            f"سفارش {order.order_number} ثبت شد. لطفاً مبلغ را کارت‌به‌کارت واریز کنید.",
        )
        return redirect("order:payment", order_number=order.order_number)


def _payment_context(order, receipt_form=None):
    return {
        "order": order,
        "bank_accounts": BankAccount.objects.filter(is_active=True),
        "receipt_form": receipt_form or ReceiptUploadForm(),
        "latest_receipt": order.receipts.order_by("-uploaded_at").first(),
    }


class PaymentView(LoginRequiredMixin, DetailView):
    """نمایش کارت مقصد + فرم آپلود فیش"""
    model = Order
    template_name = "order/payment.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items", "receipts")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_payment_context(self.object))
        return context


class ReceiptUploadView(LoginRequiredMixin, View):
    """آپلود فیش برای سفارش"""
    login_url = reverse_lazy("accounts:login")

    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        if not order.can_upload_receipt:
            messages.error(request, "برای این سفارش امکان آپلود فیش نیست.")
            return redirect(order.get_absolute_url())

        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.order = order
            receipt.status = PaymentReceipt.Status.PENDING
            receipt.save()
            order.mark_awaiting_verify()
            messages.success(request, "فیش ارسال شد. پس از بررسی، وضعیت سفارش به‌روز می‌شود.")
            return redirect("order:order_detail", order_number=order.order_number)

        # به‌جای ریدایرکت، همان صفحه با خطاهای فرم نمایش داده می‌شود
        messages.error(request, "فیش ارسال نشد؛ خطاهای فرم را بررسی کنید.")
        return render(request, "order/payment.html", _payment_context(order, form))


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "order/order_list.html"
    context_object_name = "orders"
    paginate_by = 10
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "order/order_detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items", "receipts")