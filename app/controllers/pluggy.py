from fastapi import APIRouter, Depends, status, Query
from app.services.pluggy import PluggyService
from app.dto.pluggy import CategoryDTO, ConnectDTO, TransactionDTO, InformationsResponseDTO, CategoryInfoDTO
from typing import List
from datetime import datetime
from app.factories.pluggy import get_pluggy_service

router = APIRouter(
    prefix="/pluggy",
    tags=["pluggy"]
)

@router.get('/categories', status_code=status.HTTP_200_OK, response_model=List[CategoryDTO])
async def read_categories(services: PluggyService = Depends(get_pluggy_service)):
    return await services.get_categories()

@router.get('/connect', status_code=status.HTTP_200_OK, response_model=ConnectDTO)
async def read_connect(services: PluggyService = Depends(get_pluggy_service)):
    return await services.get_connect_token()

@router.get('/transactions/{item_id}', status_code=status.HTTP_200_OK, response_model=List[TransactionDTO])
async def read_transactions(
    item_id: str,
    services: PluggyService = Depends(get_pluggy_service)
    ):
    return await services.get_transactions(item_id)

@router.get('/informations/{item_id}', status_code=status.HTTP_200_OK, response_model=InformationsResponseDTO)
async def read_informations(
    item_id: str,
    from_date: datetime = Query(None, alias='from'),
    to_date: datetime = Query(None, alias='to'),
    services: PluggyService = Depends(get_pluggy_service)
    ):
    return await services.get_informations(item_id, from_date, to_date)

@router.put('/update-category', status_code=status.HTTP_200_OK)
async def update_category(
    category_info: CategoryInfoDTO,
    services: PluggyService = Depends(get_pluggy_service)
    ):
    return await services.update_category(category_info)