# Cadmium-FastAPI SDK

This SDK captures and sends errors from your FastAPI application to the Cadmium server.

## Installation

```bash
pip install cadmium-fastapi-sdk
```

## Configuration

Add the following to your FastAPI application:

```python
from fastapi import FastAPI
from cadmium_fastapi import CadmiumMiddleware

app = FastAPI()

# Add Cadmium middleware
app.add_middleware(
    CadmiumMiddleware,
    application_id="your-application-id",
    cd_secret="your-secret",
    cd_id="your-cd-id"
)
```

## Environment Variables (Alternative Configuration)

You can also configure using environment variables:

```bash
export CADMIUM_APPLICATION_ID="your-application-id"
export CADMIUM_CD_SECRET="your-secret"
export CADMIUM_CD_ID="your-cd-id"
```

Then simply add the middleware without parameters:

```python
from cadmium_fastapi import CadmiumMiddleware

app.add_middleware(CadmiumMiddleware)
```

## Usage

Once configured, any unhandled exception will automatically be sent to the Cadmium server.

## Manual Error Reporting

You can also manually report errors:

```python
from cadmium_fastapi import report_error

try:
    # Your code here
    pass
except Exception as e:
    await report_error(e, request)
```