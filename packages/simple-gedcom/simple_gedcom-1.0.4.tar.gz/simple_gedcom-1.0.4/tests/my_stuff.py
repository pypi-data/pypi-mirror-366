from simple_gedcom import load_gedcom

gedcom = load_gedcom('data/tree.ged')

gedcom.save_person_list_to_csv()

gedcom.save_pedigree_to_csv()

gedcom.save_source_list_to_csv()

gedcom.save_person_source_list_to_csv()

# use pandas
import pandas as pd
pd.set_option('display.max_colwidth', 100)

person_list = gedcom.get_person_list()
df_person_list = pd.DataFrame(person_list)
print("PERSON LIST")
print(df_person_list.head())

sources = gedcom.get_source_list()
df_sources = pd.DataFrame(sources)
print("")
print("SOURCE LIST")
print(df_sources.head()) 

person_sources = gedcom.get_person_source_list()
df_person_sources = pd.DataFrame(person_sources)
print("")
print("PERSON SOURCES")
print(df_person_sources.head())


pedigree = gedcom.get_pedigree()
df_pedigree = pd.DataFrame(pedigree)
print("")
print("PEDIGREE")
print(df_pedigree.head())




found = gedcom.find_persons_by_name(first_name="Theodore")
df_found = pd.DataFrame(found)
print(df_found.head())

# pedigree = gedcom.get_pedigree()
pedigree = gedcom.get_pedigree("@I162694122750@")
df_pedigree = pd.DataFrame(pedigree)
print("")
print("PEDIGREE")
print(df_pedigree.head())
