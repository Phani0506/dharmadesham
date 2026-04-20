import csv
for split in ['train_full', 'dev', 'test']:
 with open(f'itihasa/{split}.sn.csv', 'r', encoding='utf-8') as f:
  count = sum(1 for line in f if '??????' in line)
  print(f'{split}: {count}')
