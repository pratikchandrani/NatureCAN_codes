import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
# Plant Description data




file='Description_of_Plants_combined_excel.xlsx'
print(f"Plants Description Data File - {file}")
data=pd.read_excel(file)
print("-----------------------------------------------------")
# print(data.head(3))



print('Shape of Input Data : ',data.shape)
print("-----------------------------------------------------")
data1=data['Plant Name'][:3]  #Number of Plants
print(f"Top 5 Plants Names {data1.head()}") 
      
      
        
print("-----------------------------------------------------")

## Fetch Abstract using Plant name from PubMed
# No Abstracts Found - 
# data1=Ayurvedic Plants Data
plants = data1  #data1 = Plants_Names
results = []

for plant in plants:
    print(f"\n Searching for: {plant} AND cancer")

    # Step 1: Search PubMed
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": f"{plant} AND cancer", 

        "retmode": "json",
        "retmax": 5000 #maximum articles of 1 PMID
    }

    try:
        res = requests.get(search_url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])
        count = data.get("esearchresult", {}).get("count", "0")

        if not pmids:
            print(f" No articles found for: {plant}")
            results.append({
                "Plant Name": plant,
                "PMID": "N/A",
                "Abstract": "No article found"
            })
            continue

        print(f"Found {len(pmids)} of {count} articles")

        # Step 2: Loop through each PMID
        for pmid in pmids:
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml"
            }

            fetch_res = requests.get(fetch_url, params=fetch_params, timeout=10)
            soup = BeautifulSoup(fetch_res.text, "xml")

            abstract_tag = soup.find("AbstractText")
            if abstract_tag:
                abstract_text = abstract_tag.text.strip()
                results.append({
                    "Plant Name": plant,
                    "PMID": pmid,
                    "Abstract": abstract_text
                })
#                 print(f" Got abstract for PMID: {pmid}")
            else:
                results.append({
                    "Plant Name": plant,
                    "PMID": pmid,
                    "Abstract": "No abstract found"
                })
#                 print(f" No abstract for PMID: {pmid}")

    except requests.exceptions.RequestException as e:
#         print(f" Error while processing {plant}: {e}")
        results.append({
            "Plant Name": plant,
            "PMID": "N/A",
            "Abstract": f"Error: {e}"
        })


    
    
    
data1_1 = pd.DataFrame(results)
# data2=data1_1['PMID']

# print('Shape of PMID Abstract and Plant name is ,'data2.shape)
print("-----------------------------------------------------")

      
# Data Cleaning
import pandas as pd
print(f"Count of OG data is {data1_1.count()}")
data3=data1_1.copy()
print("--------------------------------------------------------------------")
print(f"Count of Copied data is {data3.count()}")   
print("--------------------------------------------------------------------")

      
data4 = data3.dropna(subset=["PMID"])# Or, using the inplace parameter:
print("Shape of data4 (Filtering data) is : ",data4.shape)
print("--------------------------------------------------------------------")
print("Count of data4 is (Filtering Data): ",data4.count())
print("--------------------------------------------------------------------")

      
      
# df4 is previous dataframe
data5=data4[['Plant Name','PMID']]
data6=data5[:] #Slicing - IF you wish to pass in sets
print(f"Length of PlantName and PMID is {len(data6)}")
print("--------------------------------------------------------------------")
      
      
      
      
      

    #EXTRATING Full Article data
import requests
from bs4 import BeautifulSoup

# EXTRACTING Full Article Data with "Cited by" info
import requests
from bs4 import BeautifulSoup

