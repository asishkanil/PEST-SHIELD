from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
import tensorflow as tf
from django.http import HttpResponse
from django.contrib.sessions.backends.db import SessionStore
import numpy as np
import os
from PIL import Image
from .models import Pesticide,Cart # Assuming you have a Pesticide model
from django.shortcuts import render, redirect, get_object_or_404
from .models import Pesticide
from .forms import PesticideForm
from .models import Order
from datetime import datetime




# Load the trained pest classification model
MODEL_PATH = os.path.join(settings.BASE_DIR, "store/pest_classifier_resnet_v2.keras")
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels (must match training dataset)
class_labels = ["Aphids", "Armyworm", "Beetle", "Bollworm", "Grasshopper", "Mites", "Mosquito", "Sawfly", "Stem Borer"]

# Function to preprocess images
def preprocess_image(image_path):
    image = Image.open(image_path)
    image = image.resize((256, 256))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# Function to make predictions
def predict(image_path):
    processed_image = preprocess_image(image_path)
    predictions = model.predict(processed_image)
    predicted_class = np.argmax(predictions)
    confidence = np.max(predictions) * 100
    return class_labels[predicted_class], confidence

# Home Page
def home(request):
    return render(request, "store/home.html")

# Pest detection page
@login_required
def detect_pest(request):
    if request.method == "POST" and request.FILES.get("pest_image"):
        uploaded_file = request.FILES["pest_image"]
        
        # Save the uploaded image in media/uploads/
        file_path = os.path.join(settings.MEDIA_ROOT, "uploads", uploaded_file.name)
        path = default_storage.save(file_path, ContentFile(uploaded_file.read()))

        # Predict pest type
        pest_name, confidence = predict(path)

        # Fetch pesticide recommendations from the database
        # (Assuming your Pesticide model stores the pest name in the 'pest_name' field)
        pesticides = Pesticide.objects.filter(pest_name__iexact=pest_name).values_list("pesticide_name", flat=True)

        # Render a result page that displays the pest name and recommendations
        return render(request, "store/detection_result.html", {
            "pest_name": pest_name,
            "confidence": round(confidence, 2),
            "pesticides": list(pesticides) if pesticides else ["No recommendations found"],
        })

    return render(request, "store/detect_pest.html")


# User Signup
def signup(request):
    if request.user.is_authenticated:
        return redirect("home")  # Redirect if already logged in

    # if request.method == "POST":
    #     username = request.POST["username"].strip()
    #     email = request.POST["email"].strip()
    #     password = request.POST["password"]
    #     confirm_password = request.POST["confirm_password"]

    #     # Validate form fields
    #     if not username or not email or not password:
    #         messages.error(request, "All fields are required!")
    #     elif password != confirm_password:
    #         messages.error(request, "Passwords do not match!")
    #     elif User.objects.filter(username=username).exists():
    #         messages.error(request, "Username already exists!")
    #     elif User.objects.filter(email=email).exists():
    #         messages.error(request, "Email already in use!")
    #     else:
    #         user = User.objects.create_user(username=username, email=email, password=password)
    #         user.save()
    #         messages.success(request, "Account created successfully! You can log in now.")
    #         return redirect("login")  # Redirect to login page

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after successful signup
            messages.success(request, "Account created successfully!")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "store/register.html", {"form": form})

def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin_dashboard")
        else:
            return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if user.is_staff:  # Check if the user is an admin
                messages.success(request, "Welcome to the Admin Dashboard!")
                return redirect("admin_dashboard")
            else:
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("home")  # Redirect to user dashboard

        else:
            messages.error(request, "Invalid Username or Password!")
    else:
        form = AuthenticationForm()

    return render(request, "store/login.html", {"form": form})


# User Logout
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")  # Redirect to login page


def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, "store/cart.html", {"cart_items": cart_items, "total": total})


# Shop Page: Display all pesticides (or recommended ones)
@login_required
def shop(request):
    recommended_pesticides = []
    all_pesticides = Pesticide.objects.all()  # Use Pesticide.objects.all() directly

    if 'detected_pest' in request.session:  # Check if a pest was detected
        detected_pest = request.session['detected_pest']
        recommended_pesticides = Pesticide.objects.filter(pest_name=detected_pest)
        all_pesticides = all_pesticides.exclude(pest_name=detected_pest)  # Exclude recommended ones

    context = {
        'recommended_pesticides': recommended_pesticides,
        'all_pesticides': all_pesticides,  # Correct variable name
    }
    return render(request, 'store/shop.html', context)

def shop_view(request):
    pest_query = request.GET.get('pest', '').strip()  # Get the search input
    if pest_query:
        recommended_pesticides = Pesticide.objects.filter(pest_name__icontains=pest_query)
    else:
        recommended_pesticides = Pesticide.objects.all()

    return render(request, 'store/shop.html', {'recommended_pesticides': recommended_pesticides})
    
    

