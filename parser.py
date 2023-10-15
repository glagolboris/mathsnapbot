import aiohttp
from wolfram_alpha import WolframAlphaSolver


class Parser:
    def __init__(self, photo_in_base64):
        self.url_for_get_text = 'https://www.mathway.com/chat/editor'
        self.url_for_OCR = 'https://www.mathway.com/OCR'
        self.for_solve = 'https://www.mathway.com/chat/topics'
        self.base64_image = photo_in_base64

    async def run_solve(self):
        response_get_equation = await self.get_equation
        solver = WolframAlphaSolver(eq=response_get_equation)
        answer = solver.solve_eq
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url_for_OCR, headers=headers, data=data) as response:
                response_json = await response.json()
                if response_json['AsciiMath'].count(',') == 1:
                    return response_json['AsciiMath'].replace('{', '').replace('}', '').replace(':', '').replace('[', '').replace(']', '')
                else:
                    return response_json['AsciiMath'].replace('{', '').replace('}', '').replace(':', '')
