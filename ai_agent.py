import streamlit as st
import pathlib as Path
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
import os 
from langchain_groq.chat_models import ChatGroq
st.set_page_config(page_title="Langchain: Chat with sql db ",page_icon="😂")
st.title("(●'◡'●)    Langchain : chat with sql db ")
LOCALDB = "USE_LOCALDB"
MYSQL= "USE_MYSQL"
radio_opt=["Use SQLLite 3 Database-Student.db","Connect to you Sql database"]
selected_opt=st.sidebar.radio(label="chose the db which you want to chat",options=radio_opt)
if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("provide my sql Host")
    mysql_user=st.sidebar.text_input("MySQL user")
    mysql_password=st.sidebar.text_input("Mysql password",type="password")
    mysql_db=st.sidebar.text_input("My sql database")
else:
    db_uri=LOCALDB
api_key=st.sidebar.text_input(label="Groq api key",type="password")
if not db_uri:
    st.info("Please enter the database info and uri")
if not api_key:
    st.info("Please add the groq api key")
llm = ChatGroq(groq_api_key=api_key,model="llama3-8b-8192",streaming=True)
@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri==LOCALDB:
        dbfilepath="test.db"
        st.write(dbfilepath)
        creator=lambda:sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))
    elif db_uri==MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MYSQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db=configure_db(db_uri)
toolkit=SQLDatabaseToolkit(db=db,llm=llm)
agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)
if "messages" not in st.session_state or st.sidebar.button("clear message history"):
    st.session_state["messages"] = [{"role":"assistant","content":"How can i help you ?"}]
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="ask anything")
if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistent","content":response})
        st.write(response)
