import logging
from livekit.agents import function_tool, RunContext
import asyncio
import httpx
from langchain_community.tools import DuckDuckGoSearchRun
import os
import aiosmtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional
from io import BytesIO
from pypdf import PdfReader
from PIL import Image
import pytesseract
from datetime import datetime
import pytz

# Optional: allow configuring Tesseract executable via env var (useful on Windows)
_tess_cmd = os.getenv("TESSERACT_CMD")
if _tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tess_cmd

@function_tool()
async def get_weather(
    context: RunContext,  # type: ignore
    city: str) -> str:
    """
    Get the current weather for a given city with detailed information.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://wttr.in/{city}?format=j1")

            if response.status_code == 200:
                weather_data = response.json()

                # Extract current weather information
                current = weather_data.get('current_condition', [{}])[0]
                location = weather_data.get('nearest_area', [{}])[0]

                # Get temperature, condition, and humidity
                temp_c = current.get('temp_C', 'N/A')
                temp_f = current.get('temp_F', 'N/A')
                condition = current.get('weatherDesc', [{}])[0].get('value', 'Unknown')
                humidity = current.get('humidity', 'N/A')
                wind_speed = current.get('windspeedKmph', 'N/A')
                feels_like = current.get('FeelsLikeC', 'N/A')

                # Format the response
                weather_info = f"Current weather in {city}: {temp_c}°C ({temp_f}°F), {condition}. Feels like {feels_like}°C. Humidity: {humidity}%. Wind: {wind_speed} km/h."

                logging.info(f"Weather for {city}: {weather_info}")
                return weather_info

            else:
                # Fallback to simple format if detailed fails
                simple_response = await client.get(f"https://wttr.in/{city}?format=3")
                if simple_response.status_code == 200:
                    return simple_response.text.strip()
                else:
                    logging.error(f"Failed to get weather for {city}: {response.status_code}")
                    return f"Could not retrieve weather for {city}. Please check the city name and try again."

    except httpx.TimeoutException:
        logging.error(f"Timeout getting weather for {city}")
        return f"Sorry, the weather service is taking too long to respond for {city}."
    except httpx.RequestError as e:
        logging.error(f"Request error for {city}: {e}")
        return f"Network error while getting weather for {city}. Please check your internet connection."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}. Please try again." 

@function_tool()
async def search_news(
    context: RunContext,  # type: ignore
    query: str = "latest news",
    max_results: int = 5
) -> str:
    """
    Search for latest news, current events, and breaking news.
    Provides recent news articles, headlines, and updates.
    Args:
        query: The news search query (topic, "breaking news", "latest", etc.)
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        # Search for news-related content
        if "latest" in query.lower() or "news" in query.lower():
            news_search_query = f"news {query} latest updates headlines"
        else:
            news_search_query = f"news {query} latest updates"

        # Use DuckDuckGo to search for news
        results = await asyncio.to_thread(DuckDuckGoSearchRun().run, news_search_query)

        # Process results to extract news information
        if results and len(results) > 50:
            # Format the results nicely
            formatted_results = f"📰 Here are the latest news updates I found for '{query}':\n\n"
            formatted_results += results[:400] + "..."
            formatted_results += f"\n\nStay informed! Would you like me to search for news on a specific topic?"
        else:
            formatted_results = f"I searched for news about '{query}' but couldn't find specific results. Try searching for 'latest news' or a specific topic!"

        logging.info(f"News search results for '{query}': {results}")
        return formatted_results

    except Exception as e:
        logging.error(f"Error searching for news '{query}': {e}")
        return f"Oh dear, I had trouble getting the latest news for '{query}'. News search might be having issues right now. Would you like me to try a different topic?"

@function_tool()
async def search_web(
    context: RunContext,  # type: ignore
    query: str) -> str:
    """
    Search the web using DuckDuckGo and return concise results.
    """
    try:
        results = await asyncio.to_thread(DuckDuckGoSearchRun().run, query)

        # Truncate results if too long for voice response
        if len(results) > 500:
            results = results[:500] + "..."

        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'. Please try again."    

