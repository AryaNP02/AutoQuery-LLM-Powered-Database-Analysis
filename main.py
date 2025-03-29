import os
import streamlit as st
from pymongo import MongoClient
import pandas as pd
import json
import warnings
from datetime import datetime 
import streamlit as st
from db_utils import load_db, chain_create, sql_infer, mongodb_infer, get_mongodb_collections
import json



def main():
    st.set_page_config(page_icon="🤖", layout="wide", page_title="AutoQuery")
    st.title( "AutoQuery: LLM-Powered Database Analysis")
   
    
    # Initialize session state for database connection
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False
    if "db_type" not in st.session_state:
        st.session_state.db_type = None
    if "db" not in st.session_state:
        st.session_state.db = None
    if "mongo_collections" not in st.session_state:
        st.session_state.mongo_collections = []

    col1, col2 = st.columns([2, 3])

    with col1:
        file_name_or_uri = st.text_input("Enter name of a DB file or MongoDB URI")
        
        if st.button("Load DB"):
            if file_name_or_uri.strip():  
                try:
                    db, db_type = load_db(file_name_or_uri)
                    st.session_state.db = db
                    st.session_state.db_type = db_type
                    st.session_state.db_connected = True

                    if db_type == "sql":
                        st.subheader("Table Names")
                        table_names = db.get_usable_table_names()
                        if isinstance(table_names, list):
                            for table_name in table_names:
                                st.code(table_name)
                        else:
                            st.code(table_names)

                       
                        table_info = db.get_table_info()
                        if isinstance(table_info, dict):  
                            st.subheader("Schemas")
                            for table_name, schema in table_info.items():
                                with st.expander(f"Schema for table: {table_name}"):
                                    st.json(schema)
                      
                    elif db_type == "mongodb":
                        st.subheader("Collections")
                        collections = db.list_collection_names()
                        st.session_state.mongo_collections= collections
                        st.code(collections)

                        st.subheader("Schemas")
                        for collection_name in collections:
                            with st.expander(f"Schema for collection: {collection_name}"):
                                sample_doc = db[collection_name].find_one()
                                if sample_doc:
                                   
                                    schema = {key: str(type(value).__name__) for key, value in sample_doc.items()}
                                    st.json(schema)
                                else:
                                    st.write("No documents found in this collection.")
                except Exception as e:
                    st.error(f"Failed to load database: {str(e)}")
            else:
                st.warning("Please enter a valid database file name or MongoDB URI.")
            
    with col2:
        if st.session_state.db_connected:
            if st.session_state.db_type == "mongodb":
               
                st.subheader("Query MongoDB")
                collection_name = st.selectbox(
                    "Select collection to query",
                    options=st.session_state.mongo_collections
                )
                
                user_question = st.text_area("What would you like to know about this collection?")
                
                if st.button("Analyze with LLM"):
                    if user_question and collection_name:
                        max_attempts = 5
                        attempt = 0
                        while attempt < max_attempts:
                            with st.spinner("Processing your query with LLM..."):
                                try:
                                    answer = mongodb_infer(
                                        st.session_state.db, 
                                        collection_name, 
                                        user_question
                                    )
                                    st.subheader("Analysis")
                                    st.write(answer)
                                    break
                                except Exception as e:
                                    continue
                    else:
                        st.warning("Please enter a question and select a collection.")
                        
            else:
                # SQL query interface
                st.subheader("Query SQL Database")
                user_question = st.text_area("Ask a question about the database")
                
                if st.button("Generate SQL & Analyze"):
                    if user_question:
                        max_attempts = 5
                        attempt = 0
                        while attempt < max_attempts:
                            try:
                                chain = chain_create(st.session_state.db)
                                answer = sql_infer(st.session_state.db, chain, user_question)
                                st.subheader("Analysis")
                                st.write(answer)
                                break
                            except Exception as e:
                                continue

                    else:
                        st.warning("Please enter a question.")


if __name__ == "__main__":
    main()