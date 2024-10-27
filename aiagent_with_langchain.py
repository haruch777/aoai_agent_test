import os
import datetime
from langchain_openai import AzureChatOpenAI
from langchain.agents import tool

# from langchain_community.tools import DuckDuckGoSearchRun
from langchain.callbacks import StdOutCallbackHandler
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
import google_custom_search

load_dotenv(override=True)

# Azure OpenAIの設定
AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")  # Azure OpenAI Serviceのエンドポイント
AOAI_API_VERSION = os.environ.get(
    "AOAI_API_VERSION"
)  # Azure OpenAI ServiceのAPIバージョン
AOAI_API_KEY = os.environ.get("AOAI_API_KEY")  # Azure OpneAI ServiceのAPIキー
AOAI_CHAT_MODEL_NAME = os.environ.get(
    "AOAI_CHAT_MODEL_NAME"
)  # Azure OpenAI Servicenのデプロイモデル名
print(AOAI_CHAT_MODEL_NAME)
GOOGLE_SEARCH_API_KEY = os.environ.get(
    "GOOGLE_SEARCH_API_KEY"
)  # Google Custome Search APIのAPIキー
GOOGLE_SEARCH_ENGINE_ID = os.environ.get(
    "GOOGLE_SEARCH_ENGINE_ID"
)  # Google Custome Search APIのエンジンID

# LLMの初期化
llm = AzureChatOpenAI(
    azure_endpoint=AOAI_ENDPOINT,
    api_key=AOAI_API_KEY,
    api_version=AOAI_API_VERSION,
    openai_api_type="azure",
    azure_deployment=AOAI_CHAT_MODEL_NAME,
)


# 指定されたクエリでWebを検索する関数
@tool
def search_web(query: str):
    """
    指定されたクエリでWebを検索します。
    """
    final_result = ""
    google = google_custom_search.CustomSearch(
        apikey=GOOGLE_SEARCH_API_KEY, engine_id=GOOGLE_SEARCH_ENGINE_ID
    )
    results = google.search(query)
    for result in results:
        final_result = final_result + result.snippet + "\n"

    return final_result


# 与えられた計算式に基づき計算を行う関数
@tool
def calculate(formula: str):
    """
    与えられた計算式に基づき計算を行います。
    """
    return str(eval(formula))


# 現在の日付を取得する関数
@tool
def get_current_date():
    """
    現在の日付を取得します。
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [search_web, calculate, get_current_date]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "あなたは役立つアシスタントです。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=ConversationBufferWindowMemory(
        return_messages=True, memory_key="chat_history", k=10
    ),
)

executor.invoke(
    {
        "input": "トム・クルーズの次の誕生日にケーキをプレゼントしたいです。彼の年齢分のろうそくを購入するための金額を計算してください。ろうそくは一本100円です。"
    },
    callback_handler=StdOutCallbackHandler(),
)
