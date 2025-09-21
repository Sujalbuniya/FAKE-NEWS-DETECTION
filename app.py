# app.py - Enhanced Fake News Detector
from flask import Flask, request, jsonify, render_template
import spacy
import re
import requests
import json
import wikipediaapi

# Initialize Flask App
app = Flask(__name__)

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Fallback if model isn't available
    nlp = None

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia('FakeNewsDetector/1.0', 'en')

# ==================== CORE MODULES ====================

def extract_claim(full_text):
    """
    Extracts the core claim from a sentence that reports what someone said.
    Example: "X claimed that Y is true" -> returns "Y is true"
    """
    if not full_text or not isinstance(full_text, str):
        return full_text
        
    # If spaCy isn't available, use regex fallback
    if nlp is None:
        return regex_extract_claim(full_text)
    
    try:
        doc = nlp(full_text)
        report_phrases = [
            r'(claimed|said|stated|argued|reported|alleged)( that|,)',
            r'(according to|as per)(.*)',
            r'(claimed|said|stated|argued|reported|alleged)'
        ]
        
        for sent in doc.sents:
            sent_text = sent.text
            for pattern in report_phrases:
                if re.search(pattern, sent_text, re.IGNORECASE):
                    match = re.search(pattern, sent_text, re.IGNORECASE)
                    start_idx = match.end()
                    claim = sent_text[start_idx:].strip()
                    claim = re.sub(r'^[\'",:\-–—\s]+', '', claim)
                    if claim:
                        return claim
    except Exception as e:
        print(f"Error in extract_claim: {e}")
    
    return full_text

