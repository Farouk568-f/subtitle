# Subtitle API

A Flask-based API for retrieving movie and TV show subtitles.

## Features

- Get subtitles for movies by TMDB ID
- Get subtitles for TV shows by TMDB ID, season, and episode
- Supports both Arabic and English content
- Built with Flask and Python

## API Endpoints

### Get Movie Subtitles
```
GET /subs?type=movie&id={tmdb_id}
```

### Get TV Show Subtitles
```
GET /subs?type=tv&id={tmdb_id}&season={season}&episode={episode}
```

## Example Usage

```bash
# For a movie
curl "https://your-vercel-app.vercel.app/subs?type=movie&id=872585"

# For a TV show
curl "https://your-vercel-app.vercel.app/subs?type=tv&id=1399&season=1&episode=1"
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python ddd.py
```

3. The API will be available at `http://localhost:5000`

## Deployment

This project is configured for deployment on Vercel. Simply connect your GitHub repository to Vercel for automatic deployments.

## License

MIT
