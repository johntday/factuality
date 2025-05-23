import asyncio
import os
# from gpt_json import GPTJSON, GPTMessage, GPTMessageRole
from openai import OpenAI
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)

class Conclusion(BaseModel):
    score: int = Field(description="From 0 - 100, extract how truthfull is the statement?")
    description: str


SYSTEM_PROMPT = """
You will receive a statement and a list of claims. Those claims will already have references and source quotes. Your task is to
evaluate all of this together and provide a comprehensive conclusion. You will provide a score from 0 - 100 how truthfull you
think this statement is and a description of why you think so.
"""

async def final_conclusion(investigation_results: str, oai_key: str, oai_model: str) -> Conclusion:
    logger.info(f"Generating final conclusion")
    # gpt_json = GPTJSON[Conclusion](oai_key, model=oai_model)

    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model=oai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": investigation_results},
        ],
        response_format=Conclusion,
    )

    payload = completion.choices[0].message.parsed

    # payload = await gpt_json.run(
    #     messages=[
    #         GPTMessage(
    #             role=GPTMessageRole.SYSTEM,
    #             content=SYSTEM_PROMPT,
    #         ),
    #         GPTMessage(
    #             role=GPTMessageRole.USER,
    #             content=investigation_results,
    #         )
    #     ]
    # )
    logger.info(f"Final conclusion", score=payload.score)
    return payload
