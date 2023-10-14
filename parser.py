import re
import aiohttp
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, session, photo_in_base64):
        self.session: aiohttp.ClientSession = session
        self.url_for_get_text = 'https://www.mathway.com/chat/editor'
        self.url_for_OCR = 'https://www.mathway.com/OCR'
        self.for_solve = 'https://www.mathway.com/chat/topics'
        self.base64_image = photo_in_base64

    async def run_solve(self):
        response_get_equation = await self.get_equation
        response_get_editor = self.get_editor(response_get_equation)
        answer = await self.solve_eq(await response_get_editor, response_get_equation)
        return answer

    @property
    async def get_equation(self) -> str:
        data = {
            'imageData': f'data:image/png;base64,{self.base64_image.decode("utf-8")}',
            'culture': 'ru'
        }
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'accept-encoding': 'gzip, deflate, br',
            'referer': 'https://www.mathway.com/ru/Algebra',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'x-requested-with': 'XMLHttpRequest'
        }

        async with self.session.post(url=self.url_for_OCR, headers=headers, data=data) as response:
            response_json = await response.json()
            print(response_json)
            if response_json['AsciiMath'].count(',') == 1:
                return response_json['AsciiMath'].replace('{', '').replace('}', '').replace(':', '').replace(',', '\n').replace('[', '').replace(']', '')
            else:
                return response_json['AsciiMath'].replace('{', '').replace('}', '').replace(':', '')

    async def get_editor(self, response_get_equation) -> tuple:
        json_data = {"metadata": {
            "route": "en",
            "version": "3.1.7"},
            "subject": "Algebra",
            "asciiMath": response_get_equation,
            "isOCR": True,
        }

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'x-requested-with': 'XMLHttpRequest',
            'referer': 'https://www.mathway.com/ru/Algebra',
            'origin': 'https://www.mathway.com'
        }

        async with self.session.post(url=self.url_for_get_text, headers=headers, json=json_data) as response:
            response_json = await response.json()
            return response_json['topics'][0]['Text'], response_json['topics'][0]['Id']

    async def solve_eq(self, response_get_editor, response_get_equation):
        json_data = {"metadata": {"userId": 0,
                                  "acceptLanguages": "ru",
                                  "route": "ru",
                                  "version": "3.1.7",
                                  },
                     "topicId": f"{response_get_editor[1]}",
                     "topicText": response_get_editor[0],
                     "subject": "Algebra",
                     "asciiMath": response_get_equation,
        }

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'content-type': 'application/json',
            'referer': 'https://www.mathway.com/Algebra',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'x-requested-with': 'XMLHttpRequest'
        }

        async with self.session.post(url=self.for_solve, headers=headers, json=json_data) as response:
            response_json = await response.json()
            answer_in_html_tags = re.findall('<math>(.*?)</math>', response_json['messages'][0]['content'])
            solution_method_soup = BeautifulSoup(response_json['messages'][0]['content'], 'html.parser')
            solution_method = solution_method_soup.find('div', class_='Explanation').text
            answer: str = f'{solution_method}\n'
            for ans in answer_in_html_tags:
                print(BeautifulSoup(ans, 'html.parser').text)
                if re.search('×', BeautifulSoup(ans, 'html.parser').text):
                    continue
                else:
                    answer += f"{BeautifulSoup(ans, 'html.parser').text};"
            return answer
