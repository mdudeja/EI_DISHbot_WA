from pywa import WhatsApp
from pywa.types import Message, SectionList, Section, SectionRow, CallbackSelection
from fastapi import FastAPI
from pywa import filters as fil
import uvicorn
from Fetcher.Fetcher import Fetcher
from config import settings


selected_language_code = 'en'

supported_languages = [
    {"label": 'English', "code": 'en'},
    {"label": 'Hindi', "code": 'hi'},
    {"label": 'Kannada', "code": 'kn'},
]

fetcher = Fetcher(
    answer_endpoint=settings.answer_endpoint,
    translate_endpoint=settings.translate_endpoint,
    session_id=settings.session_id,
    access_token=settings.access_token
)

app = FastAPI()

wa = WhatsApp(
    phone_id=settings.phone_id,
    token=settings.token,
    server=app,
    callback_url=settings.callback_url,
    verify_token=settings.verify_token,
    app_id=settings.app_id,
    app_secret=settings.app_secret
)


@wa.on_message(fil.matches('hello', 'hi', ignore_case=True))
def handle_hello_message(wa: WhatsApp, message: Message):
    print("RECEIVED MESSAGE ------------------->")
    print(message.from_user.name)
    print(message.text)
    message.react('👋')  # React with a waving hand emoji
    message.reply(
        f'Hello, {message.from_user.name}! I am DISHBot from Enable India. You can ask me questions.')
    wa.send_message(message.from_user.wa_id,
                    f'{message.from_user.name}, your default language is set to English. Please type CL to change it')
    message.stop_handling()


@wa.on_message(fil.matches('CL', ignore_case=True))
def handle_change_language(wa: WhatsApp, message: Message):
    print("RECEIVED MESSAGE ------------------->")
    print(message.from_user.name)
    print(message.text)

    wa.send_message(
        to=message.from_user.wa_id,
        header='Please select your preferred language',
        text='Select your preferred language from the list below',
        buttons=SectionList(
            button_title='Select Language',
            sections=[
                Section(
                    title='Supported Languages',
                    rows=[
                        SectionRow(
                            title=language['label'],
                            callback_data='ls:' + language['code'],
                        ) for language in supported_languages
                    ]
                )
            ]
        )
    )

    message.stop_handling()


@wa.on_callback_selection(fil.startswith('ls:'))
def handle_language_selection(wa: WhatsApp, sel: CallbackSelection):
    global selected_language_code
    print("RECEIVED CALLBACK ------------------->")
    print(sel.data)
    selected_language_code = sel.data.split(':')[1]
    sel.stop_handling()


@wa.on_message(fil.text)
def handle_text_message(wa: WhatsApp, message: Message):
    print("RECEIVED MESSAGE ------------------->")
    print(message.from_user.name)
    print(message.text)

    if selected_language_code == 'en':
        answer = fetcher.answer(message.text)
    else:
        answer = fetcher.non_eng_answer(message.text, selected_language_code)

    print("SENDING ANSWER ------------------->")
    print(answer)
    message.reply(answer)


if __name__ == '__main__':
    uvicorn.run(app, port=8080)


import http.client
import mimetypes
from codecs import encode

conn = http.client.HTTPSConnection("enablesolutions.org")
dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=source_lang;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode("hi"))
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=target_lang;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode("en"))
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=text;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode("मेरा बेटा पढ़ाई नहीं कर सकता"))
dataList.append(encode('--'+boundary+'--'))
dataList.append(encode(''))
body = b'\r\n'.join(dataList)
payload = body
headers = {
  'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJyNnI3QTRtNlFIYzR6VFBkMnpiMTJWYVdCSl9BOW9teWFORV92eFpncmtnIn0.eyJleHAiOjE3MjI0MjA5ODksImlhdCI6MTcyMjQyMDY4OSwiYXV0aF90aW1lIjoxNzIyNDIwNjg5LCJqdGkiOiJjNTQyNDNjNy0zZWFjLTQ4YmEtYjc0YS1iMzk4MDk5ZTU1OGEiLCJpc3MiOiJodHRwczovL2VuYWJsZXNvbHV0aW9ucy5vcmcvYXV0aC9yZWFsbXMvR29vZ2xlQXV0aCIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJiYjEyZTljNC04YTZjLTQ0MjctYWRiYi1lYTU5NWRlZjE0NjEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJESVNIYm90Iiwibm9uY2UiOiJhMjg2NmEyNy00ZTA4LTQzMzAtYWM5OS02ZjI1MDhhMjlhNDUiLCJzZXNzaW9uX3N0YXRlIjoiYjIwMTEyOWEtZjk1MS00ZDhkLTg0MmMtZTE2M2M4OGZkNzljIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJlaV9hZG1pbiIsIm9mZmxpbmVfYWNjZXNzIiwiZGVmYXVsdC1yb2xlcy1nb29nbGVhdXRoIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJESVNIYm90Ijp7InJvbGVzIjpbIk5DRl9BRE1JTiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsInNpZCI6ImIyMDExMjlhLWY5NTEtNGQ4ZC04NDJjLWUxNjNjODhmZDc5YyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IlByYWR5dW1uYSBOIiwicHJlZmVycmVkX3VzZXJuYW1lIjoicHJhZHl1bW5hQGtlbnBhdGguaW8iLCJnaXZlbl9uYW1lIjoiUHJhZHl1bW5hIiwiZmFtaWx5X25hbWUiOiJOIiwiZW1haWwiOiJwcmFkeXVtbmFAa2VucGF0aC5pbyJ9.XCQeww9FSlrnJgJ7qderpMDV-bT8iUCIFXbE9WzUkWXumeDC3ifygRnZzP2ilHGLBU61VgbiqjuPWR_hJayFyL11Z_Cv7k0Y9ecZv9WQWHMd1BXJOCnSM4VMJYb6iXmWsb3jxkiD_b0Jh_A93etmLBBJpTYKvyCEsoFVql7VbX7rGaJRLMDWiH-q2cHOge866bNXvMUxpDdDjkvvbV0lXbu3HNNWHaqmCEytsBlk6l6pjKtMfdjdHZbwXsgUpVOcvSSPS4YlYq_tS-Zec5SbkMrs_3aZwVopF3vE8cTh0tUNS21dNaD0XwRS-omGWUFKXu8blsji3OP2Fu6jj0wuNA',
  'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
}
conn.request("POST", "/dish-util/translate", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
