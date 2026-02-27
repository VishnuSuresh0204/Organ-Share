from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import timedelta, datetime

# -----------------------
# 1. Login/User
# -----------------------
class Login(AbstractUser):
    usertype = models.CharField(max_length=50)
    viewpassword = models.CharField(max_length=100, blank=True, null=True)


# -----------------------
# 2. Recipient
# -----------------------
class Recipient(models.Model):
    login = models.ForeignKey('Login', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=200)
    blood_group = models.CharField(max_length=10)
    age = models.IntegerField(null=True)
    status = models.IntegerField(default=0)  # 0 = pending, 1 = approved
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.name


# -----------------------
# 3. Doctor
# -----------------------
class Doctor(models.Model):
    login = models.ForeignKey('Login', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=200)
    status = models.IntegerField(default=0)  # 0 = Pending, 1 = Approved
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.name


# -----------------------
# 4. Donor
# -----------------------
class Donor(models.Model):
    login = models.ForeignKey('Login', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=200)
    age = models.IntegerField(null=True)
    blood_group = models.CharField(max_length=10)
    can_donate_liver = models.BooleanField(default=False)
    can_donate_kidney = models.BooleanField(default=False)
    after_death_donation = models.BooleanField(default=True)
    status = models.IntegerField(default=0)  # 0 = Pending, 1 = Approved, 2 = Blocked
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.name


# -----------------------
# 5. Slot
# -----------------------
class Slot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']

    def clean(self):
        # Ensure start < end
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        # Ensure slot duration is exactly 30 minutes
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        if (end_dt - start_dt) != timedelta(minutes=30):
            raise ValidationError("Slot duration must be 30 minutes.")

        # Ensure no overlapping slots for the same doctor
        overlapping = Slot.objects.filter(
            doctor=self.doctor,
            date=self.date
        ).exclude(id=self.id)

        for s in overlapping:
            if not (self.end_time <= s.start_time or self.start_time >= s.end_time):
                raise ValidationError("Slots must not overlap for the same doctor.")

    def __str__(self):
        return f"{self.doctor.name} - {self.date} {self.start_time} to {self.end_time}"


# -----------------------
# 6. Appointment
# -----------------------
APPOINTMENT_STATUS_CHOICES = [
    ('Scheduled', 'Scheduled'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled')
]

class Appointment(models.Model):
    slot = models.OneToOneField(Slot, on_delete=models.CASCADE)  # only one appointment per slot
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, null=True, blank=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default='Scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slot__date', 'slot__start_time']
        unique_together = ('slot',)  # prevent double booking

    def __str__(self):
        return f"{self.recipient.name} with {self.slot.doctor.name} on {self.slot.date} at {self.slot.start_time}"


# -----------------------
# 7. Feedback
# -----------------------
class Feedback(models.Model):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, null=True, blank=True)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(default=0)  # 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.recipient.name}: {self.subject} (Rating: {self.rating})"
