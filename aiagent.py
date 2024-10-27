from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import google_custom_search
import datetime
import sys

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

template = """
次の質問に出来る限り答えてください。次のツールにアクセスできます。
- 検索ツール：検索するときに使います
- 計算ツール：計算するときに使います
- 今日の日付取得ツール：今日の日付を取得するときに使います
次のフォーマットを使用します。
質問：回答する必要がある入力質問
思考：次に何をすべきかを常に考える
行動：実行するアクションは、「計算ツール」「検索ツール」「今日の日付取得ツール」のいずれかである必要があります。
行動の入力：アクションへの入力（ツールによっては行動の入力が不要の場合がありますので、その場合は「無し」にしてください）
観察：行動の結果
...（この思考／行動／行動の入力／観察はN回繰り返すことができます）
最終的な答えがわかったら以下を出力します。
思考：今、最終的な答えがわかりました
最終回答：元の入力質問に対する最終回答

計算ツールを使うときの行動の入力は、計算式を入力してください。

例：52 * 100
例：100 - 1

質問：{question}

さあ始めましょう。

思考：
"""

question = "次の、トム・クルーズの誕生日にケーキをプレゼントしたいです。彼の年齢分のろうそくを購入するための金額を計算してください。ろうそくは一本100円です。"

message = template.format(question=question)

final_observation = ""

print(message)


while True:
    # LLMにプロンプトを送り、思考させる
    openai_client = AzureOpenAI(
        azure_endpoint=AOAI_ENDPOINT, api_key=AOAI_API_KEY, api_version=AOAI_API_VERSION
    )
    # response = openai_client.chat.completions.create(
    #     messages=[
    #         {"role": "assistant", "content": message},
    #     ],
    #     stop={"観察："},
    # )
    response = openai_client.chat.completions.create(
        model=AOAI_CHAT_MODEL_NAME,  # Model = should match the deployment name you chose for your model deployment
        # response_format={"type": "json_object"},
        messages=[
            # {
            #     "role": "system",
            #     "content": "You are a helpful assistant designed to output JSON.",
            # },
            # {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": message},
        ],
        stop=["観察："],
    )
    # print(response.choices[0].message.content)

    # response = openai_client.chat.completions.create(
    #     model=AOAI_CHAT_MODEL_NAME,
    #     response_format={"type": "json_object"},
    #     messages=[
    #         {"role": "assistant", "content": message},
    #     ],
    #     stop={"観察："},
    # )
    # print(response)
    # sys.exit()
    result = response.choices[0].message.content.strip()
    # print(result)
    # sys.exit()

    # 最終回答が出たかどうかを判断する。
    # resultの変数の最後の行に、つまりresultの変数を開業で分割した配列の最後の要に「最終回答：」がある場合、終了する
    if "最終回答：" in result.split("\n")[-1]:
        final_observation = result.split("最終回答：")[1].strip()
        print("★最終回答★", final_observation)
        break

    # resultの"行動"と"行動の入力"を取得し、それに合ったツールを実行する
    if "行動" in result:
        action = result.split("行動の入力：")[0].split("行動：")[1].strip()
        action_input = result.split("行動の入力：")[1].strip()

        print("★action★", action)
        print("action_input", action_input)
        # sys.exit()

        observation = ""
        if action in "検索ツール":
            # if "検索ツール" in action:
            # 検索ツール実行
            google = google_custom_search.CustomSearch(
                apikey=GOOGLE_SEARCH_API_KEY, engine_id=GOOGLE_SEARCH_ENGINE_ID
            )
            results = google.search(action_input)
            for result in results:
                observation = observation + result.snippet + "\n"
            print("検索ツール", observation)
        elif action in "計算ツール":
            # elif "計算ツール" in action:
            # 計算ツール実行
            observation = str(eval(action_input))
            print("計算ツール実行", observation)
        elif action in "今日の日付取得ツール":
            # elif "今日の日付取得ツール" in action:
            # 今日の日付取得ツール実行
            observation = str(datetime.datetime.now())
            print("今日の日付取得ツール実行", observation)
    message = (
        message
        + "\n行動："
        + action
        + "\n行動の入力："
        + action_input
        + "\n観察："
        + observation
        + "\n思考："
    )
    print("\n観察：" + observation + "\n思考：")
