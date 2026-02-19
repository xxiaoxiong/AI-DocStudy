from fastapi import APIRouter
from .exam import router as exam_router

router = APIRouter()
router.include_router(exam_router)
