# Soweto Business Directory

A Django REST Framework (DRF) API for managing local businesses in Soweto.

## Features

- Business listings with categories, reviews, and ratings.
- Search and filter functionality.
- Map integration for business locations.

## Tech Stack

- **Frontend**: React.js
- **Backend**: Django
- **Database**: SQLite (development), PostgreSQL (production)
- **Maps API**: Google Maps or OpenStreetMap

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/soweto-business-directory.git
   ```

2. Set up a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Run migrations:

```
python manage.py migrate
```

5. Start the development server:

```
python manage.py runserver
```

## API Endpoints

- Categories: /api/categories/
- Businesses: /api/businesses/
- Reviews: /api/reviews/

## License

This project is licensed under the MIT License.
