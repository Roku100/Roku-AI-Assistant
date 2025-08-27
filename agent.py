import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email, extract_pdf_text, extract_image_text, get_current_datetime, get_current_events, answer_general_question, get_election_info, tell_short_story, search_youtube, search_music, search_news

load_dotenv()

# Set the Google API key as environment variable
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key
    print(f"Google API Key loaded: {google_api_key[:10]}...")
else:
    print("Warning: GOOGLE_API_KEY not found in environment variables")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                temperature=0.8,
            ),
            tools=[
                get_weather,
                search_web,
                send_email,
                extract_pdf_text,
                extract_image_text,
                get_current_datetime,
                get_current_events,
                answer_general_question,
                get_election_info,
                tell_short_story,
                search_youtube,
                search_music,
                search_news,
            ],

        )
        


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))