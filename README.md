<p align="center">
  <img src="https://raw.githubusercontent.com/khoomeik/interrupting-cow/main/interrupting_cow.png" height="250" alt="Interrupting Cow" />
</p>
<p align="center">
  <em>🐮📢 The first AI voice assistant that interrupts *you*</em>
</p>
<!-- <p align="center">
    <a href="https://pypi.org/project/llamagym/" target="_blank">
        <img alt="Python" src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
        <img alt="Version" src="https://img.shields.io/pypi/v/llamagym?style=for-the-badge&color=3670A0">
    </a>
</p> -->
<p align="center">
<a href="https://reworkd.ai/">🔗 Agents for Web Data Extraction</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://x.com/khoomeik/">🐦 Twitter</a>

# Interrupting Cow 🐮📢

Interruptions make conversations feel natural. Much work has focused on AI voice assistants that can *be interrupted* by humans, but systems that know much more than us should be able to *interrupt us* too.

As you speak, Interrupting Cow 🐮📢 predicts the next *K* tokens you'll say, and when it gets *N* tokens (*N < K*) correct, it becomes "confident" enough to interrupt you. It then uses the entire *K*-token prediction to generate a response.

Interrupting Cow 🐮📢 currently uses Whisper-Realtime for speech recognition, GPT-3.5-Turbo for interruption prediction, GPT-4 for response generation, and OpenAI TTS for text-to-speech.

# Issues
- [ ] refactor and modularize for use as a Python package
- [ ] realtime speech recognition is too slow and choppy
- [ ] migrate from GPT-3.5-Turbo to a faster local LLM