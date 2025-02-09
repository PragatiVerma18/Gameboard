# GameBoard API

> GameBoard is a leaderboard and game session management system that allows tracking contestant scores, game popularity, and real-time leaderboards.

See views [below](https://github.com/PragatiVerma18/Gameboard/#views) ⬇️

## Features

- Create and manage games
- Add contestants and track their game sessions
- Assign scores to contestants
- Retrieve leaderboards at game and global levels
- Compute a game popularity index, refreshing every 5 minutes using Celery

## Table of Contents

1. [Setup Instructions](#setup-instructions)
   - [Using Docker](#using-docker)
2. [API Documentation](#api-documentation)
3. [Primary API Endpoints](#primary-api-endpoints)
   - [Get Popularity Rankings](#1-get-popularity-rankings)
   - [Get Global Leaderboard](#2-get-global-leaderboard)
   - [Get Game-Specific Leaderboard](#3-get-game-specific-leaderboard)
4. [Celery Tasks & Caching Strategy](#celery-tasks--caching-strategy)
   - [Celery Tasks & Their Schedule](#celery-tasks--their-schedule)
   - [Caching Strategy](#caching-strategy)
5. [Views](#views)

## Setup Instructions

### Using Docker

1. Clone the Repository

```
git clone https://github.com/PragatiVerma18/Gameboard.git
cd gameboard
```

2. Build and Start Containers

Run the following command to build the images and start the services:

```
docker-compose up --build
```

This will:

- Build the Django API container
- Start a Redis container for Celery
- Start Celery worker and Celery beat for background tasks 3. Verify the Setup

Once the containers are up, check the running services:

```
docker ps
```

4. Apply Database Migrations

If not already applied, run:

```
docker-compose exec web python manage.py migrate
```

5. (Optional) Create a Superuser for Django Admin

```
docker-compose exec web python manage.py createsuperuser
```

6. (Optional) Seed Test Data

```
docker-compose exec web python manage.py add_test_data
```

7. Access the API & Services

- API Base URL: http://127.0.0.1:8000/api/
- Django Admin: http://127.0.0.1:8000/admin/
- Swagger UI: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/

### Without Docker

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

- The server will run at http://127.0.0.1:8000.
- Access Django Admin at http://127.0.0.1:8000/admin using the username and password you used earlier.
- Access all APIs at http://127.0.0.1:8000/api/

10. Seed Test Data using Management Command in the terminal

```
python manage.py add_test_data
```

## API Documentation

Swagger and ReDoc endpoints:

- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/

## Primary API Endpoints

### 1. Get Popularity Rankings

> Fetches the popularity scores of all games with pagination and ranking continuity.

**Endpoint:** `GET /api/games/popularity-leaderboard/`

**Query Parameters:**

| Parameter   | Type   | Required | Description                                                           | Example            |
| ----------- | ------ | -------- | --------------------------------------------------------------------- | ------------------ |
| `date`      | string | No       | Fetch rankings for a specific date (`YYYY-MM-DD`). Defaults to today. | `?date=2025-02-09` |
| `page`      | int    | No       | Fetch a specific page of results.                                     | `?page=2`          |
| `page_size` | int    | No       | Number of results per page (max 100). Defaults to 10.                 | `?page_size=5`     |

**Example Request**:

```
GET /api/games/popularity-leaderboard/?page=1&page_size=2
```

**Example Response**:

```json
{
  "count": 5,
  "next": "http://127.0.0.1:8000/api/games/popularity-leaderboard/?page=2&page_size=2",
  "previous": null,
  "results": {
    "games": [
      {
        "game_id": "0194e9d7-7384-cd62-882b-6e25d03a59ee",
        "game__name": "Chess",
        "popularity_score": 0.6,
        "rank": 1
      },
      {
        "game_id": "0194e9d7-7386-4c61-d596-4db5a6772fae",
        "game__name": "Fortnite",
        "popularity_score": 0.59,
        "rank": 2
      }
    ]
  }
}
```

### 2. Get Global Leaderboard

> Fetches the top players across all games, ranked by their total scores.

**Endpoint**: `GET /api/leaderboard/global/`

**Query Parameters**:

| Parameter   | Type | Required | Description                                           | Example        |
| ----------- | ---- | -------- | ----------------------------------------------------- | -------------- |
| `page`      | int  | No       | Fetch a specific page of results.                     | `?page=2`      |
| `page_size` | int  | No       | Number of results per page (max 100). Defaults to 10. | `?page_size=5` |

**Example Request**:

```
GET /api/leaderboard/?page=1&page_size=3
```

**Example Response**:

```json
{
  "count": 10,
  "next": "http://127.0.0.1:8000/api/leaderboard/?page=2&page_size=3",
  "previous": null,
  "results": {
    "leaderboard": [
      {
        "contestant_id": "0194e9d7-738b-ed42-3738-6c34467bad34",
        "contestant__name": "Player_9",
        "total_score": 99,
        "rank": 1
      },
      {
        "contestant_id": "0194e9d7-738a-41f9-446c-c3637079e458",
        "contestant__name": "Player_7",
        "total_score": 98,
        "rank": 2
      },
      {
        "contestant_id": "0194e9d7-7389-e2ed-b43f-34df291def7f",
        "contestant__name": "Player_4",
        "total_score": 91,
        "rank": 3
      }
    ]
  }
}
```

### 3. Get Game-Specific Leaderboard

> Fetches the top players for a specific game, ranked by their scores in that game.

**Endpoint**: `GET /api/leaderboard/game/{game_id}/`

**Query Parameters**:

| Parameter   | Type | Required | Description                                           | Example        |
| ----------- | ---- | -------- | ----------------------------------------------------- | -------------- |
| `page`      | int  | No       | Fetch a specific page of results.                     | `?page=2`      |
| `page_size` | int  | No       | Number of results per page (max 100). Defaults to 10. | `?page_size=5` |

**Example Request**:

```
GET /api/leaderboard/game/0194e9d7-7384-cd62-882b-6e25d03a59ee/?page=1&page_size=5
```

**Example Response**:

```json
{
  "count": 4,
  "next": "http://127.0.0.1:8000/api/leaderboard/game/0194e9d7-7384-cd62-882b-6e25d03a59ee/?page=2&page_size=3",
  "previous": null,
  "results": {
    "leaderboard": [
      {
        "contestant": "0194e9d7-738a-41f9-446c-c3637079e458",
        "contestant__name": "Player_7",
        "total_score": 98,
        "rank": 1
      },
      {
        "contestant": "0194e9d7-738b-2a05-4d0e-93e3922d6a5c",
        "contestant__name": "Player_8",
        "total_score": 90,
        "rank": 2
      },
      {
        "contestant": "0194e9d7-7388-5346-d843-d0f5a7efeb20",
        "contestant__name": "Player_2",
        "total_score": 50,
        "rank": 3
      }
    ]
  }
}
```

## **Celery Tasks & Caching Strategy**

### **Celery Tasks & Their Schedule**

1. **Cache Popularity Factors & Maximum Values**

   - **Task**: Computes and caches non-changing popularity factors for games, such as:
     - Number of players who played yesterday
     - Maximum session length for a game (from yesterday’s sessions)
     - Total sessions played yesterday
   - **Schedule**: Runs **once every 24 hours** since these values do not change throughout the day.

2. **Refresh Game Popularity Scores**
   - **Task**: Updates the popularity score for each game based on both cached and real-time values. It uses:
     - Cached non-changing factors (from the previous task)
     - Dynamic values (e.g., current active players, upvotes) fetched in real time
   - **Schedule**: Runs **every 5 minutes** to keep scores updated while avoiding excessive database queries.

### **Caching Strategy**

- **Cached for 24 Hours** (Non-Changing Factors)

  - **Yesterday’s Player Count per Game**
  - **Maximum Session Length per Game**
  - **Yesterday’s Total Sessions per Game**
  - **Global Maximum Values for Normalization** (e.g., max upvotes, max daily players)

- **Cached for 5 Minutes** (Dynamic Factors)
  - **Popularity Scores**: Stored briefly to avoid unnecessary recalculations but remain up to date.

By separating static and dynamic factors, caching ensures efficient computation while keeping real-time data accurate. 🚀

## Views

![Home Page](https://github.com/user-attachments/assets/ba2de675-fde6-4009-9196-9109df007a34)

![Global Leaderboard](https://github.com/user-attachments/assets/6d9aa399-b9e6-48a1-bb82-e0df2739436f)

![Game Level Leaderboard](https://github.com/user-attachments/assets/3a0c7f72-a35e-4ecb-8e7b-f86e7fd3946d)

![Date level Leaderboard](https://github.com/user-attachments/assets/efabe72b-e937-475f-96b7-e59ec48d9085)

![Game Popularity Index](https://github.com/user-attachments/assets/537fc243-ccac-4644-984c-f0e33858e739)
