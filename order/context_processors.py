from django.db.models import Sum

from .models import CartItem
from .services import CART_SESSION_KEY


def cart(request):
    """
    تعداد کالاهای سبد برای بج نوبار.
    فقط می‌خواند و برای بازدیدکننده‌ای که سبد ندارد، سبد یا سشن جدید نمی‌سازد.
    """
    if request.user.is_authenticated:
        filters = {"cart__user": request.user}
    else:
        cart_id = request.session.get(CART_SESSION_KEY)
        if not cart_id:
            return {"cart_count": 0}
        filters = {"cart_id": cart_id}

    total = CartItem.objects.filter(**filters).aggregate(n=Sum("quantity"))["n"] or 0
    return {"cart_count": total}
