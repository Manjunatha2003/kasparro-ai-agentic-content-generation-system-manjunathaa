from typing import List, Dict, Any
from utils import logger

class QualityEnforcer:
    
    def deduplicate_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_questions = set()
        deduplicated = []
        
        for q in questions:
            question_text = q['question'].lower().strip()
            
            if question_text not in seen_questions:
                seen_questions.add(question_text)
                deduplicated.append(q)
            else:
                logger.warning(f"Duplicate question removed: {q['question']}")
        
        logger.info(f"Deduplication: {len(questions)} -> {len(deduplicated)}")
        return deduplicated
    
    def score_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        
        for q in questions:
            score = self._calculate_question_quality(q)
            q['quality_score'] = score
            scored.append(q)
        
        avg_score = sum(q['quality_score'] for q in scored) / len(scored) if scored else 0
        logger.info(f"Question quality scores: avg={avg_score:.1f}")
        
        return scored
    
    def _calculate_question_quality(self, question: Dict[str, Any]) -> int:
        score = 100
        
        question_text = question['question']
        answer_text = question['answer']
        
        if len(question_text) < 10:
            score -= 30
        
        if len(answer_text) < 20:
            score -= 20
        
        if question_text.count(' ') < 3:
            score -= 20
        
        if not question_text.endswith('?'):
            score -= 10
        
        quality_words = ['how', 'what', 'why', 'when', 'which', 'can', 'should', 'does']
        if not any(word in question_text.lower() for word in quality_words):
            score -= 15
        
        if question_text.lower() == answer_text.lower():
            score -= 50
        
        return max(0, score)
    
    def validate_block_quality(self, blocks: Dict[str, Any]) -> bool:
        benefits = blocks.get('benefits', [])
        if len(benefits) < 2:
            logger.error("Insufficient benefits in content blocks")
            return False
        
        ingredients = blocks.get('ingredients_block', [])
        if len(ingredients) < 1:
            logger.error("Insufficient ingredients in content blocks")
            return False
        
        usage = blocks.get('usage_block', '')
        if len(usage) < 10:
            logger.error("Usage block too short")
            return False
        
        return True
    
    def detect_low_quality_comparison(self, comparison: Dict[str, Any]) -> bool:
        price_diff = comparison.get('price_difference', 0)
        
        if price_diff == 0:
            logger.warning("Price difference is zero - low quality comparison")
            return True
        
        stronger = comparison.get('stronger_formulation', '')
        if not stronger:
            logger.warning("No stronger formulation identified")
            return True
        
        return False