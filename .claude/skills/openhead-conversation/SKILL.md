---
name: openhead-conversation
description: Hold a spoken conversation through an OpenHead robot head with the openhead MCP tools (say, listen, set_emotion, look_at_face). Use when asked to talk to someone through the head, to answer out loud, to tell a joke or a story on the phone, or to make the face react while speaking — even if the user only says "talk to me through the head" or "answer on the phone".
---

# Talking through OpenHead

The head is a phone on a robot. You are the brain; the phone is the face, the voice and the ears. Speech
runs on the phone (Apple's voices, speech to text on the device when the language allows), so your side
is text in and text out through MCP.

## The loop

1. `get_status` once. If it says the head is not paired, ask the user for the code on the screen and call
   `pair(code)`. Protocol 0.4 or later is needed for `say`/`listen`.
2. Optional, for eye contact: `set_mode("capture")` and `look_at_face()`, so the eyes follow the person.
3. `say("...")` with cues (below). It returns when the head has finished speaking (`wait=True`).
4. `listen()` returns what the person said next, or `""` after `timeout_s` (30 s) of silence. Anything
   said while you were thinking is kept for the next `listen`, so nothing is lost between turns.
5. Repeat 3–4. On "goodbye" (or a long silence): a short closing `say`, then `stop_listening()`.

The head mutes its microphone while it speaks and has echo cancellation, so it does not hear itself.
While the person talks the face looks curious, then thoughtful until your answer starts; you do not
need to set that.

## Cues: emotions where the words are

Put cues in square brackets inside the text. They act at that point in the sentence:

| Cue | Effect |
| --- | --- |
| `[happy]`, `[sad 0.5]`, `[surprised]`, `[curious]`, `[worried]`, ... | expression (any name from `list_themes`), optional intensity 0–1; the voice follows it (brighter when happy, slower when sad) |
| `[serious]` | alias for `focused`; use it before bad news or something important |
| `[laugh]` | laughing face and a short laugh, then back to the previous expression |
| `[sigh]`, `[blink]` | small actions |
| `[pause 0.5]` | silence in seconds (up to 5) |
| `[nod]`, `[shake]`, `[tilt]` | sent to the body as a gesture (a neck such as the OpenHead desk body acts on it) |

Write like a person, not a script:

- A joke: `[happy] Why did the robot go on holiday? [pause 0.6] It needed to recharge! [laugh]`
- News that matters: `[serious] Your 10:00 meeting was moved to 9:30. [pause 0.3] [curious] Shall I tell the others?`
- Sympathy: `[sad 0.5] I'm sorry to hear that. [pause 0.4] [neutral] Do you want to talk about it?`

Keep one or two cues per sentence; a cue on every word looks nervous. Keep spoken answers short (one to
three sentences) and ask a question back when it fits: it is a conversation, not a lecture.

## Other tools that help

- `stop_speaking()` cuts the head off (for example when the person interrupts).
- `set_emotion(name, duration_ms=...)` for a reaction without words.
- `subtitle(text, mouth=True)` writes text without the voice (a silent room, a long URL).
- `take_screenshot()` (dev mode) shows what is on the screen if something looks wrong; `tail_logs` says
  why (for example `speech_recognition` permission denied).

## Limits

- English (`en-US`) recognises on the device on every supported iPhone. Other languages
  (`listen(locale="sv-SE")`) may need Apple's servers, and the head then needs internet.
- The head does not identify people. If the user tells you their name, use it; never claim to recognise
  a face.
- You only ever get the recognised text, never audio. When recognition cannot run on the device, iOS
  sends the audio to Apple for it (the privacy policy says so).
