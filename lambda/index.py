# lambda/index.py
import json
import urllib.request
# モデルID（今回はFastAPIサーバーのエンドポイント）
MODEL_ID = "https://89fc-35-203-174-176.ngrok-free.app/generate"
def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        print("Processing message:", message)
        print("Using model:", MODEL_ID)
        # 会話履歴を含めて、プロンプトを作成する
        messages = conversation_history.copy()
        messages.append({
            "role": "user",
            "content": message
        })
        # ここでは単純化して、最新のuser発言のみを送る
        # （もし会話履歴も一緒に送りたければ、ここを工夫する）
        request_payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
        # FastAPIサーバーにリクエストを送る
        headers = {"Content-Type": "application/json"}
        data = json.dumps(request_payload).encode("utf-8")
        req = urllib.request.Request(MODEL_ID, data=data, headers=headers)
        with urllib.request.urlopen(req) as res:
            response_body = res.read()
        # レスポンスを取得
        response_json = json.loads(response_body)
        assistant_response = response_json['generated_text']
        # 会話履歴にアシスタントの応答を追加
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        # 成功レスポンスを返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }