import csv

with open('Tags.csv') as f:
    reader = csv.reader(f)
    counts = {}
    for id, tag in reader:
        if tag not in counts:
            counts[tag] = 0
        counts[tag] += 1
    l = [(count, tag) for tag, count in counts.items()]
    l.sort(reverse=True)
    print(f'\n{"Tag":<30}|Count')
    print('=' * 30 + '|' + '=' * 10)
    for count, tag in l[:100]:
        print(f'{tag:<30}|{count}')

    print([tag for count, tag in l[1:100]])