def get_pubmed_article_details(pmid):
    xml_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    xml_params = {"db": "pubmed", "id": pmid, "retmode": "xml"}

    try:
        xml_response = requests.get(xml_url, params=xml_params, timeout=10)
        xml_response.raise_for_status()
    except requests.RequestException as e:
        return {"PMID": pmid, "Error": f"XML fetch failed: {e}"}

    soup = BeautifulSoup(xml_response.content, "xml")
    article = soup.find("PubmedArticle")
    if not article:
        return {"PMID": pmid, "Error": "PubmedArticle tag not found"}

    def get_text(tag, parent=article):
        found = parent.find(tag) if parent else None
        return found.text.strip() if found else "Not available"

    def get_authors():
        authors = article.find_all("Author")
        return [f"{a.find('ForeName').text} {a.find('LastName').text}"
                for a in authors if a.find("ForeName") and a.find("LastName")] or ["Not available"]

    def get_mesh_terms():
        return [mh.DescriptorName.text for mh in article.find_all("MeshHeading")] or ["Not available"]

    def get_references():
        return [ref.Citation.text for ref in article.find_all("Reference") if ref.find("Citation")] or ["Not available"]

    def get_publication_types():
        return [pt.text for pt in article.find_all("PublicationType")] or ["Not available"]

    def get_substances():
        return [s.text for s in article.find_all("NameOfSubstance")] or ["Not available"]

    def get_related_pmids_info():
        return [
            f"{cc.get('RefType', 'Ref')}: {cc.PMID.text}" 
            for cc in article.find_all("CommentsCorrections") if cc.find("PMID")
        ] or ["Not available"]

    def get_doi():
        for aid in article.find_all("ArticleId"):
            if aid.get("IdType") == "doi":
                return aid.text
        return "Not available"

    # HTML part for Cited By and Full Text Sources
    html_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    try:
        html_response = requests.get(html_url, timeout=10)
        html_response.raise_for_status()
    except requests.RequestException as e:
        return {"PMID": pmid, "Error": f"HTML fetch failed: {e}"}

    html_soup = BeautifulSoup(html_response.content, "html.parser")

    def format_links(header_text):
        section = html_soup.find("h3", string=header_text)
        result = []
        if section:
            ul = section.find_next_sibling("ul")
            if ul:
                for li in ul.find_all("li"):
                    a_tag = li.find("a")
                    if a_tag:
                        name = a_tag.text.strip()
                        href = a_tag.get("href")
                        if href and not href.startswith("http"):
                            href = "https://pubmed.ncbi.nlm.nih.gov" + href
                        result.append(f"{name}: {href}")
        return ", ".join(result) if result else "Not available"

    def get_related_information():
        related_div = html_soup.find("h3", string="Related information")
        results = []
        if related_div:
            ul = related_div.find_next_sibling("ul")
            if ul:
                for li in ul.find_all("li"):
                    a = li.find("a")
                    if a:
                        name = a.text.strip()
                        href = a.get("href")
                        if href and not href.startswith("http"):
                            href = "https://pubmed.ncbi.nlm.nih.gov" + href
                        results.append(f"{name}: {href}")
        return ", ".join(results) if results else "Not available"

    def get_cited_by_articles():
        cited_by_section = html_soup.find("div", id="citedby")
        if not cited_by_section:
            return "Not available", []

        pmid_links = cited_by_section.find_all("a", class_="docsum-title", href=True)
        cited_pmids = []

        for link in pmid_links:
            href = link['href']
            if href.startswith("/"):
                href_parts = href.strip("/").split("/")
                for part in href_parts:
                    if part.isdigit():
                        cited_pmids.append(part)
                        break

        return len(cited_pmids), cited_pmids if cited_pmids else ["Not available"]


    # Get cited by info
    cited_by_count, cited_by_pmids = get_cited_by_articles()

    journal_tag = article.find("Journal")

    return {
        
        "Title": get_text("ArticleTitle"),
        "Journal": get_text("Title", journal_tag) if journal_tag else "Not available",
        "PMID": pmid,
        "DOI": get_doi(),
        "Authors": get_authors(),
        "Abstract": get_text("AbstractText", article.find("Abstract")) if article.find("Abstract") else "Not available",
        "Publication Types": get_publication_types(),
        "MeSH Terms": get_mesh_terms(),
        "Substances": get_substances(),
        "References": get_references(),
        "Related Information": get_related_pmids_info(),
        "Full Text Sources": format_links("Full Text Sources"),
        "Other Literature Sources": format_links("Other Literature Sources"),
        "Related Links Section": get_related_information(),
        "Cited By Count": cited_by_count,
        "Cited By PMIDs": cited_by_pmids
    }


# === Runner ===

pmid_list = data6['PMID']   #["37358060", "37830808", "36982585"]  # Add more PMIDs if needed

# all_articles = []
# for pmid in pmid_list:
# #     print(f"Fetching PMID: {pmid}")
#     result = get_pubmed_article_details(pmid)
#     all_articles.append(result)
    
    
    

    
    
# Runner - loop through each row of data6 (which has Plant Name and PMID)
all_articles = []

for idx, row in data6.iterrows():
    plant_name = row['Plant Name']
    pmid = str(row['PMID'])  # Ensure it's string
    
    result = get_pubmed_article_details(pmid)
    result["Plant Name"] = plant_name  # Add Plant Name before Title
    all_articles.append(result)
    
    
    
    
    
    
    
    
print("Total Articles fetched : ",len(all_articles))      
      
print("--------------------------------------------------------------------")
      
print("Total PMID fetched : ",len(pmid_list))



print("--------------------------------------------------------------------")

    #Save Data in 1 Dataframe
data7 = pd.DataFrame(all_articles)
data7.to_excel('Step1_Output.xlsx')
print("--------------------------------------------------------------------")
