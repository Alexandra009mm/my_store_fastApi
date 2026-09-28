from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, select 

# Importamos solo lo necesario de Pydantic sin chocar con SQLModel
from pydantic import BaseModel

from src.models.product_model import Poduct, ProductCreate
from src.shared.session_db import get_session, SessionDep

app = FastAPI()

# Aquí va a ejecutarse el código cuando se inicie la aplicación
@app.on_event("startup")
def on_startup():
    print('Hello, starting up the application') # Es mejor un print en consola para startup


@app.get('/products') 
def get_products(session: SessionDep):
    """
    ESPAÑOL: Obtiene todos los productos de la base de datos.
    Returns: lista de todos los productos disponibles.
    Raises: HTTPException 404 si no hay productos.
    
    ENGLISH: Retrieves all products from the database.
    Returns: list of all available products.
    Raises: HTTPException 404 if there are no products.
    """
    products = session.exec(select(Poduct)).all()
    if not products:
        raise HTTPException(status_code=404, detail="data not found or empty")
    return products
 
 


@app.post('/products')
def create_product(product: ProductCreate | list[ProductCreate], session: SessionDep):
    """
    ESPAÑOL: Crea uno o múltiples productos. Convierte nombre/categoria a minusculas.
    No permite duplicados. Precio > 0, Stock >= 0. Devuelve el/los producto(s) con ID.
    Acepta un objeto o una lista de objetos.
    
    ENGLISH: Creates one or multiple products. Converts name/category to lowercase.
    No duplicates allowed. Price > 0, Stock >= 0. Returns product(s) with ID.
    Accepts a single object or a list of objects.
    """
    # Si es una lista, procesarla
    if isinstance(product, list):
        created_products = []
        
        # Validar todos antes de crear ninguno
        for prod in product:
            name_lower = prod.name.lower().strip()
            category_lower = prod.category.lower().strip()
            
            existing = session.exec(
                select(Poduct).where(
                    (Poduct.name == name_lower) & (Poduct.category == category_lower)
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product with name '{name_lower}' and category '{category_lower}' already exists"
                )
        
        # Crear todos los productos
        for prod in product:
            name_lower = prod.name.lower().strip()
            category_lower = prod.category.lower().strip()
            
            product_db = Poduct(
                name=name_lower,
                category=category_lower,
                price=prod.price,
                stock=prod.stock
            )
            
            session.add(product_db)
            session.flush()
            created_products.append(product_db)
        
        session.commit()
        
        for product_db in created_products:
            session.refresh(product_db)
        
        return {
            "message": f"{len(created_products)} products created successfully",
            "products": created_products
        }
    
    # Si es un solo producto
    else:
        name_lower = product.name.lower().strip()
        category_lower = product.category.lower().strip()
        
        existing_product = session.exec(
            select(Poduct).where(
                (Poduct.name == name_lower) & (Poduct.category == category_lower)
            )
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=400, 
                detail=f"Product with name '{name_lower}' and category '{category_lower}' already exists"
            )
        
        product_db = Poduct(
            name=name_lower,
            category=category_lower,
            price=product.price, 
            stock=product.stock
        )

        session.add(product_db)
        session.commit()        
        session.refresh(product_db)

        return product_db



@app.put('/products/{product_id}')
def update_product(product_id: int, product: ProductCreate, session: SessionDep):
    """
    ESPAÑOL: Actualiza un producto existente. Valida que exista (404).
    Convierte a minusculas, no permite duplicados. Precio > 0, Stock >= 0.
    
    ENGLISH: Updates an existing product. Validates it exists (404).
    Converts to lowercase, no duplicates allowed. Price > 0, Stock >= 0.
    """
    db_product = session.get(Poduct, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Convertir a minúsculas
    name_lower = product.name.lower().strip()
    category_lower = product.category.lower().strip()
    
    # Validar que no exista otro producto con el mismo nombre y categoría
    existing_product = session.exec(
        select(Poduct).where(
            (Poduct.name == name_lower) & 
            (Poduct.category == category_lower) & 
            (Poduct.id != product_id)  # Excluir el producto actual
        )
    ).first()
    
    if existing_product:
        raise HTTPException(
            status_code=400, 
            detail=f"already exists a product with name '{name_lower}' and category '{category_lower}'"
        )
    
    db_product.name = name_lower
    db_product.category = category_lower
    db_product.price = product.price
    db_product.stock = product.stock
    
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    
    return db_product


@app.delete('/products/{product_id}')
def delete_product(product_id: int, session: SessionDep):
    """
    ESPAÑOL: Elimina un producto por ID. Valida que exista (404 si no).
    Devuelve mensaje de confirmacion.
    
    ENGLISH: Deletes a product by ID. Validates it exists (404 if not).
    Returns confirmation message.
    """
    db_product = session.get(Poduct, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    session.delete(db_product)
    session.commit()
    
    return {"message": "Product deleted successfully"}


@app.get('/categories')
def get_categories(
    session: SessionDep,
    category: Annotated[str | None, Query()] = None
):
    """
    ESPAÑOL: 
    Sin parametro: Devuelve todas las categorias unicas: {"categories": ["cat1", "cat2"]}
    Con parametro ?category=nombre: Devuelve lista de productos de esa categoria.
    Error 404 si BD vacia (sin param) o categoria no existe (con param).
    
    ENGLISH:
    Without parameter: Returns all unique categories: {"categories": ["cat1", "cat2"]}
    With parameter ?category=name: Returns list of products in that category.
    Error 404 if DB empty (without param) or category doesn't exist (with param).
    """
    if category:
        # Si proporciona parámetro, busca productos por categoría
        category_lower = category.lower().strip()
        products = session.exec(
            select(Poduct).where(Poduct.category == category_lower)
        ).all()
        
        if not products:
            raise HTTPException(
                status_code=404, 
                detail=f"Category '{category_lower}' not found or has no products"
            )
        
        return products
    else:
        # Sin parámetro, devuelve solo las categorías únicas
        products = session.exec(select(Poduct)).all()
        if not products:
            raise HTTPException(
                status_code=404, 
                detail="No products in database. The database is empty."
            )
        
        # Extrae categorías únicas y las ordena
        categories = sorted(list(set([p.category for p in products])))
        return {"categories": categories}


@app.on_event("shutdown")
def on_shutdown():
    print('Shutting down the application. bye!')
