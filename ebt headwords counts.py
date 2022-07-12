#!/usr/bin/env python3.10
# coding: utf-8

from os import sep
import pandas as pd
import pickle
import re
from timeis import timeis, tic, toc, yellow, line, green, white

tic()
print(f"{timeis()} {yellow}ebt headword pos counts")
print(f"{timeis()} {line}")

def setup():
	print(f"{timeis()} {green}setting up df's and dicts")
	
	# ebts counts df

	ebṭ_counts_df = pd.read_csv(
		"../frequency maps/output/word count csvs/ebts.csv", sep="\t", header=None)
	# print(ebṭ_counts_df)

	# dpd df

	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype = str)
	dpd_df.fillna("", inplace=True)
	# print(dpd_df)

	# all inflections dict

	with open("../inflection generator/output/all inflections dict", "rb") as p:
		all_inflections_dict = pickle.load(p)
	# print(all_inflections_dict)

	# sandhi matches df

	sandhi_matches_df = pd.read_csv(
		"../inflection generator/output/sandhi/matches sorted.csv", sep="\t")
	# print(sandhi_matches_df)

	sandhi_matches_dict = {}
	for row in range(len(sandhi_matches_df)):
		sandhi = sandhi_matches_df.loc[row, "word"]
		if sandhi not in sandhi_matches_dict.keys():
			sandhi_split = sandhi_matches_df.loc[row, "split"]
			sandhi_split = re.sub(r" \+ ", "-", sandhi_split)
			sandhi_matches_dict[sandhi] = sandhi_split
	sandhi_matches_dict_df = pd.DataFrame.from_dict(sandhi_matches_dict, orient="index")
	sandhi_matches_dict_df.to_csv("output/sandhi_matches.csv", sep="\t", header =None)


	# make headwords pos count dict
	headwords_pos_count_dict = {}

	# for headword in all_inflections_dict:
	# 	headword_clean = re.sub(" \d*$", "", headword)
	# 	pos = all_inflections_dict[headword]['pos']
	# 	headword_pos = f"{headword_clean}_{pos}"

	pos_exceptions = ["ve", "letter", "cs", "prefix", "suffix", "root", "sandhi", "idiom"]

	for row in range(len(dpd_df)):
		headword = dpd_df.loc[row, "Pāli1"]
		headword_clean = re.sub(" \d*$", "", headword)
		pos = dpd_df.loc[row, "POS"]
		headword_pos = f"{headword_clean}_{pos}"
		stem = dpd_df.loc[row, "Stem"]
		pattern = dpd_df.loc[row, "Pattern"]
		inflections = all_inflections_dict[headword]["inflections"]

		if (not re.findall ("!", stem) and 
		pos not in pos_exceptions and
		headword_pos not in headwords_pos_count_dict):
			headwords_pos_count_dict[headword_pos] = {'headword':headword_clean, 'pos': pos, 'pattern':pattern, 'inflections': inflections, 'count': 0, 'found':{}}
	# print(len(headwords_pos_count_dict))
	# counter = 0
	# for word in headwords_pos_count_dict.items():
	# 	if counter < 20:
	# 		print (word)
	# 		counter+=1

	return ebṭ_counts_df, dpd_df, all_inflections_dict, sandhi_matches_dict, headwords_pos_count_dict


ebṭ_counts_df, dpd_df, all_inflections_dict, sandhi_matches_dict, headwords_pos_count_dict = setup()


def step1_clean_inflection():
	print(f"{timeis()} {green}finding clean inflections")
	not_matched_dict = {}
	ebt_length = len(ebṭ_counts_df)
	for row in range(30000):  # lebt_length
		flag = False
		inflected_word = ebṭ_counts_df.iloc[row, 0]
		value = ebṭ_counts_df.iloc[row, 1]
		if row %1000==0:
			print(f"{timeis()} {white}{row}/{ebt_length}\t{inflected_word} {value}")

		for headword in headwords_pos_count_dict:
			if inflected_word in headwords_pos_count_dict[headword]['inflections']:
				headwords_pos_count_dict[headword]['count'] += value
				headwords_pos_count_dict[headword]['found'][inflected_word] = value
				flag = True
		if flag == False:
			not_matched_dict[inflected_word] = value

	print(f"{timeis()} {green}saving csvs")

	# df = pd.DataFrame.from_dict(headwords_pos_count_dict, orient="index")
	# df.sort_values("count", inplace=True, ascending=False)
	# df.drop("inflections", axis="columns", inplace=True)
	# df.to_csv("output/headword pos count1.csv", sep="\t")
	
	not_matched_df = pd.DataFrame.from_dict(not_matched_dict, orient="index")
	not_matched_df.to_csv("output/not matched.csv", sep="\t", header=None)

	# print(not_matched)
	# print(len(not_matched))

	return headwords_pos_count_dict, not_matched_dict
	

headwords_pos_count_dict, not_matched_dict = step1_clean_inflection()


def step2_split_sandhis():
	print(f"{timeis()} {green}splitting sandhis")

	flag = False
	still_unmatched_dict = {}
	matched = []
	for not_matched in not_matched_dict:
		print(f"{timeis()} {white}{not_matched}")
		value = not_matched_dict[not_matched]
		if not_matched in sandhi_matches_dict:
			sandhi_words = sandhi_matches_dict[not_matched].split("-")
			for sandhi_word in sandhi_words:
				for headword in headwords_pos_count_dict:
					if sandhi_word in headwords_pos_count_dict[headword]['inflections']:
						headwords_pos_count_dict[headword]['count'] += value
						matched.append(not_matched)
						flag = True
						if sandhi_word in headwords_pos_count_dict[headword]['found']:
							headwords_pos_count_dict[headword]['found'][sandhi_word] += value							
						else:
							headwords_pos_count_dict[headword]['found'][sandhi_word] = value
								
				if flag == False:
					still_unmatched_dict[not_matched] = value


	# print(f"{timeis()} {green}not_matched_dict")
	# for key, value in not_matched_dict.items():
	# 	print(f"{timeis()} {white}{key} {value}")
	
	print(f"{timeis()} {green}still unmatched")
	for key, value in still_unmatched_dict.items():
		print(f"{timeis()} {white}{key} {value}")

	df = pd.DataFrame.from_dict(headwords_pos_count_dict, orient="index")
	df.sort_values("count", inplace=True, ascending=False)
	df.drop("inflections", axis="columns", inplace=True)
	df.to_csv("output/headword pos count.csv", sep="\t")

step2_split_sandhis()


toc()