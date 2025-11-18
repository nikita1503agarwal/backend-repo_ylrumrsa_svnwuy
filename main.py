import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Perfume

app = FastAPI(title="Elanor Luxury Perfume API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"brand": "Elanor", "message": "Backend ready"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# ---- Perfume endpoints ----
class SeedStatus(BaseModel):
    seeded: bool
    count: int


SEED_DATA: List[Perfume] = [
    Perfume(
        slug="wrath",
        name="Wrath",
        sin="Wrath",
        color="#7a0a12",
        price=280.0,
        short="Dark leather. Smoked oud. Commanding heat.",
        story_nature=(
            "Not rage. Not anger. Wrath is clarity. It refuses mediocrity and burns through pretense."
        ),
        story_interpretation=(
            "Dark leather, smoked oud, black pepper. Frankincense rising like smoke from an ancient pyre."
        ),
        story_who=(
            "CEOs who refuse to compromise. Artists who burn what is unworthy. Lovers who demand all."
        ),
        story_ritual=(
            "Spray once at the base of the throat. Let it settle. Wrath is not reapplied—it endures."
        ),
        notes_top=["Black Pepper", "Bergamot"],
        notes_heart=["Leather", "Saffron"],
        notes_base=["Smoked Oud", "Frankincense", "Amber"],
        symbol="skull",
    ),
    Perfume(
        slug="envy",
        name="Envy",
        sin="Envy",
        color="#065f46",
        price=260.0,
        short="Green bite. Cut florals. Quiet hunger.",
        story_nature=(
            "A serpent thought. A gaze that lingers. Envy is the ache toward what gleams across the room."
        ),
        story_interpretation=(
            "Galbanum, crushed leaves, cold iris. Vetiver roots winding through damp earth."
        ),
        story_who=(
            "Collectors who prefer whispers to shouts. Strategists who play the long game."
        ),
        story_ritual=(
            "Mist once behind each ear. Let the green hum meet your pulse."
        ),
        notes_top=["Galbanum", "Crushed Leaves"],
        notes_heart=["Iris", "Green Rose"],
        notes_base=["Vetiver", "Oakmoss"],
        symbol="serpent",
    ),
]


@app.get("/api/perfumes")
async def list_perfumes(limit: Optional[int] = None):
    try:
        if db is None:
            # Return seed data if DB not configured
            items = [p.model_dump() for p in SEED_DATA]
            return items[:limit] if limit else items
        docs = get_documents("perfume", {}, limit)
        if not docs:
            # fallback to seed if collection empty
            return [p.model_dump() for p in SEED_DATA]
        # convert ObjectId to string safely
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/perfumes/seed", response_model=SeedStatus)
async def seed_perfumes():
    try:
        if db is None:
            return SeedStatus(seeded=False, count=len(SEED_DATA))
        existing = db["perfume"].count_documents({})
        if existing > 0:
            return SeedStatus(seeded=False, count=existing)
        for p in SEED_DATA:
            create_document("perfume", p)
        count = db["perfume"].count_documents({})
        return SeedStatus(seeded=True, count=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
