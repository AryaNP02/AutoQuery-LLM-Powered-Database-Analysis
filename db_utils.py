from langchain_community.utilities.sql_database import SQLDatabase
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, create_sql_query_chain
from pymongo import MongoClient
import pandas as pd
import json
from datetime import datetime

def load_db(db_name_or_uri):
    if db_name_or_uri.startswith("mongodb://"):
        client = MongoClient(db_name_or_uri)
        db = client.get_database()
        return db, "mongodb"
    else:
        db = SQLDatabase.from_uri(f"sqlite:///{db_name_or_uri}")
        return db, "sql"

def chain_create(db):
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    chain = create_sql_query_chain(llm, db)
    return chain

def sql_infer(db, chain, user_question):
    sql_query = chain.invoke({"question": user_question})
    result = db.run(sql_query)
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, generate a proper reply to give to user 

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )
    llm_model = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    llm = LLMChain(llm=llm_model, prompt=answer_prompt)
    ans = llm(inputs={"question": user_question, "query": sql_query, "result": result})
    return ans["text"]

def load_mongodb_data(mongo_db, collection_name):
    collection = mongo_db[collection_name]
    cursor = collection.find({})
    documents = list(cursor)
    for doc in documents:
        for key, value in doc.items():
            if isinstance(value, (datetime, pd.Timestamp)):
                doc[key] = value.isoformat()
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
    return documents

def get_mongodb_collections(mongo_db):
    return mongo_db.list_collection_names()

def mongodb_infer(mongo_db, collection_name, user_question):
    documents = load_mongodb_data(mongo_db, collection_name)
    documents_json = json.dumps(documents[:10], indent=2)
    mongo_prompt = PromptTemplate.from_template(
        """You are a MongoDB data analyst. Given the following user question and MongoDB documents, 
        analyze the data and provide a detailed answer. If relevant, suggest a MongoDB query that would 
        help answer the question.

        Question: {question}
        MongoDB Collection: {collection_name}
        Documents Sample (first 10): {documents_sample}
        Total Documents: {total_documents}
        Answer: """
    )
    llm_model = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    llm = LLMChain(llm=llm_model, prompt=mongo_prompt)
    ans = llm(inputs={
        "question": user_question,
        "collection_name": collection_name,
        "documents_sample": documents_json,
        "total_documents": len(documents)
    })
    return ans["text"]
