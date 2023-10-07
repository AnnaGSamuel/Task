from pymongo import MongoClient
from faker import Faker
import requests

client = MongoClient('mongodb+srv://annagsamuel:ansam13@cluster1.q6qrewn.mongodb.net/')
db = client['company_db']

employees_collection = db['user']
department_collection = db['Departments']

fake = Faker()
num_records = 10 

hf_token = "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"
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text: str) -> list[float]:
    response = requests.post(
		embedding_url,
		headers={"Authorization": f"Bearer {hf_token}"},
		json={"inputs": text})
    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
    return response.json()

department_data = [{"name": "HR"}, {"name": "IT"}, {"name": "Sales"}, {"name": "Finance"}]
department_collection.insert_many(department_data)

for _ in range(num_records):
    department = fake.random_element(elements=department_data)
    
    salary_data = {
        "amount": fake.random_int(min=20000, max=100000),
        "currency": fake.currency_code()
    }

    employee_data = {
        "uid": fake.uuid4(),
        "employee_id": fake.unique.random_number(),
        "email": fake.email(),
        "name": fake.name(),
        "joinedAt": fake.date_time_this_decade(),
        "gender": fake.random_element(elements=("Male", "Female","Other")),
        "dob": fake.date(),
        "mobile": fake.phone_number(),
        "department": department,  # Reference to department object
        "salary": salary_data  # Reference to salary object
    }
    employees_collection.insert_one(employee_data)

    #VECTOR EMBEDDING
    for doc in employees_collection.find({'name':{"$exists": True},'salary':{"$exists": True}}).limit(50):
        doc['name_embedding_hf'] = generate_embedding(doc['name'])
       # doc['salary_embedding_hf'] = generate_embedding(doc['salary'])
        print(doc['name_embedding_hf'])
        employees_collection.replace_one({'_id': doc['_id']}, doc)