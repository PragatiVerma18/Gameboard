# GameBoard API

> GameBoard is a leaderboard and game session management system that allows tracking contestant scores, game popularity, and real-time leaderboards.

## Features

- Create and manage games
- Add contestants and track their game sessions
- Assign scores to contestants
- Retrieve leaderboards at game and global levels
- Compute a game popularity index, refreshing every 5 minutes using Celery

## Setup Instructions

1. Clone the Repository

```
git clone https://github.com/PragatiVerma18/Gameboard.git
cd gameboard
```

2. Create and activate Virtual Environment

```
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies

```
pip install -r requirements.txt
```

4. Set Up the Database

```
python manage.py migrate
```

5. Create a Superuser (Optional, for Django Admin)

```
python manage.py createsuperuser
```

6. Run Redis (Required for Celery)

```
redis-server
```

7. Start Celery Worker

```
celery -A gameboard worker --loglevel=info
```

8. Start Celery Beat (For Scheduled Tasks)

```
celery -A gameboard beat --loglevel=info
```

9. Run the Django Development Server

```
python manage.py runserver
```

> The server will run at http://127.0.0.1:8000.
> Access Django Admin at http://127.0.0.1:8000/admin using the username and password you used earlier.
> Access all APIs at http://127.0.0.1:8000/api/

10. Seed Test Data using Management Command in the terminal

```
python manage.py add_test_data
```

## API Documentation

Swagger and ReDoc endpoints:

- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/
