import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-f7013f64434f"

def seed():
    db = firestore.Client(project=PROJECT_ID)
    plants_ref = db.collection("semi_hydro_plants")

    seeds = [
        {
            "id": "spinach-planter-01",
            "name": "Kitchen Window Brazilian Spinach",
            "variety": "Brazilian Spinach (Alternanthera sissoo)",
            "substrate": "LECA",
            "system_type": "Passive Wicking Pot",
            "reservoir_volume_liters": 1.5,
            "target_ec": 1.4,
            "target_ph": 6.0,
            "current_ec": 1.35,
            "current_ph": 6.2,
            "reservoir_status": "adequate",
            "last_refill_date": "2026-10-18",
            "last_flush_date": "2026-10-04",
            "light_exposure": "Bright indirect window (12 hrs)",
            "stage": "Vegetative Growth",
            "notes": "Fast leafing, ready for light trimming in 1 week.",
        },
        {
            "id": "spinach-cutting-02",
            "name": "Desk Prop Nursery Cup",
            "variety": "Brazilian Spinach (Alternanthera sissoo)",
            "substrate": "Pumice + Perlite",
            "system_type": "Net pot reservoir",
            "reservoir_volume_liters": 0.5,
            "target_ec": 1.0,
            "target_ph": 5.8,
            "current_ec": 1.0,
            "current_ph": 5.9,
            "reservoir_status": "needs_refill",
            "last_refill_date": "2026-10-14",
            "last_flush_date": "2026-10-10",
            "light_exposure": "Grow light (14 hrs)",
            "stage": "Rooting / Early Vegetative",
            "notes": "Secondary water roots actively emerging through basket.",
        },
        {
            "id": "spinach-balcony-03",
            "name": "Balcony Tote Hydro Unit",
            "variety": "Brazilian Spinach (Alternanthera sissoo)",
            "substrate": "LECA",
            "system_type": "Kratky / Passive Semi-Hydro Tub",
            "reservoir_volume_liters": 5.0,
            "target_ec": 1.6,
            "target_ph": 6.2,
            "current_ec": 1.7,
            "current_ph": 6.4,
            "reservoir_status": "adequate",
            "last_refill_date": "2026-10-19",
            "last_flush_date": "2026-09-28",
            "light_exposure": "Partial outdoor sun",
            "stage": "Mature Harvest Stage",
            "notes": "High yield harvest. Needs complete water flush and fresh nutrient solution next week.",
        }
    ]

    for item in seeds:
        doc_id = item["id"]
        plants_ref.document(doc_id).set(item)
        print(f"Seeded plant doc: {doc_id}")

    print("Seeding complete!")

if __name__ == "__main__":
    seed()
