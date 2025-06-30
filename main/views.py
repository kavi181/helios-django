from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render
import os
import fitz  # PyMuPDF
import re
from transformers import pipeline

User = get_user_model()

# Pages
def home(request):
    bg_class = request.user.background_choice if request.user.is_authenticated else ''
    return render(request, 'main/home.html', {'bg_class': bg_class})

def about(request):
    return render(request, 'main/about.html')

def signup(request):
    return render(request, 'main/signup.html')

#def dashboard(request):
   # return render(request, 'main/dashboard.html')

def participant(request):
    return render(request, 'main/participant.html')

def contactus(request):
    return render(request, 'main/contactus.html')

def signup_choice(request):
    return render(request, 'main/signup_choice.html')


def custom_logout_view(request):
    logout(request)
    return redirect('login')

# Login View
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email=email).first()

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'main/login.html', {'error': 'Invalid email or password'})
        else:
            return render(request, 'main/login.html', {'error': 'User not found'})

    return render(request, 'main/login.html')

# Signup View
from django.contrib.auth import login, authenticate

def signup_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup_form')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup_form')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup_form')

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Automatically log in the user
            login(request, user)

            # Redirect to the participant consent page
            return redirect('participant')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('signup_form')

    return render(request, 'main/signup_form.html')

# Background Preference Handler
@login_required
def profile_view(request):
    if request.method == 'POST':
        bg = request.POST.get('background_choice')
        request.user.background_choice = bg
        request.user.save()
        return redirect('home')  # 👈 this is the key fix!
    return render(request, 'main/profile.html')


# PDF & AI Quiz Section
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_local_questions(text):
    prompt = (
        "Generate 3 unique multiple-choice questions (MCQs) from the following passage. "
        "Each question should have:\n"
        "- A question\n"
        "- Four options (A, B, C, D)\n"
        "- Correct answer labeled as: Answer: X\n\n"
        f"Passage:\n{text[:600]}"
    )

    try:
        output = qa_pipeline(prompt, max_length=512, do_sample=True, temperature=0.9)
        return output[0]['generated_text']
    except Exception as e:
        print("Error generating questions:", e)
        return ""

def extract_text_from_pdf(book_id):
    filepath = os.path.join(settings.BASE_DIR, 'main', 'static', 'pdf', f'{book_id}.pdf')
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_generated_text(text):
    question_blocks = re.findall(
        r'(?:Question:)?\s*(.*?)\s*Options:\s*A\.?\s*(.*?)\s*B\.?\s*(.*?)\s*C\.?\s*(.*?)\s*D\.?\s*(.*?)\s*Answer:\s*([A-D])',
        text,
        re.DOTALL
    )

    questions = []
    for question, a, b, c, d, answer in question_blocks:
        questions.append({
            'question': question.strip(),
            'options': [a.strip(), b.strip(), c.strip(), d.strip()],
            'answer': answer.strip()
        })
    return questions


@login_required
def quiz(request, slug):  
    book = get_object_or_404(Book, slug=slug)
    progress, _ = UserBookProgress.objects.get_or_create(user=request.user, book=book)
    questions = get_manual_questions()

    if 'attempts' not in request.session:
        request.session['attempts'] = 0

    score = None
    percent = None
    attempts = request.session['attempts']
    remaining_attempts = 3 - attempts

    # ✅ Initialize next_book    
    next_book = None
    if request.method == 'POST':
        score = 0
        for idx, q in enumerate(questions, 1):
            user_ans = request.POST.get(f'q{idx}')
            if user_ans and user_ans.upper() == q['answer']:
                score += 1

        percent = (score / len(questions)) * 100
        attempts += 1
        request.session['attempts'] = attempts
        remaining_attempts = 3 - attempts

        if percent >= 90:
            progress.quiz_completed = True
            progress.save()

            # Unlock next book
            next_book = Book.objects.filter(order=book.order + 1).first()
            if next_book:
                UserBookProgress.objects.get_or_create(user=request.user, book=next_book)

            # Reset attempts
            request.session['attempts'] = 0
            attempts = 0
            remaining_attempts = 3

    show_quiz_form = score is None or (not progress.quiz_completed and attempts < 3)

    return render(request, 'main/quiz.html', {
        'book_title': book.title,
        'questions': questions,
        'score': score,
        'percent': percent,
        'completed': progress.quiz_completed,
        'attempts': attempts,
        'remaining_attempts': remaining_attempts,
        'show_quiz_form': show_quiz_form,
        'next_book': next_book,
    })

