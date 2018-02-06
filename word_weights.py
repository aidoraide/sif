import json

def get_words(paragraph):
    sentences = paragraph.split('.')
    words = []
    for s in sentences:
        for w in s.split(' '):
            if w:
                words.append(w)
    return words

with open('tagged_questions_of_interest.json') as f:
    questions = json.load(f)

a = 1e-3
word_count = 0
word_to_count = {}
for id, question in questions.items():
    words = get_words(question['body'])
    words.extend(get_words(question['title']))
    for word in words:
        if word not in word_to_count:
            word_to_count[word] = 0
        word_to_count[word] += 1
    word_count += len(words)

word_to_weight = {word: a / (a + count/word_count) for word, count in word_to_count.items()}
with open('word_to_weight.json', 'w') as f:
    json.dump(word_to_weight, f)