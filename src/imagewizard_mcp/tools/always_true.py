from pydantic import BaseModel

class Result(BaseModel):
    result: bool
    message: str

def always_true() -> Result:
    return Result(
        result=True,
        message="This tool always returns true",
    )