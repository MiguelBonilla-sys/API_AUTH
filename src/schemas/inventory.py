from typing import Optional

from pydantic import BaseModel


class InventarioActivoBase(BaseModel):
    """Base schema for Inventario Activo - mirrors external API structure"""
    NOMBRE_DEL_ACTIVO: Optional[str] = None
    DESCRIPCION: Optional[str] = None
    TIPO_DE_ACTIVO: Optional[str] = None
    MEDIO_DE_CONSERVACIÓN: Optional[str] = None
    FORMATO: Optional[str] = None
    IDIOMA: Optional[str] = None
    PROCESO: Optional[str] = None
    DUEÑO_DE_ACTIVO: Optional[str] = None
    TIPO_DE_DATOS_PERSONALES: Optional[str] = None
    FINALIDAD_DE_LA_RECOLECCIÓN: Optional[str] = None
    CONFIDENCIALIDAD: Optional[str] = None
    INTEGRIDAD: Optional[str] = None
    DISPONIBILIDAD: Optional[str] = None
    CRITICIDAD_TOTAL_DEL_ACTIVO: Optional[str] = None
    INFORMACIÓN_PUBLICADA_O_DISPONIBLE: Optional[str] = None
    LUGAR_DE_CONSULTA: Optional[str] = None


class InventarioActivoCreate(InventarioActivoBase):
    """Schema for creating a new Inventario Activo"""
    pass


class InventarioActivoUpdate(InventarioActivoBase):
    """Schema for updating an existing Inventario Activo"""
    pass


class InventarioActivoOut(InventarioActivoBase):
    """Schema for Inventario Activo output response"""
    id: int

    class Config:
        from_attributes = True


class InventarioActivoOwner(BaseModel):
    """Schema for public endpoint - only asset owner information"""
    id: int
    DUEÑO_DE_ACTIVO: Optional[str] = None

    class Config:
        from_attributes = True