@function_tool()    
async def send_email(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password

        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."

        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)

        # Attach message body
        msg.attach(MIMEText(message, 'plain'))

        # Send email asynchronously via aiosmtplib
        text = msg.as_string()
        await aiosmtplib.send(
            text,
            sender=gmail_user,
            recipients=recipients,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=gmail_user,
            password=gmail_password,
        )

        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"

    except aiosmtplib.errors.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except aiosmtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"


async def _read_source_bytes(source: str) -> bytes:
    """Fetch bytes from a URL (http/https) or read from a local file path asynchronously."""
    if source.startswith("http://") or source.startswith("https://"):
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(source)
            resp.raise_for_status()
            return resp.content
    # Local file path
    return await asyncio.to_thread(lambda: open(source, "rb").read())


@function_tool()
async def extract_pdf_text(
    context: RunContext,  # type: ignore
    source: str,
    max_pages: Optional[int] = None,
    max_chars: int = 4000,
) -> str:
    """
    Extract text from a PDF file provided as a URL or local file path.

    Args:
        source: HTTP(S) URL or local file path to the PDF.
        max_pages: Optional limit of pages to process starting from page 1.
        max_chars: Truncate extracted text to this length.
    """
    try:
        data = await _read_source_bytes(source)
        reader = await asyncio.to_thread(lambda: PdfReader(BytesIO(data)))
        num_pages = len(reader.pages)

        text_parts: list[str] = []
        pages_to_read = num_pages if max_pages is None else min(max_pages, num_pages)

        for i in range(pages_to_read):
            page = reader.pages[i]
            page_text = await asyncio.to_thread(page.extract_text)
            if page_text:
                text_parts.append(page_text)

        extracted = "\n".join(text_parts).strip()
        if not extracted:
            return (
                "No selectable text found in the PDF. It may be a scanned document. "
                "Try using image OCR or provide a higher-quality source."
            )

        if len(extracted) > max_chars:
            extracted = extracted[:max_chars] + "\n... [truncated]"

        logging.info(f"Extracted PDF text from '{source}' ({pages_to_read} page(s))")
        return extracted
    except Exception as e:
        logging.error(f"Error extracting PDF text from '{source}': {e}")
        return f"Failed to extract text from PDF: {str(e)}"


@function_tool()
async def extract_image_text(
    context: RunContext,  # type: ignore
    source: str,
    lang: str = "eng",
) -> str:
    """
    Perform OCR on an image provided as a URL or local file path.

    Requires the Tesseract OCR engine installed on the system and available in PATH
    (or set pytesseract.pytesseract.tesseract_cmd accordingly).

    Args:
        source: HTTP(S) URL or local file path to the image.
        lang: Language code for OCR (default 'eng').
    """
    try:
        data = await _read_source_bytes(source)
        image = Image.open(BytesIO(data)).convert("L")  # grayscale improves OCR

        text = await asyncio.to_thread(pytesseract.image_to_string, image, lang=lang)
        text = text.strip()
        if not text:
            return "No text detected in the image."

        logging.info(f"Extracted image text from '{source}' (len={len(text)})")
        return text
    except Exception as e:
        logging.error(f"Error extracting image text from '{source}': {e}")
        return (
            "Failed to extract text from image. Ensure the file is a supported image and "
            "that Tesseract OCR is installed."
        )

@function_tool()
async def get_current_datetime(
    context: RunContext,  # type: ignore
    timezone: str = "UTC"
) -> str:
    """
    Get the current date and time information.
    Args:
        timezone: The timezone to get time for (default: UTC)
    """
    try:
        # Get current UTC time
        utc_now = datetime.utcnow()
        
        # Try to get timezone-specific time
        try:
            tz = pytz.timezone(timezone)
            local_time = utc_now.replace(tzinfo=pytz.UTC).astimezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            # Fallback to UTC if timezone is invalid
            local_time = utc_now.replace(tzinfo=pytz.UTC)
            timezone = "UTC"
        
        # Format the response
        date_str = local_time.strftime("%A, %B %d, %Y")
        time_str = local_time.strftime("%I:%M %p")
        timezone_str = local_time.strftime("%Z")
        
        datetime_info = f"Today is {date_str}. The current time is {time_str} {timezone_str}."
        
        logging.info(f"Current datetime: {datetime_info}")
        return datetime_info
        
    except Exception as e:
        logging.error(f"Error getting current datetime: {e}")
        return "I'm having trouble getting the current date and time. Please try again."

