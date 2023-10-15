import wolframalpha


class WolframAlphaSolver:
    def __init__(self, api_id='38XHLA-Q4RY9HJP9A', eq=''):
        self.client = wolframalpha.Client(api_id)
        self.eq = eq

    @property
    def solve_eq(self):
        res = self.client.query(self.eq)
        solution: str = ''
        for result in res['pod']:
            try:
                if type(result['subpod']) == list:
                    sub_sol = f'{result["@title"]}: '
                    for sub in result['subpod']:
                        sub_sol += f"{sub['plaintext']};"
                    solution += sub_sol
                else:
                    solution += f'{result["@title"]}: {result["subpod"]["plaintext"]};'
            except Exception:
                continue
        return solution.replace('\n', '').replace(';', '\n')
