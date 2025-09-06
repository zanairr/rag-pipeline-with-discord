from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import UploadFile

load_dotenv()
api_key=os.getenv("OPENAI_KEY")
vector_store_id=os.getenv("VECTOR_STORE_ID")


client = OpenAI(api_key=api_key)


def view_files():
    file_list = client.vector_stores.files.list(vector_store_id=vector_store_id)
    file_dict = {}


    #populates dict with all current files
    
    for item in file_list.data:
            try:
                # 'item.id' is the file_id within the vector store
                tmp_file = client.files.retrieve(file_id=item.id)
                #print(f"File ID: {tmp_file.id} found successfully")
                file_dict[str(tmp_file.filename)] = tmp_file.id
            except:
                print(f"Could not resolve file: {item.id}")

    
    return file_dict

def upload_single_file(path, vectorID):
    file_name = os.path.basename(path)
    file_dict = view_files()
    if file_name in file_dict.keys():
        return "Error: File already exists"
    try:
        file_response = client.files.create(file=open(path, "rb"), purpose='assistants')
        attach_response = client.vector_stores.files.create(
            vector_store_id=vectorID,
            file_id=file_response.id
        )
        return {"file": file_name, "status": "success"}
    except Exception as e:
        print(f"error with {file_name}, error: {e}")
        return {"file": file_name, "status": "failed"}



def delete_file(name):
    file_dict = view_files()
    try:
        file_id = file_dict[name]
        vec_status = client.vector_stores.files.delete(file_id=file_id,vector_store_id=vector_store_id)
        client_status = client.files.delete(file_id=file_id)
    except:
         print("file not found")
    return (vec_status,client_status)

def main():
    print("\tWelcome to the file management system\n"
          "----------------------------------------------\n\n" \
          "commands:\n\n" \
          "view: displays all files and ID's\n" \
          "delete [file_name]: deletes file by file name\n"\
          "upload [file_path]: uploads file by file path\n"\
          "quit: exits this program\n" \
          "Note: There is a 5 second cooldown between \ncommands to allow the vector store to update\n\n"
          "----------------------------------------------")
     
    while True:
        print("\n")
        user_input = input("command: ")
        
        user_input = user_input.split()
        try:
            match(user_input[0]):
                case 'view':
                    file_dict = view_files()
                    if len(file_dict) == 0:
                        print("This vector store is empty")
                    else:
                        for name in file_dict.keys():
                            print(f"file name: {name} | file id: {file_dict[name]}")
                case 'delete':
                    vector_status, client_status = delete_file(name=user_input[1])
                    print(f"Vector status: {(vector_status)}\nClient status: {(client_status)}")
                case 'upload':
                    result = upload_single_file(path=user_input[1],vectorID=vector_store_id)
                    try:
                        print(f"Status: {str(result['status'])}")
                    except:
                        print(result)
                case 'quit':
                    break
                case _:
                    print("unknown command")
                    continue

            time.sleep(5)

        except Exception as e:
            print(f"error: {e}")
            continue

main()
