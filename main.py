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
