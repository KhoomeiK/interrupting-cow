import pyaudio
from deepgram import Deepgram
import asyncio
from dotenv import load_dotenv
import os

# Your Deepgram API Key
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# PyAudio configuration
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

async def main():
    # Initialize the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    # Create a websocket connection to Deepgram
    # In this example, punctuation is turned on, interim results are turned off, and language is set to UK English.
    try:
        deepgramLive = await deepgram.transcription.live(
            {
                "smart_format": True,
                "interim_results": False,
                "language": "en-US",
                "model": "nova-2",
            }
        )
    except Exception as e:
        print(f"Could not open socket: {e}")
        return
    # Listen for the connection to close
    deepgramLive.register_handler(
        deepgramLive.event.CLOSE, lambda c: print(f"Connection closed with code {c}.")
    )
    # Listen for any transcripts received from Deepgram and write them to the console
    deepgramLive.register_handler(deepgramLive.event.TRANSCRIPT_RECEIVED, print)
    # Start recording from local microphone
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )
    while True:
        data = stream.read(FRAMES_PER_BUFFER)
        deepgramLive.send(data)
        # If no data is being sent from the live stream, then break out of the loop.
        if not data:
            break
    # Indicate that we've finished sending data by sending the customary zero-byte message to the Deepgram streaming endpoint, and wait until we get back the final summary metadata object
    await deepgramLive.finish()


# If running in a Jupyter notebook, Jupyter is already running an event loop, so run main with this line instead:
# await main()
asyncio.run(main())

