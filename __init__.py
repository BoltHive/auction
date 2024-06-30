import asyncio

from fastapi import APIRouter
from lnbits.db import Database
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .tasks import wait_for_paid_invoices
from .views import auction_ext_generic
from .views_api import auction_ext_api

db = Database("ext_auction")

scheduled_tasks: list[asyncio.Task] = []

auction_ext: APIRouter = APIRouter(prefix="/auction", tags=["auction"])
auction_ext.include_router(auction_ext_generic)
auction_ext.include_router(auction_ext_api)

auction_static_files = [
    {
        "path": "/auction/static",
        "name": "auction_static",
    }
]


def auction_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def auction_start():
    # ignore will be removed in lnbits `0.12.6`
    # https://github.com/lnbits/lnbits/pull/2417
    task = create_permanent_unique_task("ext_testing", wait_for_paid_invoices)  # type: ignore
    scheduled_tasks.append(task)
