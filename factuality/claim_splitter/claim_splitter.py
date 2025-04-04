# from gpt_json import GPTJSON, GPTMessage, GPTMessageRole
from openai import OpenAI
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)


class Claim(BaseModel):
    claim: str
    reference: str | None = None
    verification_query: str

    class Config:
        use_enum_values = True


class ClaimsArray(BaseModel):
    claims: list[Claim]


SYSTEM_PROMPT = """
You are an claim extractor. You are given a piece of text and you need to extract the references and claims from it. If there are
no references please provide None. Also afterwards provide a verification query to find search results on google to verify the claim.
"""


async def extract_claims(text: str, oai_key: str, oai_model: str) -> list[Claim]:
    logger.info(f"Extracting claims from statement", statement=text)
    # gpt_json = GPTJSON[ClaimsArray](oai_key, model=oai_model)
    # payload = await gpt_json.run(
    #     messages=[
    #         GPTMessage(
    #             role=GPTMessageRole.SYSTEM,
    #             content=SYSTEM_PROMPT,
    #         ),
    #         GPTMessage(
    #             role=GPTMessageRole.USER,
    #             content=text,
    #         ),
    #     ]
    # )
    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model=oai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format=ClaimsArray,
    )

    payload = completion.choices[0].message.parsed
    logger.info(payload)
    logger.info(text)

    logger.info(
        f"Succesfully extracted claims", statement=text, claims=payload.response.claims
    )
    return payload.response.claims
