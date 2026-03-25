import math
import os
import base64
from typing import List, Union
from os.path import dirname, abspath, join
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

current_dir = dirname(abspath(__file__))
static_path = join(current_dir, "static")

app = FastAPI()
app.mount("/ui", StaticFiles(directory=static_path), name="ui")


class Body(BaseModel):
    length: Union[int, None] = 20


class PaginatedResponse(BaseModel):
    items: List[str]
    total: int
    page: int
    page_size: int = Field(alias="page_size")
    total_pages: int


@app.get('/health')
def health():
    return {'status': 'healthy'}


@app.get('/')
def root():
    html_path = join(static_path, "index.html")
    return FileResponse(html_path)


@app.post('/generate')
def generate(body: Body):
    """
    Generate a pseudo-random token ID of twenty characters by default. Example POST request body:

    {
        "length": 20
    }
    """
    string = base64.b64encode(os.urandom(64))[:body.length].decode('utf-8')
    return {'token': string}


def _generate_token(length: int) -> str:
    return base64.b64encode(os.urandom(64))[:length].decode('utf-8')


@app.get('/token', response_model=PaginatedResponse)
def list_tokens(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    total: int = Query(50, ge=0, description="Total number of tokens to generate across all pages"),
    length: int = Query(20, ge=1, description="Character length of each token"),
):
    """
    Generate multiple pseudo-random tokens with pagination.

    The caller supplies `total` (how many tokens exist across all pages).
    Only the tokens for the requested `page` are generated and returned,
    along with pagination metadata.

    Example: `GET /token?page=1&page_size=10&total=25&length=20`
    """
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    if total > 0 and page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"page {page} exceeds total_pages {total_pages}",
        )

    start = (page - 1) * page_size
    count = min(page_size, total - start) if total > 0 else 0
    items = [_generate_token(length) for _ in range(count)]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )