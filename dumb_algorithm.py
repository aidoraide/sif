import json

from const import TAGS_OF_INTEREST

with open('tagged_questions_of_interest.json') as f:
    questions = json.load(f)

correct, total, multi_total, multi_correct = 0, 0, 0, 0

for id, q in questions.items():
    title = q['title'].lower()
    body = q['body'].lower()
    predictions = [tag for tag in TAGS_OF_INTEREST if tag in title or tag in body]
    if len(q['tags']) > 1:
        multi_total += 1
    if predictions == q['tags']:
        correct += 1
        if len(q['tags']) > 1:
            multi_correct += 1
    # elif predictions:
    #     print(f'Bad prediction of {predictions}')
    #     print(f'Gud prediction is {q["tags"]}\n')
    total += 1

print(f'Dumb Algorithm got {correct} correct out of {total} ({100.0 * correct / total}%)')
print(f'There were {multi_total} posts with multiple tags. That is {100.0 * multi_total / total}% of all posts.')
print(
    f'Of all multiple tag posts Dumb Algorithm got {multi_correct} correct ({100.0 * multi_correct / multi_total}% for multi tag posts)')
print(
    f'Of all single tag posts Dumb Algorithm got {correct - multi_correct} correct ({100.0 * (correct - multi_correct) / (total - multi_total)}% for single tag posts)')