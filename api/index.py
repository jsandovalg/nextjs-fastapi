from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 

from PIL import Image, PngImagePlugin
import base64
import json
from io import BytesIO
import random
from pydantic import BaseModel
from typing import Dict

class ImageData(BaseModel):
    image_b64: str
    user_comment: Dict 

app = FastAPI(
  docs_url="/api/images/docs", 
  redoc_url="/api/images/redoc", 
  openapi_url="/api/images/openapi.json"
)

# cors stuff
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/api/images/healthchecker")
def healthchecker():
    return {
      "status": "success", 
      "message": "Integrate FastAPI Framework with Next.js"
    }

@app.post('/api/images/update_metadata')
async def update_metadata(data: ImageData):
    try:
        new_image_b64 = update_png_metadata(data.image_b64, data.user_comment)
        return {"updated_image": new_image_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Function
def update_png_metadata(image_b64, user_comment):
    # Decode the base64 image
    image_data = base64.b64decode(image_b64)
    image = Image.open(BytesIO(image_data))

    # Ensure the image is in PNG format
    if image.format != 'PNG':
        raise ValueError("The provided image is not a PNG")

	# Convert dictionary to JSON string
    user_comment_str = json.dumps(user_comment)

    # Create a new metadata dictionary
    meta = PngImagePlugin.PngInfo()

    # Adding or updating the custom metadata. This uses the 'tEXt' chunk for textual data.
    meta.add_text("UserComment", user_comment_str)

    # Save the modified image to a bytes buffer with the updated metadata
    output_buffer = BytesIO()
    image.save(output_buffer, format="PNG", pnginfo=meta)
    output_buffer.seek(0)  # Move to the beginning of the buffer

    # Return the modified image as base64
    return base64.b64encode(output_buffer.getvalue()).decode('utf-8')
