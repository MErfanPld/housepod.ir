"""منطق سبد خرید و ساخت سفارش"""

from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from products.models import Product

from .models import BankAccount, Cart, CartItem, Order, OrderItem

# شناسهٔ سبد مهمان در *دادهٔ* سشن نگه داشته می‌شود، نه در session_key.
# Django هنگام لاگین session_key را عوض می‌کند (cycle_key) ولی داده‌ها را نگه می‌دارد؛
# پس با این کلید، سبد مهمان بعد از ورود هم پیدا و ادغام می‌شود.
CART_SESSION_KEY = "cart_id"


def _clamp_quantity(quantity: int, product: Product) -> int:
    """تعداد را به موجودی انبار محدود می‌کند (حداقل ۱)."""
    quantity = max(1, int(quantity))
    if product.stock > 0:
        quantity = min(quantity, product.stock)
    return quantity


def get_or_create_cart(request) -> Cart:
    """سبد کاربر لاگین‌شده، یا سبد مهمان مبتنی بر سشن"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        guest = None
        guest_id = request.session.pop(CART_SESSION_KEY, None)
        if guest_id:
            guest = Cart.objects.filter(pk=guest_id, user__isnull=True).first()
        if guest is None and request.session.session_key:
            # سازگاری با سبدهای قدیمی که فقط session_key داشتند
            guest = Cart.objects.filter(
                session_key=request.session.session_key, user__isnull=True
            ).first()

        if guest and guest.pk != cart.pk:
            _merge_carts(guest, cart)
            guest.delete()
        return cart

    cart = None
    cart_id = request.session.get(CART_SESSION_KEY)
    if cart_id:
        cart = Cart.objects.filter(pk=cart_id, user__isnull=True).first()
    if cart is None:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key, user=None
        )
        request.session[CART_SESSION_KEY] = cart.pk
    return cart


def _merge_carts(source: Cart, target: Cart) -> None:
    for item in source.items.select_related("product"):
        existing = target.items.filter(product=item.product).first()
        if existing:
            existing.quantity = _clamp_quantity(existing.quantity + item.quantity, item.product)
            existing.save(update_fields=["quantity"])
        else:
            item.cart = target
            item.quantity = _clamp_quantity(item.quantity, item.product)
            item.save(update_fields=["cart", "quantity"])


def add_to_cart(request, product: Product, quantity: int = 1):
    """
    محصول را به سبد اضافه می‌کند.
    خروجی: (item, limited) — limited یعنی تعداد به‌خاطر موجودی محدود شد.
    """
    cart = get_or_create_cart(request)
    requested = max(1, int(quantity))
    item = CartItem.objects.filter(cart=cart, product=product).first()
    wanted = requested + (item.quantity if item else 0)
    final = _clamp_quantity(wanted, product)

    if item:
        item.quantity = final
        item.save(update_fields=["quantity"])
    else:
        item = CartItem.objects.create(cart=cart, product=product, quantity=final)
    return item, final < wanted


def update_cart_item(cart: Cart, product_id: int, quantity: int) -> bool:
    """خروجی True یعنی تعداد به‌خاطر موجودی محدود شد."""
    item = get_object_or_404(CartItem.objects.select_related("product"), cart=cart, product_id=product_id)
    if quantity <= 0:
        item.delete()
        return False
    final = _clamp_quantity(quantity, item.product)
    item.quantity = final
    item.save(update_fields=["quantity"])
    return final < quantity


def remove_from_cart(cart: Cart, product_id: int) -> None:
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()


@transaction.atomic
def create_order_from_cart(
    *,
    user,
    cart: Cart,
    shipping_cost: Decimal = Decimal("0"),
    user_note: str = "",
    receiver_name: str = "",
    receiver_phone: str = "",
    province: str = "",
    city: str = "",
    postal_code: str = "",
    address: str = "",
) -> Order:
    items = list(cart.items.select_related("product"))
    if not items:
        raise ValueError("سبد خرید خالی است.")

    # قفل ردیف محصولات تا دو سفارش هم‌زمان موجودی را بیش از حد کم نکنند
    locked = {
        p.pk: p
        for p in Product.objects.select_for_update().filter(pk__in=[i.product_id for i in items])
    }

    for item in items:
        product = locked[item.product_id]
        if not product.is_in_stock:
            raise ValueError(f"محصول «{product.name}» موجود نیست.")
        if item.quantity > product.stock:
            raise ValueError(
                f"موجودی «{product.name}» کافی نیست (موجودی: {product.stock})."
            )

    subtotal = sum((item.line_total for item in items), Decimal("0"))
    total = subtotal + shipping_cost
    bank = BankAccount.objects.filter(is_active=True).order_by("order").first()

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING_PAYMENT,
        payment_method=Order.PaymentMethod.CARD_TO_CARD,
        receiver_name=receiver_name or user.get_shipping_receiver(),
        receiver_phone=receiver_phone or user.get_shipping_phone(),
        province=province or user.province,
        city=city or user.city,
        postal_code=postal_code or user.postal_code,
        address=address or user.address,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        user_note=user_note,
        bank_account=bank,
    )

    for item in items:
        product = locked[item.product_id]
        unit = item.unit_price
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=unit,
            quantity=item.quantity,
            line_total=unit * item.quantity,
        )
        product.stock = max(0, product.stock - item.quantity)
        product.save(update_fields=["stock"])

    cart.items.all().delete()
    return order