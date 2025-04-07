from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, ProfileForm
from firebase.firebase import admin_portal_db, student_portal_db
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm, ProfileForm
from firebase_admin import firestore
 # Assuming you've set up Firebase clients
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, ProfileForm
from firebase_admin import firestore
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm
from firebase_admin import firestore
  # Reference to the ConnectPlatform Firebase Project

import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm, ProfileForm
from firebase_admin import firestore

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.models import User

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                # Verify in AlumniConnect Firebase Project (admin_portal_db)
                alumni_query = admin_portal_db.collection('alumni').where('email', '==', email).get()
                if alumni_query:
                    alumni_data = alumni_query[0].to_dict()
                    if alumni_data.get('enrollmentDetails') == password:
                        # Simulate user creation and login in Django
                        user, created = User.objects.get_or_create(username=email, email=email)
                        if created:
                            user.set_password(password)  # Set a password for Django auth
                            user.save()

                        # Authenticate the user and set session
                        login(request, user)

                        # Redirect to profile_view with the email
                        student_query = student_portal_db.collection('student').where('email', '==', email).get()
                        if not student_query:  # If student doesn't already exist
                            # Store in ConnectPlatform Firebase Project (without profile)
                            student_portal_db.collection('student').document(email).set({'email': email, 'password': password})
                        return redirect('profile_form', email=email)
                    else:
                        messages.error(request, "Invalid password. Please check your password.")
                else:
                    messages.error(request, "Email not found. Please check your email.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Form data is invalid. Please fill in all fields correctly.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirects to login page after logout


from firebase.firebase import admin_portal_db
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignUpForm
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase app
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("firebase/alumniconnect-adminsdk.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Check if email exists in alumni collection
            alumni_query = db.collection('alumni').where('email', '==', data['email']).get()
            if alumni_query:
                return render(request, 'accounts/signup.html', {'form': form, 'message': 'You already have an account. Please log in.'})
            
            # Check if email already exists in requests collection
            requests_query = db.collection('requests').where('email', '==', data['email']).get()
            if requests_query:
                return render(request, 'accounts/signup.html', {'form': form, 'message': 'Your request is already submitted. Please wait for admin approval.'})
            
            # Add data to requests collection
            db.collection('requests').add(data)

            # Redirect to waiting page
            return redirect('waiting_view', email=data['email'])
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})

def waiting_view(request, email):
    if request.method == 'GET':
        # Check if the user's email exists in alumni collection
        alumni_query = db.collection('alumni').where('email', '==', email).get()
        if alumni_query:
            return render(request, 'accounts/waiting.html', {'approved': True, 'email': email})

    return render(request, 'accounts/waiting.html', {'approved': False, 'email': email})

def approve_request(request, email):
    if request.method == 'POST':
        print(f"Approving request for email: {email}")
        # Get the request document
        requests_query = db.collection('requests').where('email', '==', email).get()
        if requests_query:
            print(f"Found requests for {email}")
            # Move data to alumni collection
            for doc in requests_query:
                print(f"Adding document to alumni collection: {doc.to_dict()}")
                db.collection('alumni').add(doc.to_dict())
                # Delete from requests collection
                db.collection('requests').document(doc.id).delete()
            print(f"Successfully processed approval for {email}")

    return redirect('admin_dashboard')  # Replace with your admin dashboard URL
import cloudinary
import cloudinary.uploader

# Cloudinary credentials
cloudinary.config(
    cloud_name="dfowgh13y",
    api_key="117416958248445",
    api_secret="g5ebVCUx4mPDsnXsB7IFpfvndzc"
)

