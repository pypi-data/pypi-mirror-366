from fastapi import FastAPI, HTTPException
from cadmium_fastapi import CadmiumMiddleware, report_error

app = FastAPI(title="Cadmium FastAPI Example")

# Add Cadmium middleware
app.add_middleware(
    CadmiumMiddleware,
    application_id="your-application-id",
    cd_secret="your-secret",
    cd_id="your-cd-id"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/error")
async def trigger_error():
    """This endpoint will trigger an unhandled exception"""
    raise ValueError("This is a test error!")

@app.get("/manual-error")
async def manual_error():
    """This endpoint demonstrates manual error reporting"""
    try:
        # Simulate some operation that might fail
        result = 1 / 0
    except Exception as e:
        # Manually report the error
        await report_error(e, extra_data={"custom_field": "custom_value"})
        raise HTTPException(status_code=500, detail="Something went wrong")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)