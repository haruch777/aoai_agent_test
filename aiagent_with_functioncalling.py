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

# 最初のメッセージ
messages = [
    {"role": "system", "content": "あなたは役立つアシスタントです。"},
    {
        "role": "user",
        "content": "次のトム・クルーズの誕生日にケーキをプレゼントしたいです。彼の年齢分のろうそくを購入するための金額を計算してください。ろうそくは一本100円です。",
    },
]

# 関数の定義
functions = [
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
    {"name": "get_current_date", "description": "現在の日付を取得します。"},
]


# 指定されたクエリでWebを検索する関数
def search_web(query: str):
    # 検索ツール実行
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
    return str(eval(formula))


def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# メインループ
while True:
    # リクエストデータの準備
    # 最初のリクエストデータ：Web検索関数を呼び出し
    data = {"messages": messages, "functions": functions, "function_call": "auto"}

    # リクエストを送信
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()

    # アシスタントの返信を取得
    assistant_message = result["choices"][0]["message"]
    # アシスタントのメッセージを履歴に追加
    messages.append(assistant_message)

    # アシスタントが関数を呼び出したか確認
    if "function_call" in assistant_message:
        function_call = assistant_message["function_call"]
        # 関数名を取得
        function_name = function_call["name"]

        # 関数に渡す引数を取得
        arguments = json.loads(function_call["arguments"])  # 文字列を辞書に変換

        # 関数を実行
        func = globals()[function_name]
        function_response = func(**arguments)

        print(f"実行された関数： {function_name}")
        print(f"関数に渡された引数： {arguments}")
        print(f"関数の実行結果： {function_response}")

        # 関数の応答をメッセージに追加
        messages.append(
            {"role": "function", "name": function_name, "content": function_response}
        )
    else:
        # 最終回答が得られた場合
        final_observation = assistant_message["content"]
        print(f"最終回答： {final_observation}")
        break
