import csv

with open('eggs.csv', 'a', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])  # Writes: Spam,Spam,Spam,Spam,Spam,Baked Beans
    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])  # Writes: Spam,Lovely Spam,Wonderful Spam
    row=['a']
    n=1
    while n<=3:
        row.extend(['b','a'])
        n+=1
    spamwriter.writerow(row)