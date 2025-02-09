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

## Primary API Endpoints

### 1. Get Popularity Rankings

> Fetches the popularity scores of all games with pagination and ranking continuity.

**Endpoint:** `GET /api/game-popularity/`

**Query Parameters:**

| Parameter   | Type   | Required | Description                                                           | Example            |
| ----------- | ------ | -------- | --------------------------------------------------------------------- | ------------------ |
| `date`      | string | No       | Fetch rankings for a specific date (`YYYY-MM-DD`). Defaults to today. | `?date=2025-02-09` |
| `page`      | int    | No       | Fetch a specific page of results.                                     | `?page=2`          |
| `page_size` | int    | No       | Number of results per page (max 100). Defaults to 10.                 | `?page_size=5`     |

**Example Request**:

```
GET /api/game-popularity/?date=2025-02-09&page=1&page_size=2
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

| Parameter | Type | Required | Description | Example |
| --------- | ---- | -------- | ----------- | ------- |

| `page` | int | No | Fetch a specific page of results. | `?page=2` |

| `page_size` | int | No | Number of results per page (max 100). Defaults to 10. | `?page_size=5` |

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
