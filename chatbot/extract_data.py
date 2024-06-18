# import requests
# from bs4 import BeautifulSoup
# from scholarly import scholarly

# def fetch_article_content(url):
#     try:
#         print({"url":url})
#         response = requests.get(url)
#         print({"url":response})
#         html_content = response.text
#         soup = BeautifulSoup(html_content, 'html.parser')
#         # Extract the article content based on the HTML structure
#         print({"sou^p":soup})
#         print({"soup.find('div', class_='article-content')":soup.find('div', class_='article-content')})
#         article_content = soup.find('div', class_='article-content').get_text()
#         return article_content
#     except Exception as e:
#         print(f"An error occurred while fetching article content: {e}")
#         return ''

# def fetch_scholar_data(query, num_results=10):
#     try:
#         search_query = scholarly.search_pubs(query)
#         papers = []
#         for i in range(num_results):
#             paper = next(search_query)
#             title = paper.bib.get('title', '')
#             abstract = paper.bib.get('abstract', '')
#             author_names = ', '.join(paper.bib.get('author', []))
#             venue = paper.bib.get('venue', '')
#             year = paper.bib.get('pub_year', '')

#             # Fetch the URL of the article (if available)
#             url = paper.bib.get('url', '')

#             # If URL is available, fetch the content of the article
#             article_content = fetch_article_content(url) if url else ''
#             print({"article_content":article_content})
#             papers.append({
#                 'title': title,
#                 'abstract': abstract,
#                 'author': author_names,
#                 'venue': venue,
#                 'year': year,
#                 'content': article_content
#             })
#         return papers
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return []

# # Example usage
# query = "sustainability and ESG"
# papers = fetch_scholar_data(query)
# # for paper in papers:
# #     print(f"Title: {paper['title']}")
# #     print(f"Abstract: {paper['abstract']}")
# #     print(f"Authors: {paper['author']}")
# #     print(f"Venue: {paper['venue']}")
# #     print(f"Year: {paper['year']}")
# #     print(f"Content: {paper['content']}")
# #     print("\n")
from scholarly import scholarly
import requests
from bs4 import BeautifulSoup

def fetch_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Attempt to find the article content based on common HTML structures
        article_content = ''

        # Try to extract text from known tags used for article content
        possible_tags = [
            'div.article', 'div.content', 'div.post-content', 
            'div.entry-content', 'section', 'article',
            "meta.content"
        ]

        for tag in possible_tags:
            content_div = soup.select_one(tag)
            if content_div:
                article_content = content_div.get_text()
                # break
        
        # Fallback to getting all text content
        if not article_content:
            article_content = soup.get_text()

        return article_content.strip()
    except Exception as e:
        print(f"An error occurred while fetching article content: {e}")
        return ''

def fetch_scholar_data(query, num_results=10):
    try:
        search_query = scholarly.search_pubs(query)
        papers = []
        for i in range(num_results):
            paper = next(search_query)
            title = paper.bib.get('title', '')
            abstract = paper.bib.get('abstract', '')
            author_names = ', '.join(paper.bib.get('author', []))
            venue = paper.bib.get('venue', '')
            year = paper.bib.get('pub_year', '')

            # Fetch the URL of the article (if available)
            url = paper.bib.get('url', '')

            # If URL is available, fetch the content of the article
            article_content = fetch_article_content(url) if url else ''
            
            papers.append({
                'title': title,
                'abstract': abstract,
                'author': author_names,
                'venue': venue,
                'year': year,
                'content': article_content
            })
        return papers
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def add_to_corpus(papers, corpus_file):
    try:
        with open(corpus_file, 'a', encoding='utf-8') as f:
            for paper in papers:
                f.write(f"Title: {paper['title']}\n")
                f.write(f"Abstract: {paper['abstract']}\n")
                f.write(f"Authors: {paper['author']}\n")
                f.write(f"Venue: {paper['venue']}\n")
                f.write(f"Year: {paper['year']}\n")
                f.write(f"Content: {paper['content']}\n")
                f.write("\n---\n\n")
    except Exception as e:
        print(f"An error occurred while writing to the corpus: {e}")

# Example usage
query = "sustainability and ESG"
corpus_file = 'corpus.txt'
papers = fetch_scholar_data(query)
add_to_corpus(papers, corpus_file)

# Print the results
for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Abstract: {paper['abstract']}")
    print(f"Authors: {paper['author']}")
    print(f"Venue: {paper['venue']}")
    print(f"Year: {paper['year']}")
    print(f"Content: {paper['content']}")
    print("\n")
