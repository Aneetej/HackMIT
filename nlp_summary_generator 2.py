"""
NLP-based Summary Generator for Student Learning Analytics

This module uses advanced natural language processing techniques to generate
comprehensive class summaries from individual student summaries.
"""

import re
import nltk
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import spacy

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.download('wordnet')
except:
    pass

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class NLPSummaryGenerator:
    """Advanced NLP-based summary generator for student learning analytics"""
    
    def __init__(self):
        """Initialize NLP components"""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Mathematical subject keywords for domain detection
        self.math_domains = {
            'algebra': ['equation', 'variable', 'solve', 'linear', 'quadratic', 'polynomial', 'factor'],
            'geometry': ['triangle', 'circle', 'angle', 'area', 'volume', 'proof', 'theorem'],
            'calculus': ['derivative', 'integral', 'limit', 'function', 'optimization', 'rate'],
            'statistics': ['probability', 'data', 'mean', 'distribution', 'hypothesis', 'correlation'],
            'trigonometry': ['sine', 'cosine', 'tangent', 'angle', 'triangle', 'periodic']
        }
        
        # Sentiment indicators for academic performance
        self.positive_indicators = {
            'strong', 'excellent', 'good', 'solid', 'excels', 'understands', 'grasps',
            'proficient', 'skilled', 'confident', 'progress', 'improvement', 'mastery'
        }
        
        self.negative_indicators = {
            'struggles', 'difficulty', 'challenges', 'problems', 'confusion', 'unclear',
            'needs work', 'weak', 'poor', 'lacks', 'missing', 'errors', 'mistakes'
        }
        
        # Initialize TF-IDF vectorizer for semantic analysis
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
    
    def generate_nlp_summary(self, individual_summaries: List[str]) -> str:
        """
        Generate comprehensive class summary using advanced NLP techniques
        
        Args:
            individual_summaries: List of individual student summary strings
            
        Returns:
            Comprehensive class summary with NLP-based insights
        """
        if not individual_summaries:
            return "No individual student summaries available for analysis."
        
        # Preprocess summaries
        processed_summaries = self._preprocess_summaries(individual_summaries)
        
        # Extract semantic themes using TF-IDF and clustering
        themes = self._extract_semantic_themes(processed_summaries)
        
        # Perform sentiment analysis for strengths and challenges
        sentiment_analysis = self._analyze_academic_sentiment(individual_summaries)
        
        # Extract mathematical domain patterns
        domain_patterns = self._extract_domain_patterns(individual_summaries)
        
        # Identify key concepts using named entity recognition
        key_concepts = self._extract_key_concepts(individual_summaries)
        
        # Generate coherent summary using extracted insights
        summary = self._synthesize_nlp_summary(
            individual_summaries,
            themes,
            sentiment_analysis,
            domain_patterns,
            key_concepts
        )
        
        return summary
    
    def _preprocess_summaries(self, summaries: List[str]) -> List[str]:
        """Preprocess summaries for NLP analysis"""
        processed = []
        
        for summary in summaries:
            # Clean and normalize text
            text = re.sub(r'[^\w\s]', ' ', summary.lower())
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Tokenize and lemmatize
            tokens = word_tokenize(text)
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                     if token not in self.stop_words and len(token) > 2]
            
            processed.append(' '.join(tokens))
        
        return processed
    
    def _extract_semantic_themes(self, processed_summaries: List[str]) -> List[Dict]:
        """Extract semantic themes using TF-IDF and clustering"""
        if len(processed_summaries) < 2:
            return [{'theme': 'Individual Learning Patterns', 'keywords': [], 'frequency': 1}]
        
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_summaries)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Perform clustering to identify themes
            n_clusters = min(3, len(processed_summaries))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            themes = []
            for cluster_id in range(n_clusters):
                # Get documents in this cluster
                cluster_docs = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                
                if cluster_docs:
                    # Find top keywords for this cluster
                    cluster_tfidf = tfidf_matrix[cluster_docs].mean(axis=0).A1
                    top_indices = cluster_tfidf.argsort()[-5:][::-1]
                    top_keywords = [feature_names[i] for i in top_indices if cluster_tfidf[i] > 0]
                    
                    themes.append({
                        'theme': f'Learning Pattern {cluster_id + 1}',
                        'keywords': top_keywords,
                        'frequency': len(cluster_docs)
                    })
            
            return themes
            
        except Exception as e:
            print(f"Error in semantic theme extraction: {e}")
            return [{'theme': 'General Learning Patterns', 'keywords': [], 'frequency': len(processed_summaries)}]
    
    def _analyze_academic_sentiment(self, summaries: List[str]) -> Dict:
        """Analyze academic sentiment to identify strengths and challenges"""
        strengths = []
        challenges = []
        neutral_aspects = []
        
        for summary in summaries:
            sentences = sent_tokenize(summary)
            
            for sentence in sentences:
                words = set(word_tokenize(sentence.lower()))
                
                # Calculate sentiment scores
                positive_score = len(words.intersection(self.positive_indicators))
                negative_score = len(words.intersection(self.negative_indicators))
                
                if positive_score > negative_score:
                    strengths.append(self._extract_academic_aspect(sentence, words))
                elif negative_score > positive_score:
                    challenges.append(self._extract_academic_aspect(sentence, words))
                else:
                    neutral_aspects.append(self._extract_academic_aspect(sentence, words))
        
        return {
            'strengths': self._consolidate_aspects(strengths),
            'challenges': self._consolidate_aspects(challenges),
            'neutral': self._consolidate_aspects(neutral_aspects)
        }
    
    def _extract_academic_aspect(self, sentence: str, words: Set[str]) -> str:
        """Extract the main academic aspect from a sentence"""
        # Look for mathematical concepts
        for domain, keywords in self.math_domains.items():
            if any(keyword in words for keyword in keywords):
                return f"{domain} concepts"
        
        # Look for general academic terms
        academic_terms = {'problem', 'concept', 'skill', 'understanding', 'application', 'reasoning'}
        found_terms = words.intersection(academic_terms)
        
        if found_terms:
            return f"{list(found_terms)[0]} areas"
        
        return "general mathematical concepts"
    
    def _consolidate_aspects(self, aspects: List[str]) -> List[str]:
        """Consolidate similar academic aspects"""
        aspect_counts = Counter(aspects)
        return [aspect for aspect, count in aspect_counts.most_common(5)]
    
    def _extract_domain_patterns(self, summaries: List[str]) -> Dict[str, int]:
        """Extract mathematical domain patterns using NLP"""
        domain_scores = defaultdict(int)
        
        for summary in summaries:
            words = set(word_tokenize(summary.lower()))
            
            for domain, keywords in self.math_domains.items():
                # Calculate domain relevance score
                matches = sum(1 for keyword in keywords if keyword in words)
                if matches > 0:
                    domain_scores[domain] += matches
        
        return dict(domain_scores)
    
    def _extract_key_concepts(self, summaries: List[str]) -> List[str]:
        """Extract key mathematical concepts using frequency analysis"""
        all_concepts = []
        
        # Mathematical concept keywords to look for
        math_concepts = [
            'equation', 'algebra', 'geometry', 'calculus', 'statistics', 'probability',
            'derivative', 'integral', 'function', 'variable', 'theorem', 'proof',
            'triangle', 'circle', 'angle', 'area', 'volume', 'graph', 'slope',
            'polynomial', 'quadratic', 'linear', 'exponential', 'logarithm'
        ]
        
        for summary in summaries:
            words = word_tokenize(summary.lower())
            # Find mathematical concepts in the summary
            for word in words:
                if word in math_concepts and len(word) > 3:
                    all_concepts.append(word)
        
        # Return most frequent concepts
        concept_counts = Counter(all_concepts)
        return [concept for concept, count in concept_counts.most_common(10) if count > 1]
    
    def _synthesize_nlp_summary(self, summaries: List[str], themes: List[Dict], 
                               sentiment: Dict, domains: Dict, concepts: List[str]) -> str:
        """Synthesize comprehensive summary from NLP analysis in paragraph format"""
        
        total_students = len(summaries)
        
        # Generate cohesive paragraph-style summary
        summary_paragraphs = []
        
        # Opening paragraph with overview
        opening = f"This comprehensive analysis of {total_students} individual student summaries reveals distinct learning patterns and academic trends within the class."
        if themes:
            theme_info = self._generate_theme_paragraph(themes)
            opening += f" {theme_info}"
        summary_paragraphs.append(opening)
        
        # Academic performance paragraph
        performance_paragraph = self._generate_performance_paragraph(sentiment, domains)
        if performance_paragraph:
            summary_paragraphs.append(performance_paragraph)
        
        # Mathematical focus paragraph
        focus_paragraph = self._generate_focus_paragraph(domains, concepts)
        if focus_paragraph:
            summary_paragraphs.append(focus_paragraph)
        
        # Synthesis paragraph
        synthesis = self._generate_synthesis_paragraph(total_students, themes, sentiment)
        summary_paragraphs.append(synthesis)
        
        # Join paragraphs with proper spacing
        return "\n\n".join(summary_paragraphs)
    
    def _generate_theme_paragraph(self, themes: List[Dict]) -> str:
        """Generate paragraph describing semantic themes"""
        if not themes:
            return "The analysis did not identify distinct learning themes across the student summaries."
        
        if len(themes) == 1:
            theme = themes[0]
            keywords = ", ".join(theme['keywords'][:3])
            return f"The semantic analysis identified a primary learning pattern involving {theme['frequency']} students, with focus areas including {keywords}."
        
        theme_count = len(themes)
        primary_theme = themes[0]
        keywords = ", ".join(primary_theme['keywords'][:3])
        
        return f"The semantic clustering analysis identified {theme_count} distinct learning patterns, with the most prominent pattern involving {primary_theme['frequency']} students focusing on {keywords}."
    
    def _generate_performance_paragraph(self, sentiment: Dict, domains: Dict) -> str:
        """Generate paragraph describing academic performance patterns"""
        sentences = []
        
        # Strengths
        if sentiment['strengths']:
            strength_areas = ", ".join(sentiment['strengths'][:2])
            sentences.append(f"Students demonstrate notable strengths in {strength_areas}")
        
        # Challenges
        if sentiment['challenges']:
            challenge_areas = ", ".join(sentiment['challenges'][:2])
            if sentences:
                sentences.append(f"while showing consistent challenges in {challenge_areas}")
            else:
                sentences.append(f"The analysis reveals consistent challenges in {challenge_areas}")
        
        if not sentences:
            return ""
        
        return ". ".join(sentences) + "."
    
    def _generate_focus_paragraph(self, domains: Dict[str, int], concepts: List[str]) -> str:
        """Generate paragraph describing mathematical focus areas"""
        sentences = []
        
        if domains:
            sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_domains) == 1:
                domain, mentions = sorted_domains[0]
                sentences.append(f"The mathematical content analysis shows a primary focus on {domain} with {mentions} relevant mentions across student summaries")
            else:
                top_domains = [domain for domain, _ in sorted_domains[:2]]
                sentences.append(f"Mathematical content spans multiple domains, with particular emphasis on {' and '.join(top_domains)}")
        
        if concepts:
            concept_list = ", ".join(concepts[:3])
            if sentences:
                sentences.append(f"Key mathematical concepts frequently discussed include {concept_list}")
            else:
                sentences.append(f"The most frequently mentioned mathematical concepts include {concept_list}")
        
        if not sentences:
            return ""
        
        return ". ".join(sentences) + "."
    
    def _generate_synthesis_paragraph(self, total_students: int, themes: List[Dict], sentiment: Dict) -> str:
        """Generate synthesis paragraph with overall assessment"""
        sentences = []
        
        # Overall pattern assessment
        if themes and len(themes) > 1:
            sentences.append(f"The diversity of learning patterns across {total_students} students indicates varied mathematical learning trajectories within the class")
        else:
            sentences.append(f"The analysis of {total_students} individual student profiles reveals consistent mathematical learning patterns")
        
        # Balance assessment
        strength_count = len(sentiment.get('strengths', []))
        challenge_count = len(sentiment.get('challenges', []))
        
        if strength_count > challenge_count:
            sentences.append("with more identified strengths than areas of concern, suggesting overall positive academic progress")
        elif challenge_count > strength_count:
            sentences.append("with several areas requiring focused instructional attention to support student success")
        else:
            sentences.append("showing a balanced profile of both strengths and areas for continued development")
        
        return ". ".join(sentences) + ". This comprehensive analysis provides actionable insights for differentiated instruction and targeted academic support."


