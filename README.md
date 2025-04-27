# Mentorship Platform Backend

This is the backend API for a mentorship platform focused on connecting mentees with tech mentors.

## Features

- Language selection for mentees (English/Swahili)
- Profile setup for mentees and mentors
- Mentor-mentee matching algorithm
- Tech pathway selection and resource recommendations
- Resource management for mentors
- USSD integration for feature phones

## Tech Stack

- Django / Django REST Framework
- PostgreSQL
- JWT Authentication
- Africa's Talking USSD Integration

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual environment (recommended)

### Installation

1. Clone the repository
```
git clone https://github.com/yourusername/mentorship-platform.git
cd mentorship-platform
```

2. Create and activate a virtual environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Create a PostgreSQL database
```
createdb mentorship_db
```

5. Configure environment variables
- Copy `.env.example` to `.env`
- Update the values in `.env` with your configuration

6. Run migrations
```
python manage.py migrate
```

7. Create a superuser
```
python manage.py createsuperuser
```

8. Run the development server
```
python manage.py runserver
```

The API will be available at http://localhost:8000/api/

## API Endpoints

### Authentication
- POST `/api/auth/register/` - Register a new user
- POST `/api/auth/token/` - Get JWT tokens
- POST `/api/auth/token/refresh/` - Refresh JWT token

### Mentee Endpoints
- POST `/api/mentee/language-select/` - Select language preference
- POST `/api/mentee/setup/` - Set up mentee profile
- POST `/api/mentee/tech-pathway/` - Choose tech pathway and get resources
- GET `/api/mentee/resources/` - Get resources (optionally filtered by interest)

### Mentor Endpoints
- POST `/api/mentor/setup/` - Set up mentor profile
- POST `/api/mentor/upload-resource/` - Upload a resource
- GET `/api/mentor/upload-resource/` - List uploaded resources

### Matching
- POST `/api/match-mentor/` - Match a mentee with an appropriate mentor

### USSD
- POST `/api/ussd/callback/` - Handle USSD requests

## License

MIT License