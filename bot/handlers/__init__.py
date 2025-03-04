from aiogram import Router

from .quotes.add_quote import router as add_quote_router
from .quotes.get_quote import router as get_quote_router
from .settings.authors import router as authors_settings_router
from .settings.frequency import router as frequency_settings_router
from .settings.general import router as general_settings_router
from .start import router as start_router



router = Router()

router.include_router(add_quote_router)
router.include_router(get_quote_router)
router.include_router(authors_settings_router)
router.include_router(frequency_settings_router)
router.include_router(general_settings_router)
router.include_router(start_router)


