from crewai import Agent
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from collections import defaultdict
import re

class TakeawayAgent:
    """
    Takeaway Agent - Session summarization and RAG store management
    
    Responsibilities:
    - Summarize completed learning sessions
    - Extract successful learning patterns
    - Build and maintain RAG store of effective methods
    - Identify breakthrough moments
    - Generate insights for future sessions
    """
    
    def __init__(self):
        self.session_summaries = {}
        self.success_patterns = defaultdict(list)
        self.effective_methods = defaultdict(list)
        self.rag_store = []
        
        # Initialize the crewAI agent
        self.agent = Agent(
            role="Learning Session Analyst and Knowledge Curator",
            goal="""Analyze completed learning sessions to extract valuable insights, 
                   successful patterns, and effective teaching methods that can be used 
                   to improve future tutoring sessions and build a comprehensive 
                   knowledge base of proven educational strategies.""",
            backstory="""You are an expert educational researcher specializing in learning 
                        analytics and knowledge management. You have extensive experience 
                        in identifying what makes learning sessions successful, extracting 
                        key insights from educational interactions, and building knowledge 
                        repositories that enhance future learning experiences.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )
    
    def get_crewai_agent(self) -> Agent:
        """Return the crewAI agent instance"""
        return self.agent
    
    async def analyze_session(
        self, 
        session_id: str, 
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a completed learning session and extract takeaways
        
        Args:
            session_id: Unique session identifier
            session_data: Complete session interaction data
            
        Returns:
            Dict containing session analysis and takeaways
        """
        
        # Extract session metadata
        student_id = session_data.get('student_id')
        interactions = session_data.get('interactions', [])
        concepts_covered = session_data.get('concepts_covered', [])
        duration = session_data.get('duration_minutes', 0)
        
        if not interactions:
            return {
                'session_id': session_id,
                'message': 'No interactions to analyze',
                'takeaways': []
            }
        
        # Analyze session effectiveness
        effectiveness_analysis = await self._analyze_session_effectiveness(interactions)
        
        # Extract learning breakthroughs
        breakthroughs = await self._identify_learning_breakthroughs(interactions)
        
        # Identify successful methods
        successful_methods = await self._identify_successful_methods(interactions, effectiveness_analysis)
        
        # Generate session summary
        session_summary = await self._generate_session_summary(
            session_id, student_id, interactions, concepts_covered, duration
        )
        
        # Extract patterns for RAG store
        rag_entries = await self._extract_rag_entries(
            session_summary, successful_methods, breakthroughs
        )
        
        # Store takeaways
        takeaways = {
            'session_id': session_id,
            'student_id': student_id,
            'summary': session_summary,
            'effectiveness_score': effectiveness_analysis.get('score', 0.0),
            'breakthroughs': breakthroughs,
            'successful_methods': successful_methods,
            'key_insights': await self._generate_key_insights(interactions, effectiveness_analysis),
            'recommendations': await self._generate_future_recommendations(
                effectiveness_analysis, successful_methods
            ),
            'rag_entries': rag_entries,
            'analyzed_at': datetime.utcnow().isoformat()
        }
        
        # Store in memory
        self.session_summaries[session_id] = takeaways
        
        # Update success patterns
        await self._update_success_patterns(student_id, takeaways)
        
        # Update RAG store
        await self._update_rag_store(rag_entries)
        
        return takeaways
    
    async def get_relevant_insights(
        self, 
        student_context: Dict[str, Any], 
        current_question: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant insights from RAG store for current learning context
        
        Args:
            student_context: Current student learning context
            current_question: The current question being asked
            limit: Maximum number of insights to return
            
        Returns:
            List of relevant insights and successful methods
        """
        
        # Extract key terms from current question
        question_terms = await self._extract_key_terms(current_question)
        student_concepts = student_context.get('recent_concepts', [])
        student_preferences = student_context.get('preferences', {})
        
        # Score RAG entries for relevance
        scored_entries = []
        for entry in self.rag_store:
            relevance_score = await self._calculate_relevance_score(
                entry, question_terms, student_concepts, student_preferences
            )
            if relevance_score > 0.3:  # Minimum relevance threshold
                scored_entries.append((entry, relevance_score))
        
        # Sort by relevance and return top results
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                'insight': entry['content'],
                'method': entry.get('method', ''),
                'success_rate': entry.get('success_rate', 0.0),
                'relevance_score': score,
                'source_sessions': entry.get('source_sessions', []),
                'applicable_concepts': entry.get('concepts', [])
            }
            for entry, score in scored_entries[:limit]
        ]
    
    async def get_success_patterns(
        self, 
        student_id: Optional[str] = None,
        concept: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get success patterns, optionally filtered by student or concept
        
        Args:
            student_id: Optional student filter
            concept: Optional concept filter
            
        Returns:
            Dict containing success patterns and statistics
        """
        
        if student_id:
            patterns = self.success_patterns.get(student_id, [])
        else:
            patterns = [pattern for student_patterns in self.success_patterns.values() 
                       for pattern in student_patterns]
        
        if concept:
            patterns = [p for p in patterns if concept in p.get('concepts', [])]
        
        if not patterns:
            return {
                'message': 'No success patterns found for the specified criteria',
                'patterns': []
            }
        
        # Analyze patterns
        pattern_analysis = await self._analyze_success_patterns(patterns)
        
        return {
            'total_patterns': len(patterns),
            'analysis': pattern_analysis,
            'top_methods': await self._get_top_successful_methods(patterns),
            'common_breakthroughs': await self._get_common_breakthrough_types(patterns),
            'effectiveness_trends': await self._analyze_effectiveness_trends(patterns)
        }
    
    async def generate_session_insights_report(
        self, 
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights report from recent sessions
        
        Args:
            time_period: Time period to analyze
            
        Returns:
            Dict containing comprehensive insights report
        """
        
        # Filter sessions by time period
        end_time = datetime.utcnow()
        if time_period == "day":
            start_time = end_time - timedelta(days=1)
        elif time_period == "week":
            start_time = end_time - timedelta(weeks=1)
        elif time_period == "month":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(weeks=1)
        
        recent_sessions = [
            session for session in self.session_summaries.values()
            if datetime.fromisoformat(session['analyzed_at']) >= start_time
        ]
        
        if not recent_sessions:
            return {
                'message': f'No sessions analyzed in the last {time_period}',
                'insights': {}
            }
        
        # Generate comprehensive analysis
        insights = {
            'period_summary': {
                'total_sessions': len(recent_sessions),
                'avg_effectiveness': await self._calculate_avg_effectiveness(recent_sessions),
                'total_breakthroughs': sum(len(s.get('breakthroughs', [])) for s in recent_sessions),
                'concepts_covered': await self._get_period_concepts(recent_sessions)
            },
            'top_successful_methods': await self._get_period_top_methods(recent_sessions),
            'breakthrough_analysis': await self._analyze_period_breakthroughs(recent_sessions),
            'learning_trends': await self._identify_learning_trends(recent_sessions),
            'recommendations': await self._generate_period_recommendations(recent_sessions)
        }
        
        return {
            'time_period': time_period,
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def _analyze_session_effectiveness(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how effective the learning session was"""
        
        effectiveness_indicators = {
            'student_engagement': 0.0,
            'concept_understanding': 0.0,
            'question_resolution': 0.0,
            'learning_progression': 0.0
        }
        
        if not interactions:
            return {'score': 0.0, 'indicators': effectiveness_indicators}
        
        # Analyze student engagement
        engagement_score = await self._calculate_engagement_from_interactions(interactions)
        effectiveness_indicators['student_engagement'] = engagement_score
        
        # Analyze concept understanding
        understanding_score = await self._assess_concept_understanding(interactions)
        effectiveness_indicators['concept_understanding'] = understanding_score
        
        # Analyze question resolution
        resolution_score = await self._assess_question_resolution(interactions)
        effectiveness_indicators['question_resolution'] = resolution_score
        
        # Analyze learning progression
        progression_score = await self._assess_learning_progression(interactions)
        effectiveness_indicators['learning_progression'] = progression_score
        
        # Calculate overall effectiveness score
        overall_score = sum(effectiveness_indicators.values()) / len(effectiveness_indicators)
        
        return {
            'score': round(overall_score, 2),
            'indicators': effectiveness_indicators,
            'analysis': await self._generate_effectiveness_analysis(effectiveness_indicators)
        }
    
    async def _identify_learning_breakthroughs(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify moments of learning breakthroughs in the session"""
        
        breakthroughs = []
        
        for i, interaction in enumerate(interactions):
            # Look for breakthrough indicators in student messages
            student_message = interaction.get('student_message', '').lower()
            agent_response = interaction.get('agent_response', '').lower()
            
            breakthrough_indicators = [
                'i understand', 'i get it', 'now i see', 'that makes sense',
                'oh i see', 'i got it', 'clear now', 'understand now'
            ]
            
            if any(indicator in student_message for indicator in breakthrough_indicators):
                breakthroughs.append({
                    'type': 'understanding_breakthrough',
                    'interaction_index': i,
                    'description': 'Student expressed understanding',
                    'context': interaction.get('concepts_covered', []),
                    'trigger': await self._identify_breakthrough_trigger(interactions[:i+1])
                })
            
            # Look for method breakthroughs
            if any(phrase in student_message for phrase in ['this method', 'this way', 'this approach']):
                breakthroughs.append({
                    'type': 'method_breakthrough',
                    'interaction_index': i,
                    'description': 'Student found effective method',
                    'context': interaction.get('concepts_covered', []),
                    'method': await self._extract_method_from_context(interactions[:i+1])
                })
        
        return breakthroughs
    
    async def _identify_successful_methods(
        self, 
        interactions: List[Dict[str, Any]], 
        effectiveness: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify teaching methods that were successful in this session"""
        
        successful_methods = []
        
        # Only analyze if session was reasonably effective
        if effectiveness.get('score', 0) < 0.6:
            return successful_methods
        
        # Analyze response formats that led to breakthroughs
        for interaction in interactions:
            response_format = interaction.get('response_format', 'text')
            concepts = interaction.get('concepts_covered', [])
            
            # Check if this interaction led to positive student response
            if await self._interaction_led_to_success(interaction, interactions):
                successful_methods.append({
                    'method': f"{response_format}_explanation",
                    'concepts': concepts,
                    'effectiveness_score': effectiveness.get('score', 0),
                    'context': interaction.get('context', ''),
                    'student_response_indicators': await self._extract_success_indicators(interaction)
                })
        
        # Deduplicate and rank methods
        return await self._rank_and_deduplicate_methods(successful_methods)
    
    async def _generate_session_summary(
        self, 
        session_id: str, 
        student_id: str, 
        interactions: List[Dict[str, Any]], 
        concepts: List[str], 
        duration: int
    ) -> str:
        """Generate a comprehensive session summary"""
        
        summary_parts = []
        
        # Basic session info
        summary_parts.append(f"Session {session_id} for student {student_id}")
        summary_parts.append(f"Duration: {duration} minutes, {len(interactions)} interactions")
        
        # Concepts covered
        if concepts:
            summary_parts.append(f"Concepts explored: {', '.join(concepts)}")
        
        # Key highlights
        if len(interactions) > 5:
            summary_parts.append("Extended learning session with deep exploration")
        elif len(interactions) > 2:
            summary_parts.append("Focused learning session")
        else:
            summary_parts.append("Brief learning interaction")
        
        # Learning outcomes
        outcomes = await self._summarize_learning_outcomes(interactions)
        if outcomes:
            summary_parts.append(f"Outcomes: {outcomes}")
        
        return ". ".join(summary_parts) + "."
    
    async def _extract_rag_entries(
        self, 
        summary: str, 
        methods: List[Dict[str, Any]], 
        breakthroughs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract entries for the RAG store"""
        
        rag_entries = []
        
        # Create entries from successful methods
        for method in methods:
            rag_entries.append({
                'type': 'successful_method',
                'content': f"Method '{method['method']}' was effective for concepts: {', '.join(method['concepts'])}",
                'method': method['method'],
                'concepts': method['concepts'],
                'success_rate': method.get('effectiveness_score', 0.0),
                'context': method.get('context', ''),
                'source_sessions': [summary]
            })
        
        # Create entries from breakthroughs
        for breakthrough in breakthroughs:
            rag_entries.append({
                'type': 'breakthrough_pattern',
                'content': f"Breakthrough of type '{breakthrough['type']}' occurred when working on: {', '.join(breakthrough['context'])}",
                'breakthrough_type': breakthrough['type'],
                'concepts': breakthrough['context'],
                'trigger': breakthrough.get('trigger', ''),
                'source_sessions': [summary]
            })
        
        return rag_entries
    
    async def _generate_key_insights(
        self, 
        interactions: List[Dict[str, Any]], 
        effectiveness: Dict[str, Any]
    ) -> List[str]:
        """Generate key insights from the session"""
        
        insights = []
        
        # Effectiveness insights
        score = effectiveness.get('score', 0)
        if score > 0.8:
            insights.append("Highly effective session with strong student engagement")
        elif score > 0.6:
            insights.append("Good learning session with positive outcomes")
        elif score > 0.4:
            insights.append("Moderate effectiveness - room for improvement")
        else:
            insights.append("Low effectiveness - consider different approaches")
        
        # Interaction pattern insights
        if len(interactions) > 8:
            insights.append("Student showed persistence with extended interaction")
        
        # Concept insights
        concepts_covered = set()
        for interaction in interactions:
            concepts_covered.update(interaction.get('concepts_covered', []))
        
        if len(concepts_covered) > 3:
            insights.append("Session covered multiple mathematical concepts")
        elif len(concepts_covered) == 1:
            insights.append("Focused deep dive into single concept")
        
        return insights
    
    async def _generate_future_recommendations(
        self, 
        effectiveness: Dict[str, Any], 
        methods: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for future sessions"""
        
        recommendations = []
        
        # Based on effectiveness
        indicators = effectiveness.get('indicators', {})
        
        if indicators.get('student_engagement', 0) < 0.6:
            recommendations.append("Focus on increasing student engagement through interactive methods")
        
        if indicators.get('concept_understanding', 0) < 0.6:
            recommendations.append("Provide more scaffolding and examples for concept explanation")
        
        if indicators.get('question_resolution', 0) < 0.6:
            recommendations.append("Ensure student questions are fully addressed before moving on")
        
        # Based on successful methods
        if methods:
            top_method = max(methods, key=lambda x: x.get('effectiveness_score', 0))
            recommendations.append(f"Continue using '{top_method['method']}' as it showed good results")
        
        return recommendations
    
    async def _update_success_patterns(self, student_id: str, takeaways: Dict[str, Any]):
        """Update success patterns for the student"""
        
        pattern_entry = {
            'session_id': takeaways['session_id'],
            'effectiveness_score': takeaways['effectiveness_score'],
            'successful_methods': takeaways['successful_methods'],
            'breakthroughs': takeaways['breakthroughs'],
            'concepts': [method.get('concepts', []) for method in takeaways['successful_methods']],
            'timestamp': takeaways['analyzed_at']
        }
        
        self.success_patterns[student_id].append(pattern_entry)
        
        # Keep only recent patterns (last 20)
        if len(self.success_patterns[student_id]) > 20:
            self.success_patterns[student_id] = self.success_patterns[student_id][-20:]
    
    async def _update_rag_store(self, new_entries: List[Dict[str, Any]]):
        """Update the RAG store with new entries"""
        
        for entry in new_entries:
            # Check for similar existing entries
            similar_entry = await self._find_similar_rag_entry(entry)
            
            if similar_entry:
                # Update existing entry
                similar_entry['source_sessions'].extend(entry['source_sessions'])
                similar_entry['success_rate'] = (
                    similar_entry.get('success_rate', 0) + entry.get('success_rate', 0)
                ) / 2
            else:
                # Add new entry
                self.rag_store.append(entry)
        
        # Keep RAG store manageable (last 500 entries)
        if len(self.rag_store) > 500:
            self.rag_store = self.rag_store[-500:]
    
    async def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for relevance matching"""
        
        # Remove common stop words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return key_terms[:10]  # Return top 10 key terms
    
    async def _calculate_relevance_score(
        self, 
        rag_entry: Dict[str, Any], 
        question_terms: List[str], 
        student_concepts: List[str], 
        student_preferences: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for a RAG entry"""
        
        score = 0.0
        
        # Term matching
        entry_content = rag_entry.get('content', '').lower()
        term_matches = sum(1 for term in question_terms if term in entry_content)
        term_score = term_matches / len(question_terms) if question_terms else 0
        score += term_score * 0.4
        
        # Concept matching
        entry_concepts = rag_entry.get('concepts', [])
        concept_matches = len(set(student_concepts) & set(entry_concepts))
        concept_score = concept_matches / max(len(student_concepts), 1)
        score += concept_score * 0.4
        
        # Success rate
        success_rate = rag_entry.get('success_rate', 0.0)
        score += success_rate * 0.2
        
        return min(score, 1.0)
    
    # Additional helper methods for analysis
    async def _calculate_engagement_from_interactions(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate engagement score from interactions"""
        if not interactions:
            return 0.0
        
        engagement_indicators = 0
        total_possible = len(interactions) * 3  # Max 3 indicators per interaction
        
        for interaction in interactions:
            message = interaction.get('student_message', '').lower()
            
            # Check for engagement indicators
            if '?' in message:
                engagement_indicators += 1
            if len(message.split()) > 10:  # Detailed messages
                engagement_indicators += 1
            if any(word in message for word in ['help', 'explain', 'understand']):
                engagement_indicators += 1
        
        return engagement_indicators / total_possible if total_possible > 0 else 0.0
    
    async def _assess_concept_understanding(self, interactions: List[Dict[str, Any]]) -> float:
        """Assess level of concept understanding achieved"""
        understanding_indicators = 0
        total_interactions = len(interactions)
        
        for interaction in interactions:
            message = interaction.get('student_message', '').lower()
            
            if any(phrase in message for phrase in ['i understand', 'makes sense', 'i see']):
                understanding_indicators += 2
            elif any(phrase in message for phrase in ['got it', 'clear', 'okay']):
                understanding_indicators += 1
        
        return min(understanding_indicators / (total_interactions * 2), 1.0) if total_interactions > 0 else 0.0
    
    async def _assess_question_resolution(self, interactions: List[Dict[str, Any]]) -> float:
        """Assess how well questions were resolved"""
        questions = sum(1 for i in interactions if '?' in i.get('student_message', ''))
        if questions == 0:
            return 1.0  # No questions to resolve
        
        # Simple heuristic: if session continued with engagement, questions were likely resolved
        return min(len(interactions) / (questions * 2), 1.0)
    
    async def _assess_learning_progression(self, interactions: List[Dict[str, Any]]) -> float:
        """Assess learning progression throughout session"""
        if len(interactions) < 2:
            return 0.5
        
        # Look for progression in complexity or understanding
        early_interactions = interactions[:len(interactions)//2]
        later_interactions = interactions[len(interactions)//2:]
        
        early_complexity = sum(len(i.get('concepts_covered', [])) for i in early_interactions)
        later_complexity = sum(len(i.get('concepts_covered', [])) for i in later_interactions)
        
        if later_complexity > early_complexity:
            return 0.8  # Good progression
        elif later_complexity == early_complexity:
            return 0.6  # Stable
        else:
            return 0.4  # Possible regression
    
    async def _generate_effectiveness_analysis(self, indicators: Dict[str, float]) -> str:
        """Generate text analysis of effectiveness indicators"""
        analysis_parts = []
        
        for indicator, score in indicators.items():
            if score > 0.7:
                analysis_parts.append(f"{indicator.replace('_', ' ')} was strong")
            elif score > 0.4:
                analysis_parts.append(f"{indicator.replace('_', ' ')} was moderate")
            else:
                analysis_parts.append(f"{indicator.replace('_', ' ')} needs improvement")
        
        return "; ".join(analysis_parts)
    
    async def _identify_breakthrough_trigger(self, interactions: List[Dict[str, Any]]) -> str:
        """Identify what triggered a learning breakthrough"""
        if len(interactions) < 2:
            return "initial_explanation"
        
        last_agent_response = interactions[-2].get('agent_response', '')
        
        if 'step' in last_agent_response.lower():
            return "step_by_step_explanation"
        elif 'example' in last_agent_response.lower():
            return "concrete_example"
        elif 'video' in last_agent_response.lower():
            return "visual_content"
        else:
            return "detailed_explanation"
    
    async def _extract_method_from_context(self, interactions: List[Dict[str, Any]]) -> str:
        """Extract the teaching method from interaction context"""
        recent_responses = [i.get('response_format', 'text') for i in interactions[-3:]]
        
        if 'video' in recent_responses:
            return "video_explanation"
        elif 'step_by_step' in recent_responses:
            return "step_by_step_method"
        elif 'interactive' in recent_responses:
            return "interactive_practice"
        else:
            return "text_explanation"
    
    async def _interaction_led_to_success(
        self, 
        interaction: Dict[str, Any], 
        all_interactions: List[Dict[str, Any]]
    ) -> bool:
        """Check if an interaction led to successful learning"""
        interaction_index = all_interactions.index(interaction)
        
        # Look at next few interactions for success indicators
        next_interactions = all_interactions[interaction_index+1:interaction_index+3]
        
        for next_interaction in next_interactions:
            message = next_interaction.get('student_message', '').lower()
            if any(indicator in message for indicator in ['understand', 'got it', 'makes sense']):
                return True
        
        return False
    
    async def _extract_success_indicators(self, interaction: Dict[str, Any]) -> List[str]:
        """Extract indicators of success from interaction"""
        indicators = []
        
        response = interaction.get('agent_response', '').lower()
        
        if 'step' in response:
            indicators.append('structured_approach')
        if 'example' in response:
            indicators.append('concrete_examples')
        if len(response) > 200:
            indicators.append('detailed_explanation')
        
        return indicators
    
    async def _rank_and_deduplicate_methods(self, methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank and remove duplicate methods"""
        # Group by method name
        method_groups = defaultdict(list)
        for method in methods:
            method_groups[method['method']].append(method)
        
        # Take best example from each group
        ranked_methods = []
        for method_name, method_list in method_groups.items():
            best_method = max(method_list, key=lambda x: x.get('effectiveness_score', 0))
            ranked_methods.append(best_method)
        
        # Sort by effectiveness
        ranked_methods.sort(key=lambda x: x.get('effectiveness_score', 0), reverse=True)
        
        return ranked_methods
    
    async def _summarize_learning_outcomes(self, interactions: List[Dict[str, Any]]) -> str:
        """Summarize the learning outcomes of the session"""
        outcomes = []
        
        concepts = set()
        for interaction in interactions:
            concepts.update(interaction.get('concepts_covered', []))
        
        if concepts:
            outcomes.append(f"explored {len(concepts)} mathematical concepts")
        
        # Look for understanding indicators
        understanding_count = 0
        for interaction in interactions:
            message = interaction.get('student_message', '').lower()
            if any(phrase in message for phrase in ['understand', 'got it', 'clear']):
                understanding_count += 1
        
        if understanding_count > 0:
            outcomes.append(f"achieved understanding in {understanding_count} areas")
        
        return ", ".join(outcomes) if outcomes else "general mathematical discussion"
    
    async def _find_similar_rag_entry(self, new_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find similar existing RAG entry"""
        new_content = new_entry.get('content', '').lower()
        new_concepts = set(new_entry.get('concepts', []))
        
        for existing_entry in self.rag_store:
            existing_content = existing_entry.get('content', '').lower()
            existing_concepts = set(existing_entry.get('concepts', []))
            
            # Check content similarity and concept overlap
            content_similarity = len(set(new_content.split()) & set(existing_content.split())) / max(len(new_content.split()), 1)
            concept_overlap = len(new_concepts & existing_concepts) / max(len(new_concepts | existing_concepts), 1)
            
            if content_similarity > 0.6 or concept_overlap > 0.7:
                return existing_entry
        
        return None
