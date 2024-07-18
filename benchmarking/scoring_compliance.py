import spacy
from PyPDF2 import PdfReader
from textblob import TextBlob

import pandas as pd

# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")

# Define your criteria for due diligence scoring
criteria = {
    "Long-term sustainability capital": ["robust sustainability capital", "increasing sustainability capital",
                                         "weak sustainability capital", "fragile sustainability capital"],
    "Perception of ESG criticality": ["strong perception with alignment in the strategy and operation",
                                      "some sense of ESG with integration efforts",
                                      "poor notion of ESG without any integration in the strategy and operations",
                                      "absence of ESG notions"],
    "Notion of Materiality": ["strong perception of material risks with existing strategy management",
                              "some notion of materiality with efforts to streamline a strategy",
                              "poor notion of materiality",
                              "absence of any materiality approach"],
    "Integration of ESG": ["strong integration of ESG in the strategy and operations",
                            "some integration of ESG in the strategy and operations",
                            "poor integration of ESG in the strategy and operations",
                            "absence of ESG integration"],
    "Risk Management": ["strong risk management with ESG integration",
                          "some risk management with ESG integration",
                          "poor risk management with ESG integration",
                          "absence of risk management with ESG integration"],
    "Innovation": ["strong innovation with ESG integration",
                     "some innovation with ESG integration",
                     "poor innovation with ESG integration",
                     "absence of innovation with ESG integration"],
    "Stakeholder Engagement": ["strong stakeholder engagement with ESG integration",
                                 "some stakeholder engagement with ESG integration",
                                 "poor stakeholder engagement with ESG integration",
                                 "absence of stakeholder engagement with ESG integration"],
    "Disclosure": ["strong disclosure with ESG integration",
                        "some disclosure with ESG integration",
                        "poor disclosure with ESG integration",
                        "absence of disclosure with ESG integration"],
    "Business Model": ["strong business model with ESG integration",
                        "some business model with ESG integration",
                        "poor business model with ESG integration",
                        "absence of business model with ESG integration"],
    "Human Capital": ["strong human capital with ESG integration",
                        "some human capital with ESG integration",
                        "poor human capital with ESG integration",
                        "absence of human capital with ESG integration"],
    "Social Capital": ["strong social capital with ESG integration",
                        "some social capital with ESG integration",
                        "poor social capital with ESG integration",
                        "absence of social capital with ESG integration"],
    "Natural Capital": ["strong natural capital with ESG integration",
                        "some natural capital with ESG integration",
                        "poor natural capital with ESG integration",
                        "absence of natural capital with ESG integration"],
    "Financial Capital": ["strong financial capital with ESG integration",
                        "some financial capital with ESG integration",
                        "poor financial capital with ESG integration",
                        "absence of financial capital with ESG integration"],
    "Physical Capital": ["strong physical capital with ESG integration",
                        "some physical capital with ESG integration",
                        "poor physical capital with ESG integration",
                        "absence of physical capital with ESG integration"],
    "Intellectual Capital": ["strong intellectual capital with ESG integration",
                        "some intellectual capital with ESG integration",
                        "poor intellectual capital with ESG integration",
                        "absence of intellectual capital with ESG integration"],
    "Relationship Capital": ["strong relationship capital with ESG integration",
                        "some relationship capital with ESG integration",
                        "poor relationship capital with ESG integration",
                        "absence of relationship capital with ESG integration"],
    "Data Management": ["strong data management with ESG integration",
                        "some data management with ESG integration",
                        "poor data management with ESG integration",
                        "absence of data management with ESG integration"],
}


def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity  # Get sentiment polarity score
    return sentiment_score

def check_due_diligence_def(document_text, criteria):
    print( criteria.items())
    doc = nlp(document_text)
    scores = {key: {"count": 0, "sentiment": 0} for key in criteria}  # Initialize scores to zero
    print("Computing due diligence scores...")
    for key, value in criteria.items():
        print("key",key)
        print("value",value)
        for term in value:
            term_lower = term.lower()
            scores[key]["count"] += document_text.lower().count(term_lower)
            print("term_lower",term_lower)
            print("scores[key][count]",scores[key]["count"])
            for sentence in doc.sents:
                print("sentence",sentence)
                if term_lower in sentence.text.lower():
                    scores[key]["sentiment"] += analyze_sentiment(sentence.text)
                    print("scores[key][sentiment]",scores[key]["sentiment"])
    print("Due diligence scores computed successfully", scores)
    return scores

