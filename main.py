from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from cloudinary_setup import cloudinary
from database import orders_collection
from typing import Optional
# from mangum import Mangum  # เผื่อ deploy vercel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# 📌 Upload Image to Cloudinary
# ----------------------------------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    result = cloudinary.uploader.upload(file.file)
    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id")
    }

# ----------------------------------------
# 📌 CREATE ORDER (POST)
# ----------------------------------------
@app.post("/orders")
async def create_order(
    name: Optional[str] = Form(None),
    product: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    amount: Optional[int] = Form(None),
    image_url: Optional[str] = Form(None),
    tracking_number: Optional[str] = Form(None),
    status: Optional[str] = Form(None)
):
    order = {
        "name": name or "",
        "product": product or "",
        "address": address or "",
        "phone": phone or "",
        "amount": amount or 0,
        "image_url": image_url or "",
        "tracking_number": tracking_number or "",
        "status": status or ""
    }

    result = orders_collection.insert_one(order)
    return {
        "message": "created",
        "id": str(result.inserted_id)
    }

# ----------------------------------------
# 📌 GET ALL ORDERS
# ----------------------------------------
@app.get("/orders")
async def get_orders():
    orders = []
    for item in orders_collection.find():
        item["_id"] = str(item["_id"])
        orders.append(item)
    return orders

# ----------------------------------------
# 📌 GET ORDER BY ID
# ----------------------------------------
@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    try:
        obj_id = ObjectId(order_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    order = orders_collection.find_one({"_id": obj_id})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order["_id"] = str(order["_id"])
    return order

# ----------------------------------------
# 📌 UPDATE ORDER (PUT)
# ----------------------------------------
@app.put("/orders/{order_id}")
async def update_order(
    order_id: str,
    name: str = Form(None),
    product: str = Form(None),   # ✅ เพิ่ม
    address: str = Form(None),
    phone: str = Form(None),
    amount: int = Form(None),
    image_url: str = Form(None),
    tracking_number: str = Form(None),
    status: str = Form(None)
):
    try:
        obj_id = ObjectId(order_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    update_data = {
        k: v for k, v in {
            "name": name,
            "product": product,   # ✅ เพิ่ม
            "address": address,
            "phone": phone,
            "amount": amount,
            "image_url": image_url,
            "tracking_number": tracking_number,
            "status": status
        }.items() if v is not None
    }

    result = orders_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "updated"}

# ----------------------------------------
# 📌 DELETE ORDER
# ----------------------------------------
@app.delete("/orders/{order_id}")
async def delete_order(order_id: str):
    try:
        obj_id = ObjectId(order_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    result = orders_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "deleted"}

# For Vercel
# handler = Mangum(app)
