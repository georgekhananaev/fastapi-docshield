#!/usr/bin/env python
"""Simple test for custom CSS/JS"""

from fastapi import FastAPI
from fastapi_docshield import DocShield
import uvicorn

app = FastAPI(title="Test Custom")

@app.get("/")
def root():
    return {"test": "custom"}

# Test with custom CSS
DocShield(
    app=app,
    credentials={"test": "test"},
    custom_css=".swagger-ui { background: red; }",
    custom_js="console.log('Custom JS works!');"
)

if __name__ == "__main__":
    print("Testing custom CSS/JS support...")
    print("Visit http://localhost:8100/docs")
    print("Credentials: test/test")
    uvicorn.run(app, host="0.0.0.0", port=8100)