from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent.inspect import BrowserUnavailableError, inspect_website
from agent.scope import ScopeError

app = FastAPI(title="Website Voice Agent", version="0.1.0")


class InspectRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


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
