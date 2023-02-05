import pickle
import re
import pandas as pd
from timeis import timeis, tic, toc, yellow, line, green, white, red
from dpd_db_tools import DpdDbTools

# 1. make a list of all compounds + compound type in dpd splitter
# 2. count freq of that list in ebts

db = DpdDbTools("../sqlite-db/dpd.db")
dpd_db = db.fetch_all()

def setup_compound_freq_dict():
	print(f"{timeis()} {green}setting up compound freq dict", end = " ")
	compound_freq_dict = {}

	for data_row in dpd_db:
		w = db.RowData(data_row)
		test1 = re.findall("\\bcomp\\b", w.grammar)
		test2 = not re.findall("comp vb", w.grammar)
		test3 = w.pos != "prefix"
		if test1 and test2 and test3:
			if re.findall("\\d", w.compound_type):
				compound_freq_dict[w.pali1] = {"count": 0, "type": "", "inflections":[]}
			else:
				compound_freq_dict[w.pali1] = {"count": 0, "type": w.compound_type, "inflections": []}
	
	print(f"{white}{len(compound_freq_dict)}")
	return compound_freq_dict

def add_inflections():
	print(f"{timeis()} {green}adding inflections", end=" ")
	with open("../inflection generator/output/all inflections dict", "rb") as p:
		all_inflections_dict = pickle.load(p)
	
	counter = 0
	for headword, details in all_inflections_dict.items():
		if headword in compound_freq_dict:
			compound_freq_dict[headword]["inflections"] = all_inflections_dict[headword]["inflections"]
			counter += len(compound_freq_dict[headword]["inflections"])
	print(f"{white}{counter}")
	return compound_freq_dict


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


def add_compound_freq():
	print(f"{timeis()} {green}adding compound freq", end=" ")

	for headword in compound_freq_dict:
		unused = []
		for inflection in compound_freq_dict[headword]["inflections"]:
			if inflection in ebt_counts_dict:
				compound_freq_dict[headword]["count"] += ebt_counts_dict[inflection]
			else:
				unused += [inflection]
		for un in unused:
			compound_freq_dict[headword]["inflections"].remove(un)

	print(f"{white}{len(compound_freq_dict)}")

	print(f"{timeis()} {green}removing compounds not in ebts", end=" ")
	for headword in compound_freq_dict.copy():
		if compound_freq_dict[headword]["count"] == 0:
			compound_freq_dict.pop(headword)
	print(f"{white}{len(compound_freq_dict)}")

	return compound_freq_dict

def save_csvs():
	compound_freq_df = pd.DataFrame.from_dict(compound_freq_dict, orient="index")
	compound_freq_df.sort_values(by=["count"], ascending=False, inplace=True)
	compound_freq_df.to_csv("output/compound freq in ebts.tsv", sep="\t")

tic()
print(f"{timeis()} {yellow}compound counts")
print(f"{timeis()} {line}")
compound_freq_dict = setup_compound_freq_dict()
compound_freq_dict = add_inflections()
ebt_counts_dict = setup_ebt_counts_df()
compound_freq_dict = add_compound_freq()
save_csvs()
toc()


