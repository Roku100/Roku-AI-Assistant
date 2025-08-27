# 🧠 Roku - Your Personal AI Assistant

Roku is a cheerful and helpful AI assistant inspired by *Jarvis*, built with Python and powered by LiveKit's advanced voice interaction capabilities. This agent combines speech recognition, natural language processing, and various tools to provide an engaging conversational experience.

## ✨ Features

- 🔍 **Web Search** - Search the internet for information
- 🌤️ **Weather Checking** - Get current weather conditions for any city
- 📨 **Email Sending** - Send emails through Gmail integration
- 📷 **Vision Analysis** - Extract text from images and PDFs
- 🗣️ **Speech Interaction** - Natural voice conversations
- 📝 **Chat Interface** - Text-based conversations through web app
- 📰 **Current Events** - Stay updated with latest news and events
- 🎭 **Storytelling** - Generate original short stories
- 🎵 **Music Search** - Find songs, artists, and music content
- 📺 **YouTube Search** - Discover videos and content
- 🗳️ **Election Information** - Get political and election data
- 🕐 **Date & Time** - Current date, time, and timezone information

## 🛠️ Prerequisites

- Python 3.8 or higher
- A Google Cloud account (for speech processing)
- A LiveKit account (100% free tier available)
- Gmail account (optional, for email functionality)

## 🚀 LiveKit Setup

LiveKit provides the voice interaction capabilities for Roku. Follow these steps to set up your LiveKit account:

1. **Visit LiveKit**: Go to [livekit.io](https://livekit.io) and click **"Start Building"**

2. **Create New Project**:
   - Click **"Create New Project"**
   - Choose a project name (e.g., "Roku Assistant")
   - Select your preferred region

3. **Access API Keys**:
   - Click on your newly created project
   - Navigate to **Settings > API Keys**
   - Click **"Create a new API key"**
   - Give your key a descriptive name (e.g., "Roku API Key")
   - **Copy all the credentials immediately and store them safely**:
     - **API Key** (public key)
     - **API Secret** (private key - keep this secure!)
     - **LiveKit URL** (WebSocket URL for your project)

4. **Security Note**: Never commit API keys to version control. Always store them securely and use environment variables.

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd roku_jarvis-main
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Copy the environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Configure your API keys in `.env`**:
   ```env
   # LiveKit Configuration (from your LiveKit project)
   LIVEKIT_URL=wss://your-project-name.livekit.cloud
   LIVEKIT_API_KEY=your_livekit_api_key_here
   LIVEKIT_API_SECRET=your_livekit_api_secret_here

   # Google API Key (for speech processing)
   GOOGLE_API_KEY=your_google_api_key_here

   # Gmail Configuration (optional - for email functionality)
   GMAIL_USER=your-email@gmail.com
   GMAIL_APP_PASSWORD=your_gmail_app_password_here
   ```

   **Note**: Replace the placeholder values with your actual API credentials from the LiveKit setup steps above.

## 🎯 Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Google AI Studio API" and "Speech-to-Text API"
4. Create API credentials (API Key)
5. Copy the API key to your `.env` file

## ▶️ Running the Application

1. **Start the LiveKit agent**:
   ```bash
   python agent.py
   ```

2. **Access the web interface** (if available):
   - Open your browser and navigate to the provided URL
   - Start interacting with Roku through voice or text

## 💬 Usage

Roku is designed to be conversational and friendly. Here are some example interactions:

- **Weather**: "What's the weather like in New York?"
- **Search**: "Search for the latest technology news"
- **Time**: "What time is it?"
- **Stories**: "Tell me a short story about space exploration"
- **Music**: "Find me some jazz music playlists"
- **Email**: "Send an email to john@example.com with the subject 'Hello' and message 'How are you?'"

Roku will respond enthusiastically and use the appropriate tools to fulfill your requests!

## 🔧 Troubleshooting

- **LiveKit Connection Issues**: Verify your LiveKit URL, API key, and secret in the `.env` file
- **Google API Errors**: Ensure your Google API key has the necessary permissions enabled
- **Email Functionality**: Check your Gmail app password and ensure less secure app access is enabled
- **Voice Issues**: Make sure your microphone permissions are granted and audio devices are working

## 📚 Additional Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [Google Cloud AI Studio](https://aistudio.google.com/)
- Tutorial Video: [Watch Setup Guide](https://youtu.be/An4NwL8QSQ4?si=v1dNDDonmpCG1Els)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Enjoy your conversations with Roku!** 🚀 

