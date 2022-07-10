text = open("text.txt", 'r')

out = "{"

temp = ""

lens = []

for line in text:
    temp = line
    lens.append(len(line))
    out = out + '"' + line[:-1] + '", '

out = out[:-3]
out = out + temp[-1]
out = out + '"}'

print(max(lens))
print(out)
