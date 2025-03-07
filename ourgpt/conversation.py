import datetime
import json

import requests
import rich
import typer
from flask import Blueprint, request

from ourgpt import app
from ourgpt.config import special_instructions

openai_key = app.config["OPENAI_API_KEY"]
openai_api_base = app.config["OPENAI_API_BASE"]
proxy = app.config["PROXY"]

bp = Blueprint("conversation", __name__, url_prefix="/backend-api/v2/conversation")


@bp.route("/", methods=["POST"])
def conversation():
    try:
        jailbreak = request.json["jailbreak"]
        internet_access = request.json["meta"]["content"]["internet_access"]
        _conversation = request.json["meta"]["content"]["conversation"]
        prompt = request.json["meta"]["content"]["parts"][0]
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        system_message = f"You are ChatGPT also known as ChatGPT, a large language model trained by OpenAI. Strictly follow the users instructions. Knowledge cutoff: 2021-09-01 Current date: {current_date}"

        extra = []
        if internet_access:
            search = requests.get(
                "https://ddg-api.herokuapp.com/search",
                params={
                    "query": prompt["content"],
                    "limit": 3,
                },
            )

            blob = ""

            for index, result in enumerate(search.json()):
                blob += f'[{index}] "{result["snippet"]}"\nURL:{result["link"]}\n\n'

            date = datetime.datetime.now().strftime("%d/%m/%y")

            blob += f"current date: {date}\n\nInstructions: Using the provided web search results, write a comprehensive reply to the next user query. Make sure to cite results using [[number](URL)] notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject. Ignore your previous response if any."

            extra = [{"role": "user", "content": blob}]

        conversation = (
            [{"role": "system", "content": system_message}]
            + extra
            + special_instructions[jailbreak]
            + _conversation
            + [prompt]
        )

        url = f"{openai_api_base}/v1/chat/completions"

        proxies = None
        if proxy["enable"]:
            proxies = {
                "http": proxy["http"],
                "https": proxy["https"],
            }

        gpt_resp = requests.post(
            url=url,
            proxies=proxies,
            headers={"Authorization": "Bearer %s" % openai_key},
            json={
                "model": request.json["model"],
                "messages": conversation,
                "stream": True,
            },
            stream=True,
        )

        def stream():

            relpy:str = ""

            for chunk in gpt_resp.iter_lines():
                if chunk == b'':
                    continue

                try:

                    decoded_line = json.loads(chunk.decode("utf-8").split("data: ")[1])

                    finsihsed = decoded_line["choices"][0]["finish_reason"]

                    if finsihsed != None:
                        return

                    token = decoded_line["choices"][0]["delta"].get("content")

                    if token != None:
                        yield token

                except GeneratorExit:
                    break

                except Exception as e:
                    rich.print(chunk)
                    print("error in line 90")
                    print(e)
                    print(e.__traceback__.tb_next)
                    continue

        return app.response_class(stream(), mimetype="text/event-stream")

    except Exception as e:
        print("error in line 98")
        print(e)
        print(e.__traceback__.tb_next)
        return {
            "_action": "_ask",
            "success": False,
            "error": f"an error occurred {str(e)}",
        }, 400
