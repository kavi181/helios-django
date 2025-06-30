from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Book

def shop_view(request):
    books = Book.objects.all()
    return render(request, 'shop/shop.html', {'books': books})

def cart_view(request):
    cart_dict = request.session.get('cart', {})
    cart_items = list(cart_dict.values())  # Convert to list of items for template loop
    return render(request, 'shop/cart.html', {'cart': cart_items})

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        title = request.POST.get('title')
        qty_ebook = int(request.POST.get('qty_ebook', 0))
        qty_soft = int(request.POST.get('qty_soft', 0))

        # Initialize cart if not existing
        if 'cart' not in request.session:
            request.session['cart'] = {}

        cart = request.session['cart']

        # Sum up quantity if product already in cart
        if product_id in cart:
            cart[product_id]['qty_ebook'] += qty_ebook
            cart[product_id]['qty_soft'] += qty_soft
        else:
            cart[product_id] = {
                'title': title,
                'qty_ebook': qty_ebook,
                'qty_soft': qty_soft
            }

        request.session.modified = True
        return redirect('cart')  # redirect to cart view


@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        action = request.POST.get('action')
        if action and action.startswith('dec_'):
            action_parts = action.split('_')
            if len(action_parts) == 3:
                field, book_index = action_parts[1], int(action_parts[2])

                cart_items = list(cart.items())
                if 0 <= book_index < len(cart_items):
                    product_id, data = cart_items[book_index]
                    if field == 'ebook':
                        data['qty_ebook'] = max(0, data['qty_ebook'] - 1)
                    elif field == 'soft':
                        data['qty_soft'] = max(0, data['qty_soft'] - 1)
                    cart[product_id] = data

        request.session['cart'] = cart
        request.session.modified = True
        return redirect('cart')
