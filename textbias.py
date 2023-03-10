# gov = 여당 의원 발언에서 키워드가 언급된 전체 횟수
# not_gov = 여당 의원 발언에서 키워드가 언급되지 않은 전체 횟수
# opp = 야당 의원 발언에서 키워드가 언급된 전체 횟수
# not_opp = 야당 의원 발언에서 키워드가 언급되지 않은 전체 횟수

import csv
import re

handle_to_catlist = {}
categories = ['government', 'opposition']
word_counts = dict([(category, {}) for category in categories]) 
category_word_count = dict([(category, 0) for category in categories]) 
total_word_count = {}

with open("../data.csv", "rb") as f:
    reader = csv.reader(f)
    category_set = set(categories)
    for row in reader:
        handle_to_catlist[row[0].lower()] = list(set(row[3].split(", ")) & category_set)

with open("../news.csv", "rb") as f:
    reader = csv.reader(f)
    for row in reader:
        handle = row[0]
        if not handle: continue
        category_list = handle_to_catlist[handle.lower()]
        category_list = filter(lambda cat: cat in categories, category_list)
        if not category_list: continue
        all_words = " ".join(row[1:]).split()
        words = filter(lambda word: not word.startswith("http") and not word.startswith("@") and not word == "RT", all_words)
        words = map(lambda word: word.strip(".,!?';:+\"/><$@(){}-~[]&").lower(), words)
        for word in words:
            for category in category_list:
                word_counts[category].setdefault(word, 0)
                word_counts[category][word] += 1
                category_word_count[category] += 1
            total_word_count.setdefault(word, 0)
            total_word_count[word] += 1



chi_sq_by_word = dict([(word, 0) for word in total_word_count.keys()])
gov_word_list = []
opp_word_list = []
for word in total_word_count.keys():
    gov = word_counts['government'][word].get(word, 0)
    not_gov = category_word_count['government'][word] - gov
    opp = word_counts['opposition'][word].get(word, 0)
    not_opp = category_word_count['opposition'][word] - opp
    chi_sq = (gov*not_opp - opp*not_gov)**2 / ((gov + opp)*(gov + not_gov)*(opp + not_opp)*(not_gov + not_opp))
    chi_sq_by_word[word] = chi_sq
    if gov*not_opp - opp*not_gov > 0:
        gov_word_list.append(word)
    elif gov*not_opp - opp*not_gov < 0:
        opp_word_list.append(word)
    else:
        pass


with open("../chisquare.csv", "wb") as f:
    writer = csv.writer(f)
    for category in categories:
        word_chi_list = list(reversed(sorted(list(chi_sq_by_word[word].iteritems()), key=lambda x: x[1])))[:1500]
        word_chi_cat = []
        for word, chi in word_chi_list:
            word_chi_cat.append([word, chi, category])
        writer.writerows(word_chi_cat)
