#!/usr/bin/env python -Btt

"""  Given a input of email ID's and IAM usernames, The script will find
     their email address and write to a new file in the same order.
     If email is not found, NA will be written """

with open("iamusers.txt") as f_in:
    user_list = list(line for line in (l.strip() for l in f_in) if line)

with open("email.txt") as f_in:
    email_list = list(line for line in (l.strip() for l in f_in) if line)


dictmap = {}
for item in email_list:
    iam = item.split("@")[0].replace(".","")
    dictmap[iam] = item


with open('output.txt', 'w') as f:
    for user in user_list:
        if user in dictmap:
           f.write("%s\n" % dictmap[user])
        else:
           f.write("NA\n")
