# swagger http://localhost:8000/docs
import uvicorn
from fastapi import FastAPI
from factuality.runner.factuality import Factuality
from factuality.utils.options import Options
app = FastAPI()
@app.get("/")
def test():
    """
    Simple example app.
    :return:
    """
    return {"GFG Example": "FastAPI"}


def factuality():

    factuality = Factuality()

    conclusion, _, _ = factuality.check("Neil armstrong land on the moon.")

    print(conclusion.description, conclusion.score)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
