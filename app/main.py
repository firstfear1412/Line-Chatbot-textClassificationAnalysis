from flask import Flask, request, abort, jsonify
import requests
import json
from app.Config import *
import joblib
from pythainlp.tokenize import word_tokenize
app=Flask(__name__)

# 1. ระบุตำแหน่งของไฟล์โมเดล .pkl ที่บันทึก
model_filename = 'naive_bayes_model.pkl'
loaded_nb_model = joblib.load(model_filename)

vectorizer_filename = 'tfidf_vectorizer.pkl'
loaded_vectorizer = joblib.load(vectorizer_filename)



@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        payload = request.json
        Reply_token = payload['events'][0]['replyToken']
        message = payload['events'][0]['message']['text']

        list_sayhi = ['สวัสดี','หวัดดี','ดีจ้า','hi','hello']
        if any(word in message.lower() for word in list_sayhi):
            reply_text = "สวัสดีครับ ชื่อ Chenchen\nผมเป็น Chatbot Text Sentiment Analysis\nสำหรับ Asian Games ครับ\nสามารถพิมพ์ข้อความที่ต้องการวิเคราะห์ได้เลยครับ"
        else:
            sentiment_label = test_sentiment(message, loaded_vectorizer, loaded_nb_model)
            reply_text = get_reply(sentiment_label)

        ReplyMessage(Reply_token, reply_text, Channel_access_token)
        return jsonify({"message": "Message processed"}), 200
    elif request.method == 'GET':
        return "this is method GET!!!", 200
    else:
        abort(400)

def test_sentiment(text,vectorizer,model):
    # แปลงข้อความเป็นเวกเตอร์ BERT
    text_tokenize = word_tokenize(text)
    to_string = ' '.join(text_tokenize)
    X_to_predict = vectorizer.transform([to_string])  # ทำ vectorize ข้อความที่ต้องการทำนาย
    predicted_label = model.predict(X_to_predict)

    return predicted_label


def get_reply(sentiment_label):
    if sentiment_label == 0:
        return "ข้อความนี้เป็นข้อความ Negative ครับ"
    elif sentiment_label == 1:
        return "ข้อความนี้เป็นข้อความ Neutral ครับ"
    elif sentiment_label == 2:
        return "ข้อความนี้เป็นข้อความ Positive ครับ"
    else:
        return "ขออภัยด้วยครับ ผมไม่สามารถวิเคราะห์ข้อความนี้ได้\nโปรดลองพิมพ์ประโยคในรูปแบบอื่นครับ "

def ReplyMessage(Reply_token, TextMessage, Line_Access_Token):
    LINE_API = 'https://api.line.me/v2/bot/message/reply/'

    Authorization = 'Bearer {}'.format(Line_Access_Token)
    headers = {
        'Content-Type': 'application/json; char=UTF-8',
        'Authorization': Authorization
    }

    data = {
        "replyToken": Reply_token,
        "messages": [{
            "type": "text",
            "text": TextMessage
        }]
    }
    data = json.dumps(data)  # Convert to JSON
    r = requests.post(LINE_API, headers=headers, data=data)
    return 200

if __name__ == '__main__':
    app.run()
