from app.models.product.product_model import CreateProduct,UpdateProduct,AssignedProductToUser
from app.core.security.auth import get_current_user,access_control_auth
from fastapi import APIRouter,HTTPException,Request,Response,Depends,Query
from fastapi.responses import JSONResponse
from app.core.db.db_connection import get_db

router = APIRouter(prefix="/products",tags=['Products'])

@router.get("/")
@access_control_auth("normal")
async def fetch_products(db=Depends(get_db),current_user:dict=Depends(get_current_user)):
    products = await db.products.find({},{"_id":0}).to_list()
    if len(products) == 0:
        raise HTTPException(status_code=409,detail="No products found")
    return JSONResponse(status_code=200,content={"products": products})

@router.get("/current")
@access_control_auth("normal")
async def fetch_product(db=Depends(get_db),current_user:dict=Depends(get_current_user),product_id: str = Query(None, description="Product ID to fetch specific product")):
    product = await db.products.find_one({'product_id':product_id},{"_id":0})
    if len(product) == 0:
        raise HTTPException(status_code=409,detail="No product found")
    return JSONResponse(status_code=200,content={"products": product})


@router.post("/")
@access_control_auth("normal")
async def create_products(db=Depends(get_db),current_user:dict=Depends(get_current_user),product:CreateProduct=...):
    product=product.dict()
    if await db.products.find_one({'product_name':product['product_name'],"product_category":product['product_category']}):
        raise HTTPException(status_code=409,detail=f"Product with name '{product['product_name']}' already exists in this category")
    result = await db.products.insert_one(product)
    if not result.inserted_id:
        raise HTTPException(status_code=409,detail="Product is not created")
    return JSONResponse(status_code=201,content={ "msg": "Product created successfully!", "inserted_id": str(result.inserted_id)})
