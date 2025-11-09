"""
Claude AI Orchestration & Chatbot
Natural language interface for the LIMS-QMS platform
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import asyncio
from anthropic import AsyncAnthropic
from backend.core.config import settings
from backend.integrations.events import event_bus, Event, EventType
import logging

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Central AI orchestration system
    Integrates Claude AI for intelligent automation and assistance
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.context_cache: Dict[str, Any] = {}

    async def chat(
        self,
        message: str,
        user_id: int,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process chat message with Claude

        Args:
            message: User message
            user_id: User ID
            context: Additional context (current page, data, etc.)
            conversation_id: Conversation ID for multi-turn dialogue

        Returns:
            AI response with suggestions and actions
        """
        if not self.client:
            return {
                "response": "AI service is not configured. Please set ANTHROPIC_API_KEY.",
                "error": True
            }

        try:
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = f"{user_id}_{int(datetime.utcnow().timestamp())}"

            # Initialize conversation history
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []

            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)

            # Add user message to history
            self.conversation_history[conversation_id].append({
                "role": "user",
                "content": message
            })

            # Call Claude API
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=self.conversation_history[conversation_id]
            )

            # Extract response
            assistant_message = response.content[0].text

            # Add assistant message to history
            self.conversation_history[conversation_id].append({
                "role": "assistant",
                "content": assistant_message
            })

            # Parse response for actions
            actions = self._extract_actions(assistant_message)

            # Publish event
            await event_bus.publish(Event(
                type=EventType.NOTIFICATION_SENT,
                source="ai_orchestrator",
                data={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "message_type": "ai_response"
                },
                user_id=user_id
            ))

            return {
                "response": assistant_message,
                "conversation_id": conversation_id,
                "actions": actions,
                "error": False
            }

        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "error": True
            }

    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt with context"""
        base_prompt = """You are an AI assistant for a LIMS-QMS Organization Operating System.

You help users with:
- Document management and search
- Form filling and validation
- Project and task management
- Workflow automation
- Quality management (NC, CAPA, Audits)
- HR operations (training, leave, recruitment)
- Procurement (RFQ, PO, vendor management)
- Financial tracking (invoices, payments)
- CRM (leads, opportunities, customers)
- Analytics and reporting
- Compliance checking
- Data extraction from documents

Be concise, professional, and action-oriented. When suggesting actions, use structured JSON format.

