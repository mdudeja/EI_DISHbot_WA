import requests
import http.client
from codecs import encode


class Fetcher:
    answer_endpoint = None
    translate_endpoint = None
    session_id = None
    access_token = None

    def __init__(self, answer_endpoint: str, translate_endpoint: str, session_id: str = None, access_token: str = None):
        self.answer_endpoint = answer_endpoint
        self.translate_endpoint = translate_endpoint
        self.session_id = session_id
        self.access_token = access_token

    def answer(self, question: str):
        response = requests.get(
            self.answer_endpoint,
            params={'q': question, 'session_id': self.session_id},
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'authorization': f'Bearer {self.access_token}'
            }
        )
        json_val = response.json()
        return json_val['answer']

    def translate(self, text: str, source_lang: str, target_lang: str):
        conn = http.client.HTTPSConnection("enablesolutions.org")
        data_list = []
        boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
        data_list.append(encode('--' + boundary))

        data_list.append(encode('Content-Disposition: form-data; name=source_lang;'))
        data_list.append(encode('Content-Type: {}'.format('text/plain')))
        data_list.append(encode(''))
        data_list.append(encode(source_lang))
        data_list.append(encode('--' + boundary))

        data_list.append(encode('Content-Disposition: form-data; name=target_lang;'))
        data_list.append(encode('Content-Type: {}'.format('text/plain')))
        data_list.append(encode(''))
        data_list.append(encode(target_lang))
        data_list.append(encode('--' + boundary))

        data_list.append(encode('Content-Disposition: form-data; name=text;'))
        data_list.append(encode('Content-Type: {}'.format('text/plain')))
        data_list.append(encode(''))
        data_list.append(encode(text))
        data_list.append(encode('--' + boundary + '--'))

        data_list.append(encode(''))
        body = b'\r\n'.join(data_list)
        payload = body
        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
        }
        conn.request("POST", "/dish-util/translate", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8").strip()

    def non_eng_answer(self, question: str, source_lang: str):
        translated_question = self.translate(question, source_lang, 'en')
        answer = self.answer(translated_question)
        # Commenting this because this gives Internal Server Error from DISH
        # answer = self.translate(answer, 'en', source_lang)
        return answer
