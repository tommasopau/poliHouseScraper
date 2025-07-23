"""
Simple LLM parser for extracting rental data using Mistral API.
"""
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
from mistralai import Mistral


from app.core.config import settings
from app.db.models import TelegramMessageData


class SimpleMistralParser:
    """
    Simple LLM parser using Mistral free tier to extract rental data.
    """

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.client = Mistral(api_key=self.api_key)
        self.model = "pixtral-12b-2409"

    async def parse_message(self, message: TelegramMessageData) -> Dict[str, Any]:
        """
        Parse rental message and extract key information.

        Args:
            message: Dictionary containing Telegram message data

        Returns:
            Dict with extracted rental data
        """
        try:

            prompt = f"""
Estrai informazioni da questo messaggio di affitto italiano. Rispondi solo con JSON valido.

Messaggio: "{message.text}"

Estrai questi campi (usa null se non trovato). Se ci sono delle alternative, scegli la più probabile:
{{
    "price": prezzo_mensile_in_euro_come_numero,
    "location": "via se esplicitamente presente, altrimenti zona (Leonardo|Città Studi|Bovisa) se menzionata",
    "property_type": "camera_singola|camera_doppia|appartamento|monolocale",
    "telephone": "numero_telefono_se_trovato",
    "email": "email_se_trovata",
    "tenant_preference": "scegli solo uno tra (ragazzo' |'ragazza' |'indifferente') ,mai più di uno, mai combinazioni, mai separatori come virgole o slash",
    "available_start": "YY-MM-DD_se_trovato",
    "available_end": "YY-MM-DD_se_trovato",
    "num_bedrooms": numero_camere_da_letto,
    "num_bathrooms": numero_bagni,
    "flatmates_count": numero_coinquilini_attuali,
    "summary": "breve sunto delle caratteristiche aggiuntive della casa (es: arredamento, servizi, trasporti, spese incluse, condizioni speciali, etc.)",
    "has_extra_expenses": "true se ci sono spese extra oltre al prezzo principale, altrimenti false",
    "extra_expenses_details": "descrizione delle spese extra se presenti, altrimenti null"
}}

Per il campo location, estrai la via se è esplicitamente presente nel testo. Se non c'è una via, usa la zona (Leonardo, Città Studi, Bovisa) se viene menzionata. Se non trovi né via né zona, imposta a null.

Per il campo summary, includi solo le informazioni extra non coperte dagli altri campi, come:
- Stato dell'arredamento (arredato/non arredato)
- Servizi inclusi (wifi, pulizie, utenze)
- Vicinanza a trasporti pubblici
- Caratteristiche speciali dell'immobile
- Condizioni particolari del contratto
- Spese aggiuntive o incluse

Se non ci sono informazioni aggiuntive, imposta summary a "Nessuna informazione aggiuntiva".

Rispondi solo con JSON valido, senza testo aggiuntivo o markdown.
JSON:
"""
            user_message = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            # Call Mistral API using official client
            chat_response = await self.client.chat.complete_async(
                model=self.model,
                messages=user_message,
                response_format={
                    "type": "json_object",
                }
            )

            # Parse response
            response_content = chat_response.choices[0].message.content
            # parsing may be not needed if response is already JSON
            data = self._parse_response(response_content)

            # Add metadata
            data["message_id"] = message.id
            data["sender_id"] = message.sender_id
            data["sender_username"] = message.sender_username
            data["date"] = message.date
            data["raw_text"] = message.text
            data["has_media"] = message.has_media

            return data

        except Exception as e:
            return {
                "raw_text": message.text,
                "error": str(e)
            }

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to JSON."""
        try:
            # Clean response
            cleaned = response.strip()
            if "```" in cleaned:
                # Extract JSON from markdown
                start = cleaned.find("{")
                end = cleaned.rfind("}") + 1
                cleaned = cleaned[start:end]

            return json.loads(cleaned)

        except json.JSONDecodeError:
            # Return empty dict if parsing fails
            return {}

    async def batch_parse(self, messages: list[str], delay: float = 2.0) -> list[Dict[str, Any]]:
        """
        Parse multiple messages with delay for rate limiting.

        Args:
            messages: List of message texts
            delay: Seconds to wait between API calls

        Returns:
            List of parsed data dictionaries
        """
        results = []

        for i, message in enumerate(messages):
            if i > 0:
                await asyncio.sleep(delay)

            result = await self.parse_message(message)
            results.append(result)
            print(f"Processed {i+1}/{len(messages)}")

        return results