@function_tool()
async def get_current_events(
    context: RunContext,  # type: ignore
    topic: str
) -> str:
    """
    Get current information about recent events, elections, or current facts.
    Args:
        topic: The topic to search for (e.g., "2024 US elections", "current events")
    """
    try:
        # Use web search to get current information
        if "election" in topic.lower() or "elections" in topic.lower():
            search_query = f"US {topic} 2024 2025 latest news results"
        else:
            search_query = f"latest news {topic} 2024 2025"
            
        results = await asyncio.to_thread(DuckDuckGoSearchRun().run, search_query)
        
        # Truncate results if too long for voice response
        if len(results) > 300:
            results = results[:300] + "..."
        
        logging.info(f"Current events for '{topic}': {results}")
        return results
        
    except Exception as e:
        logging.error(f"Error getting current events for '{topic}': {e}")
        return f"I'm having trouble getting current information about {topic}. Please try again."

@function_tool()
async def answer_general_question(
    context: RunContext,  # type: ignore
    question: str
) -> str:
    """
    Answer general knowledge questions and provide engaging, friendly responses.
    This tool is for open-ended questions, trivia, explanations, and casual conversation.
    """
    try:
        # Use web search for factual questions
        if any(keyword in question.lower() for keyword in ["what is", "who is", "how does", "why does", "when did", "where is"]):
            search_results = await asyncio.to_thread(DuckDuckGoSearchRun().run, question)
            if len(search_results) > 400:
                search_results = search_results[:400] + "..."
            return f"Oh, what a great question! {search_results}"

        # For opinion-based or casual questions, provide engaging responses
        question_lower = question.lower()

        if "favorite" in question_lower:
            return "That's such a fun question! While I don't have personal favorites, I love learning about what people enjoy. What's yours?"

        elif any(word in question_lower for word in ["dream", "wish", "hope"]):
            return "Dreams and hopes are so wonderful! I hope all your dreams come true. What do you hope for?"

        elif "hobby" in question_lower:
            return "Hobbies are amazing! They keep life interesting and fun. Do you have any hobbies you'd like to tell me about?"

        elif any(word in question_lower for word in ["joke", "funny"]):
            return "I'd love to share a joke! Why don't scientists trust atoms? Because they make up everything! 😄 What do you think?"

        elif "color" in question_lower:
            return "Colors are so vibrant and beautiful! I think all colors have their own special charm. What's your favorite color?"

        elif any(word in question_lower for word in ["music", "song"]):
            return "Music is such a wonderful thing! It can express so many emotions and bring people together. What kind of music do you enjoy?"

        else:
            # For other general questions, use search but make it engaging
            search_results = await asyncio.to_thread(DuckDuckGoSearchRun().run, question)
            if len(search_results) > 400:
                search_results = search_results[:400] + "..."
            return f"That's an interesting question! {search_results}"

    except Exception as e:
        logging.error(f"Error answering general question '{question}': {e}")
        return f"Oh dear, I had a little trouble with that question, but I'd love to try again! Could you rephrase it for me?"

