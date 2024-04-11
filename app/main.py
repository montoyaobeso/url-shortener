import asyncio
import logging
import os
import time
import traceback

import validators
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.status import HTTP_504_GATEWAY_TIMEOUT

from app.code_generator import CodeGenerator
from app.database.client import RedisClient
from app.database.models import URL, URLBase, URLInfo
from app.shortener import Shortener
from app.telemetry.traces import tracer

# Get the general logger
logger = logging.getLogger(__name__)

# Get environment variables
load_dotenv()

# Get database client
redisdb = RedisClient()

# Initialize FastAPI app
app = FastAPI(
    title="MercadoLibre: URL Shortener",
    version="0.0.1",
    description="A utility to reduce URLs to a fixed lenght.",
)

# Instrument app
FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["x-process-time"] = str(process_time)
    return response


@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        start_time = time.time()
        return await asyncio.wait_for(
            call_next(request), timeout=float(os.environ["REQUEST_TIMEOUT_ERROR"])
        )

    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        return JSONResponse(
            {
                "detail": "Request processing time excedeed limit",
                "processing_time": process_time,
            },
            status_code=HTTP_504_GATEWAY_TIMEOUT,
        )


@app.post("/url", response_model=URLInfo, status_code=status.HTTP_201_CREATED)
async def create_url(url_base: URLBase):
    """
    Endpoint to short URLs.
    """

    with tracer.start_as_current_span("input-validation"):
        if not validators.url(url_base.url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="The provided URL is not valid."
            )

    try:
        with tracer.start_as_current_span("code-generation"):
            code = CodeGenerator().get_code()
        
            while redisdb.get_by_id(code):
                code = CodeGenerator().get_code()

            short_url = Shortener().get_url(code)

            url = URL(
                url=url_base.url,
                code=code,
                clicks=0,
                is_active=1,
            )

        with tracer.start_as_current_span("redis-save"):
            redisdb.set_by_id(code, data=dict(url))

        with tracer.start_as_current_span("return-response"):
            return URLInfo(**url.model_dump(), short_url=short_url)
    
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            detail="Oops, something went wrong, try again later.", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/{code}", response_class=RedirectResponse)
async def forward(code: str):
    """
    Endpoint to redirect to original URLs.
    """ 

    if (url := redisdb.get_by_id(code)):
        if int(url["is_active"]):
            url["clicks"] = int(url["clicks"]) + 1
            redisdb.set_by_id(code, data=url)
            return RedirectResponse(url=url["url"], status_code=302)
        else:
            raise HTTPException(
                detail="This shortened URL is not active.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
    else:
        raise HTTPException(
            detail="The original URL for the shortened URL provided was not found.",
            status_code=404,
        )



@app.get("/info/{code}")
async def get_info(code: str):
    """
    Endpoint to get original URLs from shortened URLs.
    """
    try:
        if (url := redisdb.get_by_id(code)): 
            url_info = URLInfo(**url, short_url=Shortener().get_url(url["code"]))
            return url_info
        else:
            raise HTTPException(
                detail="The original URL for the shortened URL provided was not found!",
                status_code=status.HTTP_404_NOT_FOUND,
            )
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            detail="Oops, something went wrong, try again later.", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.delete(
    "/delete/{code}", response_class=JSONResponse, status_code=status.HTTP_200_OK
)
async def delete_url(code: str):
    """
    Endpoint to delete (deactivate) URLs.
    """
    try:
        if (url := redisdb.get_by_id(code)):
            if int(url["is_active"]):
                url["is_active"] = 0
                redisdb.set_by_id(code, data=url)
                return JSONResponse({"detail": "URL deleted."})

        raise HTTPException(
            detail="The original URL for the shortened URL provided was not found!",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            detail="Oops, something went wrong, try again later.", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )