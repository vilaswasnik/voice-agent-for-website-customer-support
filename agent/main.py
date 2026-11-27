from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent.inspect import BrowserUnavailableError, inspect_website
from agent.scope import ScopeError
from agent.search import search_site

app = FastAPI(title="Website Voice Agent", version="0.1.0")


class InspectRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class SearchRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    query: str = Field(min_length=1, max_length=500)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/inspect", tags=["inspection"])
async def inspect(request: InspectRequest) -> dict[str, object]:
    try:
        return await inspect_website(request.url)
    except ScopeError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except BrowserUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.post("/search", tags=["search"])
async def search(request: SearchRequest) -> dict[str, object]:
    try:
        return await search_site(request.url, request.query)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ScopeError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except BrowserUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
