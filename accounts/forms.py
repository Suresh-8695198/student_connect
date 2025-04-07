from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email Address", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

from django import forms

class SignUpForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    degree = forms.CharField(max_length=100)
    department = forms.CharField(max_length=100)
    graduationYear = forms.CharField(max_length=4)
    enrollmentDetails = forms.CharField(max_length=100)
    status = forms.CharField(max_length=20)

from django import forms

class ProfileForm(forms.Form):
    profile_photo = forms.ImageField(required=False)  # Photo upload is optional
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'}))
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    phone_no = forms.CharField(max_length=15, required=True)
    home_district= forms.CharField(max_length=15, required=True)
    home_state= forms.CharField(max_length=25, required=True)
    home_country= forms.CharField(max_length=25, required=True)
    company_district = forms.CharField(max_length=25, required=False)
    company_state = forms.CharField(max_length=25, required=False)
    company_country = forms.CharField(max_length=25, required=False)
    admissionYear = forms.CharField(max_length=25, required=True)
    degree = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    graduationYear = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    status = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    current_job = forms.CharField(max_length=35, required=False)
    current_company = forms.CharField(max_length=35, required=False)
    skills = forms.CharField(max_length=50, required=False)
    about = forms.CharField(max_length=100, required=False)

from django import forms
from datetime import datetime

class ExperienceForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
        label="Job Title"
    )
    employment_type = forms.ChoiceField(
        choices=[
            ('Full-time', 'Full-time'),
            ('Part-time', 'Part-time'),
            ('Internship', 'Internship'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Employment Type"
    )
    company = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
        label="Company"
    )
    start_date = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}),
        label="Start Date"
    )
    end_date = forms.CharField(
        required=False,  # Make end_date optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD or At present'}),
        label="End Date"
    )
    district = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'}),
        label="District"
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
        label="State"
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        label="Description",
        required=False
    )
    profile_headline = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profile Headline'}),
        label="Profile Headline"
    )
    skills = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated skills'}),
        label="Skills"
    )

    # Custom validation for date fields
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate date format
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            if end_date and end_date != "At present":
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_date_obj = None
        except ValueError:
            raise forms.ValidationError("Dates must be in YYYY-MM-DD format or 'At present'.")

        # Validate start_date and end_date relationship
        if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
            self.add_error('end_date', 'End date must be after the start date.')

        # Handle "At present" or blank end_date
        if not end_date or end_date == "At present":
            cleaned_data['end_date'] = "At present"

        return cleaned_data


from django import forms

class EducationForm(forms.Form):
    institute_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institute Name'}),
        label="Institute Name"
    )
    degree = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Degree'}),
        label="Degree"
    )
    field_of_study = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Field of Study'}),
        label="Field of Study"
    )
    start_year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Start Year'}),
        label="Start Year"
    )
    end_year = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'End Year or Ongoing'}),
        label="End Year"
    )
    grade = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grade'}),
        label="Grade",
        required=False
    )
    activities_and_societies = forms.CharField(
        max_length=300,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Activities and Societies'}),
        label="Activities and Societies",
        required=False
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description'}),
        label="Description",
        required=False
    )
    skills = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated skills'}),
        label="Skills"
    )
