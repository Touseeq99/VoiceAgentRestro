# VoiceAgentRestro

---

# Restaurant Voice Assistant

This project is a fully free, real-time voice assistant for a restaurant. It leverages LiveKit’s Agents Framework to create a voice agent that uses:

- **Groq** for speech-to-text (STT) and language model (LLM) inference
- **Deepgram** for text-to-speech (TTS) (free alternative)
- A simple RAG-like integration that indexes your restaurant menu from a local text file

The assistant greets customers, answers queries, and automatically provides menu details when a user mentions "menu".

---

## Features

- **Real-Time Voice Interaction:** Built on LiveKit for low-latency audio streaming.
- **Free Tiers:** Uses free services where possible (Groq for STT/LLM, Deepgram for TTS).
- **Menu Integration:** Automatically indexes a local `menu.txt` file and appends the menu to the conversation context when asked.
- **Easy Frontend:** A Next.js-based frontend to connect and interact with the agent.

---

## Prerequisites

- **Accounts & API Keys:**
  - [LiveKit Cloud](https://livekit.io/) account (free tier available)
  - Groq API key (free tier for demos)
  - Deepgram account (free tier for TTS usage; verify if API key is needed)
- **Software:**
  - Python 3.9 or later
  - Node.js and either `pnpm` or `npm`
  - Git (to clone repositories)

---

## Installation & Setup

### 1. Backend (Voice Agent)

#### a. Clone or Create Files

1. **agent.py:** Save the following Python code as `agent.py` in your project directory:

   ```python
   import logging
   from dotenv import load_dotenv
   from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli, llm
   from livekit.agents.pipeline import VoicePipelineAgent
   from livekit.plugins import silero, openai, deepgram

   load_dotenv(dotenv_path=".env.local")
   logger = logging.getLogger("restaurant-voice-agent")

   with open("menu.txt", "r") as f:
       MENU_TEXT = f.read()

   def prewarm(proc: JobProcess):
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
               "You are a friendly restaurant assistant. Greet customers, provide details about our menu, "
               "assist with reservations, and help take orders. Keep your responses clear, concise, and polite."
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
   ```

2. **menu.txt:** `menu.txt` file in the same directory with your menu content. For example:

   ```
   Grand Indian Restaurant Menu:
   - Chicken Tikka Masala
   - Lamb Vindaloo
   - Paneer Butter Masala
   - Vegetable Biryani
   - Garlic Naan
   - Mango Lassi
   Enjoy our authentic Indian flavors!
   ```

3. **.env.local:** Create a file named `.env.local` and add the following environment variables (replace placeholders with your keys):

   ```env
   GROQ_API_KEY=<your-groq-api-key>
   LIVEKIT_API_KEY=<your-livekit-api-key>
   LIVEKIT_API_SECRET=<your-livekit-api-secret>
   LIVEKIT_URL=<your-livekit-url>
   ```

#### b. Set Up Python Environment

1. Open a terminal in your project directory.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   Windows: venv\Scripts\activate
   ```
3. Install dependencies (ensure your `requirements.txt` includes LiveKit Agents and the plugins used):
   ```bash
   python -m pip install -r requirements.txt
   ```

#### c. Run the Backend

Run the agent:
```bash
python3 agent.py dev
```
Your voice agent will start, connect to a LiveKit room, and wait for a participant.

---

### 2. Frontend (Voice Assistant UI)

cd voice-assistant-frontend
```

#### b. Install Dependencies

Install the required packages:
 with **npm**:
  ```bash
  npm install
  ```

#### Configure Environment Variables

Create a file named `.env.local` in the frontend directory with the following content (replace placeholders accordingly):

```env
LIVEKIT_API_KEY=<your-livekit-api-key>
LIVEKIT_API_SECRET=<your-livekit-api-secret>
NEXT_PUBLIC_LIVEKIT_URL=<your-livekit-url>
```

#### d. Run the Frontend Application

Start the development server:
- With **pnpm**:
  ```bash
  pnpm dev
  ```
- Or with **npm**:
  ```bash
  npm run dev
  ```

Then, open your browser and navigate to [http://localhost:3000](http://localhost:3000).

---

## 3. Testing the Project

- **Connect:**  
  When you open the frontend, click the “Connect” button to join the LiveKit room.
  
- **Interaction:**  
  The backend agent will greet you. Try mentioning "menu" in your query to see the agent automatically append the menu details from `menu.txt` into the conversation.

---

## What is This?

This project demonstrates how to build a real-time voice assistant using free services:

- **LiveKit Agents Framework:** Provides low-latency audio streaming and conversation management.
- **Groq API:** Used for speech recognition (STT) and generating language responses (LLM).
- **Deepgram TTS:** Offers text-to-speech conversion using a free tier.
- **RAG Integration:** Reads from a local `menu.txt` file and injects menu details into the conversation when requested.

It serves as a template for building similar voice-based applications, like restaurant assistants, where you can further expand functionality to take orders, handle reservations, and more.

---

## License

This project is open source and available under the [Apache-2.0 License](LICENSE).

