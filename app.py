{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyPa8OWul3BSVF+A2rcBjPNO",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/880121andy/NSYSU-Soulink/blob/main/NSYSU_Soulink.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import os\n",
        "\n",
        "from flask import Flask, request, abort\n",
        "from linebot.v3 import WebhookHandler\n",
        "from linebot.v3.exceptions import InvalidSignatureError\n",
        "from linebot.v3.webhooks import MessageEvent, TextMessageContent\n",
        "from linebot.v3.messaging import (\n",
        "    Configuration, ApiClient, MessagingApi,\n",
        "    ReplyMessageRequest,\n",
        "    TextMessage,\n",
        "    StickerMessage,\n",
        "    ImageMessage,\n",
        "    VideoMessage,\n",
        "    LocationMessage,\n",
        "    TemplateMessage,\n",
        "    ConfirmTemplate, MessageAction,\n",
        "    ButtonsTemplate, URIAction, LocationAction, CameraAction, CameraRollAction,\n",
        "    CarouselTemplate, CarouselColumn, URIAction, PostbackAction\n",
        ")\n",
        "\n",
        "app = Flask(__name__)\n",
        "\n",
        "configuration = Configuration(access_token=os.getenv('Line_Access_Token'))\n",
        "line_handler = WebhookHandler(os.getenv('Line_Channel_Secret'))\n",
        "\n",
        "@app.route(\"/callback\", methods=['POST'])\n",
        "def callback():\n",
        "    signature = request.headers['X-Line-Signature']\n",
        "    body = request.get_data(as_text=True)\n",
        "    try:\n",
        "        line_handler.handle(body, signature)\n",
        "    except InvalidSignatureError:\n",
        "        abort(400)\n",
        "    return 'OK'\n",
        "\n",
        "import google.generativeai as genai\n",
        "\n",
        "genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))\n",
        "model = genai.GenerativeModel('gemini-2.0-flash')\n",
        "def ask_gemini(question):\n",
        "      prompt = (\n",
        "        \"你是一個為台灣中山大學學生設立的，溫暖、具理解心且專業的心理諮詢Line Bot，名稱是NSYSU Soulink\"\n",
        "        \"你的任務是透過文字提供心理支持與情緒陪伴，幫助使用者梳理思緒、表達感受，並提供基礎的心理健康知識與放鬆技巧\"\n",
        "        \"你不是執業心理師，不能提供診斷或治療，但可以鼓勵使用者就醫或尋求專業協助\"\n",
        "        \"你的語氣要溫柔、有同理心，避免使用命令式語氣，也不做價值判斷\"\n",
        "        \"如果使用者有自傷或他傷傾向，你會溫和地提醒他可以撥打當地的心理諮詢專線，並強調他不是一個人\"\n",
        "        \"若你判斷使用者需要學校諮商，請向他或她介紹台灣中山大學的諮商中心\"\n",
        "        f\"根據以上你的設定，回覆這個使用者的對話: {question}\"\n",
        "    )\n",
        "      response = model.generate_content(prompt)\n",
        "      return response.text\n",
        "\n",
        "@line_handler.add(MessageEvent, message=TextMessageContent)\n",
        "def handle_message(event):\n",
        "    with ApiClient(configuration) as api_client:\n",
        "        line_bot_api = MessagingApi(api_client)\n",
        "\n",
        "        action = event.message.text\n",
        "        if action() == '心理測驗':\n",
        "          reply = TextMessage(text='以下為華人心理治療基金會製作的心理與性格免費評估測驗：https://www.tip.org.tw/evaluatefree，另中山大學諮健組也提供專業的心理測驗服務，若您需要，請回覆「諮商」，已獲取中山諮健組的更多資訊與連結。')\n",
        "        elif action() == '位置'\n",
        "          reply = LocationMessage(title=\"中山諮商中心\",address=\"804高雄市鼓山區中山大學行政大樓5001\",latitude=22.62611651661031, longitude=120.26617734788009)\n",
        "        elif action() == '諮商':\n",
        "           button_template = ButtonsTemplate(\n",
        "            thumbnail_image_url='',\n",
        "            title=\"中山大學諮商資訊\",\n",
        "            text=\"行政大樓5樓\",\n",
        "            actions=[\n",
        "                URIAction(label=\"中山諮健組網站\", uri=\"https://ccd-osa.nsysu.edu.tw/\"),\n",
        "                URIAction(label=\"中山諮健組Instagram\", uri=\"https://www.instagram.com/nsysucounseling/\"),\n",
        "                URIAction(label=\"中山個別諮商申請\", uri=\"https://ccd-osa.nsysu.edu.tw/p/412-1091-3687.php?Lang=zh-tw\"),\n",
        "            ]\n",
        "           )\n",
        "           reply = TemplateMessage(\n",
        "              alt_text = '中山大學諮商資訊',\n",
        "              template = button_template)\n",
        "        else:\n",
        "          response = ask_gemini(action) #gemini回覆\n",
        "          reply = TextMessage(text=response)\n",
        "\n",
        "\n",
        "        response = ask_gemini(event.message.text)\n",
        "        line_bot_api.reply_message(\n",
        "            ReplyMessageRequest(\n",
        "                reply_token=event.reply_token,\n",
        "                messages=[\n",
        "                    reply\n",
        "                ]\n",
        "            )\n",
        "        )\n",
        "\n",
        "\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "    app.run()"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/",
          "height": 245
        },
        "id": "-9SxOwSeu5Yj",
        "outputId": "7f964733-a7e8-4e8c-efdc-950dca74c40c"
      },
      "execution_count": null,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            " * Serving Flask app '__main__'\n",
            " * Debug mode: off\n"
          ]
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "INFO:werkzeug:\u001b[31m\u001b[1mWARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.\u001b[0m\n",
            " * Running on http://127.0.0.1:5000\n",
            "INFO:werkzeug:\u001b[33mPress CTRL+C to quit\u001b[0m\n"
          ]
        },
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            " * Running on http://ed62-34-86-101-38.ngrok-free.app\n",
            " * Traffic stats available on http://127.0.0.1:4040\n"
          ]
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "INFO:werkzeug:127.0.0.1 - - [13/May/2025 08:21:12] \"POST /callback HTTP/1.1\" 200 -\n",
            "INFO:werkzeug:127.0.0.1 - - [13/May/2025 08:21:12] \"POST /callback HTTP/1.1\" 200 -\n",
            "INFO:werkzeug:127.0.0.1 - - [13/May/2025 08:21:23] \"POST /callback HTTP/1.1\" 200 -\n",
            "WARNING:pyngrok.process.ngrok:t=2025-05-13T08:27:18+0000 lvl=warn msg=\"Stopping forwarder\" name=http-5000-d2d30baf-dc83-4ced-9206-7d3de9f53c64 acceptErr=\"failed to accept connection: Listener closed\"\n",
            "WARNING:pyngrok.process.ngrok:t=2025-05-13T08:27:18+0000 lvl=warn msg=\"Error restarting forwarder\" name=http-5000-d2d30baf-dc83-4ced-9206-7d3de9f53c64 err=\"failed to start tunnel: session closed\"\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [],
      "metadata": {
        "id": "3xgFNO3fpiWQ"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
