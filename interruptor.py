from concurrent.futures import ThreadPoolExecutor
import threading
import time
import numpy
import io
import soundfile as sf
import sounddevice as sd
from fuzzywuzzy import fuzz
from openai import OpenAI
from llama_cpp import Llama
from dotenv import load_dotenv
import os

# whisper(user audio) -> query
# llama(query) -> completion
# loop until k-token convergence
# gpt(completion) -> response
# tts(response) -> response audio

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=openai_api_key,
    base_url="http://oai.hconeai.com/v1",
    default_headers={"Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}"},
)

query_completions = []


def find_converged_completion(query):
    # Given an incomplete query, complete it. When a prior completion matches the last k tokens of the user's query, return it.
    for old_query, completion in query_completions[::-1]:
        if check_match(completion, query):
            return " ".join([old_query, completion])

    completion = llm(query)
    if completion.startswith(query):
        completion = completion.replace(query, "")

    query_completions.append((query, completion))
    return None


def check_match(completion, query, k=3, fuzz_threshold=60):
    # Given a completion and a query, check if the last k tokens of the query match the completion. If so, return True.
    query_toks = query.split(" ")[-k:]
    completion_toks = completion.split(" ")[:k]

    query_str = " ".join(query_toks)
    completion_str = " ".join(completion_toks)

    if fuzz.ratio(query_str, completion_str) > fuzz_threshold:
        return True
    else:
        return False


# model = Llama("./models/llama-2-7b.Q4_K_M.gguf")

# def llm(query):
#     response = model(
#         query,
#         max_tokens=6,
#         stop=[
#             ".",
#             "\n",
#         ],
#         echo=False,  # Echo the prompt back in the output
#     )
#     completion = response['choices'][0]['text']

#     print("COMPLETION: ", completion, "\n")

#     return completion


def llm(query):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Please complete the user's text. Do not repeat the user's text. Do not add or say anything else. Do NOT answer their query or respond to them. Simply respond by 'autocompleting' their sentence. If they've completed a sentence, continue with the next sentence.",
            },
            {"role": "user", "content": query},
        ],
        max_tokens=64,
    )

    print("COMPLETION: ", response.choices[0].message.content, "\n")

    return response.choices[0].message.content


def gpt(completion):
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": completion},
        ],
        max_tokens=48,
    )

    print("INTERRUPTION: ", response.choices[0].message.content)

    return response.choices[0].message.content


def tts(response, voice="onyx"):
    spoken_response = client.audio.speech.create(
        model="tts-1", voice=voice, response_format="opus", input=response
    )

    buffer = io.BytesIO()
    for chunk in spoken_response.iter_bytes(chunk_size=4096):
        buffer.write(chunk)
    buffer.seek(0)

    with sf.SoundFile(buffer, "r") as sound_file:
        data = sound_file.read(dtype="int16")
        sd.play(data, sound_file.samplerate)
        sd.wait()


def tts_from_future(future):
    gpt_result = future.result()  # This will block until the gpt function completes
    tts(gpt_result, "onyx")


def thoughtocomplete(query):
    completion = find_converged_completion(query)
    if completion:
        print("THOUGHTOCOMPLETE: ", completion)
        # tts(f"Thought o complete: {completion}", voice="shimmer")
        threading.Thread(
            target=tts,
            args=("interrupting cow! interrupting cow! interrupting cow!", "onyx"),
        ).start()
        with ThreadPoolExecutor() as executor:
            future = executor.submit(gpt, completion)
            threading.Thread(target=tts_from_future, args=(future,)).start()
            return True
    return False


if __name__ == "__main__":
    query = (
        "What is the following song? On a dark desert highway, cool wind in my hair."
    )
    # query = "Who said this quote? To be or not to be, that is the question."
    query_toks = query.split(" ")

    for i in range(1, len(query_toks)):
        curr_query = " ".join(query_toks[:i])
        print(curr_query)
        # tts(query_toks[i-1], voice="nova")
        done = thoughtocomplete(curr_query)
        if done:
            break

    # query = "What is the following song? On a dark desert highway"
    # completion = llm(query)
    # print(completion)


# For AI to be an extension of thought, convos must be fluid.
# When I speak, you predict what I'll say.
# If you understand what I'm saying, you interrupt me.
# LLMs don't do this.
