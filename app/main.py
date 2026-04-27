from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Calculator API", version="1.0.0")


class BinaryOperation(BaseModel):
    a: float
    b: float


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/sum")
def sum_numbers(payload: BinaryOperation):
    return {
        "operation": "sum", 
        "result": payload.a + payload.b
    }


@app.post("/subtract")
def subtract_numbers(payload: BinaryOperation):
    return {
        "operation": "subtract", 
        "result": payload.a - payload.b
    }


@app.post("/multiply")
def multiply_numbers(payload: BinaryOperation):
    return {
        "operation": "multiply", 
        "result": payload.a * payload.b
    }


@app.post("/divide")
def divide_numbers(payload: BinaryOperation):
    if payload.b == 0:
        raise HTTPException(status_code=400, detail="division by zero is not allowed")
    return {
        "operation": "divide", 
        "result": payload.a / payload.b
    }
