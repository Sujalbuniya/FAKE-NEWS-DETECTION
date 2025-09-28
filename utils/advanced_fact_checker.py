import logging
from typing import Dict, List
from .fact_checker import fact_checker

class AdvancedFactChecker:
    def __init__(self):
        self.fact_checker = fact_checker
        self.logger = logging.getLogger(__name__)
        
    def comprehensive_verify(self, claim: str) -> Dict:
        """
        Advanced verification with detailed analysis and enhanced results
        """
        try:
            # Get basic verification result
            basic_result = self.fact_checker.verify_claim(claim)
            
            # Enhance the result with additional analysis
            enhanced_result = self._enhance_verification_result(basic_result, claim)
            
            # Add metadata and analytics
            enhanced_result = self._add_analytics_metadata(enhanced_result, claim)
            
            self.logger.info(f"Verified claim: '{claim}' -> Status: {enhanced_result.get('status', 'UNKNOWN')}")
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive_verify: {str(e)}")
            return self._create_error_result(claim, str(e))
    
    def _enhance_verification_result(self, result: Dict, claim: str) -> Dict:
        """Add additional context, analysis, and recommendations to the result"""
        
        # Add claim analysis
        result['claim_analysis'] = self._analyze_claim_complexity(claim)
        
        # Enhance based on confidence level
        confidence = result.get('confidence', 0)
        
        if confidence == 1.0:
            result['verification_level'] = "HIGHEST_CONFIDENCE"
            result['user_guidance'] = "This is an established fact requiring no further verification"
            result['trust_indicator'] = "VERY_HIGH"
            result['color_code'] = "green"
            
        elif confidence >= 0.8:
            result['verification_level'] = "HIGH_CONFIDENCE"
            result['user_guidance'] = "Likely true based on available evidence"
            result['trust_indicator'] = "HIGH"
            result['color_code'] = "lightgreen"
            
        elif confidence >= 0.6:
            result['verification_level'] = "MEDIUM_CONFIDENCE"
            result['user_guidance'] = "Additional verification recommended"
            result['trust_indicator'] = "MEDIUM"
            result['color_code'] = "yellow"
            
        else:
            result['verification_level'] = "LOW_CONFIDENCE"
            result['user_guidance'] = "Requires thorough verification from multiple sources"
            result['trust_indicator'] = "LOW"
            result['color_code'] = "orange"
        
        # Add specific recommendations based on claim type
        result['recommendations'] = self._generate_recommendations(result, claim)
        
        # Add timestamp and version info
        result['analysis_timestamp'] = self._get_current_timestamp()
        result['verifier_version'] = "2.0_corrected"
        
        return result
    
    def _analyze_claim_complexity(self, claim: str) -> Dict:
        """Analyze the complexity and structure of the claim"""
        word_count = len(claim.split())
        sentence_count = len([s for s in claim.split('.') if s.strip()])
        avg_word_length = sum(len(word) for word in claim.split()) / max(word_count, 1)
        
        # Complexity assessment
        if word_count <= 5:
            complexity = "simple"
        elif word_count <= 15:
            complexity = "medium"
        else:
            complexity = "complex"
        
        # Type assessment
        if any(word in claim.lower() for word in ['blames', 'accuses', 'claims']):
            claim_type = "accusation"
        elif any(word in claim.lower() for word in ['is in', 'is the capital of', 'located in']):
            claim_type = "factual_statement"
        elif '?' in claim:
            claim_type = "question"
        else:
            claim_type = "statement"
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "average_word_length": round(avg_word_length, 2),
            "complexity_level": complexity,
            "claim_type": claim_type,
            "readability": "high" if complexity == "simple" else "medium" if complexity == "medium" else "low"
        }
    
    def _generate_recommendations(self, result: Dict, claim: str) -> List[str]:
        """Generate specific recommendations based on verification result"""
        recommendations = []
        status = result.get('status', '')
        confidence = result.get('confidence', 0)
        
        if confidence == 1.0:
            recommendations.append("No further action needed - high confidence verification")
            recommendations.append("This can be accepted as reliable information")
        elif status == "COMPONENT_ANALYSIS":
            recommendations.append("Verify each component of the claim separately")
            recommendations.append("Check multiple news sources for consistency")
            recommendations.append("Look for official statements from involved parties")
        elif confidence < 0.7:
            recommendations.append("Consult multiple independent sources")
            recommendations.append("Verify with primary sources when possible")
            recommendations.append("Check the date and context of the information")
            recommendations.append("Be cautious of potential misinformation")
        
        # Always include these general recommendations
        general_recommendations = [
            "Consider the source of the original claim",
            "Check the date and timeliness of information",
            "Look for corroborating evidence from multiple sources"
        ]
        
        recommendations.extend(general_recommendations)
        return recommendations
    
    def _add_analytics_metadata(self, result: Dict, claim: str) -> Dict:
        """Add analytics and metadata to the result"""
        if 'metadata' not in result:
            result['metadata'] = {}
        
        result['metadata'].update({
            "claim_length": len(claim),
            "verification_time": self._get_current_timestamp(),
            "processing_steps": ["claim_classification", "type_specific_verification", "result_enhancement"],
            "system_version": "corrected_v2.0",
            "issue_corrected": "fixed_50_percent_confidence_bug"
        })
        
        return result
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in readable format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _create_error_result(self, claim: str, error_msg: str) -> Dict:
        """Create error result when verification fails"""
        return {
            "status": "SYSTEM_ERROR",
            "confidence": 0.0,
            "explanation": f"Verification system error: {error_msg}",
            "claim": claim,
            "timestamp": self._get_current_timestamp(),
            "recommendation": "Please try again or check the claim manually",
            "color_code": "red"
        }
    
    def batch_verify(self, claims: List[str]) -> Dict:
        """Verify multiple claims at once"""
        results = {}
        for i, claim in enumerate(claims):
            results[f"claim_{i+1}"] = self.comprehensive_verify(claim)
        
        summary = self._generate_batch_summary(results)
        results['batch_summary'] = summary
        
        return results
    
    def _generate_batch_summary(self, results: Dict) -> Dict:
        """Generate summary for batch verification"""
        total_claims = len(results)
        verified_count = 0
        confidence_sum = 0
        
        for key, result in results.items():
            if key != 'batch_summary':
                if result.get('status') in ['VERIFIED', 'LIKELY_TRUE']:
                    verified_count += 1
                confidence_sum += result.get('confidence', 0)
        
        avg_confidence = confidence_sum / max(total_claims, 1)
        
        return {
            "total_claims": total_claims,
            "verified_claims": verified_count,
            "verification_rate": f"{(verified_count/total_claims)*100:.1f}%" if total_claims > 0 else "0%",
            "average_confidence": round(avg_confidence, 2),
            "summary": f"Verified {verified_count} out of {total_claims} claims with average confidence {avg_confidence:.2f}"
        }

# Global instance for use across the application
advanced_fact_checker = AdvancedFactChecker()