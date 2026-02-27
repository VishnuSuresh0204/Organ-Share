# views.py (refactored)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Login, Recipient, Donor, Doctor, Appointment, Slot, Feedback

# ----------------------
# 1. General Views
# ----------------------
def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")


# ----------------------
# 2. Authentication
# ----------------------
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                request.session['uid'] = user.id
                request.session['usertype'] = getattr(user, 'usertype', None)

                usertype = request.session.get('usertype')
                if usertype == 'admin':
                    messages.success(request, "Welcome Admin")
                    return redirect('/admin_home')
                elif usertype == 'recipient':
                    messages.success(request, "Welcome Recipient")
                    return redirect('/recipient_home')
                elif usertype == 'donor':
                    messages.success(request, "Welcome Donor")
                    return redirect('/donor_home')
                elif usertype == 'doctor':
                    messages.success(request, "Welcome Doctor")
                    return redirect('/doctor_home')
                else:
                    messages.info(request, "Welcome")
                    return redirect('/')
            else:
                messages.error(request, "Your account is not approved yet!")
        else:
            messages.error(request, "Invalid Email or Password")
    return render(request, "login.html")


def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect('/')


# ----------------------
# 3. Registration Views
# ----------------------
def recipient_register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        address = request.POST.get('address', '').strip()
        blood_group = request.POST.get('blood_group', '')
        age = request.POST.get('age', '').strip()
        gender = request.POST.get('gender', '')

        if not all([name, email, phone, password, address, blood_group, age, gender]):
            messages.error(request, "All fields are required.")
            return render(request, "user_reg.html")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "user_reg.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "user_reg.html")

        if Recipient.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "user_reg.html")

        try:
            age_int = int(age)
        except ValueError:
            age_int = None

        login_user = Login.objects.create_user(
            username=email, password=password, usertype='recipient',
            viewpassword=password, is_active=False
        )
        Recipient.objects.create(
            login=login_user,
            name=name,
            email=email,
            phone=phone,
            address=address,
            blood_group=blood_group,
            age=age_int
        )
        messages.success(request, "Registered successfully! Waiting for admin approval.")
        return redirect('/login/')
    return render(request, "user_reg.html")


def donor_register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        address = request.POST.get('address', '').strip()
        blood_group = request.POST.get('blood_group', '')
        age = request.POST.get('age', '').strip()
        can_liver = 'can_liver' in request.POST
        can_kidney = 'can_kidney' in request.POST
        after_death = 'after_death' in request.POST

        if not all([name, email, phone, password, address, blood_group, age]):
            messages.error(request, "All fields are required.")
            return render(request, "donr_reg.html")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "donr_reg.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "donr_reg.html")

        if Donor.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "donr_reg.html")

        try:
            age_int = int(age)
        except ValueError:
            age_int = None

        login_user = Login.objects.create_user(
            username=email, password=password, usertype='donor',
            viewpassword=password, is_active=False
        )
        Donor.objects.create(
            login=login_user,
            name=name,
            email=email,
            phone=phone,
            address=address,
            blood_group=blood_group,
            age=age_int,
            can_donate_liver=can_liver,
            can_donate_kidney=can_kidney,
            after_death_donation=after_death
        )
        messages.success(request, "Registered successfully! Waiting for admin approval.")
        return redirect('/login/')
    return render(request, "donr_reg.html")


