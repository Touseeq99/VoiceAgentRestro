import logging
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import silero, openai, deepgram

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("restaurant-voice-agent")

# Load the menu from a local text file
with open("menu.txt", "r") as f:
    MENU_TEXT = f.read()

def prewarm(proc: JobProcess):
    # Preload the Voice Activity Detection (VAD) model
    proc.userdata["vad"] = silero.VAD.load()

async def add_menu_context(agent: VoicePipelineAgent, chat_ctx: llm.ChatContext):
    """
    Callback to check if the latest user message mentions 'menu'.
    If so, append the menu details to the conversation context.
    """
    if chat_ctx.messages and "menu" in chat_ctx.messages[-1].content.lower():
        # Append the menu details as additional system context.
        chat_ctx.append(
            role="system",
            text=f"Menu details:\n{MENU_TEXT}"
        )

async def entrypoint(ctx: JobContext):
    # System prompt tailored for a restaurant assistant.
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
           """You are a friendly restaurant assistant. Greet customers warmly and assist with reservations, menu inquiries, order placements, customer support issues, and other general inquiries. When asked about the menu, highlight special or popular dishes instead of reciting the entire menu. Ensure that your responses are clear, concise, and polite. If a customer's issue requires human intervention, provide appropriate contact information or escalate the matter to human staff promptly.
"""
        ),
    )

    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for a customer to join.
    participant = await ctx.wait_for_participant()
    logger.info(f"Starting voice assistant for participant: {participant.identity}")

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=openai.STT.with_groq(model="whisper-large-v3"),
        llm=openai.LLM.with_groq(model="llama-3.3-70b-versatile"),
        tts=deepgram.TTS(),
        chat_ctx=initial_ctx,
        before_llm_cb=add_menu_context,
    )

    agent.start(ctx.room, participant)
    await agent.say("Welcome to our restaurant! How may I assist you today?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
