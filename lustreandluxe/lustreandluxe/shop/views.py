from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Product
from django.views.decorators.http import require_POST


# Product views
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

# Cart views
def cart_detail(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    # Use list(cart.items()) in case we modify cart inside loop
    for product_id, quantity in list(cart.items()):
        try:
            product = Product.objects.get(pk=int(product_id))
        except Product.DoesNotExist:
            # Remove invalid product from cart
            del cart[product_id]
            request.session['cart'] = cart  # update session
            continue

        subtotal = product.price * quantity
        total += subtotal
        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'shop/cart_detail.html', {'cart_products': products, 'total': total})



def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    return redirect('cart_detail')



def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('cart_detail')

#checkout views

def checkout(request):
    cart = request.session.get('cart', {})

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        # Create the Order
        order = Order.objects.create(
            customer_name=name,
            email=email,
            phone=phone,
            address=address
        )

        # Add items to Order
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, pk=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

            # reduce stock
            product.stock -= quantity
            product.save()

        # clear cart
        request.session['cart'] = {}
        messages.success(request, "Your order has been placed successfully!")

        return redirect('product_list')

    return render(request, 'shop/checkout.html')

