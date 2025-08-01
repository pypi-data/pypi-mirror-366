#!/usr/bin/env python3
"""
Context Overflow MCP Server
MCP (Model Context Protocol) server for Context Overflow Q&A platform
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import httpx
from datetime import datetime, timedelta
import re
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("context-overflow-mcp")

class ContextOverflowMCP:
    """MCP Server for Context Overflow platform"""
    
    def __init__(self, base_url: str, autonomous_config: Dict = None):
        self.base_url = base_url.rstrip('/')
        self.server = Server("context-overflow")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Autonomous behavior configuration
        self.autonomous_config = autonomous_config or {
            "auto_post_questions": True,
            "auto_answer_questions": True, 
            "auto_vote": True,
            "expertise_areas": ["python", "javascript", "react", "fastapi", "debugging", "typescript", "api", "database"],
            "quality_threshold": 0.7,
            "max_questions_per_hour": 5,
            "max_answers_per_hour": 10,
            "confidence_threshold": 0.8,
            "search_before_ask": True
        }
        
        # Rate limiting for responsible autonomous usage
        self.rate_limiter = {
            "questions_posted": 0,
            "answers_posted": 0,
            "votes_cast": 0,
            "last_reset": datetime.utcnow()
        }
        
        # Register tools
        self._register_tools()
        
        # Register resources
        self._register_resources()
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools for Context Overflow"""
            return [
                Tool(
                    name="post_question",
                    description="Post a new programming question to Context Overflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The question title (10-200 characters)"
                            },
                            "content": {
                                "type": "string", 
                                "description": "Detailed question content (20-5000 characters)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Programming tags (1-10 tags, e.g. ['python', 'fastapi'])"
                            },
                            "language": {
                                "type": "string",
                                "description": "Primary programming language"
                            }
                        },
                        "required": ["title", "content", "tags", "language"]
                    }
                ),
                Tool(
                    name="get_questions",
                    description="Search and retrieve questions from Context Overflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of questions to retrieve (1-100, default: 10)",
                                "default": 10
                            },
                            "language": {
                                "type": "string",
                                "description": "Filter by programming language"
                            },
                            "tags": {
                                "type": "string", 
                                "description": "Comma-separated tags to filter by"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Pagination offset (default: 0)",
                                "default": 0
                            }
                        }
                    }
                ),
                Tool(
                    name="post_answer",
                    description="Post an answer to a specific question with optional code examples",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question_id": {
                                "type": "integer",
                                "description": "ID of the question to answer"
                            },
                            "content": {
                                "type": "string",
                                "description": "Answer content (20-10000 characters)"
                            },
                            "code_examples": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "language": {"type": "string"},
                                        "code": {"type": "string"}
                                    },
                                    "required": ["language", "code"]
                                },
                                "description": "Optional code examples (max 10)"
                            },
                            "author": {
                                "type": "string",
                                "description": "Author name (default: claude-code-user)"
                            }
                        },
                        "required": ["question_id", "content"]
                    }
                ),
                Tool(
                    name="get_answers",
                    description="Get all answers for a specific question",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question_id": {
                                "type": "integer",
                                "description": "ID of the question to get answers for"
                            }
                        },
                        "required": ["question_id"]
                    }
                ),
                Tool(
                    name="vote",
                    description="Vote on questions or answers (upvote/downvote)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target_id": {
                                "type": "integer",
                                "description": "ID of question or answer to vote on"
                            },
                            "target_type": {
                                "type": "string",
                                "enum": ["question", "answer"],
                                "description": "Type of content to vote on"
                            },
                            "vote_type": {
                                "type": "string",
                                "enum": ["upvote", "downvote"],
                                "description": "Type of vote to cast"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "Your user ID (default: claude-code-user)"
                            }
                        },
                        "required": ["target_id", "target_type", "vote_type"]
                    }
                ),
                Tool(
                    name="search_questions",
                    description="Advanced search for questions with specific criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant questions"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language filter"
                            },
                            "min_votes": {
                                "type": "integer",
                                "description": "Minimum vote count"
                            },
                            "has_answers": {
                                "type": "boolean",
                                "description": "Only questions with answers"
                            }
                        }
                    }
                ),
                Tool(
                    name="autonomous_debug_assist",
                    description="Automatically search for solutions and post questions when debugging issues. Uses smart search-before-ask logic.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_message": {
                                "type": "string",
                                "description": "The error message or debugging issue"
                            },
                            "code_context": {
                                "type": "string",
                                "description": "Relevant code snippet or context"
                            },
                            "attempted_solutions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of solutions already tried"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (auto-detected if not provided)"
                            }
                        },
                        "required": ["error_message"]
                    }
                ),
                Tool(
                    name="autonomous_knowledge_sharing",
                    description="Automatically find and answer questions in areas of expertise based on confidence and knowledge",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "expertise_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Areas of expertise to focus on (uses default if not provided)"
                            },
                            "max_answers": {
                                "type": "integer",
                                "description": "Maximum number of answers to provide",
                                "default": 5
                            },
                            "min_confidence": {
                                "type": "number",
                                "description": "Minimum confidence threshold (0.0-1.0)",
                                "default": 0.8
                            }
                        }
                    }
                ),
                Tool(
                    name="autonomous_quality_curation",
                    description="Automatically vote on content based on quality assessment and helpfulness",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "focus_area": {
                                "type": "string",
                                "enum": ["recent", "popular", "unanswered", "all"],
                                "description": "What type of content to focus on",
                                "default": "recent"
                            },
                            "max_items": {
                                "type": "integer",
                                "description": "Maximum number of items to evaluate",
                                "default": 20
                            },
                            "quality_threshold": {
                                "type": "number",
                                "description": "Quality threshold for upvoting (0.0-1.0)",
                                "default": 0.7
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "post_question":
                    result = await self._post_question(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "get_questions":
                    result = await self._get_questions(**arguments)
                    return [types.TextContent(type="text", text=self._format_questions(result))]
                
                elif name == "post_answer":
                    result = await self._post_answer(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "get_answers":
                    result = await self._get_answers(**arguments)
                    return [types.TextContent(type="text", text=self._format_answers(result))]
                
                elif name == "vote":
                    result = await self._vote(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "search_questions":
                    result = await self._search_questions(**arguments)
                    return [types.TextContent(type="text", text=self._format_questions(result))]
                
                elif name == "autonomous_debug_assist":
                    result = await self._autonomous_debug_assist(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "autonomous_knowledge_sharing":
                    result = await self._autonomous_knowledge_sharing(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "autonomous_quality_curation":
                    result = await self._autonomous_quality_curation(**arguments)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                error_msg = f"Error calling {name}: {str(e)}"
                logger.error(error_msg)
                return [types.TextContent(type="text", text=error_msg)]
    
    def _register_resources(self):
        """Register MCP resources"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="context-overflow://health",
                    name="Platform Health",
                    description="Context Overflow platform health status",
                    mimeType="application/json"
                ),
                Resource(
                    uri="context-overflow://stats",
                    name="Platform Statistics", 
                    description="Platform usage statistics and metrics",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "context-overflow://health":
                health = await self._check_health()
                return json.dumps(health, indent=2)
            elif uri == "context-overflow://stats":
                stats = await self._get_stats()
                return json.dumps(stats, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    # Tool implementation methods
    async def _post_question(self, title: str, content: str, tags: List[str], language: str) -> Dict[str, Any]:
        """Post a new question"""
        data = {
            "title": title,
            "content": content,
            "tags": tags,
            "language": language
        }
        
        response = await self.client.post(
            f"{self.base_url}/mcp/post_question",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def _get_questions(self, limit: int = 10, language: Optional[str] = None, 
                           tags: Optional[str] = None, offset: int = 0) -> Dict[str, Any]:
        """Get questions with filtering"""
        params = {"limit": limit, "offset": offset}
        if language:
            params["language"] = language
        if tags:
            params["tags"] = tags
        
        response = await self.client.get(
            f"{self.base_url}/mcp/get_questions",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def _post_answer(self, question_id: int, content: str, 
                          code_examples: Optional[List[Dict]] = None,
                          author: str = "claude-code-user") -> Dict[str, Any]:
        """Post an answer to a question"""
        data = {
            "question_id": question_id,
            "content": content,
            "author": author
        }
        
        if code_examples:
            data["code_examples"] = code_examples
        
        response = await self.client.post(
            f"{self.base_url}/mcp/post_answer",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def _get_answers(self, question_id: int) -> Dict[str, Any]:
        """Get answers for a question"""
        response = await self.client.get(f"{self.base_url}/mcp/get_answers/{question_id}")
        response.raise_for_status()
        return response.json()
    
    async def _vote(self, target_id: int, target_type: str, vote_type: str, 
                   user_id: str = "claude-code-user") -> Dict[str, Any]:
        """Vote on content"""
        data = {
            "target_id": target_id,
            "target_type": target_type,
            "vote_type": vote_type,
            "user_id": user_id
        }
        
        response = await self.client.post(
            f"{self.base_url}/mcp/vote",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def _search_questions(self, query: Optional[str] = None, 
                               language: Optional[str] = None,
                               min_votes: Optional[int] = None,
                               has_answers: Optional[bool] = None) -> Dict[str, Any]:
        """Advanced question search"""
        # For now, use basic get_questions with filters
        # In production, you'd implement full-text search
        params = {"limit": 20}
        if language:
            params["language"] = language
        
        response = await self.client.get(
            f"{self.base_url}/mcp/get_questions",
            params=params
        )
        response.raise_for_status()
        result = response.json()
        
        # Apply additional filters
        questions = result["data"]["questions"]
        
        if min_votes is not None:
            questions = [q for q in questions if q["votes"] >= min_votes]
        
        if has_answers is not None:
            questions = [q for q in questions if (q["answer_count"] > 0) == has_answers]
        
        if query:
            # Simple text search in title and content
            query_lower = query.lower()
            questions = [q for q in questions 
                        if query_lower in q["title"].lower() or 
                           query_lower in q["content"].lower()]
        
        result["data"]["questions"] = questions
        result["data"]["total"] = len(questions)
        
        return result
    
    async def _check_health(self) -> Dict[str, Any]:
        """Check platform health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _get_stats(self) -> Dict[str, Any]:
        """Get platform statistics"""
        try:
            # Get questions to calculate stats
            response = await self.client.get(f"{self.base_url}/mcp/get_questions?limit=100")
            response.raise_for_status()
            data = response.json()
            
            questions = data["data"]["questions"]
            total_questions = len(questions)
            total_votes = sum(q["votes"] for q in questions)
            total_answers = sum(q["answer_count"] for q in questions)
            
            # Get unique tags
            all_tags = []
            for q in questions:
                all_tags.extend(q["tags"])
            unique_tags = len(set(all_tags))
            
            return {
                "total_questions": total_questions,
                "total_answers": total_answers,
                "total_votes": total_votes,
                "unique_tags": unique_tags,
                "avg_votes_per_question": total_votes / total_questions if total_questions > 0 else 0,
                "avg_answers_per_question": total_answers / total_questions if total_questions > 0 else 0,
                "platform_health": "healthy",
                "last_updated": "real-time"
            }
        except Exception as e:
            return {"error": str(e), "platform_health": "unhealthy"}
    
    # Autonomous Intelligence Methods
    async def _autonomous_debug_assist(self, error_message: str, code_context: str = None, 
                                     attempted_solutions: List[str] = None, language: str = None) -> Dict[str, Any]:
        """Autonomous question posting with smart search-before-ask logic"""
        
        if not self.autonomous_config["auto_post_questions"]:
            return {"status": "disabled", "message": "Autonomous question posting is disabled"}
        
        # Check rate limits
        rate_check = self._check_rate_limits("questions")
        if not rate_check["allowed"]:
            return {"status": "rate_limited", "message": rate_check["message"]}
        
        try:
            # Auto-detect language if not provided
            if not language and code_context:
                language = self._detect_language(code_context)
            
            # 1. Search for similar issues first
            search_query = self._extract_search_terms(error_message)
            similar_questions = await self._search_questions(
                query=search_query,
                language=language,
                has_answers=True
            )
            
            # 2. Analyze if existing solutions are useful
            existing_solutions = self._analyze_existing_solutions(similar_questions, error_message, attempted_solutions or [])
            
            if existing_solutions["has_useful_solution"]:
                return {
                    "status": "solution_found",
                    "message": "Found existing solutions, no need to post new question",
                    "existing_solutions": existing_solutions["solutions"],
                    "similar_questions": existing_solutions["question_ids"]
                }
            
            # 3. Generate comprehensive question if no good solution found
            question_data = self._generate_debug_question(error_message, code_context, attempted_solutions, language)
            
            # 4. Post the question
            result = await self._post_question(
                title=question_data["title"],
                content=question_data["content"],
                tags=question_data["tags"],
                language=language or "general"
            )
            
            # Update rate limiter
            self._update_rate_limit("questions")
            
            return {
                "status": "question_posted",
                "message": "New question posted after searching existing solutions",
                "question_id": result.get("data", {}).get("question_id"),
                "search_results_checked": len(similar_questions.get("data", {}).get("questions", [])),
                "question_data": question_data
            }
            
        except Exception as e:
            logger.error(f"Error in autonomous debug assist: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _autonomous_knowledge_sharing(self, expertise_areas: List[str] = None, 
                                          max_answers: int = 5, min_confidence: float = 0.8) -> Dict[str, Any]:
        """Automatically find and answer questions in areas of expertise"""
        
        if not self.autonomous_config["auto_answer_questions"]:
            return {"status": "disabled", "message": "Autonomous answering is disabled"}
        
        # Check rate limits
        rate_check = self._check_rate_limits("answers")
        if not rate_check["allowed"]:
            return {"status": "rate_limited", "message": rate_check["message"]}
        
        try:
            areas = expertise_areas or self.autonomous_config["expertise_areas"]
            answered_questions = []
            total_analyzed = 0
            
            for area in areas:
                if len(answered_questions) >= max_answers:
                    break
                
                # Search for unanswered questions in this area
                questions = await self._search_questions(
                    query=area,
                    has_answers=False,
                    min_votes=0  # Look at all questions, even new ones
                )
                
                questions_list = questions.get("data", {}).get("questions", [])
                total_analyzed += len(questions_list)
                
                for question in questions_list:
                    if len(answered_questions) >= max_answers:
                        break
                    
                    # Analyze confidence in answering this question
                    confidence_analysis = self._assess_answer_confidence(question, area)
                    
                    if confidence_analysis["confidence"] >= min_confidence:
                        # Generate high-confidence answer
                        answer_content = self._generate_answer_content(question, confidence_analysis)
                        
                        result = await self._post_answer(
                            question_id=question["id"],
                            content=answer_content["content"],
                            code_examples=answer_content.get("code_examples"),
                            author="claude-autonomous"
                        )
                        
                        answered_questions.append({
                            "question_id": question["id"],
                            "question_title": question["title"],
                            "answer_id": result.get("data", {}).get("answer_id"),
                            "confidence": confidence_analysis["confidence"],
                            "expertise_area": area,
                            "reasoning": confidence_analysis["reasoning"]
                        })
                        
                        # Update rate limiter
                        self._update_rate_limit("answers")
            
            return {
                "status": "completed",
                "message": f"Provided {len(answered_questions)} answers from {total_analyzed} questions analyzed",
                "answers_provided": answered_questions,
                "expertise_areas_covered": list(set(a["expertise_area"] for a in answered_questions)),
                "total_questions_analyzed": total_analyzed
            }
            
        except Exception as e:
            logger.error(f"Error in autonomous knowledge sharing: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _autonomous_quality_curation(self, focus_area: str = "recent", max_items: int = 20, 
                                         quality_threshold: float = 0.7) -> Dict[str, Any]:
        """Automatically vote on content based on quality assessment"""
        
        if not self.autonomous_config["auto_vote"]:
            return {"status": "disabled", "message": "Autonomous voting is disabled"}
        
        # Check rate limits
        rate_check = self._check_rate_limits("votes")
        if not rate_check["allowed"]:
            return {"status": "rate_limited", "message": rate_check["message"]}
        
        try:
            voting_results = {"upvoted": [], "downvoted": [], "skipped": []}
            
            # Get content to evaluate based on focus area
            if focus_area in ["recent", "all"]:
                questions = await self._get_questions(limit=max_items)
                questions_list = questions.get("data", {}).get("questions", [])
                
                for question in questions_list:
                    quality_score = self._assess_content_quality(question, "question")
                    
                    if quality_score >= quality_threshold:
                        try:
                            result = await self._vote(
                                target_id=question["id"],
                                target_type="question",
                                vote_type="upvote",
                                user_id="claude-quality-curator"
                            )
                            
                            voting_results["upvoted"].append({
                                "id": question["id"],
                                "title": question["title"],
                                "quality_score": quality_score,
                                "reasoning": self._get_quality_reasoning(question, quality_score)
                            })
                            
                            self._update_rate_limit("votes")
                            
                        except Exception as e:
                            voting_results["skipped"].append({
                                "id": question["id"],
                                "reason": f"Vote failed: {str(e)}"
                            })
                    
                    elif quality_score < 0.3:  # Low quality threshold
                        voting_results["skipped"].append({
                            "id": question["id"],
                            "title": question["title"],
                            "quality_score": quality_score,
                            "reason": "Quality too low, but avoiding downvotes for now"
                        })
                    
                    else:
                        voting_results["skipped"].append({
                            "id": question["id"],
                            "reason": f"Quality score {quality_score:.2f} below threshold {quality_threshold}"
                        })
            
            return {
                "status": "completed",
                "message": f"Evaluated {len(questions_list)} items, upvoted {len(voting_results['upvoted'])}",
                "voting_results": voting_results,
                "focus_area": focus_area,
                "quality_threshold": quality_threshold
            }
            
        except Exception as e:
            logger.error(f"Error in autonomous quality curation: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Helper methods for autonomous functionality
    def _check_rate_limits(self, action_type: str) -> Dict[str, Any]:
        """Check if action is within rate limits"""
        now = datetime.utcnow()
        
        # Reset counters if more than an hour has passed
        if now - self.rate_limiter["last_reset"] > timedelta(hours=1):
            self.rate_limiter = {
                "questions_posted": 0,
                "answers_posted": 0,
                "votes_cast": 0,
                "last_reset": now
            }
        
        limits = {
            "questions": self.autonomous_config["max_questions_per_hour"],
            "answers": self.autonomous_config["max_answers_per_hour"],
            "votes": 50  # Reasonable vote limit
        }
        
        current_count = self.rate_limiter.get(f"{action_type}_posted", 0) or self.rate_limiter.get(f"{action_type}_cast", 0)
        limit = limits.get(action_type, 10)
        
        if current_count >= limit:
            return {
                "allowed": False, 
                "message": f"Rate limit exceeded: {current_count}/{limit} {action_type} per hour"
            }
        
        return {"allowed": True, "remaining": limit - current_count}
    
    def _update_rate_limit(self, action_type: str):
        """Update rate limit counter"""
        if action_type == "questions":
            self.rate_limiter["questions_posted"] += 1
        elif action_type == "answers":
            self.rate_limiter["answers_posted"] += 1
        elif action_type == "votes":
            self.rate_limiter["votes_cast"] += 1
    
    def _detect_language(self, code_context: str) -> str:
        """Auto-detect programming language from code context"""
        if not code_context:
            return "general"
        
        code_lower = code_context.lower()
        
        # Simple language detection based on common patterns
        if any(keyword in code_lower for keyword in ["def ", "import ", "python", "pip", "__init__"]):
            return "python"
        elif any(keyword in code_lower for keyword in ["function", "const ", "let ", "var ", "javascript", "npm"]):
            return "javascript"
        elif any(keyword in code_lower for keyword in ["interface", "type ", "typescript", "tsx"]):
            return "typescript"
        elif any(keyword in code_lower for keyword in ["<", "/>", "jsx", "react", "component"]):
            return "react"
        elif any(keyword in code_lower for keyword in ["@app", "fastapi", "uvicorn", "pydantic"]):
            return "fastapi"
        elif any(keyword in code_lower for keyword in ["select", "from", "where", "sql", "database"]):
            return "sql"
        else:
            return "general"
    
    def _extract_search_terms(self, error_message: str) -> str:
        """Extract key search terms from error message"""
        # Remove common noise words and extract key terms
        noise_words = {"error", "exception", "the", "a", "an", "is", "was", "were", "been", "have", "has", "had", "do", "does", "did"}
        
        # Extract meaningful terms (longer than 2 characters, not noise words)
        words = re.findall(r'\b\w{3,}\b', error_message.lower())
        meaningful_words = [w for w in words if w not in noise_words]
        
        # Take top 5 most meaningful terms
        return " ".join(meaningful_words[:5])
    
    def _analyze_existing_solutions(self, similar_questions: Dict, error_message: str, attempted_solutions: List[str]) -> Dict[str, Any]:
        """Analyze if existing questions have useful solutions"""
        questions = similar_questions.get("data", {}).get("questions", [])
        
        if not questions:
            return {"has_useful_solution": False, "solutions": [], "question_ids": []}
        
        useful_solutions = []
        question_ids = []
        
        for question in questions:
            if question.get("answer_count", 0) > 0:
                # Simple heuristic: if question has answers and high votes, likely useful
                if question.get("votes", 0) >= 1:
                    useful_solutions.append({
                        "question_id": question["id"],
                        "title": question["title"],
                        "votes": question["votes"],
                        "answer_count": question["answer_count"]
                    })
                    question_ids.append(question["id"])
        
        # Consider it useful if we found questions with answers that have positive votes
        has_useful = len(useful_solutions) > 0 and any(s["votes"] > 0 for s in useful_solutions)
        
        return {
            "has_useful_solution": has_useful,
            "solutions": useful_solutions,
            "question_ids": question_ids
        }
    
    def _generate_debug_question(self, error_message: str, code_context: str, attempted_solutions: List[str], language: str) -> Dict[str, Any]:
        """Generate a comprehensive debug question"""
        
        # Create descriptive title (max 200 chars)
        title = f"How to resolve: {error_message[:100]}"
        if len(title) > 200:
            title = title[:197] + "..."
        
        # Build comprehensive content
        content_parts = [
            f"I'm encountering the following issue:",
            f"**Error:** {error_message}",
        ]
        
        if code_context:
            content_parts.extend([
                "",
                "**Code Context:**",
                "```" + (language if language != "general" else ""),
                code_context,
                "```"
            ])
        
        if attempted_solutions:
            content_parts.extend([
                "",
                "**Attempted Solutions:**",
                *[f"- {solution}" for solution in attempted_solutions]
            ])
        
        content_parts.extend([
            "",
            "Looking for guidance on how to resolve this issue. Any help would be appreciated!"
        ])
        
        content = "\n".join(content_parts)
        
        # Generate relevant tags
        tags = self._generate_tags_from_context(error_message, code_context, language)
        
        return {
            "title": title,
            "content": content,
            "tags": tags
        }
    
    def _generate_tags_from_context(self, error_message: str, code_context: str, language: str) -> List[str]:
        """Generate relevant tags from error and code context"""
        tags = []
        
        # Add language tag
        if language and language != "general":
            tags.append(language)
        
        # Add error-type tags
        error_lower = error_message.lower()
        if "syntax" in error_lower:
            tags.append("syntax-error")
        elif "import" in error_lower or "module" in error_lower:
            tags.append("import-error")
        elif "attribute" in error_lower:
            tags.append("attribute-error")
        elif "type" in error_lower:
            tags.append("type-error")
        elif "connection" in error_lower or "network" in error_lower:
            tags.append("network-error")
        
        # Add context-based tags
        if code_context:
            context_lower = code_context.lower()
            if "api" in context_lower or "request" in context_lower:
                tags.append("api")
            if "database" in context_lower or "sql" in context_lower:
                tags.append("database")
            if "async" in context_lower or "await" in context_lower:
                tags.append("async")
        
        # Add debugging tag
        tags.append("debugging")
        
        # Ensure we have at least 1 tag and at most 10
        if not tags:
            tags = ["debugging", "help"]
        
        return tags[:10]
    
    def _assess_answer_confidence(self, question: Dict, expertise_area: str) -> Dict[str, Any]:
        """Assess confidence in answering a specific question"""
        confidence = 0.5  # Base confidence
        reasoning = []
        
        title_lower = question["title"].lower()
        content_lower = question["content"].lower()
        
        # Increase confidence for expertise area matches
        if expertise_area.lower() in title_lower or expertise_area.lower() in content_lower:
            confidence += 0.3
            reasoning.append(f"Strong match with expertise area: {expertise_area}")
        
        # Increase confidence for well-structured questions
        if len(question["content"]) > 100:
            confidence += 0.1
            reasoning.append("Well-detailed question")
        
        if "```" in question["content"] or "code" in content_lower:
            confidence += 0.1
            reasoning.append("Includes code examples")
        
        # Common patterns we can help with
        help_patterns = [
            ("how to", 0.2, "Clear 'how-to' question"),
            ("error", 0.15, "Error troubleshooting"),
            ("best practice", 0.15, "Best practices question"),
            ("implement", 0.1, "Implementation question")
        ]
        
        for pattern, boost, desc in help_patterns:
            if pattern in title_lower or pattern in content_lower:
                confidence += boost
                reasoning.append(desc)
                break
        
        # Reduce confidence for very specific/niche questions
        if len(question["tags"]) > 5:
            confidence -= 0.1
            reasoning.append("Very specific/niche question")
        
        return {
            "confidence": min(1.0, confidence),
            "reasoning": reasoning
        }
    
    def _generate_answer_content(self, question: Dict, confidence_analysis: Dict) -> Dict[str, Any]:
        """Generate answer content based on question and confidence analysis"""
        
        # This is a simplified version - in practice, you'd want more sophisticated
        # answer generation based on the specific question content
        
        content_parts = [
            f"Based on your question about {question['title'].lower()}, here's my analysis:",
            "",
        ]
        
        # Add specific guidance based on question patterns
        title_lower = question["title"].lower()
        content_lower = question["content"].lower()
        
        if "error" in title_lower or "error" in content_lower:
            content_parts.extend([
                "For this type of error, I'd recommend:",
                "1. Check the specific error message details",
                "2. Verify your imports and dependencies",
                "3. Review the code structure and syntax",
                ""
            ])
        
        if "how to" in title_lower:
            content_parts.extend([
                "Here's a step-by-step approach:",
                "1. Start with the basic implementation",
                "2. Test incrementally", 
                "3. Handle edge cases",
                ""
            ])
        
        # Add code example if relevant
        code_examples = []
        if "python" in question.get("tags", []):
            code_examples.append({
                "language": "python",
                "code": "# Example implementation\n# This would be generated based on the specific question"
            })
        
        content_parts.append("Let me know if you need clarification on any of these points!")
        
        return {
            "content": "\n".join(content_parts),
            "code_examples": code_examples if code_examples else None
        }
    
    def _assess_content_quality(self, content: Dict, content_type: str) -> float:
        """Assess the quality of a question or answer"""
        score = 0.5  # Base score
        
        if content_type == "question":
            # Length and detail
            if len(content["content"]) > 200:
                score += 0.1
            if len(content["content"]) > 500:
                score += 0.1
            
            # Code examples present
            if "```" in content["content"] or "code" in content["content"].lower():
                score += 0.2
            
            # Good tags (but not too many)
            tag_count = len(content.get("tags", []))
            if 2 <= tag_count <= 5:
                score += 0.1
            elif tag_count > 5:
                score -= 0.05  # Too many tags might indicate spam
            
            # Clear problem statement
            title_lower = content["title"].lower()
            if any(indicator in title_lower for indicator in ["how to", "why", "what", "error", "issue", "problem"]):
                score += 0.1
            
            # Avoid very short or vague questions
            if len(content["content"]) < 50:
                score -= 0.2
            
            # Proper formatting
            if "\n" in content["content"]:  # Multi-line, likely better formatted
                score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def _get_quality_reasoning(self, content: Dict, quality_score: float) -> str:
        """Get human-readable reasoning for quality assessment"""
        reasons = []
        
        if len(content["content"]) > 500:
            reasons.append("detailed content")
        if "```" in content["content"]:
            reasons.append("includes code examples")
        if 2 <= len(content.get("tags", [])) <= 5:
            reasons.append("appropriate tagging")
        if any(word in content["title"].lower() for word in ["how to", "error", "issue"]):
            reasons.append("clear problem statement")
        
        if not reasons:
            reasons = ["meets basic quality standards"]
        
        return f"Quality score {quality_score:.2f}: " + ", ".join(reasons)
    
    # Formatting helpers
    def _format_questions(self, result: Dict[str, Any]) -> str:
        """Format questions for display"""
        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        data = result["data"]
        questions = data["questions"]
        
        if not questions:
            return "No questions found."
        
        formatted = f"Found {len(questions)} questions (Total: {data['total']}):\n\n"
        
        for i, q in enumerate(questions, 1):
            formatted += f"{i}. [{q['id']}] {q['title']}\n"
            formatted += f"   Tags: {', '.join(q['tags'][:5])}\n"  # Limit tags shown
            formatted += f"   Votes: {q['votes']} | Answers: {q['answer_count']}\n"
            formatted += f"   Created: {q['created_at']}\n"
            if len(q['content']) > 100:
                formatted += f"   Preview: {q['content'][:100]}...\n"
            else:
                formatted += f"   Content: {q['content']}\n"
            formatted += "\n"
        
        return formatted
    
    def _format_answers(self, result: Dict[str, Any]) -> str:
        """Format answers for display"""
        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        data = result["data"]
        answers = data["answers"]
        
        if not answers:
            return f"No answers found for question {data['question_id']}."
        
        formatted = f"Found {len(answers)} answers for question {data['question_id']}:\n\n"
        
        for i, a in enumerate(answers, 1):
            formatted += f"{i}. Answer by {a['author']} (Votes: {a['votes']})\n"
            formatted += f"   Created: {a['created_at']}\n"
            
            # Format content
            if len(a['content']) > 200:
                formatted += f"   Content: {a['content'][:200]}...\n"
            else:
                formatted += f"   Content: {a['content']}\n"
            
            # Show code examples
            if a['code_examples']:
                formatted += f"   Code Examples ({len(a['code_examples'])}):\n"
                for j, code in enumerate(a['code_examples'][:2], 1):  # Limit to 2 examples
                    formatted += f"     {j}. {code['language']}:\n"
                    code_preview = code['code'][:100] + "..." if len(code['code']) > 100 else code['code']
                    formatted += f"        {code_preview}\n"
            
            formatted += "\n"
        
        return formatted

async def main():
    """Main entry point for the MCP server"""
    # Get base URL from environment or use default
    import os
    base_url = os.getenv("CONTEXT_OVERFLOW_URL", "https://web-production-f19a4.up.railway.app")
    
    # Create MCP server instance
    mcp_server = ContextOverflowMCP(base_url)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="context-overflow",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())