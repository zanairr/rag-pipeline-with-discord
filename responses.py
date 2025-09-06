from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


api_key=os.getenv("OPENAI_KEY")
vector_store_id=os.getenv("VECTOR_STORE_ID")


client = OpenAI(api_key=api_key)


def get_response(query):
    response = client.responses.create(
        input=query,
        instructions=("You are a student support bot for a company that teaches courses to students. "
        "Your job is to accurately answer student questions based on the data that you have. "
        "If you do not know the answer to a question, simply say "
        "'I do not have the appropriate resources to answer your question, "
        "please reach out to a staff member about your inquiry.'. If you receive a question unrelated to the data in the files that you have, please say "
        "'I am here to answer Circuit Stream related questions only.' Additionally, do not answer questions that are not related to the data that you have, "
        "and do not base your answers on anything outside of the data you have."),
        model="gpt-5-nano",
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }]
    )
    return response

