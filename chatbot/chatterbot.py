try:
    from scholarly import scholarly
    import httpx
except ImportError as e:
    print(f"ImportError: {e}. Please ensure you have the required packages installed.")

def fetch_scholar_data(query, num_results=10):
    try:
        search_query = scholarly.search_pubs(query)
        papers = []
        for i in range(num_results):
            paper = next(search_query)
            # print(paper['bib'])
            papers.append({
                'title': paper.bib['title'],
                'abstract': paper.bib.get('abstract', ''),
                'author': ', '.join(paper.bib.get('author', [])),
                'venue': paper.bib.get('venue', ''),
                'year': paper.bib.get('pub_year', '')
            })
            # print({"papers":papers})
        return papers
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
query = "sustainability and ESG"
papers = fetch_scholar_data(query)
# print(papers)
for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Abstract: {paper['abstract']}")
    print(f"Authors: {paper['author']}")
    print(f"Venue: {paper['venue']}")
    print(f"Year: {paper['year']}")
    print("\n")
