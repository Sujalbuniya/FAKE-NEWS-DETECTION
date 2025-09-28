from flask import Flask, render_template, request, jsonify, session
import logging
import os
from datetime import datetime
from utils.advanced_fact_checker import advanced_fact_checker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fake_news_detection.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
app.secret_key = 'fake-news-detection-secret-key-2024'

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page with fake news detection form"""
    session['detection_count'] = session.get('detection_count', 0)
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify_claim():
    """Verify a single claim for fake news detection"""
    try:
        # Get claim from form data or JSON
        if request.content_type == 'application/json':
            data = request.get_json()
            claim = data.get('claim', '').strip()
        else:
            claim = request.form.get('claim', '').strip()
        
        if not claim:
            logger.warning("Empty claim received")
            return jsonify({
                'status': 'ERROR',
                'confidence': 0.0,
                'message': 'No claim provided. Please enter a news claim to analyze.',
                'timestamp': datetime.now().isoformat()
            })
        
        # Update session counter
        session['detection_count'] = session.get('detection_count', 0) + 1
        session['last_claim'] = claim
        
        logger.info(f"Analyzing claim for fake news: '{claim}'")
        
        # Use the corrected fact checker
        result = advanced_fact_checker.comprehensive_verify(claim)
        
        # Add session info to result
        result['session'] = {
            'detection_count': session['detection_count'],
            'claim_length': len(claim)
        }
        
        # Enhance result with fake news specific terminology
        result = enhance_with_fake_news_terminology(result)
        
        logger.info(f"Fake news detection result: {result.get('status', 'UNKNOWN')} "
                   f"with confidence {result.get('confidence', 0)}")
        
        # Return JSON for API calls, render template for form submissions
        if request.content_type == 'application/json':
            return jsonify(result)
        else:
            return render_template('result.html', 
                                 claim=claim,
                                 result=result,
                                 timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
    except Exception as e:
        logger.error(f"Error analyzing claim for fake news: {str(e)}", exc_info=True)
        error_result = {
            'status': 'ERROR',
            'confidence': 0.0,
            'message': f'AI analysis error: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'recommendation': 'Please try again with a different claim or check the system logs'
        }
        
        if request.content_type == 'application/json':
            return jsonify(error_result), 500
        else:
            return render_template('error.html', 
                                 error_message=str(e),
                                 timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def enhance_with_fake_news_terminology(result):
    """Enhance results with fake news detection terminology"""
    confidence = result.get('confidence', 0)
    
    # Add fake news risk assessment
    if confidence >= 0.8:
        result['fake_news_risk'] = 'LOW'
        result['risk_level'] = 'Verified Information'
    elif confidence >= 0.6:
        result['fake_news_risk'] = 'MEDIUM'
        result['risk_level'] = 'Needs Verification'
    else:
        result['fake_news_risk'] = 'HIGH'
        result['risk_level'] = 'Potential Misinformation'
    
    # Enhance explanation with fake news context
    if 'explanation' in result:
        if confidence >= 0.8:
            result['explanation'] = f"✅ AI Analysis: This claim appears to be credible. {result['explanation']}"
        elif confidence >= 0.6:
            result['explanation'] = f"⚠️ AI Analysis: Exercise caution. {result['explanation']}"
        else:
            result['explanation'] = f"🚨 AI Analysis: Potential fake news detected. {result['explanation']}"
    
    return result

@app.route('/api/verify', methods=['GET', 'POST'])
def api_verify():
    """API endpoint for fake news detection"""
    try:
        if request.method == 'GET':
            claim = request.args.get('claim', '')
        else:
            if request.content_type == 'application/json':
                data = request.get_json()
                claim = data.get('claim', '')
            else:
                claim = request.form.get('claim', '')
        
        claim = claim.strip()
        
        if not claim:
            return jsonify({
                'error': 'Claim parameter required',
                'usage': 'Send a GET request to /api/verify?claim=YOUR_CLAIM or POST with JSON',
                'example': '/api/verify?claim=Breaking: Amazing discovery announced',
                'system': 'Fake News Detection AI'
            }), 400
        
        logger.info(f"API fake news detection request for: '{claim}'")
        
        result = advanced_fact_checker.comprehensive_verify(claim)
        result = enhance_with_fake_news_terminology(result)
        
        # Add API-specific metadata
        result['api'] = {
            'version': '2.0',
            'endpoint': '/api/verify',
            'response_format': 'json',
            'system': 'Fake News Detection AI'
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error in fake news detection: {str(e)}")
        return jsonify({
            'error': 'AI analysis failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat(),
            'system': 'Fake News Detection AI'
        }), 500

@app.route('/api/batch-verify', methods=['POST'])
def api_batch_verify():
    """API endpoint for batch fake news detection"""
    try:
        if request.content_type != 'application/json':
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        claims = data.get('claims', [])
        
        if not claims or not isinstance(claims, list):
            return jsonify({
                'error': 'Claims must be provided as a list',
                'example': {'claims': ['Claim 1', 'Claim 2', 'Claim 3']},
                'system': 'Fake News Detection AI'
            }), 400
        
        if len(claims) > 50:  # Limit batch size
            return jsonify({'error': 'Batch size limited to 50 claims maximum'}), 400
        
        logger.info(f"Batch fake news detection request for {len(claims)} claims")
        
        result = advanced_fact_checker.batch_verify(claims)
        
        # Enhance each result with fake news terminology
        for key, res in result.items():
            if key != 'batch_summary':
                result[key] = enhance_with_fake_news_terminology(res)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Batch API error in fake news detection: {str(e)}")
        return jsonify({
            'error': 'Batch fake news detection failed',
            'message': str(e),
            'system': 'Fake News Detection AI'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0_corrected',
        'system': 'Fake News Detection AI',
        'issue_fixed': '50_percent_confidence_bug',
        'features': ['AI-Powered Detection', 'Confidence Scoring', 'Real-time Analysis']
    })

@app.route('/stats')
def stats():
    """Statistics endpoint"""
    stats_data = {
        'detection_count': session.get('detection_count', 0),
        'last_claim_analyzed': session.get('last_claim', 'None'),
        'system_version': '2.0_corrected',
        'system_name': 'Fake News Detection AI',
        'fixes_applied': [
            'Basic facts now return 100% confidence',
            'Added proper claim classification',
            'Improved fake news detection algorithms',
            'Fixed confidence calculation bugs'
        ],
        'ai_capabilities': [
            'Pattern recognition',
            'Credibility assessment',
            'Risk evaluation',
            'Source verification'
        ],
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(stats_data)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'system': 'Fake News Detection AI',
        'available_endpoints': ['/', '/verify', '/api/verify', '/health', '/stats']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'AI system error',
        'message': 'Fake news detection system encountered an error',
        'system': 'Fake News Detection AI'
    }), 500

if __name__ == '__main__':
    # Check if we're in development mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("FAKE NEWS DETECTION AI - CORRECTED VERSION 2.0")
    print("=" * 60)
    print("ISSUES FIXED:")
    print("✓ Basic facts now return 100% confidence (not 50%)")
    print("✓ Added proper claim classification system")
    print("✓ Improved fake news detection algorithms")
    print("✓ Fixed confidence calculation bugs")
    print("=" * 60)
    print("Starting Fake News Detection AI on http://localhost:5000")
    print("Available endpoints:")
    print("  GET  /                    - Web interface")
    print("  POST /verify              - Detect fake news")
    print("  GET  /api/verify?claim=X  - API detection")
    print("  POST /api/batch-verify    - Batch detection")
    print("  GET  /health              - Health check")
    print("  GET  /stats               - Statistics")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        threaded=True
    )