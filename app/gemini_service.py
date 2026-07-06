import google.generativeai as genai
from fastapi import HTTPException
import os
import json
import re
from app.schemas import ToneEnum

# Configure Gemini once at import time
_API_KEY = os.getenv("GEMINI_API_KEY", "")
if _API_KEY:
    genai.configure(api_key=_API_KEY)

MODEL_NAME = "gemini-1.5-flash"

_TONE_DESC = {
    ToneEnum.formal:        "very formal, structured, and respectful",
    ToneEnum.professional:  "professional, polished, and clear",
    ToneEnum.friendly:      "warm and friendly while remaining appropriate for work",
    ToneEnum.concise:       "extremely concise — say only what is necessary, no filler",
}


def _get_model() -> genai.GenerativeModel:
    if not _API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable is not set."
        )
    return genai.GenerativeModel(MODEL_NAME)


def _generate(prompt: str, system: str = "") -> str:
    model = _get_model()
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")


# ── Feature functions ────────────────────────────────────────────

def compose_email(purpose: str, recipient: str | None,
                  context: str | None, tone: ToneEnum) -> str:
    tone_str = _TONE_DESC[tone]
    parts = [f'Write a {tone_str} email for the following purpose: "{purpose}"']
    if recipient:
        parts.append(f"The recipient is: {recipient}.")
    if context:
        parts.append(f"Additional context: {context}.")
    parts.append(
        "Format your response as:\n"
        "Subject: <subject line>\n\n"
        "<email body>\n\n"
        "Make it complete and ready to send."
    )
    system = (
        "You are an expert professional email writer. "
        "Write clear, well-structured emails that match the requested tone exactly. "
        "Always include a Subject line as the very first line."
    )
    return _generate(" ".join(parts), system)


def generate_reply(email: str, instruction: str | None) -> str:
    prompt = f"Write a professional reply to the following email:\n\n{email}"
    if instruction:
        prompt += f"\n\nAdditional instructions: {instruction}"
    prompt += (
        "\n\nFormat your response as:\n"
        "Subject: Re: <original subject if identifiable>\n\n"
        "<reply body>"
    )
    system = (
        "You are a professional email writing assistant. "
        "Write natural, polished replies that address every point in the received email. "
        "Match the formality of the original email unless instructed otherwise."
    )
    return _generate(prompt, system)


def convert_tone(email: str, target_tone: ToneEnum) -> str:
    tone_str = _TONE_DESC[target_tone]
    prompt = (
        f"Rewrite the following email to be {tone_str}. "
        "Preserve the core message and all key information. "
        "Do not add new information.\n\n"
        f"Original email:\n{email}"
    )
    system = (
        "You are an expert at adjusting email tone. "
        "Rewrite emails precisely to match the requested tone without changing the meaning."
    )
    return _generate(prompt, system)


def summarize_thread(thread: str) -> dict:
    prompt = (
        "Analyze the following email thread and respond ONLY with a valid JSON object "
        "(no markdown fences, no extra text) in exactly this format:\n"
        '{"key_points": ["...", "..."], "action_items": ["...", "..."], "deadlines": ["...", "..."]}\n\n'
        "Rules:\n"
        "- key_points: 3–6 main topics or decisions discussed\n"
        "- action_items: specific tasks someone must do (empty array [] if none)\n"
        "- deadlines: any dates or time-sensitive mentions (empty array [] if none)\n\n"
        f"Email thread:\n{thread}"
    )
    system = (
        "You are an email summarizer. "
        "Always respond with valid JSON only. Never include markdown, backticks, or explanations."
    )
    raw = _generate(prompt, system)

    # Strip any accidental markdown fences
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail=f"Could not parse AI summary response. Raw: {raw[:200]}"
        )