def doctor_register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        address = request.POST.get('address', '').strip()

        if not all([name, email, phone, password, address]):
            messages.error(request, "All fields are required.")
            return render(request, "doc_reg.html")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "doc_reg.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "doc_reg.html")

        if Doctor.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "doc_reg.html")

        login_user = Login.objects.create_user(
            username=email, password=password, usertype='doctor',
            viewpassword=password, is_active=False
        )
        Doctor.objects.create(
            login=login_user,
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        messages.success(request, "Registered successfully! Waiting for admin approval.")
        return redirect('/login/')
    return render(request, "doc_reg.html")


# ----------------------
# 4. Admin Views
# ----------------------
def admin_home(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')

    return render(request, 'ADMIN/admin_home.html')


# Recipients
def view_recipients(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    recipients = Recipient.objects.all()
    return render(request, "ADMIN/view_user.html", {"recipients": recipients})

def approve_recipient(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    rid = request.GET.get('id')
    status = request.GET.get('status')

    try:
        recipient = Recipient.objects.get(id=rid)
    except Recipient.DoesNotExist:
        messages.error(request, "Recipient not found!")
        return redirect('/view_recipients')

    login_user = recipient.login
    if status == '1':
        recipient.status = 1
        if login_user:
            login_user.is_active = True
            login_user.save()
        messages.success(request, "Recipient approved/unblocked successfully")
    else:
        recipient.status = 2
        if login_user:
            login_user.is_active = False
            login_user.save()
        messages.info(request, "Recipient rejected/blocked successfully")

    recipient.save()
    return redirect('/view_recipients')

def edit_recipient(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    rid = request.GET.get('id')
    if not rid:
        messages.error(request, "Invalid recipient ID!")
        return redirect('/view_recipients')

    try:
        recipient = Recipient.objects.get(id=rid)
    except Recipient.DoesNotExist:
        messages.error(request, "Recipient not found!")
        return redirect('/view_recipients')

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        address = request.POST.get('address')
        blood_group = request.POST.get('blood_group')

        # Synchronized registration validation
        import re
        if not name or not re.match(r'^[A-Za-z ]{3,}$', name):
            messages.error(request, "Name should contain only letters and spaces (min 3 characters).")
            return render(request, "ADMIN/edit_user.html", {"recipient": recipient})

        if not phone or not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(request, "Enter a valid 10-digit mobile number.")
            return render(request, "ADMIN/edit_user.html", {"recipient": recipient})

        try:
            age_int = int(age)
            if age_int < 1 or age_int > 120:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Enter a valid age between 1 and 120.")
            return render(request, "ADMIN/edit_user.html", {"recipient": recipient})

        if not address or len(address) < 10:
            messages.error(request, "Address must be at least 10 characters long.")
            return render(request, "ADMIN/edit_user.html", {"recipient": recipient})

        recipient.name = name
        recipient.phone = phone
        recipient.blood_group = blood_group
        recipient.age = age
        recipient.address = address
        recipient.save()
        messages.success(request, "Recipient updated successfully!")
        return redirect('/view_recipients')

    return render(request, "ADMIN/edit_user.html", {"recipient": recipient})

def delete_recipient(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    rid = request.GET.get('id')
    if not rid:
        messages.error(request, "Invalid recipient ID!")
        return redirect('/view_recipients')

    try:
        recipient = Recipient.objects.get(id=rid)
    except Recipient.DoesNotExist:
        messages.error(request, "Recipient not found!")
        return redirect('/view_recipients')

    # Delete related login first if present
    if recipient.login:
        recipient.login.delete()
    recipient.delete()
    messages.success(request, "Recipient deleted successfully!")
    return redirect('/view_recipients')


# Donors
def view_donors(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    donors = Donor.objects.all()
    return render(request, "ADMIN/view_donor.html", {"donors": donors})

def approve_donor(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    donor_id = request.GET.get('id')
    status = request.GET.get('status')

    try:
        donor = Donor.objects.get(id=donor_id)
    except Donor.DoesNotExist:
        messages.error(request, "Donor not found!")
        return redirect('/viw_donors')

    login_user = donor.login
    if status == '1':
        donor.status = 1
        if login_user:
            login_user.is_active = True
            login_user.save()
        messages.success(request, "Donor approved/unblocked successfully")
    else:
        donor.status = 2
        if login_user:
            login_user.is_active = False
            login_user.save()
        messages.info(request, "Donor rejected/blocked successfully")

    donor.save()
    return redirect('/viw_donors')  # fixed typo


def edit_donor(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    did = request.GET.get('id')
    try:
        donor = Donor.objects.get(id=did)
    except Donor.DoesNotExist:
        messages.error(request, "Donor not found!")
        return redirect('/viw_donors')

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        address = request.POST.get('address')
        blood_group = request.POST.get('blood_group')

        # Synchronized registration validation
        import re
        if not name or not re.match(r'^[A-Za-z ]{3,}$', name):
            messages.error(request, "Name should contain only letters and spaces (min 3 characters).")
            return render(request, "ADMIN/edit_donor.html", {"donor": donor})

        if not phone or not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(request, "Enter a valid 10-digit mobile number.")
            return render(request, "ADMIN/edit_donor.html", {"donor": donor})

        try:
            age_int = int(age)
            if age_int < 1 or age_int > 120:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Enter a valid age between 1 and 120.")
            return render(request, "ADMIN/edit_donor.html", {"donor": donor})

        if not address or len(address) < 10:
            messages.error(request, "Address must be at least 10 characters long.")
            return render(request, "ADMIN/edit_donor.html", {"donor": donor})

        donor.name = name
        donor.phone = phone
        donor.age = age
        donor.address = address
        donor.blood_group = blood_group
        donor.can_donate_liver = request.POST.get('can_donate_liver') == "True"
        donor.can_donate_kidney = request.POST.get('can_donate_kidney') == "True"
        donor.after_death_donation = request.POST.get('after_death_donation') == "True"
        donor.save()
        messages.success(request, "Donor updated successfully!")
        return redirect('/viw_donors')

    return render(request, "ADMIN/edit_donor.html", {"donor": donor})


def delete_donor(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    did = request.GET.get('id')
    if not Donor.objects.filter(id=did).exists():
        messages.error(request, "Donor not found!")
        return redirect('/viw_donors')

    donor = Donor.objects.get(id=did)
    if donor.login:
        donor.login.delete()
    donor.delete()
    messages.success(request, "Donor deleted successfully!")
    return redirect('/viw_donors')


# Doctors
def view_doctors(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    doctors = Doctor.objects.all()
    return render(request, "ADMIN/view_doctor.html", {"doctors": doctors})

def approve_doctor(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    did = request.GET.get('id')
    action = request.GET.get('status')
    try:
        doctor = Doctor.objects.get(id=did)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor record not found!")
        return redirect('/view_doctors')

    login_user = doctor.login
    if action == '1':
        doctor.status = 1
        if login_user:
            login_user.is_active = True
            login_user.save()
        messages.success(request, "Doctor approved/unblocked successfully")
    else:
        doctor.status = 2
        if login_user:
            login_user.is_active = False
            login_user.save()
        messages.info(request, "Doctor rejected/blocked successfully")

    doctor.save()
    return redirect('/view_doctors')


def edit_doctor(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    did = request.GET.get('id')
    try:
        doctor = Doctor.objects.get(id=did)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found!")
        return redirect('/view_doctors')

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Synchronized registration validation
        import re
        if not name or not re.match(r'^[A-Za-z. ]{3,}$', name):
            messages.error(request, "Name should contain only letters, spaces, or dots (min 3 characters).")
            return render(request, "ADMIN/edit_doctor.html", {"doctor": doctor})

        if not phone or not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(request, "Enter a valid 10-digit mobile number.")
            return render(request, "ADMIN/edit_doctor.html", {"doctor": doctor})

        if not address or len(address) < 10:
            messages.error(request, "Address must be at least 10 characters long.")
            return render(request, "ADMIN/edit_doctor.html", {"doctor": doctor})

        doctor.name = name
        doctor.phone = phone
        doctor.address = address
        doctor.save()
        messages.success(request, "Doctor updated successfully!")
        return redirect('/view_doctors')

    return render(request, "ADMIN/edit_doctor.html", {"doctor": doctor})


def delete_doctor(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    did = request.GET.get('id')
    if not did:
        messages.error(request, "Invalid doctor ID!")
        return redirect('/view_doctors')

    try:
        doctor = Doctor.objects.get(id=did)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found!")
        return redirect('/view_doctors')

    if doctor.login:
        doctor.login.delete()
    doctor.delete()
    messages.success(request, "Doctor deleted successfully!")
    return redirect('/view_doctors')


# ----------------------
# 5. Appointment Views (slot-based)
# ----------------------
def view_appointments(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    appointments = Appointment.objects.all().order_by('slot__date', 'slot__start_time')
    return render(request, "ADMIN/viewAppointments.html", {"appointments": appointments})


def admin_create_appointment_slot_based(request):
    """
    Admin-facing appointment creation using pre-created slots.
    """
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    recipients = Recipient.objects.filter(login__is_active=True)
    doctors = Doctor.objects.filter(login__is_active=True)
    donors = Donor.objects.filter(login__is_active=True)

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        slot_id = request.POST.get('slot')
        donor_id = request.POST.get('donor')
        purpose = request.POST.get('purpose')

        try:
            recipient = Recipient.objects.get(id=recipient_id)
        except Recipient.DoesNotExist:
            messages.error(request, "Recipient not found.")
            return redirect('/view_appointments')

        try:
            slot = Slot.objects.select_for_update().get(id=slot_id)
        except Slot.DoesNotExist:
            messages.error(request, "Selected slot not found.")
            return redirect('/view_appointments')

        if slot.is_booked:
            messages.error(request, "This slot is already booked.")
            return redirect('/view_appointments')

        donor = Donor.objects.filter(id=donor_id).first() if donor_id else None

        # Create appointment and mark slot as booked atomically
        with transaction.atomic():
            Appointment.objects.create(slot=slot, recipient=recipient, donor=donor, purpose=purpose)
            slot.is_booked = True
            slot.save()

        messages.success(request, "Appointment scheduled successfully")
        return redirect('/view_appointments')

    # GET
    today = timezone.localtime(timezone.now()).date()
    slots = Slot.objects.filter(is_booked=False, date__gte=today).order_by('date', 'start_time')
    donors = Donor.objects.filter(login__is_active=True)
    return render(request, "ADMIN/addAppointment.html", {
        "recipients": recipients,
        "doctors": doctors,
        "slots": slots,
        "donors": donors
    })


# ----------------------
# 6. Feedback Views
# ----------------------
def add_feedback_from_recipient(request, appointment_id=None):
    """Recipient-facing add-feedback tied to a specific appointment (uses session auth)."""
    uid = request.session.get('uid')
    if not uid or request.session.get('usertype') != 'recipient':
        messages.error(request, "Please login as recipient first!")
        return redirect('/login')

    try:
        recipient = Recipient.objects.get(login__id=uid)
    except Recipient.DoesNotExist:
        messages.error(request, "Recipient not found.")
        return redirect('/login')

    if not appointment_id:
        messages.error(request, "No appointment specified.")
        return redirect('/recipient_home')

    try:
        appointment = Appointment.objects.get(id=appointment_id, recipient=recipient)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found or not yours.")
        return redirect('/recipient_home')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        rating = int(request.POST.get('rating', 0))
        Feedback.objects.create(
            recipient=recipient,
            appointment=appointment,
            subject=subject,
            message=message,
            rating=rating
        )
        messages.success(request, "Feedback submitted successfully")
        return redirect('/recipient_home')

    return render(request, "RECIPIENT/addFeedback.html", {"appointment": appointment})


def view_feedbacks_admin(request):
    if not request.session.get('uid') or request.session.get('usertype') != 'admin':
        messages.error(request, "Please log in as admin first!")
        return redirect('/login')
    feedbacks = Feedback.objects.select_related(
        'recipient',
        'appointment__slot__doctor'
    ).order_by('-id')

    return render(request, "ADMIN/viewFeedbacks.html", {"feedbacks": feedbacks})


# Recipient/Donor/Doctor Home Views
def recipient_home(request):
    uid = request.session.get('uid')
    if not uid or request.session.get('usertype') != 'recipient':
        messages.error(request, "Please log in as recipient first!")
        return redirect('/login')

    try:
        user = Recipient.objects.get(login__id=uid)
    except Recipient.DoesNotExist:
        messages.error(request, "Recipient not found.")
        return redirect('/login')

    appointments = Appointment.objects.filter(recipient=user).order_by('slot__date', 'slot__start_time')
    return render(request, "USER/user_home.html", {"user": user, "appointments": appointments})

def recipient_profile(request):
    uid = request.session.get('uid')
    if not uid or request.session.get('usertype') != 'recipient':
        messages.error(request, "Please log in!")
        return redirect('/login')
    try:
        user = Recipient.objects.get(login__id=uid)
    except Recipient.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('/login')
    return render(request, "USER/profile.html", {"user": user})

def edit_recipient_profile(request):
    uid = request.session.get('uid')
    if not uid or request.session.get('usertype') != 'recipient':
        messages.error(request, "Please log in!")
        return redirect('/login')
    try:
        user = Recipient.objects.get(login__id=uid)
    except Recipient.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('/login')

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        age_val = request.POST.get('age', '').strip()

        error = None
        if not name or len(name) < 3:
            error = "Name must be at least 3 characters."
        elif not phone or len(phone) < 10:
            error = "Please enter a valid phone number."
        elif not address or len(address) < 10:
            error = "Address must be at least 10 characters long."

        if error:
            messages.error(request, error)
            return render(request, "USER/edit_profile.html", {"user": user})

        user.name = name
        user.phone = phone
        user.address = address
        user.blood_group = blood_group
        try:
            user.age = int(age_val) if age_val else None
        except ValueError:
            user.age = None
        if request.FILES.get('image'):
            user.image = request.FILES['image']
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('/recipient_profile/')

    return render(request, "USER/edit_profile.html", {"user": user})


def donor_home(request):
    uid = request.session.get('uid')
    if not uid or request.session.get('usertype') != 'donor':
        messages.error(request, "Please log in as donor first!")
        return redirect('/login')

    try:
        user = Donor.objects.get(login__id=uid)
    except Donor.DoesNotExist:
        messages.error(request, "Donor not found.")
        return redirect('/login')

    # For dashboard, maybe show upcoming appointments
    appointments = Appointment.objects.filter(donor=user, status='Scheduled').order_by('slot__date', 'slot__start_time')
    return render(request, "DONOR/donorHome.html", {"user": user, "appointments": appointments})


def donor_profile(request):
    uid = request.session.get('uid')
    if not uid or request.session.get('usertype') != 'donor':
        messages.error(request, "Please log in!")
        return redirect('/login')
    try:
        user = Donor.objects.get(login__id=uid)
    except Donor.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('/login')
    return render(request, "DONOR/profile.html", {"user": user})

def edit_donor_profile(request):
    uid = request.session.get('uid')
    if not uid or request.session.get('usertype') != 'donor':
        messages.error(request, "Please log in!")
        return redirect('/login')
    try:
        user = Donor.objects.get(login__id=uid)
    except Donor.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('/login')

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        age_val = request.POST.get('age', '').strip()

        error = None
        if not name or len(name) < 3:
            error = "Name must be at least 3 characters."
        elif not phone or len(phone) < 10:
            error = "Please enter a valid phone number."
        elif not address or len(address) < 10:
            error = "Address must be at least 10 characters long."

        if error:
            messages.error(request, error)
            return render(request, "DONOR/edit_profile.html", {"user": user})

        user.name = name
        user.phone = phone
        user.address = address
        user.blood_group = blood_group
        try:
            user.age = int(age_val) if age_val else None
        except ValueError:
            user.age = None
        user.can_donate_liver = request.POST.get('can_donate_liver') == 'on'
        user.can_donate_kidney = request.POST.get('can_donate_kidney') == 'on'
        user.after_death_donation = request.POST.get('after_death_donation') == 'on'
        if request.FILES.get('image'):
            user.image = request.FILES['image']
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('/donor_profile/')

    return render(request, "DONOR/edit_profile.html", {"user": user})


def doctor_home(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype != 'doctor':
        messages.error(request, "Only doctors can access this page!")
        return redirect('/login')

    try:
        doctor = Doctor.objects.get(login__id=uid)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found.")
        return redirect('/login')

    # Appointments for this doctor's slots (slot-based model)
    appointments = Appointment.objects.filter(slot__doctor=doctor).order_by('slot__date', 'slot__start_time')
    return render(request, "DOCTOR/doc_home.html", {"doctor": doctor, "appointments": appointments})


def doctor_profile(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype != 'doctor':
        messages.error(request, "Only doctors can access this page!")
        return redirect('/login')

    try:
        doctor = Doctor.objects.get(login__id=uid)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('/login')
    return render(request, "DOCTOR/profile.html", {"doctor": doctor})


def doctor_edit_profile(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype != 'doctor':
        messages.error(request, "Only doctors can access this page!")
        return redirect('/login')

    try:
        doctor = Doctor.objects.get(login__id=uid)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('/login')

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        error = None
        if not name or len(name) < 3:
            error = "Name must be at least 3 characters."
        elif not phone or len(phone) < 10:
            error = "Please enter a valid phone number."
        elif not address or len(address) < 10:
            error = "Address must be at least 10 characters long."

        if error:
            messages.error(request, error)
            return render(request, "DOCTOR/edit_profile.html", {"doctor": doctor})

        doctor.name = name
        doctor.phone = phone
        doctor.address = address
        if request.FILES.get('image'):
            doctor.image = request.FILES['image']
        doctor.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('/doctor_profile/')

    return render(request, "DOCTOR/edit_profile.html", {"doctor": doctor})


# ----------------------
# Doctor: Add Slot
# ----------------------
def doctor_add_slot(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype != 'doctor':
        messages.error(request, "Only doctors can access this page!")
        return redirect('/login')

    try:
        doctor = Doctor.objects.get(login__id=uid)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found.")
        return redirect('/login')

    if request.method == "POST":
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except Exception:
            messages.error(request, "Invalid date/time format.")
            return redirect('/doctor_add_slot')

        today_dt = timezone.localtime(timezone.now())
        today = today_dt.date()
        
        if date <= today:
            messages.error(request, f"Slots must be scheduled for future dates only (from tomorrow onwards). Today is {today}")
            return redirect('/doctor_add_slot')

        current_start = timezone.make_aware(datetime.combine(date, start_time))
        final_end = timezone.make_aware(datetime.combine(date, end_time))

        # This is now redundant due to date <= today, but kept for safety
        if current_start < today_dt:
            messages.error(request, "Cannot add slots in the past.")
            return redirect('/doctor_add_slot')

        if current_start >= final_end:
            messages.error(request, "End time must be after start time.")
            return redirect('/doctor_add_slot')

        slots_created = 0
        while current_start + timedelta(minutes=30) <= final_end:
            slot_start = current_start.time()
            slot_end = (current_start + timedelta(minutes=30)).time()

            overlapping = Slot.objects.filter(
                doctor=doctor,
                date=date,
            ).exclude(start_time__gte=slot_end).exclude(end_time__lte=slot_start)

            if overlapping.exists():
                current_start += timedelta(minutes=30)
                continue

            Slot.objects.create(doctor=doctor, date=date, start_time=slot_start, end_time=slot_end)
            slots_created += 1
            current_start += timedelta(minutes=30)

        if slots_created > 0:
            messages.success(request, f"{slots_created} slot(s) added successfully!")
        else:
            messages.warning(request, "No new slots were added (all overlapping).")

        return redirect('/doctor_add_slot')

    # Show only today and future slots in management page
    today_dt = timezone.localtime(timezone.now())
    today = today_dt.date()
    tomorrow = today + timedelta(days=1)

    # Filter using localized today
    slots = Slot.objects.filter(doctor=doctor, date__gte=today).order_by('date', 'start_time')
    return render(request, "DOCTOR/slot.html", {
        "doctor": doctor, 
        "slots": slots, 
        "today": str(today),
        "tomorrow": str(tomorrow)
    })


# Doctor view appointments
def doctor_view_appointments(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype != 'doctor':
        messages.error(request, "Only doctors can access this page!")
        return redirect('/login')

    try:
        doctor = Doctor.objects.get(login__id=uid)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor not found.")
        return redirect('/login')

    appointments = Appointment.objects.filter(slot__doctor=doctor).order_by('slot__date', 'slot__start_time')
    recipient_appointments = appointments.filter(recipient__isnull=False)
    donor_appointments = appointments.filter(donor__isnull=False)

    return render(request, "DOCTOR/view_appointment.html", {
        "doctor": doctor,
        "recipient_appointments": recipient_appointments,
        "donor_appointments": donor_appointments
    })


# For patients: view slots, filter by doctor
def view_available_slots(request):
    doctor_id = request.GET.get('doctor')
    today = timezone.localtime(timezone.now()).date()
    slots = Slot.objects.filter(date__gte=today).order_by('date', 'start_time')
    if doctor_id:
        slots = slots.filter(doctor__id=doctor_id)
    booked_slots = Appointment.objects.values_list('slot_id', flat=True)
    doctors = Doctor.objects.filter(login__is_active=True)
    context = {
        "slots": slots,
        "doctors": doctors,
        "selected_doctor": int(doctor_id) if doctor_id else None,
        "booked_slots": booked_slots
    }
    
    # Check user type to render correct template
    usertype = request.session.get('usertype')
    if usertype == 'donor':
        return render(request, "DONOR/apointment.html", context)
    return render(request, "USER/apointment.html", context)


# Book appointment (recipient)
def book_appointment(request):
    slot_id = request.GET.get('id')
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype not in ['recipient', 'donor']:
        messages.error(request, "Please log in as a recipient or donor first!")
        return redirect('/login')

    recipient = None
    donor = None

    if usertype == 'recipient':
        try:
            recipient = Recipient.objects.get(login__id=uid)
        except Recipient.DoesNotExist:
            messages.error(request, "Recipient not found.")
            return redirect('/login')
    elif usertype == 'donor':
        try:
            donor = Donor.objects.get(login__id=uid)
        except Donor.DoesNotExist:
            messages.error(request, "Donor not found.")
            return redirect('/login')

    if not slot_id:
        messages.error(request, "Invalid slot selected.")
        return redirect('/res_view_slot')

    try:
        with transaction.atomic():
            slot = Slot.objects.select_for_update().get(id=slot_id)

            # Prevent double booking
            if slot.is_booked:
                messages.warning(request, "This slot is already booked by another user.")
                return redirect('/res_view_slot')

            # Check for existing booking (Recipient or Donor)
            if recipient:
                existing = Appointment.objects.filter(
                    recipient=recipient,
                    slot__doctor=slot.doctor,
                    slot__date=slot.date
                ).exists()
            else:  # donor
                existing = Appointment.objects.filter(
                    donor=donor,
                    slot__doctor=slot.doctor,
                    slot__date=slot.date
                ).exists()

            if existing:
                messages.warning(request, "You have already booked a slot for this doctor on this date.")
                return redirect('/res_view_slot')

            # Create appointment
            Appointment.objects.create(recipient=recipient, donor=donor, slot=slot)
            slot.is_booked = True
            slot.save()

    except Slot.DoesNotExist:
        messages.error(request, "The selected slot does not exist.")
        return redirect('/res_view_slot')

    messages.success(request, f"Slot with Dr. {slot.doctor.name} on {slot.date} booked successfully!")
    return redirect('/res_view_slot')


def recipient_view_appointments(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if usertype == 'donor':
        try:
            donor = Donor.objects.get(login__id=uid)
            appointments = Appointment.objects.filter(donor=donor).order_by('-slot__date')
            return render(request, "DONOR/my_appointments.html", {"appointments": appointments})
        except Donor.DoesNotExist:
            messages.error(request, "Donor not found.")
            return redirect('/login')

    # Existing recipient logic
    if not uid or usertype != 'recipient':
        messages.error(request, "Please log in as a recipient first!")
        return redirect('/login')

    try:
        recipient = Recipient.objects.get(login__id=uid)
    except Recipient.DoesNotExist:
        messages.error(request, "Recipient not found.")
        return redirect('/login')

    appointments = Appointment.objects.filter(recipient=recipient).order_by('slot__date', 'slot__start_time')
    return render(request, 'USER/view_appointments.html', {'recipient': recipient, 'appointments': appointments})


# ----------------------
# Feedback management (user-facing)
# ----------------------
def add_feedback(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid:
        messages.error(request, "Please log in first.")
        return redirect('/login')

    if usertype == 'recipient':
        appointment_id = request.GET.get('id')
        if not appointment_id:
            messages.error(request, "No appointment selected.")
            return redirect('/add_feedback')

        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            messages.error(request, "Invalid appointment selected.")
            return redirect('/add_feedback')

        try:
            recipient = Recipient.objects.get(login__id=uid)
        except Recipient.DoesNotExist:
            messages.error(request, "Recipient not found.")
            return redirect('/login')

        if request.method == "POST":
            subject = request.POST.get('subject')
            message_text = request.POST.get('message')
            rating = int(request.POST.get('rating', 0))

            Feedback.objects.create(
                recipient=recipient,
                appointment=appointment,
                subject=subject,
                message=message_text,
                rating=rating
            )
            messages.success(request, "Feedback added successfully!")
            return redirect('/view_feedback')

        return render(request, 'USER/add_feedback.html', {'appointment': appointment})

    elif usertype == 'donor':
        try:
            donor = Donor.objects.get(login__id=uid)
        except Donor.DoesNotExist:
            messages.error(request, "Donor not found.")
            return redirect('/login')

        if request.method == "POST":
            subject = request.POST.get('subject')
            message_text = request.POST.get('message')
            rating = int(request.POST.get('rating', 0))

            Feedback.objects.create(
                donor=donor,
                subject=subject,
                message=message_text,
                rating=rating
            )
            messages.success(request, "Feedback added successfully!")
            return redirect('/view_feedback')

        return render(request, 'DONOR/add_feedback.html')

    else:
        messages.error(request, "Invalid user type.")
        return redirect('/login')



def edit_feedback(request):
    # Get feedback ID
    feedback_id = request.GET.get('id') or request.POST.get('id')
    if not feedback_id:
        messages.error(request, "No feedback selected.")
        return redirect('/view_feedback')

    # Get the feedback object
    try:
        feedback = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        messages.error(request, "Feedback not found.")
        return redirect('/view_feedback')

    # Update on POST
    if request.method == "POST":
        feedback.subject = request.POST.get('subject')
        feedback.message = request.POST.get('message')
        feedback.rating = request.POST.get('rating')
        feedback.save()
        messages.success(request, "Feedback updated successfully!")
        return redirect('/view_feedback')

    # Show edit form
    return render(request, 'USER/edit_feedback.html', {'feedback': feedback})


def delete_feedback(request):
    feedback_id = request.GET.get('id')
    if feedback_id:
        try:
            feedback = Feedback.objects.get(id=feedback_id)
            feedback.delete()
            messages.success(request, "Feedback deleted.")
        except Feedback.DoesNotExist:
            messages.warning(request, "Feedback not found.")
    return redirect('/view_feedback')


def view_feedback(request):
    usertype = request.session.get('usertype')
    uid = request.session.get('uid')
    
    if usertype == 'recipient':
        try:
            recipient = Recipient.objects.get(login__id=uid)
            feedback_list = Feedback.objects.filter(recipient=recipient).order_by('-created_at')
            return render(request, 'USER/view_feedback.html', {'feedback_list': feedback_list})
        except Recipient.DoesNotExist:
             messages.error(request, "Recipient not found.")
             return redirect('/login')
             
    elif usertype == 'donor':
        try:
            donor = Donor.objects.get(login__id=uid)
            feedback_list = Feedback.objects.filter(donor=donor).order_by('-created_at')
            return render(request, 'DONOR/view_feedback.html', {'feedback_list': feedback_list})
        except Donor.DoesNotExist:
            messages.error(request, "Donor not found.")
            return redirect('/login')
         
    return redirect('/login')



def doctor_view_recipient(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if not uid or usertype != 'doctor':
        messages.error(request, "Only doctors can access this page!")
        return redirect('/login')

    recipient_id = request.GET.get('id')  # read from URL query ?id=1
    if not recipient_id:
        messages.error(request, "No recipient ID provided!")
        return redirect('/doctor_home/')

    recipient = Recipient.objects.filter(id=recipient_id).first()
    if not recipient:
        messages.error(request, "Recipient not found!")
        return redirect('/doctor_home/')

    return render(request, "DOCTOR/view_user.html", {"recipient": recipient})

def doctor_view_donors(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if uid is None:
        messages.error(request, "Please login first.")
        return redirect('/login')

    elif usertype != 'doctor':
        messages.error(request, "Only doctors can access this page.")
        return redirect('/login')

    else:
        donors = Donor.objects.all()
        return render(request, "DOCTOR/view_donor.html", {"donors": donors})
    

def doctor_view_donor_detail(request):
    uid = request.session.get('uid')
    usertype = request.session.get('usertype')

    if uid is None:
        messages.error(request, "Please login first.")
        return redirect('/login')

    elif usertype != 'doctor':
        messages.error(request, "Only doctors can access this page.")
        return redirect('/login')

    else:
        donor_id = request.GET.get('id')

        if donor_id is None:
            messages.error(request, "No donor selected.")
            return redirect('/doc_view_donors')

        else:
            try:
                donor = Donor.objects.get(id=donor_id)
            except Donor.DoesNotExist:
                messages.error(request, "Donor not found.")
                return redirect('/doc_view_donors')

            return render(request, "DOCTOR/donor_detail.html", {"donor": donor})

