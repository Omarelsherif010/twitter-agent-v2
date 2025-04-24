# Twitter Agent V2

A Twitter agent application that uses Tweepy with OAuth 2.0 (PKCE) for multi-user authentication. This agent allows AI to interact with Twitter on behalf of authorized users, with secure token management and JSON-based storage.

## Features

- OAuth 2.0 with PKCE for secure multi-user authentication
- JSON-based token and user data storage (no database required)
- Automatic token refresh handling
- Twitter API v2 operations:
  - Post tweets
  - Read timeline
  - Like/unlike tweets
  - Follow/unfollow users
  - Search tweets
  - Get user information

## Setup

1. Clone this repository
2. Create a virtual environment: `uv venv && .venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with your Twitter API credentials (see `.env.example`):
   ```
   TWITTER_CLIENT_ID=your_client_id
   TWITTER_CLIENT_SECRET=your_client_secret
   TWITTER_CALLBACK_URL=http://localhost:8000/auth/callback
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   ```
5. For local development, set: `set OAUTHLIB_INSECURE_TRANSPORT=1` (Windows) or `export OAUTHLIB_INSECURE_TRANSPORT=1` (Linux/Mac)
6. Run the application: `python app.py`
7. Visit http://localhost:8000 in your browser
8. Connect your Twitter account using the OAuth flow

## Project Structure

```
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── .env.example            # Example environment variables
├── requirements.txt        # Project dependencies
├── auth/                   # Authentication related modules
│   ├── __init__.py
│   ├── oauth.py            # OAuth 2.0 with PKCE implementation
│   └── routes.py           # Authentication routes
├── data/                   # JSON data storage
│   ├── tokens.json         # OAuth tokens storage
│   └── users.json          # User information storage
├── database/               # Data storage related modules
│   ├── __init__.py
│   ├── models.py           # Pydantic models for JSON serialization
│   └── db.py               # JSON file operations and CRUD functions
├── twitter/                # Twitter API related modules
│   ├── __init__.py
│   ├── api.py              # Twitter API wrapper using Tweepy
│   ├── utils.py            # Twitter utility functions
│   └── routes.py           # Twitter operation routes
├── templates/              # HTML templates
├── static/                 # Static assets (CSS, JS)
└── utils/                  # Utility functions
    ├── __init__.py
    └── helpers.py          # Helper functions
```

## Usage

### Authentication Flow

1. Users visit the web application and click "Connect Twitter Account"
2. They are redirected to Twitter's OAuth authorization page
3. After authorizing, they are redirected back to the application
4. The application securely stores their OAuth tokens in JSON files
5. The tokens are automatically refreshed when they expire

### Test Scripts

The project includes test scripts to demonstrate Twitter API operations:

- `simple_tweet_test.py`: Tests multiple Twitter operations (timeline, user info, posting)
- `tweet_test.py`: Focused script for testing tweet posting

Run these scripts to test the Twitter API integration:

```bash
python tweet_test.py
```

### API Endpoints

- `/auth/login`: Start the OAuth flow
- `/auth/callback`: OAuth callback endpoint
- `/twitter/tweet`: Post a new tweet
- `/twitter/timeline`: Get user's timeline
- `/twitter/user`: Get user information

## Security Notes

- For production, always use HTTPS (disable `OAUTHLIB_INSECURE_TRANSPORT`)
- Token refresh is handled automatically when tokens expire
- All sensitive data is stored in JSON files with proper serialization

## License

MIT