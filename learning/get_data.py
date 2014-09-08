import json
with open('raw_data.txt') as f:
    lines = f.readlines()
X = list()
Y = list()
for line in lines[:-1]:
    nums = line.split(',')
    x = [int(num) for num in nums[:-1]]
    y = int(num[-1])
    X.append(x)
    Y.append(y)

with open('bigX.json', 'w') as f:
    json.dump(X, f)
with open('bigY.json', 'w') as f:
    json.dump(Y, f)