# Integration function for existing system
def generate_nlp_based_summary(individual_summaries: List[str]) -> str:
    """
    Main function to generate NLP-based summary for integration with existing system
    
    Args:
        individual_summaries: List of individual student summary strings
        
    Returns:
        Comprehensive class summary using NLP techniques
    """
    try:
        generator = NLPSummaryGenerator()
        return generator.generate_nlp_summary(individual_summaries)
    except Exception as e:
        print(f"Error in NLP summary generation: {e}")
        # Fallback to simple concatenation
        return f"**Class Summary** ({len(individual_summaries)} students): " + \
               " ".join([f"Student {i+1}: {summary}." for i, summary in enumerate(individual_summaries)])


if __name__ == "__main__":
    # Test the NLP summary generator
    test_summaries = [
        "Student shows strong understanding of algebraic equations but struggles with word problems.",
        "Excellent grasp of geometric concepts, particularly in area calculations and proofs.",
        "Needs support with calculus derivatives, shows confusion with chain rule applications.",
        "Good progress in statistics, understands probability but needs work on hypothesis testing.",
        "Strong computational skills in algebra, challenges with abstract reasoning in proofs."
    ]
    
    print("=== Testing NLP Summary Generator ===")
    summary = generate_nlp_based_summary(test_summaries)
    print(summary)