def regex_extract_claim(full_text):
    """Fallback claim extraction using regex only"""
    patterns = [
        r'(claimed|said|stated|argued|reported|alleged)\s+that\s+(.+)',
        r'(according to|as per)\s+[^,]+,?\s*(.+)',
        r'([^ ]+\s+(?:claimed|said|stated|argued|reported|alleged))\s+(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            return match.group(2).strip()
    
    return full_text

def google_fact_check(search_query):
    """
    Searches the Google Fact Check Tools API for claims related to the query.
    Returns a list of fact-check results from various organizations.
    """
    api_key = "YOUR_API_KEY_HERE"  # REPLACE WITH YOUR ACTUAL API KEY
    if api_key == "YOUR_API_KEY_HERE":
        return []  # Return empty if no API key is set
    
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    params = {
        'key': api_key,
        'query': search_query,
        'languageCode': 'en',
        'maxAgeDays': 30  # Limit to recent fact-checks
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        fact_checks = []
        if 'claims' in data:
            for claim in data['claims']:
                check = {
                    'text': claim.get('text', ''),
                    'claimant': claim.get('claimant', ''),
                    'claimDate': claim.get('claimDate', ''),
                    'rating': claim.get('claimReview', [{}])[0].get('textualRating', 'No Rating'),
                    'url': claim.get('claimReview', [{}])[0].get('url', ''),
                    'source': claim.get('claimReview', [{}])[0].get('publisher', {}).get('name', '')
                }
                fact_checks.append(check)
        
        return fact_checks[:3]  # Return top 3 results
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Fact Check API: {e}")
        return []

def wikipedia_search(query):
    """
    Search Wikipedia for information related to the claim
    """
    try:
        # Try to get a direct page first
        page = wiki_wiki.page(query)
        if page.exists():
            return {
                'title': page.title,
                'summary': page.summary[:500] + "..." if len(page.summary) > 500 else page.summary,
                'url': page.fullurl
            }
        
        # If direct page doesn't exist, search
        search_results = wiki_wiki.search(query)
        if search_results:
            # Get the first search result
            page = wiki_wiki.page(search_results[0])
            if page.exists():
                return {
                    'title': page.title,
                    'summary': page.summary[:500] + "..." if len(page.summary) > 500 else page.summary,
                    'url': page.fullurl
                }
    except Exception as e:
        print(f"Error in Wikipedia search: {e}")
    
    return None

def analyze_with_ml(claim_text):
    """
    Your existing ML model analysis function
    Replace this with your actual ML model code
    """
    # This is a placeholder - replace with your actual model inference
    # For now, returns a dummy score
    return 0.65

def generate_final_verdict(ml_score, wiki_data, fact_checks, original_claim):
    """
    Combines evidence from all sources to generate a final verdict
    """
    evidence = {
        'ml_score': ml_score,
        'has_wiki_data': wiki_data is not None,
        'fact_check_count': len(fact_checks),
        'fact_check_ratings': [],
        'context_analysis': analyze_context(original_claim)
    }
    
    # Extract ratings from fact checks
    for check in fact_checks:
        rating = check['rating'].lower()
        evidence['fact_check_ratings'].append(rating)
    
    # Decision logic
    if evidence['fact_check_count'] > 0:
        return decide_based_on_fact_checks(evidence)
    elif evidence['has_wiki_data']:
        return decide_based_on_wiki_ml(evidence)
    else:
        return decide_based_on_ml_only(evidence)

def analyze_context(claim):
    """
    Analyzes the context of the claim for red flags
    """
    red_flags = []
    
    # Check for absolute language
    absolute_terms = ['all', 'every', 'never', 'always', 'nothing', 'no one', 'everything']
    for term in absolute_terms:
        if term in claim.lower():
            red_flags.append(f"Uses absolute term: '{term}'")
    
    # Check for emotional language
    emotional_terms = ['disaster', 'catastrophe', 'bloodbath', 'evil', 'treason']
    for term in emotional_terms:
        if term in claim.lower():
            red_flags.append(f"Uses emotional language: '{term}'")
    
    return red_flags

def decide_based_on_fact_checks(evidence):
    """Decision logic when fact checks are available"""
    ratings = evidence['fact_check_ratings']
    
    true_terms = ['true', 'correct', 'accurate', 'mostly true']
    false_terms = ['false', 'incorrect', 'inaccurate', 'misleading', 'mostly false']
    mixed_terms = ['mixed', 'half true', 'partially true']
    
    true_count = sum(1 for rating in ratings if any(term in rating for term in true_terms))
    false_count = sum(1 for rating in ratings if any(term in rating for term in false_terms))
    mixed_count = sum(1 for rating in ratings if any(term in rating for term in mixed_terms))
    
    if true_count > false_count and true_count > mixed_count:
        return "LIKELY TRUE", 0.8, evidence
    elif false_count > true_count and false_count > mixed_count:
        return "LIKELY FALSE", 0.8, evidence
    elif mixed_count > 0:
        return "MIXED EVIDENCE", 0.6, evidence
    else:
        return "UNCLEAR", 0.5, evidence

def decide_based_on_wiki_ml(evidence):
    """Decision logic when only Wikipedia and ML are available"""
    if evidence['ml_score'] > 0.7:
        return "LIKELY TRUE", evidence['ml_score'], evidence
    elif evidence['ml_score'] < 0.3:
        return "LIKELY FALSE", 1 - evidence['ml_score'], evidence
    else:
        return "UNCLEAR", 0.5, evidence

def decide_based_on_ml_only(evidence):
    """Decision logic when only ML is available"""
    if evidence['ml_score'] > 0.6:
        return "LIKELY TRUE", evidence['ml_score'], evidence
    elif evidence['ml_score'] < 0.4:
        return "LIKELY FALSE", 1 - evidence['ml_score'], evidence
    else:
        return "UNCLEAR", 0.5, evidence

# ==================== FLASK ROUTES ====================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if request.method == 'POST':
            # Get news text from the form
            news_text = request.form.get('news_text', '')
            
            if not news_text.strip():
                return render_template('result.html', 
                                    error="Please enter some text to analyze.")
            
            # Extract the core claim
            claim_to_verify = extract_claim(news_text)
            
            # Perform multi-source verification
            ml_score = analyze_with_ml(claim_to_verify)
            wiki_data = wikipedia_search(claim_to_verify)
            fact_checks = google_fact_check(claim_to_verify)
            
            # Generate final verdict
            verdict, confidence, evidence = generate_final_verdict(
                ml_score, wiki_data, fact_checks, claim_to_verify
            )
            
            # Prepare results for display
            result = {
                'verdict': verdict,
                'confidence': round(confidence, 2),
                'original_text': news_text,
                'claim_analyzed': claim_to_verify,
                'wiki_data': wiki_data,
                'fact_checks': fact_checks,
                'evidence': evidence,
                'ml_score': round(ml_score, 2)
            }
            
            return render_template('result.html', result=result)
            
    except Exception as e:
        print(f"Error in analysis: {e}")
        return render_template('result.html', 
                            error="An error occurred during analysis. Please try again.")

@app.route('/api/check', methods=['POST'])
def api_check():
    """API endpoint for programmatic access"""
    try:
        data = request.get_json()
        news_text = data.get('text', '')
        
        claim_to_verify = extract_claim(news_text)
        ml_score = analyze_with_ml(claim_to_verify)
        wiki_data = wikipedia_search(claim_to_verify)
        fact_checks = google_fact_check(claim_to_verify)
        
        verdict, confidence, evidence = generate_final_verdict(
            ml_score, wiki_data, fact_checks, claim_to_verify
        )
        
        return jsonify({
            'verdict': verdict,
            'confidence': confidence,
            'claim_analyzed': claim_to_verify,
            'sources_checked': {
                'wikipedia': wiki_data is not None,
                'fact_checks': len(fact_checks)
            },
            'evidence': evidence
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)