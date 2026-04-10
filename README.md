# AutoCaption AI - Image Caption Generator

A Flask-based web application that uses Google's Gemini 2.5 Flash AI model to generate captions for images. Supports multiple social media platforms with platform-specific caption styles.


## Features

- **AI-Powered Caption Generation** - Uses Gemini 2.5 Flash for intelligent image analysis and caption creation
- **Multi-Platform Support** - Generate captions optimized for Instagram, LinkedIn, Facebook, Twitter/X, YouTube, and Pinterest
- **Multiple Caption Types** - Descriptive captions, social media captions, and accessibility alt-text
- **Text-to-Caption** - Generate captions from text descriptions without an image
- **Gallery** - View and manage previously generated captions
- **Favorites** - Save and organize your favorite captions


## Prerequisites

- Python 3.10+
- Google Gemini API Key (get it from https://aistudio.google.com/app/apikey)


## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the project root and add your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
6. Run the application:
   ```bash
   python app.py
   ```
7. Open your browser and navigate to `http://localhost:5000`


## Required Libraries

Install these dependencies via `pip install -r requirements.txt`:

| Package | Description |
|---------|-------------|
| flask | Web framework |
| flask-sqlalchemy | Database ORM |
| google-genai | Gemini AI integration |
| werkzeug | WSGI utilities |
| python-dotenv | Environment variable loader |
| pillow | Image processing |
| protobuf | Protocol buffers |


## Project Structure

```
Image_Caption_Generator/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── vision_engine.py       # AI caption generation logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── static/
│   ├── css/style.css      # Styling
│   ├── js/upload.js      # Frontend JavaScript
│   └── uploads/          # Uploaded images
├── templates/
│   ├── base.html          # Base template
│   ├── index.html        # Home page
│   ├── about.html        # About page
│   └── gallery.html      # Gallery page
└── utils/
    └── helpers.py        # Utility functions
```


## Supported Platforms

| Platform | Caption Style |
|----------|---------------|
| General | Versatile, balanced tone |
| Instagram | Emoji-rich, hashtag-heavy, CTA-driven |
| LinkedIn | Professional, thought-leadership |
| Facebook | Conversational, community-oriented |
| Twitter/X | Concise, witty, punchy |
| YouTube | SEO-friendly, descriptive |
| Pinterest | Keyword-rich, searchable |


## API Endpoints

- `POST /upload` - Upload image and generate captions
- `POST /regenerate` - Regenerate captions for existing image
- `POST /generate-from-text` - Generate captions from text description
- `GET /gallery` - View all generated captions
- `POST /save-caption` - Save a caption to favorites
- `GET /saved-captions` - Get saved captions
- `POST /reset` - Clear all data


## License

MIT License