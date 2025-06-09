# 🧠 AGENT_TASKS.md – Premium Build Plan for Rachel, the AI Voice Agent

## 🎯 Overall Objective
Transform Rachel from a static, rule-based voice assistant into a **premium-level, LLM-powered AI voice agent** for clinics. Rachel must be capable of dynamic, human-like conversation, intelligent task handling (bookings, reschedules, FAQs), emotional tone control, memory use, and API interaction — all production-ready.

---

## ❌ Current Problems & Shortcomings
- ❌ Fundamental name extraction fails regularly
- ❌ Repetitive, robotic prompt logic
- ❌ Inappropriate or emotionless tone
- ❌ Phone number validation is inconsistent or incorrect
- ❌ Cannot handle humor, sarcasm, or vague input
- ❌ Audio playback fails due to static path issues (NotSupportedError)
- ❌ Conversations follow rigid `if/elif` flows (no dynamic NLU)
- ❌ No real memory or LLM planning — replies feel mechanical

---

## ✅ Core Upgrade Goals

1. **LLM-Powered Dialog Engine**: Replace static prompts with GPT-4o mini (or equivalent) for natural, dynamic responses.
2. **Memory & Context Awareness**: Store name, intent, prior messages, current task — session memory required.
3. **Flexible NLU Intent Handling**: Use NLP to understand user goals like `book_appointment`, `cancel`, `reschedule`, `faq`, `transfer_to_human`.
4. **Real-Time STT + TTS Pipeline**: Whisper for voice input, ElevenLabs for natural voice output with SSML control.
5. **Tool & API Integration**: Enable actions like booking via Google Sheets, email updates, calendar sync, SMS.
6. **Fallback + Clarification Engine**: Graceful handling of vague or failed input, with intelligent retries and escalation.
7. **Multi-Step Task Planning**: Rachel must guide users through processes (e.g., collecting name > service > date > confirm).
8. **Dynamic UI Feedback**: Frontend should show "Listening / Thinking / Speaking" based on backend state.
9. **Logs + Debug Mode**: Full transcript logging, error printing, and test coverage for all flows.
10. **Agent Personality + Tone Control**: Warm, professional, with Emirati-friendly and international style support.

---

## 🧩 High-Level Task Plan for Codex

### 1. Stabilize Code & Fix Audio
- Ensure Flask static paths load correctly
- Fix ElevenLabs `NotSupportedError` by dynamically saving audio and updating frontend references

### 2. Enhance Input Parsing
- Use regex or spaCy to improve name and phone extraction
- Validate UAE numbers and confirm them in conversation

### 3. Add Fallback & Escalation
- Build `handle_fallback()` logic with polite retries
- Count failures and suggest transferring to human if needed

### 4. Integrate NLU Intent System
- Replace `if/elif` chains with intent detection (`book_appointment`, `faq`, etc.)
- Start with rule-based, then upgrade to LLM-powered detection

### 5. Replace Prompts with GPT-4 Logic
- Use LLM to generate replies with context: tone, filler, emotional reaction
- Build prompt system using modular config or YAML/JSON

### 6. Add Memory System (Session)
- Store: user name, last intent, current step, appointment state
- Use local memory object or LangChain-style wrapper

### 7. Add Action Tool Layer (APIs)
- Booking: Google Sheets, Calendars, SMS, etc.
- Wrap each function with error handling + logging

### 8. Voice Interaction Enhancements
- Whisper STT for real-time speech input
- ElevenLabs TTS with SSML (pauses, pitch, warmth)
- Enable interruption detection via `was_interrupted` flag

### 9. Testing & Logs
- Expand `run_tests.py` to simulate user flows (booking, fallback, joke)
- Log full transcripts + response timing for QA/debug

### 10. Final UX Polish
- Tone check for "Emirati-friendly" and international English
- Show frontend speech state: Listening / Thinking / Speaking

---

## 🚀 Optional Enhancements (Post-MVP)

- 📲 Add WhatsApp/SMS fallback via Twilio
- 📁 Save transcripts to Notion/Google Drive
- 🧾 Auto-generate invoices (Stripe API)
- 📊 Create web dashboard for Rachel's usage, logs, analytics

---

## 💬 Agent Identity: Rachel (Prompt Reference)

"You are Rachel, a kind, professional, and intelligent voice receptionist for a clinic. You help customers schedule appointments, answer questions, and guide them smoothly. Always sound warm, helpful, and human — like a real staff member."

---

## ⚠️ Codex: Your Task

> Read this file. Use it as your master instruction list. Start with Step 1 and proceed through all tasks. Reference `PROJECT_BACKGROUND_DETAILS.md` only if extra context is needed.
