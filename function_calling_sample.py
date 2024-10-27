from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import google_custom_search
import datetime
import sys
import requests
import json

load_dotenv(override=True)

# OpenAI APIの初期化
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

# リクエストURL
url = f"{AOAI_ENDPOINT}openai/deployments/{AOAI_CHAT_MODEL_NAME}/chat/completions?api-version={AOAI_API_VERSION}"

# リクエストヘッダー
headers = {"Content-Type": "application/json", "api-key": AOAI_API_KEY}

# 最初のリクエストデータ：Web検索関数を呼び出し
data = {
    "messages": [
        {"role": "system", "content": "あなたは役立つアシスタントです。"},
        {"role": "user", "content": "トム・クルーズの現在の年齢を教えてください。"},
    ],
    "functions": [
        {
            "name": "search_web",
            "description": "指定されたクエリでWebを検索します。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索するクエリ"}
                },
                "required": ["query"],
            },
        },
        {
            "name": "calculate",
            "description": "与えられた計算式に基づき計算を行います。",
            "parameters": {
                "type": "object",
                "properties": {
                    "formula": {
                        "type": "string",
                        "description": "計算式（例：52 * 100, 100 - 1)",
                    }
                },
                "required": ["formula"],
            },
        },
    ],
}


# 指定されたクエリでWebを検索する関数
def search_web(query: str):
    final_result = ""
    google = google_custom_search.CustomSearch(
        apikey=GOOGLE_SEARCH_API_KEY, engine_id=GOOGLE_SEARCH_ENGINE_ID
    )
    results = google.search(query)
    for result in results:
        final_result = final_result + result.snippet + "\n"

    return final_result


# 与えられた計算式に基づき計算を行う関数
def calculate(formula: str):
    return eval(formula)


# リクエストを送信
response = requests.post(url, headers=headers, data=json.dumps(data))

# 結果を出力
result = response.json()

# 関数を実行する
message = result["choices"][0]["message"]["function_call"]
function_name = message["name"]
arguments = json.loads(message["arguments"])  # 文字列を辞書に変換

print(f"実行された関数： {function_name}")
print(f"関数に渡された引数： {arguments}")

func = globals()[function_name]
result = func(**arguments)
print(f"関数の実行結果： {result}")
