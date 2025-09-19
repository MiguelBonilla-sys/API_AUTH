import os
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth import get_current_active_user
from src.auth.dependencies import check_asset_ownership
from src.models.user import User
from src.schemas.inventory import (
    InventarioActivoCreate,
    InventarioActivoOut,
    InventarioActivoUpdate,
    InventarioActivoOwner,
)

router = APIRouter()

# External API configuration
INVENTORY_API_BASE_URL = os.getenv("INVENTORY_API_BASE_URL", "https://inventoryapp.usbtopia.usbbog.edu.co")

# Constants
ASSET_NOT_FOUND_MSG = "Inventory asset not found"
EXTERNAL_API_ERROR_MSG = "External API error"
UNEXPECTED_ERROR_MSG = "Unexpected error"
VALIDATION_ERROR_MSG = "Validation error"
DUENO_DE_ACTIVO_FIELD = "DUEÑO_DE_ACTIVO"


@router.get("/", response_model=List[InventarioActivoOut])
async def get_inventario_activos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of inventory assets (requires authentication)
    Users can only see assets they own, admins can see all
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INVENTORY_API_BASE_URL}/inventario/",
                params={"skip": 0, "limit": 2000},  # Get more data to filter
                timeout=30.0
            )
            response.raise_for_status()
            
            all_assets = response.json()
            
            # Filter assets based on user permissions
            if current_user.is_superuser:
                # Admin can see all assets
                filtered_assets = all_assets
            else:
                # Regular users can only see their own assets
                if not current_user.dueno_de_activo:
                    return []  # User has no assigned assets
                
                user_owner = current_user.dueno_de_activo.strip()
                filtered_assets = [
                    asset for asset in all_assets
                    if asset.get(DUENO_DE_ACTIVO_FIELD, "").strip() == user_owner
                ]
            
            # Apply pagination to filtered results
            paginated_assets = filtered_assets[skip:skip + limit]
            
            return paginated_assets
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{EXTERNAL_API_ERROR_MSG}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{UNEXPECTED_ERROR_MSG}: {str(e)}"
            )


@router.get("/owners", response_model=List[InventarioActivoOwner])
async def get_inventario_owners(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """
    Get unique list of inventory asset owners (public endpoint - no authentication required)
    Returns only unique DUEÑO_DE_ACTIVO values with their first occurrence ID
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INVENTORY_API_BASE_URL}/inventario/",
                params={"skip": 0, "limit": 1000},  # Get more data to ensure uniqueness
                timeout=30.0
            )
            response.raise_for_status()
            
            # Get full data from external API
            full_data = response.json()
            
            # Track unique owners with their first occurrence
            seen_owners = {}
            unique_owners = []
            
            for item in full_data:
                if item.get("id") is not None:
                    owner = item.get(DUENO_DE_ACTIVO_FIELD)
                    
                    # Only add if we haven't seen this owner before
                    if owner not in seen_owners:
                        seen_owners[owner] = True
                        unique_owners.append({
                            "id": item.get("id"),
                            DUENO_DE_ACTIVO_FIELD: owner
                        })
            
            # Apply pagination to unique results
            paginated_owners = unique_owners[skip:skip + limit]
            
            return paginated_owners
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{EXTERNAL_API_ERROR_MSG}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{UNEXPECTED_ERROR_MSG}: {str(e)}"
            )


@router.post("/", response_model=InventarioActivoOut, status_code=status.HTTP_201_CREATED)
async def create_inventario_activo(
    activo_data: InventarioActivoCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new inventory asset (requires authentication)
    Users can only create assets for their own department
    """
    # Check if user can create assets for this owner
    activo_owner = getattr(activo_data, DUENO_DE_ACTIVO_FIELD, None)
    if activo_owner and not check_asset_ownership(current_user, activo_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear activos para este propietario"
        )
    
    # If user is not admin and no owner specified, set their own owner
    if not current_user.is_superuser and not activo_owner:
        if not current_user.dueno_de_activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene un propietario de activo asignado"
            )
        # Set the owner to user's department
        activo_dict = activo_data.model_dump(exclude_unset=True)
        activo_dict[DUENO_DE_ACTIVO_FIELD] = current_user.dueno_de_activo
    else:
        activo_dict = activo_data.model_dump(exclude_unset=True)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{INVENTORY_API_BASE_URL}/inventario/",
                json=activo_dict,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if response.status_code == 422:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=response.json() if response.content else VALIDATION_ERROR_MSG
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{EXTERNAL_API_ERROR_MSG}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{UNEXPECTED_ERROR_MSG}: {str(e)}"
            )


