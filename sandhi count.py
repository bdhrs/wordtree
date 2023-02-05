from os import error
import pandas as pd
import pickle
import re
from timeis import timeis, tic, toc, yellow, line, green, white, red

# 1. make a list of all sandhis in dpd + sandhi splitter
# 2. count freq of that list in ebts
# 3. add construction

def setup_sandhi_freq_dict():
	print(f"{timeis()} {green}setting up sandhi freq dict", end = " ")
	with open("../inflection generator/output/all inflections dict", "rb") as p:
		all_inflections_dict = pickle.load(p)
	
	sandhi_freq_dict = {}
	for headword, details in all_inflections_dict.items():
		test1 = details["pos"] == "sandhi"
		test2 = details["pos"] == "sandhix"
		if test1 or test2:
			# print(headword, details["pos"])
			headword = re.sub(" \\d.*$", "", headword)
			sandhi_freq_dict[headword] = {"count":0, "construction":"" }
	
	print(f"{white}{len(sandhi_freq_dict)}")
	return sandhi_freq_dict


def setup_sandhi_construction_dict():
	print(f"{timeis()} {green}setting up sandhi construction dict", end=" ")
	with open("../inflection generator/output/sandhi dict", "rb") as pf:
		sandhi_construction_dict = pickle.load(pf)
	print(f"{white}{len(sandhi_construction_dict)}")
	return sandhi_construction_dict


def setup_ebt_counts_df():
	print(f"{timeis()} {green}setting up ebts counts dict", end=" ")
	ebt_counts_dict = {}
	ebt_counts_df = pd.read_csv("../frequency maps/output/word count csvs/ebts.csv", sep="\t", header=None)
	print(f"{white}{len(ebt_counts_df)}")
	for row in range(len(ebt_counts_df)):
		word = ebt_counts_df.loc[row, 0]
		count = ebt_counts_df.loc[row, 1]
		ebt_counts_dict[word] = count
	return ebt_counts_dict


def setup_dpd_df():
	print(f"{timeis()} {green}setting up dpd df", end=" ")
	dpd_df = pd.read_csv("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df.fillna("", inplace=True)
	print(f"{white}{len(dpd_df)}")
	return dpd_df


def add_sandhi_freq():
	print(f"{timeis()} {green}adding sandhi freq", end=" ")
	for headword in ebt_counts_dict:
		if headword in sandhi_freq_dict:
			sandhi_freq_dict[headword]["count"] = ebt_counts_dict[headword]

	print(f"{white}{len(sandhi_freq_dict)}")

	print(f"{timeis()} {green}removing sandhis not in ebts", end=" ")
	for headword in sandhi_freq_dict.copy():
		if sandhi_freq_dict[headword]["count"] == 0:
			sandhi_freq_dict.pop(headword)
	print(f"{white}{len(sandhi_freq_dict)}")

	return sandhi_freq_dict


def add_construction():
	print(f"{timeis()} {green}adding constructions from dpd", end=" ")
	
	dpd_count = 0
	dpd_errors = []
	sandhi_count = 0
	sandhi_errors = []

	for row in range(len(dpd_df)):
		pos = dpd_df.loc[row, "POS"]
		if pos == "sandhi":
			headword = dpd_df.loc[row, "Pāli1"]
			headword_clean = re.sub(" \\d.*$", "", headword)
			construction = dpd_df.loc[row, "Construction"]
			if construction != "":
				try:
					sandhi_freq_dict[headword_clean]["construction"] = construction
					dpd_count += 1
				except KeyError as e:
					dpd_errors += [headword]
	
	print(f"{white}{dpd_count} {green}remaining {white}{len(sandhi_freq_dict) - dpd_count}")

	print(f"{timeis()} {green}adding constructions from sandhi splitter", end=" ")
	for headword in sandhi_freq_dict:
		if sandhi_freq_dict[headword]["construction"] == "":
			try:
				construction = sandhi_construction_dict[headword]
				construction = re.sub("<br>", "\n", construction)
				sandhi_freq_dict[headword]["construction"] = construction
				sandhi_count += 1
			except KeyError as e:
				sandhi_errors += [headword]
	print(f"{white}{sandhi_count} {green}")
	print(f"{timeis()} {green}dpd errors {white}{len(dpd_errors)} ")
	print(f"{timeis()} {green}sandhi errors {white}{len(sandhi_errors)} ")
	
	sandhi_freq_df = pd.DataFrame.from_dict(sandhi_freq_dict, orient="index")
	sandhi_freq_df.sort_values(by=["count"], ascending=False, inplace=True)
	sandhi_freq_df.to_csv("output/sandhi freq in ebts.tsv", sep="\t")


tic()
print(f"{timeis()} {yellow}sandhi counts")
print(f"{timeis()} {line}")
sandhi_freq_dict = setup_sandhi_freq_dict()
sandhi_construction_dict = setup_sandhi_construction_dict()
ebt_counts_dict = setup_ebt_counts_df()
dpd_df = setup_dpd_df()
sandhi_freq_dict = add_sandhi_freq()
add_construction()
toc()


