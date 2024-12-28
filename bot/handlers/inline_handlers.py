from aiogram import Router, types


inline_router = Router()


@inline_router.inline_query() # type:ignore
async def handle_inline_query(inline_query: types.InlineQuery):
    results = []
    await inline_query.answer(results)
    
