import json
import numpy as np
import spacy
import pickle

nlp = spacy.load('en_core_web_md', disable=['parser', 'tagger', 'ner'])

def get_sentence_embedding(sentence, word2weight):
    doc = nlp(sentence)
    embedding = np.zeros(doc.vector.shape)
    for token in doc:
        word = token.lower_
        weight = word2weight[word] if word in word2weight else 0
        embedding += token.vector * weight
    embedding /= len(doc)
    return embedding

with open('word_to_weight.json') as f:
    word2weight = json.load(f)

with open('tagged_questions_of_interest.json') as f:
    questions = json.load(f)

id2embeddings = {}
print('Spacy loaded. Beginning processing.')

chunk = 1
for id, q in questions.items():
    # id2embeddings[id] = {'title': [get_sentence_embedding(s, word2weight) for s in q['title'].split('.') if s],
    #                      'body':  [get_sentence_embedding(s, word2weight) for s in q['body'].split('.') if s],
    #                      'tags': q['tags']}
    id2embeddings[id] = {'title': [get_sentence_embedding(q['title'], word2weight)],
                         'body':  [get_sentence_embedding(q['body'], word2weight)],
                         'tags': q['tags']}
    print(' ' * 50, end='\r')
    print(f'Progress: {100.0 * (len(id2embeddings) + (10 * (chunk-1)))/len(questions):.3f}%', end='\r')
    if len(id2embeddings) >=  len(questions) / 10:
        print(' ' * 30)
        print(f'Saving chunk {chunk}')
        with open(f'questions_as_embeddings{chunk}.pkl', 'wb') as f:
            pickle.dump(id2embeddings, f)
        del id2embeddings
        id2embeddings = {}
        chunk += 1


if id2embeddings:
    print(' ' * 30)
    print(f'Saving chunk {chunk}')
    with open(f'questions_as_embeddings{chunk}.pkl', 'wb') as f:
        pickle.dump(id2embeddings, f)

