"""
Example using environment variables for configuration.

Set these environment variables before running:
export CADMIUM_APPLICATION_ID="your-application-id"
export CADMIUM_CD_SECRET="your-secret"
export CADMIUM_CD_ID="your-cd-id"
"""

from fastapi import FastAPI
from cadmium_fastapi import CadmiumMiddleware

app = FastAPI(title="Cadmium FastAPI Example with Env Config")

# Add Cadmium middleware (will use environment variables)
app.add_middleware(CadmiumMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World with Env Config"}

@app.get("/error")
async def trigger_error():
    """This endpoint will trigger an unhandled exception"""
    raise RuntimeError("This is a test error with env config!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)