from django.views.decorators.http import require_POST

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    return render(request, 'shop/cart.html', {'cart': cart})

@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    product_title = request.POST.get('title')
    qty_ebook = int(request.POST.get('qty_ebook', 0))
    qty_soft = int(request.POST.get('qty_soft', 0))

    if not product_id:
        return redirect('shop')

    cart = request.session.get('cart', {})

    if product_id not in cart:
        cart[product_id] = {
            'title': product_title,
            'qty_ebook': qty_ebook,
            'qty_soft': qty_soft,
        }
    else:
        cart[product_id]['qty_ebook'] += qty_ebook
        cart[product_id]['qty_soft'] += qty_soft

    request.session['cart'] = cart
    return redirect('cart')

import requests
# Replace this function for manual quiz
def get_manual_questions():
    return [
        {
            "question": "What causes dengue fever?",
            "choices": ["A. Virus from Aedes mosquito", "B. Dirty water", "C. Bacteria", "D. Cold weather"],
            "answer": "A"
        },
        {
            "question": "How can you prevent dengue?",
            "choices": ["A. Keep surroundings clean", "B. Eat more sugar", "C. Avoid water", "D. Stay indoors"],
            "answer": "A"
        },
        {
            "question": "When does the Aedes mosquito bite?",
            "choices": ["A. Morning and evening", "B. Midnight", "C. Afternoon", "D. All day"],
            "answer": "A"
        },
        {
            "question": "A common symptom of dengue is?",
            "choices": ["A. High fever", "B. Itchy eyes", "C. Cough", "D. Sneezing"],
            "answer": "A"
        },
        {
            "question": "Where do mosquitoes lay eggs?",
            "choices": ["A. Clean stagnant water", "B. Soil", "C. Sand", "D. River"],
            "answer": "A"
        },
        {
            "question": "If you have dengue symptoms?",
            "choices": ["A. Visit doctor", "B. Ignore it", "C. Play outside", "D. Eat junk"],
            "answer": "A"
        },
        {
            "question": "Protect from bites by?",
            "choices": ["A. Mosquito repellent", "B. Wear shorts", "C. Open windows", "D. No need"],
            "answer": "A"
        },
        {
            "question": "Fogging helps?",
            "choices": ["A. Kill mosquitoes", "B. Clean air", "C. Water plants", "D. Make sleepy"],
            "answer": "A"
        },
        {
            "question": "Check your home for breeding how often?",
            "choices": ["A. Weekly", "B. Every 3 months", "C. Yearly", "D. Never"],
            "answer": "A"
        },
        {
            "question": "Which is NOT a dengue symptom?",
            "choices": ["A. Toothache", "B. Headache", "C. Rash", "D. Joint pain"],
            "answer": "A"
        }
    ]


# views.py book 
import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Book, UserBookProgress
from django.contrib.auth.decorators import login_required


@login_required
def read_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    user = request.user

    # Get or create user progress
    user_progress, created = UserBookProgress.objects.get_or_create(user=user, book=book)

    # If user clicks "Mark as Read"
    if request.method == "POST" and 'mark_read' in request.POST:
        user_progress.has_read = True
        user_progress.save()
        return redirect('quiz', slug=book.slug)


    # Load all image files
    image_folder = os.path.join(settings.BASE_DIR, 'main', 'static', 'book_pages', slug)
    try:
        image_files = sorted([
            f for f in os.listdir(image_folder)
            if f.endswith(".jpg") or f.endswith(".png")
        ])
    except FileNotFoundError:
        image_files = []

    # Logic to restrict to 5 pages after read, unless purchased
    if user_progress.has_read and not getattr(user_progress, 'purchased', False):
        image_files = image_files[:5]  # Show only first 5 pages

    page_numbers = range(1, len(image_files) + 1)

    return render(request, "main/read_book.html", {
        "book": book,
        "user_progress": user_progress,
        "page_numbers": page_numbers,
        "slug": slug,
    })