@router.get("/{activo_id}", response_model=InventarioActivoOut)
async def get_inventario_activo(
    activo_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific inventory asset by ID (requires authentication)
    Users can only see assets they own, admins can see all
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INVENTORY_API_BASE_URL}/inventario/{activo_id}",
                timeout=30.0
            )
            response.raise_for_status()
            
            asset_data = response.json()
            
            # Check if user can access this asset
            asset_owner = asset_data.get(DUENO_DE_ACTIVO_FIELD, "")
            if not check_asset_ownership(current_user, asset_owner):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para acceder a este activo"
                )
            
            return asset_data
            
        except httpx.HTTPError as e:
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ASSET_NOT_FOUND_MSG
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{EXTERNAL_API_ERROR_MSG}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{UNEXPECTED_ERROR_MSG}: {str(e)}"
            )


@router.put("/{activo_id}", response_model=InventarioActivoOut)
async def update_inventario_activo(
    activo_id: int,
    activo_data: InventarioActivoUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing inventory asset (requires authentication)
    Users can only update assets they own, admins can update all
    """
    async with httpx.AsyncClient() as client:
        try:
            # First, get the current asset to check ownership
            get_response = await client.get(
                f"{INVENTORY_API_BASE_URL}/inventario/{activo_id}",
                timeout=30.0
            )
            get_response.raise_for_status()
            current_asset = get_response.json()
            
            # Check if user can access this asset
            asset_owner = current_asset.get(DUENO_DE_ACTIVO_FIELD, "")
            if not check_asset_ownership(current_user, asset_owner):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para modificar este activo"
                )
            
            # Check if user is trying to change owner to someone else's
            update_data = activo_data.model_dump(exclude_unset=True)
            new_owner = update_data.get(DUENO_DE_ACTIVO_FIELD)
            if new_owner and not check_asset_ownership(current_user, new_owner):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para asignar activos a este propietario"
                )
            
            # Perform the update
            response = await client.put(
                f"{INVENTORY_API_BASE_URL}/inventario/{activo_id}",
                json=update_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            if get_response.status_code == 404 or response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ASSET_NOT_FOUND_MSG
                )
            elif response.status_code == 422:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=response.json() if response.content else VALIDATION_ERROR_MSG
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{EXTERNAL_API_ERROR_MSG}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{UNEXPECTED_ERROR_MSG}: {str(e)}"
            )


@router.delete("/{activo_id}", response_model=InventarioActivoOut)
async def delete_inventario_activo(
    activo_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an inventory asset (requires authentication)
    Users can only delete assets they own, admins can delete all
    """
    async with httpx.AsyncClient() as client:
        try:
            # First, get the current asset to check ownership
            get_response = await client.get(
                f"{INVENTORY_API_BASE_URL}/inventario/{activo_id}",
                timeout=30.0
            )
            get_response.raise_for_status()
            current_asset = get_response.json()
            
            # Check if user can access this asset
            asset_owner = current_asset.get(DUENO_DE_ACTIVO_FIELD, "")
            if not check_asset_ownership(current_user, asset_owner):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para eliminar este activo"
                )
            
            # Perform the deletion
            response = await client.delete(
                f"{INVENTORY_API_BASE_URL}/inventario/{activo_id}",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            if get_response.status_code == 404 or response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ASSET_NOT_FOUND_MSG
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{EXTERNAL_API_ERROR_MSG}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{UNEXPECTED_ERROR_MSG}: {str(e)}"
            )