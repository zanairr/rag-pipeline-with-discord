from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_KEY")

#create instance of client
client = OpenAI(api_key=api_key)

def create_vector_store(name):
    try:
        vector_store = client.vector_stores.create(name=name)
        details = {
            "id": vector_store.id,
            "name": vector_store.name,
            "created_at": vector_store.created_at,
            "file_count": vector_store.file_counts.completed
        }
        print(details)
        return details
        
    except Exception as e:
        print(f"vector store was not created: {e}")


#create vector store

storename = "csdata"
vector_store_details = create_vector_store(storename)



