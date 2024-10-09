import json 

with open("TestDataNonAsync.json", 'r') as f:
    data = json.load(f)


with open("fullData.json", 'r') as f:
    data2 = json.load(f)


title_set_1 = []
title_set_2 = []
for item in data:
    title_set_1.add(item['title'][0])

for item in data2:
    title_set_2.add(item['title'][0])

# print(f"Set of titles from non ")
for item in title_set_1 - title_set_2:
    print(item)