data=open("2.txt", "r").read()

# create a password from the data:

# The first character of the base value is the single most frequently occurring character in the signal.
# Each following character of the base value is the one that occurs the most frequently in the signal immediately after the previous character of the base value. For example, if the first character of the base value is A, then the second character of the base value is the one that occurs the most frequently immediately after A in the signal.
# The most frequently occurring character after the last character of the base value is ;.

occur_map={}
occur_counts={}
for i in range(len(data)-1): #-1 to exclude the last character
    if data[i] not in occur_map:
        occur_map[data[i]]={data[i+1]:1}
        occur_counts[data[i]]=1
    else:
        if data[i+1] not in occur_map[data[i]]:
            occur_map[data[i]][data[i+1]]=1
        else:
            occur_map[data[i]][data[i+1]]+=1
        occur_counts[data[i]]+=1

curr_char=max(occur_counts, key=occur_counts.get)
password=""+curr_char
while curr_char!=";":
    curr_char=max(occur_map[curr_char], key=occur_map[curr_char].get)
    password+=curr_char
print(password)