Available actions:
- search_documents: Search for documents
- create_task: Create a new task
- update_form: Update form data
- generate_report: Generate analytics report
- check_compliance: Check compliance status
- extract_data: Extract data from document
- recommend_workflow: Recommend workflow steps
"""

        # Add context information
        if context:
            context_str = "\n\nCurrent Context:\n"
            if "page" in context:
                context_str += f"- Current Page: {context['page']}\n"
            if "user_role" in context:
                context_str += f"- User Role: {context['user_role']}\n"
            if "module" in context:
                context_str += f"- Current Module: {context['module']}\n"
            if "data" in context:
                context_str += f"- Available Data: {json.dumps(context['data'], indent=2)}\n"

            base_prompt += context_str

        return base_prompt

    def _extract_actions(self, message: str) -> List[Dict[str, Any]]:
        """Extract structured actions from AI response"""
        actions = []

        # Look for JSON action blocks in the message
        try:
            # Simple pattern matching for action blocks
            if "```json" in message:
                json_blocks = message.split("```json")[1:]
                for block in json_blocks:
                    json_str = block.split("```")[0].strip()
                    action = json.loads(json_str)
                    actions.append(action)
        except:
            pass

        return actions

    async def smart_search(
        self,
        query: str,
        user_id: int,
        scope: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Natural language document search

        Args:
            query: Natural language search query
            user_id: User ID
            scope: Search scope (modules to search)

        Returns:
            Search results with relevance ranking
        """
        try:
            # Build search prompt
            prompt = f"""Search for documents and data matching this query: "{query}"

Scope: {', '.join(scope) if scope else 'All modules'}

Return results in JSON format with:
- search_terms: Extracted keywords
- filters: Suggested filters (date, type, status, etc.)
- modules: Relevant modules to search
- sort_by: Recommended sort order
"""

            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            result = json.loads(response.content[0].text)

            return {
                "query": query,
                "parsed_query": result,
                "error": False
            }

        except Exception as e:
            logger.error(f"Smart search error: {e}")
            return {
                "query": query,
                "error": True,
                "message": str(e)
            }

    async def extract_data_from_document(
        self,
        document_content: str,
        document_type: str,
        fields_to_extract: List[str]
    ) -> Dict[str, Any]:
        """
        Extract structured data from documents using AI

        Args:
            document_content: Document text content
            document_type: Type of document (invoice, report, certificate, etc.)
            fields_to_extract: List of fields to extract

        Returns:
            Extracted data
        """
        try:
            prompt = f"""Extract the following fields from this {document_type}:

Fields to extract: {', '.join(fields_to_extract)}

Document content:
{document_content[:4000]}  # Limit to avoid token limits

Return data in JSON format with the extracted fields.
"""

            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            extracted_data = json.loads(response.content[0].text)

            return {
                "extracted_data": extracted_data,
                "confidence": "high",  # Could add confidence scoring
                "error": False
            }

        except Exception as e:
            logger.error(f"Data extraction error: {e}")
            return {
                "error": True,
                "message": str(e)
            }

    async def recommend_workflow(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend workflow steps for a task

        Args:
            task_description: Description of the task
            context: Additional context

        Returns:
            Recommended workflow steps
        """
        try:
            context_str = json.dumps(context, indent=2) if context else "None"

            prompt = f"""Recommend workflow steps for this task:

Task: {task_description}

Context: {context_str}

Return a structured workflow in JSON format with:
- steps: List of workflow steps
- approvals: Required approvals
- notifications: Who to notify at each step
- estimated_duration: Estimated time for completion
- dependencies: Task dependencies
"""

            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            workflow = json.loads(response.content[0].text)

            return {
                "workflow": workflow,
                "error": False
            }

        except Exception as e:
            logger.error(f"Workflow recommendation error: {e}")
            return {
                "error": True,
                "message": str(e)
            }

    async def check_compliance(
        self,
        document_type: str,
        content: Dict[str, Any],
        standards: List[str]
    ) -> Dict[str, Any]:
        """
        Check document compliance with standards

        Args:
            document_type: Type of document
            content: Document content
            standards: Compliance standards (ISO, FDA, etc.)

        Returns:
            Compliance check results
        """
        try:
            prompt = f"""Check this {document_type} for compliance with: {', '.join(standards)}

Document data:
{json.dumps(content, indent=2)}

Return compliance report in JSON format with:
- compliant: Overall compliance status
- issues: List of compliance issues
- recommendations: Recommendations to fix issues
- severity: Severity of each issue (high, medium, low)
"""

            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            compliance_report = json.loads(response.content[0].text)

            return {
                "report": compliance_report,
                "error": False
            }

        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            return {
                "error": True,
                "message": str(e)
            }

    async def generate_report_from_prompt(
        self,
        prompt: str,
        data_sources: List[str],
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Generate report from natural language prompt

        Args:
            prompt: Natural language description of report
            data_sources: Data sources to use
            format: Output format (markdown, html, pdf)

        Returns:
            Generated report
        """
        try:
            report_prompt = f"""Generate a {format} report based on this request:

{prompt}

Use data from: {', '.join(data_sources)}

Include:
- Executive summary
- Key metrics and KPIs
- Visualizations (describe them)
- Trends and insights
- Recommendations

Format the output in {format}.
"""

            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": report_prompt}]
            )

            report_content = response.content[0].text

            return {
                "report": report_content,
                "format": format,
                "error": False
            }

        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return {
                "error": True,
                "message": str(e)
            }

    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]


# Global AI orchestrator instance
ai_orchestrator = AIOrchestrator()