@csrf_exempt
def profile_form(request, email):
    # Retrieve student document from Firestore
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect('login')

    # Get student document ID and reference to the profile
    student_id = student_doc[0].id
    profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details')

    # If profile already exists, redirect to profile view
    if profile_ref.get().exists:
        return redirect('profile_view', email=email)

    # Handle POST request for form submission
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Prepare profile data from form inputs
            profile_data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'dob': form.cleaned_data['dob'].strftime('%Y-%m-%d'),
                'phone_no': form.cleaned_data['phone_no'],
                'home_district': form.cleaned_data['home_district'],
                'home_state': form.cleaned_data['home_state'],
                'home_country': form.cleaned_data['home_country'],
                'current_job': form.cleaned_data['current_job'],
                'current_company': form.cleaned_data['current_company'],
                'company_district': form.cleaned_data['company_district'],
                'company_state': form.cleaned_data['company_state'],
                'company_country': form.cleaned_data['company_country'],
                'skills': form.cleaned_data['skills'],
                'about': form.cleaned_data['about'],
                'admissionYear': form.cleaned_data['admissionYear'],
                'profile_photo': None,
                'linkedin_url': form.cleaned_data.get('linkedin_url'),
                'github_url': form.cleaned_data.get('github_url'),
                'portfolio_url': form.cleaned_data.get('portfolio_url'),
            }

            # Handle profile photo upload to Cloudinary
            if 'profile_photo' in request.FILES:
                profile_photo = request.FILES['profile_photo']
                try:
                    # Upload image to Cloudinary
                    upload_result = cloudinary.uploader.upload(profile_photo, folder="profile_pics/")
                    profile_data['profile_photo'] = upload_result['secure_url']
                except Exception as e:
                    messages.error(request, f"Error uploading photo: {str(e)}")
                    profile_data['profile_photo'] = 'https://res.cloudinary.com/dfowgh13y/image/upload/v1736879146/ixweh8lqbvl3y2igb0ua.jpg'
                    print(f"Cloudinary upload error: {str(e)}")
            else:
                # Set default profile photo if none uploaded
                profile_data['profile_photo'] = 'https://res.cloudinary.com/dfowgh13y/image/upload/v1736879146/ixweh8lqbvl3y2igb0ua.jpg'

            # Save profile data to Firestore
            try:
                profile_ref.set(profile_data)
                messages.success(request, "Profile created successfully!")
                return redirect('profile_view', email=email)
            except Exception as e:
                messages.error(request, f"Error saving profile: {str(e)}")
                print(f"Firestore save error: {str(e)}")

    # Handle GET request to pre-fill form with alumni data
    else:
        alumni_query = admin_portal_db.collection('alumni').where('email', '==', email).get()
        alumni_data = alumni_query[0].to_dict() if alumni_query else {}

        # Pre-populate form fields with alumni data
        initial_data = {
            'degree': alumni_data.get('degree'),
            'department': alumni_data.get('department'),
            'graduationYear': alumni_data.get('graduationYear'),
            'status': alumni_data.get('status'),
        }
        form = ProfileForm(initial=initial_data)

    return render(request, 'accounts/profile_form.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .forms import EducationForm
from .forms import ExperienceForm
from firebase.firebase import student_portal_db
# Profile view page to display user profile details
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import uuid  # For generating unique IDs

@login_required
def profile_view(request, email):
    # Fetch the student document for the logged-in user
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect('login')

    student_id = student_doc[0].id
    profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
    profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    
    experience_ref = student_portal_db.collection('student').document(student_id).collection('experience').get()
    experiences = [experience.to_dict() | {'id': experience.id} for experience in experience_ref] if experience_ref else []

    # Retrieve educations
    education_ref = student_portal_db.collection('student').document(student_id).collection('education').get()
    educations = [education.to_dict() | {'id': education.id} for education in education_ref] if education_ref else []

    
    alumni_query = admin_portal_db.collection('alumni').where('email', '==', email).get()
    if alumni_query:
        alumni_data = alumni_query[0].to_dict()
        profile_data.update({
            'degree': alumni_data.get('degree'),
            'department': alumni_data.get('department'),
            'graduationYear': alumni_data.get('graduationYear'),
            'status': alumni_data.get('status'),
        })
    # Fetch connection requests
    connect_requests_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').collection('connect_request').get()
    connect_requests = []

    if connect_requests_ref:
        for conn_request in connect_requests_ref:
            request_data = conn_request.to_dict()
            # Fetch the recipient email from the `student` collection
            recipient_doc = student_portal_db.collection('student').document(request_data.get('id')).get()
            if recipient_doc.exists:
                request_data['recipient_email'] = recipient_doc.to_dict().get('email')  # Add recipient email to the request data
            connect_requests.append(request_data | {'id': conn_request.id})  # Include the `id` field

    return render(request, 'accounts/profile_view.html', {
        'profile': profile_data,
        'email': email,  # Logged-in user's email
        'connect_requests': connect_requests,  # Pass connection requests with recipient_email
        'current_user_email': request.user.email, 
        'experiences': experiences,
        'educations': educations, # Pass logged-in user's email
    })

import cloudinary
import cloudinary.uploader
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from firebase_admin import firestore
from firebase.firebase import student_portal_db  # Firebase instance

# Configure Cloudinary
cloudinary.config(
    cloud_name="dfowgh13y",
    api_key="117416958248445",
    api_secret="g5ebVCUx4mPDsnXsB7IFpfvndzc"
)

@login_required
def post_job(request, email):  # Accept email as parameter
    # Fetch student document
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect("login")

    student_id = student_doc[0].id

    # Fetch profile details
    profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
    profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    # Handle form submission
    if request.method == "POST":
        # Ensure user is posting their own job
        if email != request.user.email:
            messages.error(request, "Unauthorized action.")
            return redirect("post_job", email=request.user.email)

        company_name = request.POST.get("company_name")
        location = request.POST.get("location")
        company_url = request.POST.get("company_url")
        job_id = request.POST.get("job_id")
        job_type = request.POST.get("job_type")
        title = request.POST.get("title")
        description = request.POST.get("description")
        deadline = request.POST.get("deadline")
        experience = request.POST.get("experience")
        skills = request.POST.get("skills")
        
        # Handle Image Upload to Cloudinary
        job_image_url = ""
        if 'job_image' in request.FILES:
            job_image = request.FILES['job_image']
            upload_result = cloudinary.uploader.upload(job_image)
            job_image_url = upload_result.get("secure_url", "")

        # Store job details in Firebase directly under "job" collection (as separate documents)
        job_data = {
            "company_name": company_name,
            "location": location,
            "company_url": company_url,
            "job_id": job_id,
            "job_type": job_type,
            "title": title,
            "description": description,
            "deadline": deadline,
            "experience": experience,
            "skills": skills,
            "job_image": job_image_url,
            "posted_by": email  # Store the email of the user who posted the job
        }

        # Add a new job as a separate document in "job" collection
        student_portal_db.collection("job").add(job_data)  # Auto-generates job document ID

        messages.success(request, "Job posted successfully!")
        return redirect("post_job", email=email)  # Ensure email is passed

    return render(request, "accounts/post_job.html", {
        "email": email,
        "profile": profile_data  # Pass profile data to template
    })




from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore
from firebase.firebase import student_portal_db  # Firebase instance

def browse_job(request):
    jobs = []
    email = request.user.email if request.user.is_authenticated else ""  # Get user email
    profile_data = {}  # Default empty profile data

    # Fetch student document if user is logged in
    if email:
        student_doc = student_portal_db.collection('student').where('email', '==', email).get()
        if not student_doc:
            messages.error(request, "Student not found.")
            return redirect("login")

        student_id = student_doc[0].id

        # Fetch profile details
        profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
        profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    # Fetch all jobs from Firebase (Jobs are stored directly under "job" collection)
    job_collection = student_portal_db.collection("job").stream()

    for job in job_collection:
        job_data = job.to_dict()
        print(f"🔥 Job Found: {job_data}")  # Debugging line
        jobs.append(job_data)

    print(f"✅ Total Jobs Fetched: {len(jobs)}")  # Debugging line

    return render(request, "accounts/browse_job.html", {
        "jobs": jobs,
        "total_jobs": len(jobs),  # Total job count
        "email": email,
        "profile": profile_data  # Pass profile data for navbar
    })


from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore
  # Ensure this is correctly initialized


def success_stories(request):
    query = request.GET.get('query', '')  # Get search query from request
    email = request.user.email if request.user.is_authenticated else ""  # Get user email
    profile_data = {}  # Default empty profile data

    # Fetch student profile if logged in
    if email:
        student_doc = student_portal_db.collection('student').where('email', '==', email).get()
        if student_doc:
            student_id = student_doc[0].id
            profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
            profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    # Fetch success stories and order by created_at in descending order
    stories_ref = db.collection('success_stories').order_by('created_at', direction=firestore.Query.DESCENDING).stream()

    success_stories = []
    for story in stories_ref:
        data = story.to_dict()
        data['id'] = story.id
        data['images'] = data.get('images', [])  # Ensure images list

        # Apply search filter if query is provided
        if query.lower() in data.get('title', '').lower():
            success_stories.append(data)

    return render(request, 'accounts/success_stories.html', {
        'success_stories': success_stories,
        'query': query,
        'email': email,
        'profile': profile_data
    })

from django.shortcuts import render
from firebase_admin import firestore

# Initialize Firestore database connection
db = firestore.client()

def newsletter(request):
    query = request.GET.get('query', '')  # Get search query
    email = request.user.email if request.user.is_authenticated else ""
    profile_data = {}  # Default empty profile data

    # Fetch student profile if logged in
    if email:
        student_doc = student_portal_db.collection('student').where('email', '==', email).get()
        if student_doc:
            student_id = student_doc[0].id
            profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
            profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    # Fetch newsletters and order by created_time in descending order
    newsletters_ref = db.collection('newsletter').order_by('created_time', direction=firestore.Query.DESCENDING).stream()

    newsletters = []
    for news in newsletters_ref:
        data = news.to_dict()
        data['id'] = news.id  # Add ID field
        if query.lower() in data.get('title', '').lower():  # Apply search filter
            newsletters.append(data)

    return render(request, 'accounts/newsletter.html', {
        'newsletters': newsletters,
        'query': query,
        'email': email,
        'profile': profile_data
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore


@csrf_exempt
def get_surveys(request):
    try:
        surveys_ref = db.collection('surveys')
        surveys = surveys_ref.stream()
        surveys_list = []

        for survey in surveys:
            survey_data = survey.to_dict()
            survey_data['id'] = survey.id  # Add document ID
            surveys_list.append(survey_data)

        return JsonResponse({"success": True, "surveys": surveys_list}, safe=False)

    except Exception as e:
        print("Error fetching surveys:", str(e))  # Check logs for errors
        return JsonResponse({"success": False, "message": "Failed to load surveys."})

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import firebase_admin
from firebase_admin import firestore
from firebase.firebase import admin_portal_db, student_portal_db  # Import Firebase instances

def survey_list(request):
    email = request.user.email if request.user.is_authenticated else None

    if not email:
        messages.error(request, "Please log in to access surveys.")
        return redirect("login")

    profile_data = {}  # Default empty profile data

    # Fetch student profile from ConnectPlatform (Student DB)
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if student_doc:
        student_id = student_doc[0].id
        profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
        profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    # Fetch surveys from Admin DB
    surveys_ref = admin_portal_db.collection("surveys").get()
    surveys = [{"id": survey.id, **survey.to_dict()} for survey in surveys_ref]

    # Check if user has responded
    user_responses_ref = admin_portal_db.collection("survey_responses").document(email)
    user_responses = user_responses_ref.get().to_dict() or {}

    return render(request, "accounts/survey.html", {
        "surveys": surveys, 
        "user_responses": user_responses, 
        "student_doc_id": email,
        "email":email,
        'profile': profile_data
    })
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore
import json  # Ensure json is imported

@csrf_exempt
def submit_survey_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            survey_id = data.get("survey_id")
            response = data.get("response")
            student_doc_id = data.get("student_doc_id")

            if not survey_id or not response or not student_doc_id:
                return JsonResponse({'success': False, 'message': 'Invalid survey response'}, status=400)

            # Check if the student already responded
            responses_ref = admin_portal_db.collection('surveys').document(survey_id).collection('responses')
            existing_responses = responses_ref.where('student_doc_id', '==', student_doc_id).stream()

            if any(existing_responses):
                return JsonResponse({'success': False, 'message': 'You have already responded'}, status=400)

            # Fetch student details from Admin DB (alumni collection)
            alumni_query = admin_portal_db.collection('alumni').where('email', '==', student_doc_id).get()
            if alumni_query:
                alumni_data = alumni_query[0].to_dict()
                student_name = alumni_data.get('name', 'Unknown')
                degree = alumni_data.get('degree', 'N/A')
                graduation_year = alumni_data.get('graduationYear', 'N/A')
            else:
                return JsonResponse({'success': False, 'message': 'Student details not found'}, status=400)

            # Save response to Firestore (Admin DB)
            responses_ref.add({
                'response': response,
                'student_doc_id': student_doc_id,
                'student_name': student_name,
                'degree': degree,
                'graduation_year': graduation_year,
                'created_at': firestore.SERVER_TIMESTAMP,
            })

            return JsonResponse({'success': True, 'message': 'Response submitted successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error submitting survey response: {str(e)}")  # Log the error
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


def feedback_page(request):
    email = request.user.email if request.user.is_authenticated else None

    if not email:
        messages.error(request, "Please log in to access surveys.")
        return redirect("login")

    profile_data = {}  # Default empty profile data

    # Fetch student profile from ConnectPlatform (Student DB)
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if student_doc:
        student_id = student_doc[0].id
        profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
        profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    return render(request, "accounts/feedback.html", { 
        "student_doc_id": email,
        "email":email,
        'profile': profile_data
    })

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from firebase.firebase import admin_portal_db

@csrf_exempt
def submit_feedback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            title = data.get("title")
            description = data.get("description")

            if not email or not title or not description:
                return JsonResponse({"success": False, "message": "All fields are required"}, status=400)

            # Fetch student details from "alumni" collection
            alumni_query = admin_portal_db.collection("alumni").where("email", "==", email).stream()
            student_data = None
            student_doc_id = None

            for doc in alumni_query:
                student_data = doc.to_dict()
                student_doc_id = doc.id  # Store doc ID
                break

            if not student_data:
                return JsonResponse({"success": False, "message": "Student not found"}, status=404)

            feedback_data = {
                "student_name": student_data.get("name", "Unknown"),
                "degree": student_data.get("degree", "Not Provided"),
                "graduationYear": student_data.get("graduationYear", "Not Provided"),
                "title": title,
                "description": description,
                "email": email,
                "student_doc_id": student_doc_id  # Store doc ID for admin reference
            }

            admin_portal_db.collection("feedback").add(feedback_data)

            return JsonResponse({"success": True, "message": "Feedback submitted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)







# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
@login_required
def alumni_directory(request):
    search_query = request.GET.get('search', '').strip()

    # Fetch all student documents from the student collection
    students_query = student_portal_db.collection('student').stream()
    students = []

    # Fetch the currently logged-in user's profile data
    email = request.user.email
    user_doc = student_portal_db.collection('student').where('email', '==', email).get()
    profile = {}

    if user_doc:
        user_id = user_doc[0].id
        profile_ref = student_portal_db.collection('student').document(user_id).collection('profile').document('details').get()
        profile = profile_ref.to_dict() if profile_ref.exists else {}

    # Ensure default values to avoid template errors
    profile.setdefault('profile_photo', "https://res.cloudinary.com/dfowgh13y/image/upload/v1736879146/ixweh8lqbvl3y2igb0ua.jpg")
    profile.setdefault('first_name', 'Guest')
    profile.setdefault('last_name', '')

    for student_doc in students_query:
        student_data = student_doc.to_dict()
        student_id = student_doc.id

        # Skip the logged-in student
        if student_data.get('email') == email:
            continue

        # Fetch profile details
        profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
        profile_data = profile_ref.to_dict() if profile_ref.exists else {}

        # Retrieve experiences
        experience_ref = student_portal_db.collection('student').document(student_id).collection('experience').get()
        experiences = [exp.to_dict() | {'id': exp.id} for exp in experience_ref] if experience_ref else []

        # Retrieve educations (Fixed NameError)
        education_ref = student_portal_db.collection('student').document(student_id).collection('education').get()
        educations = [edu.to_dict() | {'id': edu.id} for edu in education_ref] if education_ref else []

        # Fetch additional details from `alumni` collection in `admin_portal_db`
        alumni_query = admin_portal_db.collection('alumni').where('email', '==', student_data.get('email')).get()
        alumni_data = alumni_query[0].to_dict() if alumni_query else {}

        # Combine all data
        profile_data.update({
            'degree': alumni_data.get('degree'),
            'department': alumni_data.get('department'),
            'graduationYear': alumni_data.get('graduationYear'),
            'status': alumni_data.get('status'),
        })

        # Add the complete profile data to the student data
        student_data.update({
            'profile': profile_data,
            'experiences': experiences,
            'educations': educations,
        })
        student_data['id'] = student_id
        students.append(student_data)

    if search_query:
        students = [
            student for student in students
            if search_query.lower() in student['profile'].get('first_name', '').lower()
            or search_query.lower() in student['profile'].get('last_name', '').lower()
            or search_query.lower() in student['profile'].get('degree', '').lower()
            or search_query.lower() in student['profile'].get('department', '').lower()
        ]

    # Fetch the count of companies
    companies_query = admin_portal_db.collection('companies').stream()
    companies_count = len(list(companies_query))

    # Fetch the count of cities
    cities_query = admin_portal_db.collection('cities').stream()
    cities_count = len(list(cities_query))

    # Update student count excluding the logged-in user
    students_count = len(students)

    # Pass correct `profile` and `email` for navbar to work
    context = {
        'students': students,
        'students_count': students_count,
        'companies_count': companies_count,
        'cities_count': cities_count,
        'profile': profile,  # Now correctly passed for navbar
        'email': email,  # Ensure email is passed
        'search_query': search_query,
    }

    return render(request, 'accounts/alumni_directory.html', context)


from django.shortcuts import render
@login_required
def alumni_map(request):
    students_query = student_portal_db.collection('student').stream()
    students = []

    # Fetch the currently logged-in user's profile data
    user_email = request.user.email
    user_doc = student_portal_db.collection('student').where('email', '==', user_email).get()
    logged_in_user = {}

    if user_doc:
        user_id = user_doc[0].id
        user_profile_ref = student_portal_db.collection('student').document(user_id).collection('profile').document('details').get()
        logged_in_user = user_profile_ref.to_dict() if user_profile_ref.exists else {}

    # Add the email field explicitly
    logged_in_user['email'] = user_email

    for student_doc in students_query:
        student_data = student_doc.to_dict()
        student_id = student_doc.id

        # Skip the logged-in student
        if student_data.get('email') == logged_in_user['email']:
            continue

        # Fetch profile details
        profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
        profile_data = profile_ref.to_dict() if profile_ref.exists else {}

        # Retrieve experiences
        experience_ref = student_portal_db.collection('student').document(student_id).collection('experience').get()
        experiences = [experience.to_dict() | {'id': experience.id} for experience in experience_ref] if experience_ref else []

        # Retrieve educations
        education_ref = student_portal_db.collection('student').document(student_id).collection('education').get()
        educations = [education.to_dict() | {'id': education.id} for education in education_ref] if education_ref else []

        # Fetch additional details from `alumni` collection in `admin_portal_db`
        alumni_query = admin_portal_db.collection('alumni').where('email', '==', student_data.get('email')).get()
        alumni_data = alumni_query[0].to_dict() if alumni_query else {}

        # Combine all data
        profile_data.update({
            'degree': alumni_data.get('degree'),
            'department': alumni_data.get('department'),
            'graduationYear': alumni_data.get('graduationYear'),
            'status': alumni_data.get('status'),
        })

        # Add the complete profile data to the student data
        student_data.update({
            'profile': profile_data,
            'experiences': experiences,
            'educations': educations,
        })
        student_data['id'] = student_id
        students.append(student_data)

    

    # Fetch the count of companies
    companies_query = admin_portal_db.collection('companies').stream()
    companies_count = len(list(companies_query))

    # Fetch the count of cities
    cities_query = admin_portal_db.collection('cities').stream()
    cities_count = len(list(cities_query))

    # Update student count excluding the logged-in user
    students_count = len(students)

    # Ensure `student` context is passed
    context = {
        'students': students,
        'students_count': students_count,
        'companies_count': companies_count,
        'cities_count': cities_count,
        'logged_in_user': logged_in_user,  # Pass the logged-in user's profile data to the context
    }
    return render(request, 'accounts/alumni_map.html')




@login_required
def student_profile(request, student_id):
    # Fetch the student document
    student_ref = student_portal_db.collection('student').document(student_id).get()
    if not student_ref.exists:
        return render(request, '404.html', {'message': 'Student not found'})

    student_data = student_ref.to_dict()
    student_data['id'] = student_id
    # Fetch profile details
    profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details').get()
    profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    # Fetch experiences
    experience_ref = student_portal_db.collection('student').document(student_id).collection('experience').stream()
    experiences = [experience.to_dict() for experience in experience_ref]

    # Fetch educations
    education_ref = student_portal_db.collection('student').document(student_id).collection('education').stream()
    educations = [education.to_dict() for education in education_ref]
    alumni_query = admin_portal_db.collection('alumni').where('email', '==', student_data.get('email')).get()
    alumni_data = alumni_query[0].to_dict() if alumni_query else {}

        # Combine all data
    profile_data.update({
        'degree': alumni_data.get('degree'),
        'department': alumni_data.get('department'),
        'graduationYear': alumni_data.get('graduationYear'),
        'status': alumni_data.get('status'),
    }) 

        # Add the complete profile data to the student data
    student_data.update({
        'profile': profile_data,
        'experiences': experiences,
        'educations': educations,
    })
    # Combine all data
    student_data['profile'] = profile_data
    student_data['experiences'] = experiences
    student_data['educations'] = educations

    context = {
        'student': student_data,
    }
    return render(request, 'accounts/student_profile.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, firestore


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from google.cloud import firestore
@login_required
def chat_view(request, current_user_email, recipient_email):
    if not current_user_email or not recipient_email:
        return render(request, "404.html", {"message": "Invalid chat request"})

    try:
        # Fetch the current user's student document
        current_user_doc = student_portal_db.collection('student').where('email', '==', current_user_email).get()
        if not current_user_doc:
            return render(request, "404.html", {"message": "Current user not found in the database."})

        # Fetch the recipient's student document
        recipient_doc = student_portal_db.collection('student').where('email', '==', recipient_email).get()
        if not recipient_doc:
            return render(request, "404.html", {"message": "Recipient not found in the database."})

        # Get the recipient's document ID
        recipient_id = recipient_doc[0].id

        # Fetch recipient's profile details from the `profile/details` subcollection
        profile_ref = student_portal_db.collection('student').document(recipient_id).collection('profile').document('details').get()
        if not profile_ref.exists:
            return render(request, "404.html", {"message": "Recipient's profile details not found."})

        # Extract recipient details
        profile_data = profile_ref.to_dict()
        recipient_name = profile_data.get('first_name', 'Unknown') + " " + profile_data.get('last_name', '')
        profile_photo = profile_data.get('profile_photo', 'https://res.cloudinary.com/dfowgh13y/image/upload/v1736879146/ixweh8lqbvl3y2igb0ua.jpg')

        # Fetch messages
        chat_ref = student_portal_db.collection("Message").document(current_user_email).collection("Chats").document(recipient_email)
        chat_data = chat_ref.get()

        messages = []
        if chat_data.exists:
            messages = chat_data.to_dict().get('messages', [])
        #print("Messages sent to template:", messages)
        # Pass data to the template
        context = {
            "current_user_email": current_user_email,
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "profile_photo": profile_photo,
            "messages": messages,
        }
        return render(request, "accounts/chat_screen.html", context)

    except Exception as e:
        print(f"Error: {str(e)}")
        return render(request, "404.html", {"message": f"Error: {str(e)}"})
        
from datetime import datetime
@login_required
def send_message(request):
    """ Handle sending and storing messages. """
    if request.method == "POST":
        sender_email = request.POST.get("sender_email")
        recipient_email = request.POST.get("recipient_email")
        message_text = request.POST.get("message")

        if not sender_email or not recipient_email or not message_text:
            return JsonResponse({"error": "Invalid data"}, status=400)

        # 🔹 Reference Firebase "Message" collection
        chat_ref = student_portal_db.collection("Message").document(sender_email).collection("Chats").document(recipient_email)
        recipient_chat_ref = student_portal_db.collection("Message").document(recipient_email).collection("Chats").document(sender_email)

        # 🔹 Store messages for both sender & recipient
        new_message = {
            "sender": sender_email,
            "text": message_text,
            "timestamp": datetime.now().strftime("%d/%m/%y %I:%M %p")
        }

        chat_ref.set({
            "messages": firestore.ArrayUnion([new_message])
        }, merge=True)

        recipient_chat_ref.set({
            "messages": firestore.ArrayUnion([new_message])
        }, merge=True)

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
@login_required
def edit_message(request):
    if request.method == "POST":
        try:
            data = request.POST
            message_index = data.get("message_index")
            recipient_email = data.get("recipient_email")
            new_text = data.get("new_text")
            sender_email = request.user.email

            if message_index is None or recipient_email is None or not new_text:
                return JsonResponse({"success": False, "error": "Missing data!"})

            message_index = int(message_index)

            # 🔹 Get sender's and recipient's chat documents
            sender_chat_ref = student_portal_db.collection("Message").document(sender_email).collection("Chats").document(recipient_email)
            recipient_chat_ref = student_portal_db.collection("Message").document(recipient_email).collection("Chats").document(sender_email)

            sender_chat_data = sender_chat_ref.get()
            recipient_chat_data = recipient_chat_ref.get()

            if not sender_chat_data.exists or not recipient_chat_data.exists:
                return JsonResponse({"success": False, "error": "Chat not found!"})

            # 🔹 Get messages
            sender_messages = sender_chat_data.to_dict().get("messages", [])
            recipient_messages = recipient_chat_data.to_dict().get("messages", [])

            # 🔹 Validate index
            if message_index < 0 or message_index >= len(sender_messages):
                return JsonResponse({"success": False, "error": "Invalid message index!"})

            # 🔹 Update sender's message
            sender_messages[message_index]["text"] = new_text

            # 🔹 Find and update the same message in recipient's chat
            updated_message = sender_chat_data.to_dict()["messages"][message_index]
            recipient_index = next(
                (i for i, msg in enumerate(recipient_messages) if msg == updated_message), 
                None
            )
            if recipient_index is not None:
                recipient_messages[recipient_index]["text"] = new_text

            # 🔹 Save changes in Firestore
            sender_chat_ref.update({"messages": sender_messages})
            recipient_chat_ref.update({"messages": recipient_messages})

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})

 

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt  # If using CSRF token, you can remove this
@login_required
def delete_message(request):
    if request.method == "POST":
        try:
            data = request.POST
            message_index = data.get("message_index")
            recipient_email = data.get("recipient_email")
            sender_email = request.user.email

            if message_index is None or recipient_email is None:
                return JsonResponse({"success": False, "error": "Missing data!"})

            message_index = int(message_index)

            # 🔹 Sender's chat document
            sender_chat_ref = student_portal_db.collection("Message").document(sender_email).collection("Chats").document(recipient_email)
            sender_chat_data = sender_chat_ref.get()

            # 🔹 Recipient's chat document
            recipient_chat_ref = student_portal_db.collection("Message").document(recipient_email).collection("Chats").document(sender_email)
            recipient_chat_data = recipient_chat_ref.get()

            if not sender_chat_data.exists or not recipient_chat_data.exists:
                return JsonResponse({"success": False, "error": "Chat not found!"})

            # 🔹 Get messages
            sender_messages = sender_chat_data.to_dict().get("messages", [])
            recipient_messages = recipient_chat_data.to_dict().get("messages", [])

            # 🔹 Validate index
            if message_index < 0 or message_index >= len(sender_messages):
                return JsonResponse({"success": False, "error": "Invalid message index!"})

            # 🔹 Delete from sender's chat
            del sender_messages[message_index]

            # 🔹 Find & delete the same message in recipient's chat
            # Since order can differ (user might delete, reorder), match by sender & text
            deleted_message = sender_chat_data.to_dict()["messages"][message_index]

            recipient_index = next(
                (i for i, msg in enumerate(recipient_messages) if msg == deleted_message), 
                None
            )
            if recipient_index is not None:
                del recipient_messages[recipient_index]

            # 🔹 Update Firestore
            sender_chat_ref.update({"messages": sender_messages})
            recipient_chat_ref.update({"messages": recipient_messages})

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import uuid  # Ensure uuid is imported here
from datetime import datetime



from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import uuid  # For generating unique IDs
from datetime import datetime


from django.http import JsonResponse

@login_required
def get_connect_status(request, student_id):
    requester_email = request.user.email

    # Get the requesting user's data
    requester_ref = student_portal_db.collection('student').where('email', '==', requester_email).get()
    if not requester_ref:
        return JsonResponse({'success': False, 'message': 'Requester not found in student database.'})

    requester_doc = requester_ref[0]
    requester_id = requester_doc.id

    # Check the recipient's existence
    recipient_ref = student_portal_db.collection('student').document(student_id)
    recipient_doc = recipient_ref.get()
    if not recipient_doc.exists:
        return JsonResponse({'success': False, 'status': 'deleted', 'message': 'The recipient is no longer available.'})

    # Check if a connection request exists
    connect_request_ref = recipient_ref.collection('profile').document('details').collection('connect_request').where('id', '==', requester_id).get()
    if connect_request_ref:
        existing_request = connect_request_ref[0].to_dict()
        if existing_request.get('status') == 'accepted':
            return JsonResponse({'success': True, 'status': 'accepted'})
        elif existing_request.get('status') == 'pending':
            return JsonResponse({'success': True, 'status': 'pending'})

    return JsonResponse({'success': True, 'status': 'connect'})




from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import uuid  # For generating unique IDs
from datetime import datetime

@login_required
def send_connect_request(request, student_id):
    requester_email = request.user.email

    # Get the requesting user's data from student DB
    requester_ref = student_portal_db.collection('student').where('email', '==', requester_email).get()
    if not requester_ref:
        return JsonResponse({'success': False, 'message': 'Requester not found in student database.'})

    requester_doc = requester_ref[0]
    requester_id = requester_doc.id
    requester_data = requester_doc.to_dict()

    # Fetch requester's profile details for first_name and last_name
    profile_ref = student_portal_db.collection('student').document(requester_id).collection('profile').document('details').get()
    profile_data = profile_ref.to_dict() if profile_ref.exists else {}

    # Fetch requester's degree, department, graduationYear from alumni collection in admin DB
    alumni_query = admin_portal_db.collection('alumni').where('email', '==', requester_email).get()
    if not alumni_query:
        return JsonResponse({'success': False, 'message': 'Requester not found in alumni database.'})

    alumni_data = alumni_query[0].to_dict()

    # Get the recipient student
    recipient_ref = student_portal_db.collection('student').document(student_id)
    connect_request_ref = recipient_ref.collection('profile').document('details').collection('connect_request').where('id', '==', requester_id).get()

    if connect_request_ref:
        # If a request already exists, do not create a new one
        existing_request = connect_request_ref[0].to_dict()
        if existing_request.get('status') == 'pending':
            return JsonResponse({'success': False, 'message': 'Request already sent and pending approval.'})
        elif existing_request.get('status') == 'accepted':
            return JsonResponse({'success': False, 'message': 'You are already connected.'})

    # Add request to the recipient's connect_request subcollection
    connect_request_id = str(uuid.uuid4())  # Generate a unique ID
    connect_request_data = {
        'id': requester_id,  # Requester's student ID
        'profile_photo': profile_data.get('profile_photo', 'Unknown'),
        'first_name': profile_data.get('first_name', 'Unknown'),
        'last_name': profile_data.get('last_name', 'Unknown'),
        'degree': alumni_data.get('degree'),
        'department': alumni_data.get('department'),
        'graduationYear': alumni_data.get('graduationYear'),
        'status': 'pending',
        'timestamp': datetime.utcnow().isoformat(),
    }
    recipient_ref.collection('profile').document('details').collection('connect_request').document(connect_request_id).set(connect_request_data)
    return JsonResponse({'success': True, 'message': 'Connection request sent.'})


@login_required
def handle_connect_request(request, connect_request_id, action):
    # Iterate through all students to find the connection request
    student_ref = student_portal_db.collection('student')
    for student_doc in student_ref.stream():
        connect_request_doc = student_doc.reference.collection('profile').document('details').collection('connect_request').document(connect_request_id).get()
        if connect_request_doc.exists:
            requester_id = connect_request_doc.to_dict().get('id')
            if action == 'accept':
                # Update the recipient's connect_request status to "accepted"
                connect_request_doc.reference.update({'status': 'accepted'})

                # Add connection details to the requester's database
                requester_ref = student_portal_db.collection('student').document(requester_id)
                recipient_details = student_doc.to_dict()

                profile_details = student_doc.reference.collection('profile').document('details').get()
                profile_data = profile_details.to_dict() if profile_details.exists else {}

                # Fetch degree, department, and graduationYear from the alumni collection in the admin portal DB
                alumni_query = admin_portal_db.collection('alumni').where('email', '==', recipient_details.get('email')).get()
                alumni_data = alumni_query[0].to_dict() if alumni_query else {}

                connect_request_data = {
                    'id': student_doc.id,  # Recipient's student ID
                    'profile_photo': profile_data.get('profile_photo', 'Unknown'),
                    'first_name': profile_data.get('first_name', 'Unknown'),
                    'last_name': profile_data.get('last_name', 'Unknown'),
                    'degree': alumni_data.get('degree', None),
                    'department': alumni_data.get('department', None),
                    'graduationYear': alumni_data.get('graduationYear', None),
                    'status': 'accepted',
                    'timestamp': datetime.utcnow().isoformat(),
                }
                requester_ref.collection('profile').document('details').collection('connect_request').document(connect_request_id).set(connect_request_data)

                return JsonResponse({'success': True, 'message': 'Request accepted successfully.'})
            elif action == 'reject':
                # Remove the connection request
                connect_request_doc.reference.delete()
                return JsonResponse({'success': True, 'message': 'Request rejected successfully.'})
    return JsonResponse({'success': False, 'message': 'Request not found.'})








# Add education functionality
def add_education(request, email):
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect('profile_view', email=email)

    student_id = student_doc[0].id

    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education_data = {
                'institute_name': form.cleaned_data['institute_name'],
                'degree': form.cleaned_data['degree'],
                'field_of_study': form.cleaned_data['field_of_study'],
                'start_year': form.cleaned_data['start_year'],
                'end_year': form.cleaned_data['end_year'],
                'grade': form.cleaned_data['grade'],
                'activities_and_societies': form.cleaned_data['activities_and_societies'],
                'description': form.cleaned_data['description'],
                'skills': form.cleaned_data['skills'].split(',')
            }

            student_ref = student_portal_db.collection('student').document(student_id)
            education_ref = student_ref.collection('education').document()
            education_ref.set(education_data)

            messages.success(request, "Education added successfully.")
            return redirect('profile_view', email=email)
    else:
        form = EducationForm()

    return render(request, 'accounts/add_education.html', {'form': form, 'email': email})

# Edit education functionality
def edit_education(request, email, education_id):
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect('profile_view', email=email)

    student_id = student_doc[0].id
    education_ref = student_portal_db.collection('student').document(student_id).collection('education').document(education_id)
    education = education_ref.get()

    if not education.exists:
        messages.error(request, "Education not found.")
        return redirect('profile_view', email=email)

    education_data = education.to_dict()

    if request.method == 'POST':
        form = EducationForm(request.POST, initial=education_data)
        if form.is_valid():
            cleaned_skills = [skill.strip() for skill in form.cleaned_data['skills'].split(',')]
            updated_data = {
                'institute_name': form.cleaned_data['institute_name'],
                'degree': form.cleaned_data['degree'],
                'field_of_study': form.cleaned_data['field_of_study'],
                'start_year': form.cleaned_data['start_year'],
                'end_year': form.cleaned_data['end_year'],
                'grade': form.cleaned_data['grade'],
                'activities_and_societies': form.cleaned_data['activities_and_societies'],
                'description': form.cleaned_data['description'],
                'skills': cleaned_skills  # Store the cleaned skills
            }

            education_ref.set(updated_data)
            messages.success(request, "Education updated successfully.")
            return redirect('profile_view', email=email)
    else:
        form = EducationForm(initial=education_data)

    return render(request, 'accounts/edit_education.html', {'form': form, 'email': email})


# Add experience card functionality
def add_experience(request, email):
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect('profile_view', email=email)

    student_id = student_doc[0].id

    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience_data = {
                'title': form.cleaned_data['title'],
                'employment_type': form.cleaned_data['employment_type'],
                'company': form.cleaned_data['company'],
                'start_date': form.cleaned_data['start_date'],
                'end_date': form.cleaned_data['end_date'],
                'district': form.cleaned_data['district'],
                'state': form.cleaned_data['state'],
                'description': form.cleaned_data['description'],
                'profile_headline': form.cleaned_data['profile_headline'],
                'skills': form.cleaned_data['skills'].split(',')
            }

            student_ref = student_portal_db.collection('student').document(student_id)
            experience_ref = student_ref.collection('experience').document()
            experience_ref.set(experience_data)

            messages.success(request, "Experience added successfully.")
            return redirect('profile_view', email=email)
    else:
        form = ExperienceForm()

    return render(request, 'accounts/add_experience.html', {'form': form, 'email': email})


# Edit experience card functionality
def edit_experience(request, email, experience_id):
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect('profile_view', email=email)

    student_id = student_doc[0].id
    experience_ref = student_portal_db.collection('student').document(student_id).collection('experience').document(experience_id)
    experience = experience_ref.get()

    if not experience.exists:
        messages.error(request, "Experience not found.")
        return redirect('profile_view', email=email)

    experience_data = experience.to_dict()

    if request.method == 'POST':
        form = ExperienceForm(request.POST, initial=experience_data)
        if form.is_valid():
            # Clean the skills input by removing unwanted spaces and quotes
            cleaned_skills = [skill.strip() for skill in form.cleaned_data['skills'].split(',')]

            updated_data = {
                'title': form.cleaned_data['title'],
                'employment_type': form.cleaned_data['employment_type'],
                'company': form.cleaned_data['company'],
                'start_date': form.cleaned_data['start_date'],
                'end_date': form.cleaned_data['end_date'],
                'district': form.cleaned_data['district'],
                'state': form.cleaned_data['state'],
                'description': form.cleaned_data['description'],
                'profile_headline': form.cleaned_data['profile_headline'],
                'skills': cleaned_skills  # Store the cleaned skills
            }

            experience_ref.set(updated_data)

            messages.success(request, "Experience updated successfully.")
            return redirect('profile_view', email=email)
    else:
        form = ExperienceForm(initial=experience_data)

    return render(request, 'accounts/edit_experience.html', {'form': form, 'email': email})



# View to handle social URL input (LinkedIn, GitHub, Portfolio)(profile collection)
@csrf_exempt
def add_social_url(request, social_media, email):
    student_doc = student_portal_db.collection('student').where('email', '==', email).get()
    if not student_doc:
        messages.error(request, "Student not found.")
        return redirect('login')

    student_id = student_doc[0].id
    profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details')

    # Retrieve current profile data
    profile_data = profile_ref.get().to_dict()

    if request.method == 'POST':
        url = request.POST.get('url')
        
        # Update the URL in the profile data
        if social_media == 'linkedin':
            profile_data['linkedin_url'] = url
        elif social_media == 'github':
            profile_data['github_url'] = url
        elif social_media == 'portfolio':
            profile_data['portfolio_url'] = url

        # Save the updated profile data
        try:
            profile_ref.set(profile_data)
            messages.success(request, f"{social_media.capitalize()} URL added successfully!")
            return redirect('profile_view', email=email)  # Redirect to profile view
        except Exception as e:
            messages.error(request, f"Error while saving {social_media} URL: {str(e)}")

    return render(request, 'accounts/add_social_url.html', {'social_media': social_media, 'email': email})

import cloudinary
import cloudinary.uploader
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# Cloudinary credentials
cloudinary.config(
    cloud_name="dfowgh13y",
    api_key="117416958248445",
    api_secret="g5ebVCUx4mPDsnXsB7IFpfvndzc"
)
#Profile edit form(profile collection)
@csrf_exempt
def edit_form(request, email):
    # Handle POST request
    if request.method == 'POST':
        section = request.POST.get('section')
        student_doc = student_portal_db.collection('student').where('email', '==', email).get()

        if not student_doc:
            messages.error(request, "Student not found.")
            return redirect('edit_form', email=email)

        student_id = student_doc[0].id
        profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details')

        updates = {}

        # Handle the image upload functionality
        if 'profile_photo' in request.FILES:
            profile_photo = request.FILES['profile_photo']

            # Upload image to Cloudinary
            upload_result = cloudinary.uploader.upload(profile_photo, folder="profile_pics/")

            # Get the public URL of the uploaded image
            profile_photo_url = upload_result['secure_url']

            # Add the URL of the image to the updates
            updates['profile_photo'] = profile_photo_url

        # Handle personal information update
        if section == 'personal':
            updates.update({
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'dob': request.POST.get('dob'),
                'phone_no': request.POST.get('phone_no'),
                'home_district': request.POST.get('home_district'),
                'home_state': request.POST.get('home_state'),
                'home_country': request.POST.get('home_country'),
                'current_job': request.POST.get('current_job'),
                'current_company': request.POST.get('current_company'),
                'company_district': request.POST.get('company_district'),
                'company_state': request.POST.get('company_state'),
                'company_country': request.POST.get('company_country'),
                'skills': request.POST.get('skills'),
                'about': request.POST.get('about'),
            })

        # Handle academic information update
        elif section == 'academic':
            # Fetch degree, department, graduationYear, and status from alumni collection
            alumni_query = admin_portal_db.collection('alumni').where('email', '==', email).get()
            if alumni_query:
                alumni_data = alumni_query[0].to_dict()
                updates.update({
                    'admissionYear': int(request.POST.get('admissionYear')),  # From profile form
                    'degree': alumni_data.get('degree'),
                    'department': alumni_data.get('department'),
                    'graduationYear': alumni_data.get('graduationYear'),
                    'status': alumni_data.get('status'),
                })
            else:
                messages.error(request, "Alumni details not found in admin database.")
                return redirect('edit_form', email=email)

        # Update the student's profile document in Firestore
        try:
            profile_ref.update(updates)
            messages.success(request, "Profile updated successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while updating the profile: {str(e)}")

        # Redirect to prevent duplicate form submission on page reload
        return redirect('profile_view', email=email)

    # Handle GET request
    else:
        # Retrieve student profile data
        student_doc = student_portal_db.collection('student').where('email', '==', email).get()
        if not student_doc:
            messages.error(request, "Student not found.")
            return redirect('profile_view')  # Redirect to profile view if student is not found

        student_id = student_doc[0].id
        profile_ref = student_portal_db.collection('student').document(student_id).collection('profile').document('details')

        # Fetch profile data from Firestore
        profile_data = profile_ref.get().to_dict() if profile_ref.get().exists else {}

        # Fetch academic data from the alumni collection
        alumni_query = admin_portal_db.collection('alumni').where('email', '==', email).get()
        alumni_data = alumni_query[0].to_dict() if alumni_query else {}

        # Combine profile and alumni data for rendering
        context = {
            'profile': profile_data,
            'alumni': {
                'degree': alumni_data.get('degree'),
                'department': alumni_data.get('department'),
                'graduationYear': alumni_data.get('graduationYear'),
                'status': alumni_data.get('status'),
            }
        }
        return render(request, 'accounts/edit_form.html', context)