# Add to Cart view (for handling add-to-cart button clicks)
@login_required
def add_to_cart(request, pesticide_id):
    pesticide = get_object_or_404(Pesticide, id=pesticide_id)
    
    # For now, we assume quantity 1 (or you could get this from POST data)
    quantity = 1
    
    # Create or update a cart item for the user
    cart_item, created = Cart.objects.get_or_create(user=request.user, pesticide=pesticide)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    
    messages.success(request, f"Added {pesticide.pesticide_name} to cart!")
    # Redirect to checkout page after adding to cart
    return redirect("checkout")

from .models import Order  # Ensure Order is imported
SHIPPING_COST = 60 # Set your constant shipping cost here

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items) + SHIPPING_COST
    
    if request.method == "POST":
        address = request.POST.get("address")
        payment_option = request.POST.get("payment_option")  # For now, likely fixed to "Cash on Delivery"
        
        if not address:
            messages.error(request, "Please provide your address.")
            return render(request, "store/checkout.html", {"cart_items": cart_items, "total_price": total_price})
        
        # Create an Order for each Cart item
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                pesticide=item.pesticide,
                quantity=item.quantity,
                total_price=item.total_price() + SHIPPING_COST,  # Apply shipping cost per order/item or overall as desired
                # You can store address and payment option in the Order model if you add those fields.
            )
        # Clear the cart after order placement
        cart_items.delete()
        messages.success(request, "Thank you for your order!")
        return redirect("order_confirmation")
    
    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "shipping_cost": SHIPPING_COST,
    })


from django.shortcuts import render
from .models import Order

from .models import Order

@login_required
def order_confirmation(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-order_date')  # assuming 'user' is a ForeignKey in Order
    return render(request, 'store/order_confirmation.html', {'orders': orders})




from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "increment":
            cart_item.quantity += 1
        elif action == "decrement":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                # Optionally, delete the cart item if quantity becomes 0
                cart_item.delete()
                return HttpResponseRedirect(reverse("checkout"))
        cart_item.save()
    return HttpResponseRedirect(reverse("checkout"))





def admin_dashboard(request):
    products = Pesticide.objects.all()  # Ensure this retrieves products
    orders = Order.objects.all()  # Ensure this retrieves orders
    return render(request, 'store/admin_dashboard.html', {'products': products, 'orders': orders})


def admin_logout(request):
    logout(request)
    messages.success(request, "Admin logged out successfully.")
    return redirect("login")


def manage_stock(request):
    if not request.user.is_staff:  # Ensure only admin can access
        messages.error(request, "Access Denied.")
        return redirect("shop")

    if request.method == "POST":
        pesticide_id = request.POST.get("pesticide_id")
        new_price = request.POST.get("price")
        new_stock = request.POST.get("quantity_available")

        try:
            pesticide = Pesticide.objects.get(id=pesticide_id)
            pesticide.price = new_price
            pesticide.quantity_available = new_stock
            pesticide.save()
            messages.success(request, "Stock and price updated successfully!")
        except Pesticide.DoesNotExist:
            messages.error(request, "Pesticide not found.")

        return redirect("manage_stock")

    pesticides = Pesticide.objects.all()
    return render(request, "store/manage_stock.html", {"pesticides": pesticides})

def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to '{new_status}' successfully.")
        else:
            messages.error(request, "Invalid status update.")
        return redirect("admin_dashboard")
    
    return render(request, "store/update_order_status.html", {"order": order})


def edit_product(request, product_id):
    product = get_object_or_404(Pesticide, id=product_id)

    if request.method == "POST":
        form = PesticideForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("admin_dashboard")  # Make sure this is the correct redirect name
    else:
        form = PesticideForm(instance=product)

    return render(request, "store/edit_product.html", {"form": form})



@login_required
def order_success(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        pincode = request.POST.get('pincode')
        address = request.POST.get('address')

        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('checkout')

        for item in cart_items:
            Order.objects.create(
                user=request.user,
                pesticide=item.pesticide,
                quantity=item.quantity,
                total_price=item.total_price(),
                phone=phone,
                pincode=pincode,
                address=address,
                order_date=datetime.now(),
                status='Placed'
            )

        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return render(request, 'store/order_success.html')

    return redirect('checkout')

def add_pesticide(request):
    if request.method == 'POST':
        pest_name = request.POST.get('pest_name')
        pesticide_name = request.POST.get('pesticide_name')
        price = request.POST.get('price')
        quantity_available = request.POST.get('quantity_available')
    

        Pesticide.objects.create(
            pest_name=pest_name,
            pesticide_name=pesticide_name,
            price=price,
            quantity_available=quantity_available,
            
        )
        return redirect('shop')  # Change to your actual redirect URL name
    return render(request, 'store/add_pesticide.html')









