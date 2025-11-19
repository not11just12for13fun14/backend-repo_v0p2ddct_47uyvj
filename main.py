import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from database import create_document, get_documents, db

app = FastAPI(title="Merch Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models (request/response)
class Design(BaseModel):
    title: str = Field(..., description="Design name")
    description: Optional[str] = Field(None, description="Short description")
    image_url: HttpUrl = Field(..., description="Preview mockup image URL")
    marketplace_url: Optional[HttpUrl] = Field(None, description="Link to Merch by Amazon listing or store")
    tags: List[str] = Field(default_factory=list, description="Keywords/tags")
    colors: List[str] = Field(default_factory=list, description="Available shirt colors (hex or names)")
    price: Optional[float] = Field(None, ge=0)


class ContactMessage(BaseModel):
    name: str
    email: str
    message: str


@app.get("/")
def read_root():
    return {"message": "Merch Portfolio API running"}


@app.get("/api/designs")
def list_designs(limit: Optional[int] = 50):
    try:
        items = get_documents("design", {}, limit or 50)
        # Convert ObjectId and datetime to strings for JSON
        for it in items:
            it["_id"] = str(it.get("_id"))
            for k, v in list(it.items()):
                if hasattr(v, "isoformat"):
                    it[k] = v.isoformat()
        return {"items": items}
    except Exception as e:
        # If DB not configured, return an empty list gracefully
        return {"items": []}


@app.post("/api/contact")
def create_contact(msg: ContactMessage):
    try:
        _id = create_document("contactmessage", msg)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
