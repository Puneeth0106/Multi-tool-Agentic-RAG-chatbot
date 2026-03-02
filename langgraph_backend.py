from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()

#LLM
llm = ChatOpenAI()

#State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

#Node
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

#Configuration
conn= sqlite3.connect(database='New-chatbot.db',check_same_thread=False)

# Checkpointer
checkpointer = SqliteSaver(conn=conn)

#Graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


#Threads-Backend
def retrieve_all_threads():
    all_threads=set()
    for i in checkpointer.list(None):
        all_threads.add(i.config['configurable']['thread_id'])
    return list(all_threads)