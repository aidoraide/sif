import json
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super(MyHTMLParser, self).__init__()
        self.text_list = []
        self.tag_stack = []
        self.data_buffer = []

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        # print(f'Handle end tag {tag} with start tag {self.tag_stack[-1]} and data buffer {self.data_buffer}')
        assert tag == self.tag_stack[-1]
        self.tag_stack.pop()
        if tag == 'code':
            self.text_list.append('\nThis is code.\n')
        else:
            self.text_list.append(''.join(self.data_buffer))
        self.data_buffer = []

    def handle_data(self, data):
        self.data_buffer.append(data)

    def clear(self):
        data = ''.join(self.text_list)
        assert not self.tag_stack
        self.text_list = []
        self.tag_stack = []
        self.data_buffer = []
        return data


parser = MyHTMLParser()

with open('tagged_questions_of_interest.json') as f:
    questions = json.load(f)

sub_sample = {}
for k, i in zip(questions, range(5)):
    sub_sample[k] = questions[k]

for k, v in sub_sample.items():
    html = v['body']
    parser.feed(html)
    print(f'===={k}====')
    print(parser.clear())