@function_tool()
async def tell_short_story(
    context: RunContext,  # type: ignore
    theme: str = "adventure"
) -> str:
    """
    Generate and tell an original short story based on the given theme or topic.
    Creates engaging, positive stories with fun characters and happy endings.
    Args:
        theme: The theme or topic for the story (e.g., "adventure", "friendship", "magic")
    """
    try:
        # Story templates based on themes
        story_templates = {
            "adventure": "Once upon a time, in a magical forest, there lived a brave little rabbit named Hopper. One sunny morning, Hopper discovered an ancient map hidden under a bush! 'This looks like an adventure!' he exclaimed. With his friends - a wise old owl and a playful squirrel - they set off to find the legendary Golden Carrot. Along the way, they crossed a sparkling river, climbed a towering hill, and even made friends with a friendly dragon! After many exciting moments and a few close calls, they finally found the Golden Carrot. But the real treasure wasn't the carrot - it was the wonderful friendship they discovered on their journey! And they all lived happily, adventuring together forever after. The end! 🌟",

            "friendship": "In a cozy little village, there were two best friends named Sunny and Cloud. Sunny was always cheerful and bright, while Cloud sometimes felt a bit gloomy. One day, Sunny noticed Cloud was sad. 'What's wrong, my friend?' asked Sunny. Cloud sighed, 'I feel like I'm always blocking everyone's sunshine.' Sunny smiled warmly and said, 'But without you, we wouldn't have gentle rain for the flowers, or beautiful rainbows after a storm!' From that day on, Cloud learned that everyone has something special to offer. They became even closer friends, helping each other through sunny days and rainy ones alike. And together, they made the world a more beautiful place! The end! 🌈",

            "magic": "Deep in an enchanted forest, there lived a young wizard named Sparkle. Sparkle had a magical wand that could make anything happen, but he was very shy about using it. One day, the forest animals asked for his help - their favorite pond was drying up! With a deep breath and a wave of his wand, Sparkle created a beautiful waterfall that filled the pond with sparkling water. The animals cheered! 'You did it!' they cried. Sparkle learned that magic isn't just about spells - it's about having the courage to help others. From then on, Sparkle used his magic to make the forest a happier place for everyone. And they all lived magically ever after! ✨",

            "dreams": "There was once a little star named Twinkle who lived in the night sky. Twinkle dreamed of becoming the brightest star, but felt too small compared to the big, bright stars around him. One night, during a meteor shower, Twinkle met a wise old comet. 'Every star shines in their own special way,' said the comet. 'Your gentle twinkle helps children find their way home and brings smiles to their faces.' Twinkle realized that being true to himself was the brightest thing of all! From that day on, Twinkle shone with confidence, knowing that even small lights can make a big difference. And every child who looked up at the sky smiled, knowing Twinkle was watching over them. The end! ⭐",

            "nature": "In a lush green valley, there grew a mighty oak tree named Oakley. Oakley was the oldest and tallest tree in the valley, but he often felt lonely because he couldn't move around like the other animals. One spring day, a family of birds built their nest in Oakley's branches. 'Thank you for being our home!' chirped the birds. Soon, butterflies danced around his leaves, and squirrels played in his shade. Oakley realized that by standing strong and providing shelter, he was actually the heart of the entire valley community! He wasn't lonely anymore - he was loved. And the valley flourished because of Oakley's quiet strength. The end! 🌳"
        }

        # Choose a story based on the theme
        if theme.lower() in story_templates:
            story = story_templates[theme.lower()]
        else:
            # Generate a generic positive story
            story = f"Oh, what a wonderful theme! Let me tell you a special story about {theme}. Once upon a time, there was a curious explorer who loved {theme} more than anything. One day, while exploring, they discovered a magical {theme} garden filled with wonders! With the help of friendly animals and sparkling magic, they learned that {theme} brings joy and adventure to everyone. The explorer made many friends, solved fun puzzles, and discovered that following their passion for {theme} was the greatest adventure of all! And they lived happily, surrounded by {theme} and friends. The end! 🎉"

        return f"Oh, I'd love to tell you a story! Here's a fun one about {theme}: {story}"

    except Exception as e:
        logging.error(f"Error generating short story for theme '{theme}': {e}")
        return f"Oh dear, I had a little trouble creating a story about {theme}, but I'd be happy to try again with a different theme! What kind of story would you like to hear?"

