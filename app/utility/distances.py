import asyncio
import httpx
from typing import List, Dict, Any
from app.core.config import settings

API_KEY = settings.DISTANCE_MATRIX_API_KEY
BASE_URL = settings.DISTANCE_URL
RATE_LIMIT_SLEEP = 1.1

LEONARDO = "Politecnico di Milano, Leonardo"
BOVISA = "Politecnico di Milano, Bovisa"


def ensure_milano(address: str) -> str:
    address = address.strip()
    if not address.lower().endswith(", milano"):
        address += ", Milano"
    return address


async def get_duration_matrix_async(
    origins: List[str], destinations: List[str], mode: str
) -> Dict[str, Any]:
    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "mode": mode,
        "key": API_KEY,
    }
    if mode == "transit":
        params["transit_mode"] = "bus|train|tram|subway"
    async with httpx.AsyncClient() as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "OK":
            raise RuntimeError(f"Matrix API error: {data.get('status')}")
        return data


async def add_durations(
    apartments: List[dict], batch_size=20
):
    """
    For each apartment, append duration (in seconds) to Leonardo and Bovisa
    for both 'transit' and 'walking' modes. Modifies the dicts in-place.
    """
    destinations = [LEONARDO, BOVISA]
    addresses = []
    idx_map = []
    for i, apt in enumerate(apartments):
        address = apt.get("location")
        if not address:
            continue
        address = ensure_milano(address)
        apartments[i]["location"] = address
        addresses.append(address)
        idx_map.append(i)

    modes = ["transit", "walking"]
    for start in range(0, len(addresses), batch_size):
        batch = addresses[start:start+batch_size]
        tasks = [
            get_duration_matrix_async(batch, destinations, mode=mode)
            for mode in modes
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for mode_idx, matrix in enumerate(results):
            mode = modes[mode_idx]
            if isinstance(matrix, Exception):
                for i in range(len(batch)):
                    apt_idx = idx_map[start + i]
                    apartments[apt_idx][f"duration_to_leonardo_{mode}"] = None
                    apartments[apt_idx][f"duration_to_bovisa_{mode}"] = None

                continue
            for i, row in enumerate(matrix["rows"]):
                apt_idx = idx_map[start + i]
                elements = row["elements"]
                # Leonardo
                if elements[0]["status"] == "OK":
                    apartments[apt_idx][f"duration_to_leonardo_{mode}"] = elements[0]["duration"]["value"] / 60
                else:
                    apartments[apt_idx][f"duration_to_leonardo_{mode}"] = None
                # Bovisa
                if elements[1]["status"] == "OK":
                    apartments[apt_idx][f"duration_to_bovisa_{mode}"] = elements[1]["duration"]["value"] / 60
                else:
                    apartments[apt_idx][f"duration_to_bovisa_{mode}"] = None
        await asyncio.sleep(RATE_LIMIT_SLEEP)