# views.py

from .models import Book, UserBookProgress

def dashboard(request):
    all_books = Book.objects.order_by('order')

    # ✅ Automatically unlock the first book for every user
    if all_books.exists():
        first_book = all_books.first()
        UserBookProgress.objects.get_or_create(user=request.user, book=first_book)

    unlocked_books = []
    for book in all_books:
        progress = UserBookProgress.objects.filter(user=request.user, book=book).first()
        is_unlocked = bool(progress)
        unlocked_books.append((book, is_unlocked))

    return render(request, 'main/dashboard.html', {
        'unlocked_books': unlocked_books
    })
# views.py
def read_page(request, slug, page_number):
    book = get_object_or_404(Book, slug=slug)

    # Save progress
    PageReadProgress.objects.get_or_create(
        user=request.user,
        book=book,
        page_number=page_number
    )

    # Load image and render
    image_path = f'book_pages/{slug}/page{page_number}.jpg'
    total_pages = get_total_pages(book.slug)

    return render(request, 'main/read_page.html', {
        'book': book,
        'page_number': page_number,
        'image_path': image_path,
        'total_pages': total_pages
    })
from django.shortcuts import render, get_object_or_404
from .models import Book
import os

def get_all_page_paths(slug):
    base_dir = f'main/static/book_pages/{slug}'
    files = sorted(os.listdir(base_dir))
    return [f'book_pages/{slug}/{file}' for file in files if file.endswith('.jpg')]

@login_required
def read_scroll(request, slug):
    book = get_object_or_404(Book, slug=slug)
    user = request.user

    # Get or create progress
    progress, _ = UserBookProgress.objects.get_or_create(user=user, book=book)

    # Image loading logic
    image_folder = os.path.join(settings.BASE_DIR, 'main', 'static', 'book_pages', slug)
    try:
        image_files = sorted([
            f for f in os.listdir(image_folder)
            if f.endswith('.jpg') or f.endswith('.png')
        ])
    except FileNotFoundError:
        image_files = []

    # Show only 5 pages if already read and not purchased
    if progress.has_read and not getattr(progress, 'purchased', False):
        image_files = image_files[:5]

    image_paths = [f'book_pages/{slug}/{img}' for img in image_files]

    return render(request, 'main/read_scroll.html', {
        'book': book,
        'pages': image_paths,
        'slug': slug
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, UserBookProgress
from django.conf import settings
import os
from django.contrib.auth.decorators import login_required

@login_required
def read_page(request, slug, page_number):
    book = get_object_or_404(Book, slug=slug)
    user = request.user

    # Track progress
    user_progress, _ = UserBookProgress.objects.get_or_create(user=user, book=book)

    # Load image pages
    image_folder = os.path.join(settings.BASE_DIR, 'main', 'static', 'book_pages', slug)
    try:
        image_files = sorted([
            f for f in os.listdir(image_folder)
            if f.endswith('.jpg') or f.endswith('.png')
        ])
    except FileNotFoundError:
        image_files = []

    total_pages = len(image_files)
    if page_number < 1 or page_number > total_pages:
        return redirect('read_page', slug=slug, page_number=1)

    # Only show first 5 pages if book is read and not purchased
    if user_progress.has_read and not getattr(user_progress, 'purchased', False):
        if page_number > 5:
            return redirect('read_page', slug=slug, page_number=5)

    image_path = f'book_pages/{slug}/{image_files[page_number - 1]}'

    return render(request, 'main/read_page.html', {
        'book': book,
        'page_number': page_number,
        'total_pages': total_pages,
        'image_path': image_path,
        'slug': slug
    })