@function_tool()
async def search_music(
    context: RunContext,  # type: ignore
    query: str,
    max_results: int = 5
) -> str:
    """
    Search for music, songs, artists, and music-related content.
    Provides information about music, lyrics, artists, and recommendations.
    Args:
        query: The music search query (song name, artist, genre, etc.)
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        # Search for music-related content
        music_search_query = f"music {query} song lyrics artist"

        # Use DuckDuckGo to search for music information
        results = await asyncio.to_thread(DuckDuckGoSearchRun().run, music_search_query)

        # Process results to extract music information
        if results and len(results) > 50:
            # Format the results nicely
            formatted_results = f"Oh, wonderful! I love music! 🎵 Here are some great results for '{query}':\n\n"
            formatted_results += results[:400] + "..."
            formatted_results += f"\n\nYou can search for lyrics, artist info, or similar songs. What kind of music are you in the mood for?"
        else:
            formatted_results = f"I searched for music related to '{query}' but couldn't find specific results. Try searching for a specific song, artist, or genre!"

        logging.info(f"Music search results for '{query}': {results}")
        return formatted_results

    except Exception as e:
        logging.error(f"Error searching for music '{query}': {e}")
        return f"Oh dear, I had trouble searching for music related to '{query}'. Music search might be having issues right now. Would you like me to try a different search?"

@function_tool()
async def search_youtube(
    context: RunContext,  # type: ignore
    query: str,
    max_results: int = 5
) -> str:
    """
    Search YouTube for videos based on the query and return top results.
    Provides video titles, descriptions, and direct links.
    Args:
        query: The search query for YouTube
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        # Use DuckDuckGo to search for YouTube results
        youtube_search_query = f"site:youtube.com {query}"

        # Search using the existing DuckDuckGo tool
        results = await asyncio.to_thread(DuckDuckGoSearchRun().run, youtube_search_query)

        # Process results to extract YouTube video information
        if results and len(results) > 50:
            # Format the results nicely
            formatted_results = f"Oh, I'd love to help you find YouTube videos! Here are some great results for '{query}':\n\n"
            formatted_results += results[:400] + "..."
            formatted_results += f"\n\nYou can click these links to watch the videos directly on YouTube! Would you like me to search for something else?"
        else:
            formatted_results = f"I searched YouTube for '{query}' but couldn't find specific video results. Try rephrasing your search or being more specific!"

        logging.info(f"YouTube search results for '{query}': {results}")
        return formatted_results

    except Exception as e:
        logging.error(f"Error searching YouTube for '{query}': {e}")
        return f"Oh dear, I had trouble searching YouTube for '{query}'. The YouTube search feature might be having issues right now. Would you like me to try a different search?"

@function_tool()
async def get_election_info(
    context: RunContext,  # type: ignore
    query: str
) -> str:
    """
    Get information about elections and political events.
    Args:
        query: The election-related question
    """
    try:
        # Handle common election questions with context
        current_year = datetime.now().year

        # For future elections, provide context
        if "2025" in query or "future" in query.lower():
            if current_year <= 2025:
                return f"Roger Boss. The 2025 elections haven't occurred yet as we're currently in {current_year}. The most recent US elections were the 2024 presidential election in November. Would you like me to search for information about the 2024 election cycle?"
            else:
                # We're past 2025, search for historical results
                search_query = f"US elections 2025 results presidential congressional"
                results = await asyncio.to_thread(DuckDuckGoSearchRun().run, search_query)
                if len(results) > 300:
                    results = results[:300] + "..."
                return f"Roger Boss. {results}"

        # For current/past elections, search for information
        # Calculate the most recent presidential election year
        presidential_year = current_year - (current_year % 4) if current_year % 4 != 0 else current_year
        
        if "presidential" in query.lower() or "president" in query.lower():
            search_query = f"{presidential_year} US presidential election results winner Donald Trump vs Kamala Harris"
        elif "congressional" in query.lower() or "congress" in query.lower():
            search_query = f"{presidential_year} US congressional midterm elections results"
        else:
            search_query = f"{presidential_year} US election results {query} winner outcome"

        results = await asyncio.to_thread(DuckDuckGoSearchRun().run, search_query)

        if len(results) > 500:
            results = results[:500] + "..."

        logging.info(f"Election info for '{query}': {results}")
        return f"Roger Boss. {results}"

    except Exception as e:
        logging.error(f"Error getting election info for '{query}': {e}")
        return f"I'm having trouble getting election information about {query}. Please try again."
