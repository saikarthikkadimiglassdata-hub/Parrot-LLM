# llm_client.py

import os
import json
import logging
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv
from prompts import LIVE_ADVICE_SYSTEM_PROMPT, SESSION_SUMMARY_SYSTEM_PROMPT

# Load env variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ParrotLLMClient")

class ParrotLLMClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY environment variable is not set!")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        # Default model recommended for general text + speed
        self.model = "llama-3.1-8b-instant"

    def get_live_advice(self, telemetry: Dict[str, Any], transcript: str, session_duration: int) -> Dict[str, Any]:
        """
        Sends real-time telemetry and transcript to Groq LLM to get clinical suggestions.
        """
        if not self.client:
            return {
                "advice": "[LLM Offline] Please configure GROQ_API_KEY on the LLM server.",
                "suggested_questions": ["Please check server configuration."],
                "urgency": "normal"
            }

        # Truncate transcript to last 1000 characters to prevent burning through rate limits
        truncated_transcript = transcript[-1000:] if transcript else ""
        
        user_content = json.dumps({
            "telemetry": telemetry,
            "recent_transcript": truncated_transcript,
            "session_duration_seconds": session_duration
        }, indent=2)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": LIVE_ADVICE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1024,
            )
            response_text = chat_completion.choices[0].message.content
            logger.info(f"Groq raw advice response: {response_text}")
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error calling Groq API for advice: {e}")
            return {
                "advice": "Failed to retrieve live advice from AI assistant.",
                "suggested_questions": [
                    "How are you feeling right now?",
                    "Have you experienced any changes in your symptoms?"
                ],
                "urgency": "normal"
            }

    def get_session_summary(self, session_duration: int, transcript: str, observations: list, telemetry_summary: Dict[str, Any], pve_clinical_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates clinical post-session documentation.
        """
        if not self.client:
            return {
                "clinical_summary": "[LLM Offline] Please configure GROQ_API_KEY on the LLM server.",
                "key_findings": ["LLM API key missing."],
                "risk_flags": ["Server misconfigured."],
                "recommendations": ["Add GROQ_API_KEY to the Parrot-LLM .env file."]
            }

        # Truncate transcript to last 4000 chars for summary to avoid context limits
        truncated_transcript = transcript[-4000:] if transcript else ""

        user_content = json.dumps({
            "session_duration_seconds": session_duration,
            "transcript": truncated_transcript,
            "observations_count": len(observations) if observations else 0,
            "telemetry_summary": telemetry_summary,
            "pve_clinical_analysis": pve_clinical_analysis
        }, indent=2)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SESSION_SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2048,
            )
            response_text = chat_completion.choices[0].message.content
            logger.info(f"Groq raw summary response: {response_text}")
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error calling Groq API for summary: {e}")
            return {
                "clinical_summary": "Failed to generate session summary due to server error.",
                "key_findings": ["Error details: " + str(e)],
                "risk_flags": [],
                "recommendations": ["Please retry or document manually."]
            }
