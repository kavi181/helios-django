from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required




def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

def signup(request):
    return render(request, 'main/signup.html')

def dashboard(request):
    return render(request, 'main/dashboard.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')  # ✅ Go to dashboard after login
            else:
                return render(request, 'main/login.html', {'error': 'Invalid email or password'})

        except User.DoesNotExist:
            return render(request, 'main/login.html', {'error': 'User not found'})

    return render(request, 'main/login.html')

    return render(request, 'main/login.html')
def participant(request):
    return render(request, 'main/participant.html')
def contactus(request):
    return render(request, 'main/contactus.html')

def signup_choice(request):
    # Renders the account type selection page.
    return render(request, 'main/signup_choice.html')

def signup_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup_form')
        
        # Create user (you might also want to do further validation)
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, "Account created successfully.")
            return redirect('login') 
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('signup_form')
    
    # GET request renders the sign up form.
    return render(request, 'main/signup_form.html')
def profile(request):
    return render(request, 'main/profile.html')
def custom_logout_view(request):
    logout(request)
    return redirect('login')

from transformers import pipeline
import random
import fitz  # PyMuPDF
import os
from django.conf import settings

# Load model once
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_local_questions(text):
    question_generator = pipeline("text2text-generation", model="google/flan-t5-base")

    prompt = (
        "Generate 3 unique multiple-choice questions (MCQs) from the following passage. "
        "Each question should have:\n"
        "- A question\n"
        "- Four options (A, B, C, D)\n"
        "- Correct answer labeled as: Answer: X\n\n"
        f"Passage:\n{text[:600]}"
    )

    try:
        output = question_generator(prompt, max_length=512, do_sample=True, temperature=0.9)
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def quiz(request, book_id):
    text = extract_text_from_pdf(book_id)
    questions = generate_ai_questions(text)

    return render(request, 'main/quiz.html', {
        'book_title': book_id.replace('-', ' ').title(),
        'questions': questions
    })
import re

def parse_generated_text(text):
    import re
    question_blocks = re.findall(
        r'Question:\s*(.*?)Options:(.*?)Answer:\s*([A-D])',
        text,
        re.DOTALL
    )

    questions = []
    for question, options_str, answer in question_blocks:
        # Split options: A xxx. B yyy. etc.
        options = re.findall(r'[A-D]\.?\s*(.*?)(?=\s+[A-D]\.|$)', options_str.strip())
        if len(options) == 4:
            questions.append({
                'question': question.strip(),
                'options': options,
                'answer': answer
            })
    return questions


@login_required
def quiz(request, book_id):
    text = extract_text_from_pdf(book_id)
    try:
        raw = generate_local_questions(text)
        parsed_questions = parse_generated_text(raw)
    except Exception as e:
        print("Error generating quiz:", e)
        parsed_questions = None

    if parsed_questions is None or len(parsed_questions) == 0:
        return render(request, 'main/quiz.html', {
            'book_title': book_id.replace('-', ' ').title(),
            'questions': [],
            'error': "There was a problem generating the quiz. Please try again later."
        })

    if request.method == 'POST':
        score = 0
        for idx, q in enumerate(parsed_questions, 1):
            user_ans = request.POST.get(f'q{idx}')
            if user_ans and user_ans[0].upper() == q['answer']:
                score += 1
        return render(request, 'main/quiz.html', {
            'book_title': book_id.replace('-', ' ').title(),
            'questions': parsed_questions,
            'score': score
        })

    return render(request, 'main/quiz.html', {
        'book_title': book_id.replace('-', ' ').title(),
        'questions': parsed_questions
    })
