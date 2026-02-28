# 🫀 Organ Share

A Django-based web application for organ donation management, enabling seamless coordination between **Donors**, **Recipients**, and **Doctors**, moderated by an **Admin**.

---

## 🌟 Features

### 👤 User Roles
| Role | Capabilities |
|------|-------------|
| **Admin** | Approve/Block/Unblock Donors, Recipients, and Doctors |
| **Recipient** | View doctors, book appointment slots, give feedback, manage profile |
| **Donor** | Book slots, view appointments, give feedback, manage profile |
| **Doctor** | Manage slots, view assigned recipients/donors, manage profile |

### 📋 Core Modules
- **Registration & Login** — Separate registration for Recipients, Donors, and Doctors with admin approval workflow
- **Appointment Slots** — Doctors create 30-minute slots; Recipients and Donors can book them
- **Feedback System** — Both Recipients and Donors can submit and view feedback
- **Profile Management** — All entities can view and edit their profile, including uploading a profile picture
- **Admin Dashboard** — Full control to approve, block, and unblock all entities

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Django 5
- **Database:** SQLite3
- **Frontend:** HTML5, Bootstrap 4, CSS3, JavaScript
- **Media Handling:** Django `ImageField` with Pillow
- **Auth:** Django's built-in authentication with a custom `Login` model

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/VishnuSuresh0204/Organ-Share.git
cd Organ-Share

# 2. Install dependencies
pip install django pillow

# 3. Apply database migrations
python manage.py migrate

# 4. Create a superuser (Admin)
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📁 Project Structure

```
organ/
├── core/                  # Main app (models, views)
│   ├── models.py          # Recipient, Donor, Doctor, Slot, Appointment, Feedback
│   ├── views.py           # All view logic
│   └── migrations/        # Database migrations
├── organ/                 # Django project config
│   ├── settings.py
│   └── urls.py
├── templates/
│   ├── ADMIN/             # Admin templates
│   ├── DOCTOR/            # Doctor templates
│   ├── DONOR/             # Donor templates
│   └── USER/              # Recipient templates
├── static/                # CSS, JS, Images
├── media/                 # Uploaded profile images (not tracked in git)
└── manage.py
```

---

## 📸 User Flows

1. **Register** as Recipient / Donor / Doctor → Wait for Admin approval
2. **Admin** approves the account → User can now log in
3. **Doctor** creates appointment slots
4. **Recipient / Donor** books an available slot
5. After an appointment, **Recipient / Donor** can leave feedback
6. All users can view and edit their **Profile** with a profile picture

---

## 🔐 Notes

- `db.sqlite3` and the `media/` folder are excluded from version control via `.gitignore`
- The admin account must be created manually using `createsuperuser`
- Set `DEBUG = False` and configure a proper database before deploying to production

---

## 📄 License

This project is for educational purposes.
