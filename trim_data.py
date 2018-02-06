import csv, json
from html.parser import HTMLParser
from const import TAGS_OF_INTEREST

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super(MyHTMLParser, self).__init__()
        self.text_list = []
        self.tag_stack = []
        self.data_buffer = []

    def handle_starttag(self, tag, attrs):
        if tag == 'code':
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'code':
            self.text_list.append('\n<code>\n')
            self.tag_stack.pop()
        else:
            self.text_list.append(''.join(self.data_buffer))
        self.data_buffer = []

    def handle_data(self, data):
        self.data_buffer.append(data)

    def get_clean_text(self):
        data = ''.join(self.text_list)
        self.text_list = []
        self.tag_stack = []
        self.data_buffer = []
        return data

id_to_tags = {}
id_to_question = {}

with open('Tags.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for id, tag in reader:
        if tag not in TAGS_OF_INTEREST:
            continue
        if id not in id_to_tags:
            id_to_tags[id] = []
        id_to_tags[id].append(tag)

for id, tags in id_to_tags.items():
    tags.sort()

with open('Questions.csv', encoding='Latin-1') as f:
    reader = csv.reader(f)
    next(reader)
    for Id,OwnerUserId,CreationDate,Score,Title,Body in reader:
        if Id not in id_to_tags:
            continue
        parser = MyHTMLParser()
        parser.feed(Body)
        body = parser.get_clean_text()
        id_to_question[Id] = {'title': Title, 'body': body, 'tags': id_to_tags[Id]}


with open('tagged_questions_of_interest.json', 'w') as outfile:
    json.dump(id_to_question, outfile)
