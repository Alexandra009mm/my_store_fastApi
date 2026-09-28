from sqlmodel import Field, SQLModel
 
from pydantic import BaseModel, Field as PydanticField, StringConstraints
from typing_extensions import Annotated

#para que tener un basemodel y un sqlmodel, es para que el basemodel sea el que reciba los datos del cliente y el sqlmodel sea el que se guarde en la base de datos, ya que el basemodel no tiene que tener el id, ya que este se genera automaticamente en la base de datos, mientras que el sqlmodel si tiene que tener el id, ya que este es el que se va a guardar en la base de datos.
class ProductCreate(BaseModel):
    # 1. Restricción para que el texto tenga mínimo 1 carácter (no vacío) 
    # y 'strip_whitespace' elimina los espacios vacíos al principio y al final automáticamente.
    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

    category: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    
    # 2. Restricción para que el precio sea mayor a cero
    price: float = PydanticField(gt=0, description="El precio debe ser mayor a 0")
    
    # 3. Restricción para que el stock no sea negativo (cero o más)
    stock: int = PydanticField(ge=0, description="El stock no puede ser negativo")


class Poduct (SQLModel, table=True):

    __tablename__ = 'app_inv_products'

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=3, max_length=150)
    category: str = Field(min_length=3, max_length=150)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)




