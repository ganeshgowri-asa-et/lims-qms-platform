"""AI service for root cause analysis suggestions."""

from typing import List, Dict, Optional
from config import settings
import json


class AIService:
    """Service for AI-powered root cause suggestions."""

    @staticmethod
    def get_root_cause_suggestions(
        nc_description: str,
        problem_details: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Generate AI-powered root cause suggestions.

        Args:
            nc_description: Description of the non-conformance
            problem_details: Detailed problem information
            context: Optional additional context

        Returns:
            Dict with suggestions, model used, and confidence score
        """
        # Build the prompt
        prompt = f"""
You are a quality management expert specializing in root cause analysis for manufacturing and testing environments.

Non-Conformance: {nc_description}

Problem Details: {problem_details}
"""

        if context:
            prompt += f"\nAdditional Context: {context}"

        prompt += """

Based on the above information, provide 5-7 potential root causes for this non-conformance.
Consider the following categories:
1. Man (People): Training, competency, human error
2. Machine (Equipment): Calibration, maintenance, malfunction
3. Method (Process): Procedures, work instructions, process control
4. Material: Raw materials, consumables, specifications
5. Measurement: Testing methods, instruments, accuracy
6. Environment: Temperature, humidity, cleanliness, contamination

For each suggested root cause:
- Be specific and actionable
- Indicate the most likely category
- Provide brief reasoning

Format your response as a JSON array of objects with fields: "cause", "category", "reasoning", "likelihood" (high/medium/low)
"""

        # Try to use Anthropic Claude first, fallback to OpenAI or rule-based
        try:
            if settings.ANTHROPIC_API_KEY:
                return AIService._get_suggestions_anthropic(prompt)
            elif settings.OPENAI_API_KEY:
                return AIService._get_suggestions_openai(prompt)
            else:
                return AIService._get_suggestions_rule_based(nc_description, problem_details)
        except Exception as e:
            print(f"AI service error: {e}")
            return AIService._get_suggestions_rule_based(nc_description, problem_details)

    @staticmethod
    def _get_suggestions_anthropic(prompt: str) -> Dict:
        """Get suggestions using Anthropic Claude."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Try to extract JSON from response
            try:
                # Find JSON array in response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    suggestions_data = json.loads(response_text[start_idx:end_idx])
                else:
                    # Fallback parsing
                    suggestions_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured data from text
                suggestions_data = [
                    {
                        "cause": line.strip(),
                        "category": "General",
                        "reasoning": "Analysis based on problem description",
                        "likelihood": "medium"
                    }
                    for line in response_text.split('\n')
                    if line.strip() and not line.strip().startswith(('#', '-', '*'))
                ][:7]

            return {
                "suggestions": suggestions_data,
                "model_used": "claude-3.5-sonnet",
                "confidence_score": 0.85
            }

        except Exception as e:
            print(f"Anthropic API error: {e}")
            raise

    @staticmethod
    def _get_suggestions_openai(prompt: str) -> Dict:
        """Get suggestions using OpenAI."""
        try:
            import openai

            openai.api_key = settings.OPENAI_API_KEY

            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a quality management expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            response_text = response.choices[0].message.content

            # Parse JSON response
            try:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    suggestions_data = json.loads(response_text[start_idx:end_idx])
                else:
                    suggestions_data = json.loads(response_text)
            except json.JSONDecodeError:
                suggestions_data = [
                    {
                        "cause": line.strip(),
                        "category": "General",
                        "reasoning": "Analysis based on problem description",
                        "likelihood": "medium"
                    }
                    for line in response_text.split('\n')
                    if line.strip() and not line.strip().startswith(('#', '-', '*'))
                ][:7]

            return {
                "suggestions": suggestions_data,
                "model_used": "gpt-4-turbo",
                "confidence_score": 0.80
            }

        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise

    @staticmethod
    def _get_suggestions_rule_based(nc_description: str, problem_details: str) -> Dict:
        """
        Generate rule-based suggestions when AI is not available.

        This provides generic but useful root cause suggestions based on common QMS issues.
        """
        # Convert to lowercase for keyword matching
        text = (nc_description + " " + problem_details).lower()

        suggestions = []

        # Equipment-related keywords
        if any(word in text for word in ['equipment', 'machine', 'instrument', 'calibration', 'device']):
            suggestions.extend([
                {
                    "cause": "Equipment calibration not performed or overdue",
                    "category": "Machine",
                    "reasoning": "Equipment-related issue detected; calibration is a common root cause",
                    "likelihood": "high"
                },
                {
                    "cause": "Equipment malfunction or drift from specification",
                    "category": "Machine",
                    "reasoning": "Equipment issues often stem from mechanical or electronic failures",
                    "likelihood": "medium"
                },
                {
                    "cause": "Inadequate preventive maintenance",
                    "category": "Machine",
                    "reasoning": "Lack of maintenance can lead to equipment-related non-conformances",
                    "likelihood": "medium"
                }
            ])

        # Process/Method keywords
        if any(word in text for word in ['process', 'procedure', 'method', 'sop', 'work instruction']):
            suggestions.extend([
                {
                    "cause": "Procedure not followed correctly",
                    "category": "Method",
                    "reasoning": "Process-related terminology suggests procedural issues",
                    "likelihood": "high"
                },
                {
                    "cause": "Work instructions unclear or outdated",
                    "category": "Method",
                    "reasoning": "Ambiguous procedures can lead to incorrect execution",
                    "likelihood": "medium"
                },
                {
                    "cause": "Process parameters not properly controlled",
                    "category": "Method",
                    "reasoning": "Lack of process control is a common manufacturing issue",
                    "likelihood": "medium"
                }
            ])

        # People/Training keywords
        if any(word in text for word in ['training', 'operator', 'personnel', 'staff', 'competency']):
            suggestions.extend([
                {
                    "cause": "Insufficient training or competency",
                    "category": "Man",
                    "reasoning": "Human factors and training gaps are common root causes",
                    "likelihood": "high"
                },
                {
                    "cause": "Human error or oversight",
                    "category": "Man",
                    "reasoning": "Personnel-related issues often involve unintentional mistakes",
                    "likelihood": "medium"
                }
            ])

        # Material keywords
        if any(word in text for word in ['material', 'raw', 'component', 'supplier', 'batch']):
            suggestions.extend([
                {
                    "cause": "Material specification not met",
                    "category": "Material",
                    "reasoning": "Material-related keywords indicate potential input quality issues",
                    "likelihood": "high"
                },
                {
                    "cause": "Supplier quality variation",
                    "category": "Material",
                    "reasoning": "Supplier variations can cause non-conformances",
                    "likelihood": "medium"
                }
            ])

        # Measurement keywords
        if any(word in text for word in ['test', 'measurement', 'result', 'data', 'reading']):
            suggestions.extend([
                {
                    "cause": "Measurement system inadequate or imprecise",
                    "category": "Measurement",
                    "reasoning": "Testing and measurement issues can lead to false results",
                    "likelihood": "medium"
                },
                {
                    "cause": "Test method not validated or inappropriate",
                    "category": "Measurement",
                    "reasoning": "Measurement methodology may not be suitable for the application",
                    "likelihood": "medium"
                }
            ])

        # Environment keywords
        if any(word in text for word in ['environment', 'temperature', 'humidity', 'contamination', 'cleanliness']):
            suggestions.extend([
                {
                    "cause": "Environmental conditions not controlled",
                    "category": "Environment",
                    "reasoning": "Environmental factors can significantly impact quality",
                    "likelihood": "high"
                },
                {
                    "cause": "Contamination from surroundings",
                    "category": "Environment",
                    "reasoning": "Environmental contamination is a common issue in testing labs",
                    "likelihood": "medium"
                }
            ])

        # If no specific keywords matched, provide general suggestions
        if not suggestions:
            suggestions = [
                {
                    "cause": "Inadequate work instructions or procedures",
                    "category": "Method",
                    "reasoning": "General analysis suggests process documentation issues",
                    "likelihood": "medium"
                },
                {
                    "cause": "Insufficient training or competency",
                    "category": "Man",
                    "reasoning": "Human factors are often involved in non-conformances",
                    "likelihood": "medium"
                },
                {
                    "cause": "Equipment calibration or maintenance issues",
                    "category": "Machine",
                    "reasoning": "Equipment-related problems are common in QMS",
                    "likelihood": "medium"
                },
                {
                    "cause": "Process control parameters not monitored",
                    "category": "Method",
                    "reasoning": "Lack of process monitoring can lead to deviations",
                    "likelihood": "low"
                },
                {
                    "cause": "Material or component quality variation",
                    "category": "Material",
                    "reasoning": "Input quality variations can cause non-conformances",
                    "likelihood": "low"
                }
            ]

        # Return top 7 unique suggestions
        unique_suggestions = []
        seen_causes = set()
        for suggestion in suggestions:
            if suggestion["cause"] not in seen_causes:
                unique_suggestions.append(suggestion)
                seen_causes.add(suggestion["cause"])
            if len(unique_suggestions) >= 7:
                break

        return {
            "suggestions": unique_suggestions,
            "model_used": "rule-based",
            "confidence_score": 0.65
        }
