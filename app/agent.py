# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Hardcode project ID as a string so it does not resolve to the project number on Agent Platform
PROJECT_ID = "qwiklabs-gcp-03-f7013f64434f"
MODEL = "gemini-2.5-flash"

def _get_db() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)

def list_plants() -> List[Dict[str, Any]]:
    """List all Brazilian Spinach semi-hydro plants and their current reservoir statuses.

    Returns:
        A list of dictionaries with plant details, EC/pH parameters, and reservoir status.
    """
    db = _get_db()
    docs = db.collection("semi_hydro_plants").stream()
    plants = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        plants.append(data)
    return plants

def get_plant_details(plant_id: str) -> Dict[str, Any]:
    """Retrieve detailed monitoring and care history for a specific semi-hydro plant setup.

    Args:
        plant_id: The document ID of the plant setup (e.g., 'spinach-planter-01').

    Returns:
        A dictionary with the plant's full specs, target vs current EC/pH, and notes.
    """
    db = _get_db()
    doc_ref = db.collection("semi_hydro_plants").document(plant_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Plant with ID '{plant_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data

def record_reservoir_update(
    plant_id: str,
    current_ec: Optional[float] = None,
    current_ph: Optional[float] = None,
    reservoir_status: Optional[str] = None,
    notes: Optional[str] = None,
    refilled_now: bool = False,
    flushed_now: bool = False,
) -> Dict[str, Any]:
    """Record a reservoir check, refill, or water flush for a Brazilian Spinach semi-hydro system.

    Args:
        plant_id: The document ID of the plant setup (e.g., 'spinach-planter-01').
        current_ec: Measured electrical conductivity (EC in mS/cm, typically 1.2 - 1.8).
        current_ph: Measured pH level (typically 5.5 - 6.5).
        reservoir_status: One of 'adequate', 'low', 'needs_refill', 'flushed'.
        notes: Care observations, trimming notes, or deficiency diagnoses.
        refilled_now: Set to True if nutrient solution was topped off/refilled today.
        flushed_now: Set to True if LECA/media and reservoir were completely flushed today.

    Returns:
        A dictionary confirming the updated values.
    """
    db = _get_db()
    doc_ref = db.collection("semi_hydro_plants").document(plant_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Plant with ID '{plant_id}' not found."}

    updates: Dict[str, Any] = {}
    if current_ec is not None:
        updates["current_ec"] = float(current_ec)
    if current_ph is not None:
        updates["current_ph"] = float(current_ph)
    if reservoir_status is not None:
        updates["reservoir_status"] = reservoir_status
    if notes is not None:
        updates["notes"] = notes

    today_str = datetime.date.today().isoformat()
    if refilled_now:
        updates["last_refill_date"] = today_str
        if reservoir_status is None:
            updates["reservoir_status"] = "adequate"
    if flushed_now:
        updates["last_flush_date"] = today_str

    if updates:
        doc_ref.update(updates)

    updated_doc = doc_ref.get().to_dict()
    updated_doc["id"] = plant_id
    return {"status": "success", "updated": updated_doc}

def add_new_plant(
    plant_id: str,
    name: str,
    substrate: str = "LECA",
    system_type: str = "Passive Wicking Pot",
    reservoir_volume_liters: float = 1.5,
    target_ec: float = 1.4,
    target_ph: float = 6.0,
    light_exposure: str = "Bright indirect window",
    notes: str = "",
) -> Dict[str, Any]:
    """Add a new Brazilian Spinach semi-hydro plant setup to the Firestore database.

    Args:
        plant_id: Unique slug identifier for the plant (e.g., 'spinach-kitchen-04').
        name: Display name for the plant setup.
        substrate: Growing medium (e.g., 'LECA', 'Pumice', 'Pon').
        system_type: Hydroponic style (e.g., 'Passive Wicking Pot', 'Kratky', 'Net Pot Reservoir').
        reservoir_volume_liters: Capacity of the water reservoir in liters.
        target_ec: Target EC level (optimal: 1.2 to 1.8).
        target_ph: Target pH level (optimal: 5.5 to 6.5).
        light_exposure: Lighting conditions (e.g., 'Bright indirect', 'Grow light 14h').
        notes: Initial setup observations.

    Returns:
        A dictionary with the created plant record.
    """
    db = _get_db()
    today_str = datetime.date.today().isoformat()
    data = {
        "id": plant_id,
        "name": name,
        "variety": "Brazilian Spinach (Alternanthera sissoo)",
        "substrate": substrate,
        "system_type": system_type,
        "reservoir_volume_liters": float(reservoir_volume_liters),
        "target_ec": float(target_ec),
        "target_ph": float(target_ph),
        "current_ec": float(target_ec),
        "current_ph": float(target_ph),
        "reservoir_status": "adequate",
        "last_refill_date": today_str,
        "last_flush_date": today_str,
        "light_exposure": light_exposure,
        "stage": "Vegetative Growth",
        "notes": notes,
    }
    db.collection("semi_hydro_plants").document(plant_id).set(data)
    return {"status": "success", "created": data}


def calculate_nutrient_dosing(
    target_volume_liters: float,
    target_ec: float = 1.4,
    current_ec: float = 0.0,
    current_volume_liters: float = 0.0,
    base_water_ec: float = 0.2,
    ec_per_ml_per_liter: float = 0.4,
) -> Dict[str, Any]:
    """Calculate the precise hydroponic nutrient dosage and dilution needed for Brazilian Spinach.

    Standard semi-hydro stock nutrients (e.g., standard 2-part A/B or balanced vegetative hydroponic feed)
    typically raise EC by approximately 0.4 mS/cm per 1 mL of stock solution per 1 Liter of water.

    Args:
        target_volume_liters: The full desired volume of solution in liters.
        target_ec: Desired final electrical conductivity in mS/cm (optimal for Brazilian Spinach: 1.2 to 1.8).
        current_ec: Current EC of leftover reservoir water (if topping off existing water).
        current_volume_liters: Current volume of leftover water in the reservoir in liters.
        base_water_ec: Baseline EC of fresh tap or filtered water before nutrients (default ~0.2 mS/cm).
        ec_per_ml_per_liter: Rate of EC rise per mL of stock per Liter (default 0.4 mS/cm).

    Returns:
        A dictionary with water to add (L), required stock nutrients (mL per part), and mixing instructions.
    """
    if target_volume_liters <= 0:
        return {"error": "Target volume must be greater than 0 liters."}

    water_to_add_liters = max(0.0, target_volume_liters - current_volume_liters)

    # Total EC units needed across the full target volume
    total_target_ec_units = target_volume_liters * target_ec
    current_ec_units = current_volume_liters * current_ec
    base_water_ec_units = water_to_add_liters * base_water_ec

    # Additional EC increase needed from concentrated nutrients
    needed_ec_units = total_target_ec_units - current_ec_units - base_water_ec_units

    if needed_ec_units <= 0:
        # Over-concentrated; needs plain water dilution
        dilution_water_needed = 0.0
        if target_ec > base_water_ec:
            dilution_water_needed = max(
                0.0,
                (current_volume_liters * (current_ec - target_ec)) / (target_ec - base_water_ec)
            )
        return {
            "mode": "dilution_only",
            "message": "Current EC is already higher than or equal to target EC. Do not add nutrients.",
            "current_ec": current_ec,
            "target_ec": target_ec,
            "plain_water_to_add_liters": round(dilution_water_needed, 2),
            "nutrient_stock_ml": 0.0,
            "instructions": f"Add approximately {round(dilution_water_needed, 2)} L of plain fresh water to dilute the reservoir to {target_ec} mS/cm."
        }

    # Nutrient mL needed = needed_ec_units / ec_per_ml_per_liter
    nutrient_stock_ml = needed_ec_units / ec_per_ml_per_liter
    part_a_ml = round(nutrient_stock_ml, 1)
    part_b_ml = round(nutrient_stock_ml, 1)

    return {
        "mode": "nutrient_addition",
        "target_volume_liters": round(target_volume_liters, 2),
        "water_to_add_liters": round(water_to_add_liters, 2),
        "target_ec": round(target_ec, 2),
        "nutrient_solution_ml_part_a": part_a_ml,
        "nutrient_solution_ml_part_b": part_b_ml,
        "recommended_ph_range": "5.5 - 6.5",
        "instructions": (
            f"1. Measure out {round(water_to_add_liters, 2)} L of fresh water.\n"
            f"2. Add {part_a_ml} mL of Part A nutrient stock and stir thoroughly.\n"
            f"3. Add {part_b_ml} mL of Part B nutrient stock and stir thoroughly.\n"
            f"4. Verify final EC reaches ~{round(target_ec, 2)} mS/cm.\n"
            f"5. Check and adjust pH with pH Down/Up to sit between 5.5 and 6.5 before pouring into the LECA reservoir."
        ),
    }


from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool


async def generate_memories_callback(callback_context: CallbackContext):
    """Write callback: send the completed turn/session to Memory Bank for extraction."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        import logging
        logging.warning("Memory service not available or failed: %s", e)
    return None


import json
import os
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

def _get_code_executor() -> AgentEngineSandboxCodeExecutor:
    metadata_file = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
    agent_engine_id = None
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r") as f:
                meta = json.load(f)
                val = meta.get("remote_agent_runtime_id")
                if val and val != "None":
                    agent_engine_id = val
        except Exception:
            pass
    return AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_id)


from app.a2ui_prompt_static import SYSTEM_INSTRUCTION as a2ui_instruction
from app.a2ui_utils import a2ui_callback


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        list_plants,
        get_plant_details,
        record_reservoir_update,
        add_new_plant,
        calculate_nutrient_dosing,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    code_executor=_get_code_executor(),
)

app = App(
    root_agent=root_agent,
    name="app",
)
