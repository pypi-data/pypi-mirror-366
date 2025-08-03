"""
Layer 3: External LLM Vendor Integration
Makes calls to external LLM providers (OpenAI, Claude, etc.) for complex reasoning
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, AsyncGenerator
from enum import Enum
from dataclasses import dataclass, asdict
import time


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    CLAUDE = "claude"
    AZURE = "azure"
    LOCAL = "local"


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: LLMProvider
    api_key: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class ReasoningRequest:
    """Request for Layer 3 reasoning"""
    sensory_data: Dict[str, Any]
    interpretation_result: Dict[str, Any]
    context: Optional[str] = None
    task_type: str = "general"
    priority: str = "medium"


@dataclass
class ReasoningResponse:
    """Response from Layer 3 reasoning"""
    success: bool
    response_text: str
    reasoning_chain: List[str]
    confidence: float
    suggested_actions: List[str]
    tokens_used: int
    processing_time: float
    error_message: Optional[str] = None


class BaseLLMClient:
    """Base class for LLM clients"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0.0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Perform reasoning using the LLM"""
        raise NotImplementedError
    
    async def _rate_limit(self):
        """Apply rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()


class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.openai.com/v1"
        self.model = config.model or "gpt-3.5-turbo"
    
    async def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Reason using OpenAI API"""
        start_time = time.time()
        
        await self._rate_limit()
        
        try:
            prompt = self._build_prompt(request)
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return self._parse_openai_response(response_data, start_time)
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    return ReasoningResponse(
                        success=False,
                        response_text="",
                        reasoning_chain=[],
                        confidence=0.0,
                        suggested_actions=[],
                        tokens_used=0,
                        processing_time=time.time() - start_time,
                        error_message=f"OpenAI API error: {error_msg}"
                    )
        
        except Exception as e:
            return ReasoningResponse(
                success=False,
                response_text="",
                reasoning_chain=[],
                confidence=0.0,
                suggested_actions=[],
                tokens_used=0,
                processing_time=time.time() - start_time,
                error_message=f"Request failed: {str(e)}"
            )
    
    def _build_prompt(self, request: ReasoningRequest) -> str:
        """Build prompt for OpenAI"""
        prompt_parts = [
            "You are Cortex, an intelligent reasoning system. Analyze the following data and provide reasoning.",
            "",
            "SENSORY DATA:",
            json.dumps(request.sensory_data, indent=2),
            "",
            "INTERPRETATION RESULT:",
            json.dumps(request.interpretation_result, indent=2),
            ""
        ]
        
        if request.context:
            prompt_parts.extend([
                "CONTEXT:",
                request.context,
                ""
            ])
        
        prompt_parts.extend([
            f"TASK TYPE: {request.task_type}",
            f"PRIORITY: {request.priority}",
            "",
            "Please provide:",
            "1. Your reasoning chain (step-by-step analysis)",
            "2. Your confidence level (0-1)",
            "3. Suggested actions to take",
            "4. A concise response summarizing your analysis",
            "",
            "Format your response as JSON with keys: reasoning_chain, confidence, suggested_actions, response_text"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_openai_response(self, response_data: Dict[str, Any], start_time: float) -> ReasoningResponse:
        """Parse OpenAI response"""
        try:
            message = response_data["choices"][0]["message"]["content"]
            tokens_used = response_data.get("usage", {}).get("total_tokens", 0)
            
            # Try to parse as JSON
            try:
                parsed = json.loads(message)
                return ReasoningResponse(
                    success=True,
                    response_text=parsed.get("response_text", message),
                    reasoning_chain=parsed.get("reasoning_chain", [message]),
                    confidence=float(parsed.get("confidence", 0.7)),
                    suggested_actions=parsed.get("suggested_actions", []),
                    tokens_used=tokens_used,
                    processing_time=time.time() - start_time
                )
            except json.JSONDecodeError:
                # Fallback to treating entire message as response
                return ReasoningResponse(
                    success=True,
                    response_text=message,
                    reasoning_chain=[message],
                    confidence=0.7,
                    suggested_actions=["review_response"],
                    tokens_used=tokens_used,
                    processing_time=time.time() - start_time
                )
        
        except (KeyError, IndexError, TypeError) as e:
            return ReasoningResponse(
                success=False,
                response_text="",
                reasoning_chain=[],
                confidence=0.0,
                suggested_actions=[],
                tokens_used=0,
                processing_time=time.time() - start_time,
                error_message=f"Failed to parse response: {str(e)}"
            )


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude API client"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.anthropic.com/v1"
        self.model = config.model or "claude-3-sonnet-20240229"
    
    async def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Reason using Claude API"""
        start_time = time.time()
        
        await self._rate_limit()
        
        try:
            prompt = self._build_prompt(request)
            
            headers = {
                "x-api-key": self.config.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            async with self.session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return self._parse_claude_response(response_data, start_time)
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    return ReasoningResponse(
                        success=False,
                        response_text="",
                        reasoning_chain=[],
                        confidence=0.0,
                        suggested_actions=[],
                        tokens_used=0,
                        processing_time=time.time() - start_time,
                        error_message=f"Claude API error: {error_msg}"
                    )
        
        except Exception as e:
            return ReasoningResponse(
                success=False,
                response_text="",
                reasoning_chain=[],
                confidence=0.0,
                suggested_actions=[],
                tokens_used=0,
                processing_time=time.time() - start_time,
                error_message=f"Request failed: {str(e)}"
            )
    
    def _build_prompt(self, request: ReasoningRequest) -> str:
        """Build prompt for Claude"""
        return self._build_prompt_common(request)
    
    def _build_prompt_common(self, request: ReasoningRequest) -> str:
        """Common prompt building logic"""
        prompt_parts = [
            "I am Cortex, an intelligent reasoning system. I need to analyze sensory data and provide reasoning.",
            "",
            "SENSORY DATA:",
            json.dumps(request.sensory_data, indent=2),
            "",
            "INTERPRETATION RESULT:",
            json.dumps(request.interpretation_result, indent=2),
            ""
        ]
        
        if request.context:
            prompt_parts.extend([
                "CONTEXT:",
                request.context,
                ""
            ])
        
        prompt_parts.extend([
            f"TASK TYPE: {request.task_type}",
            f"PRIORITY: {request.priority}",
            "",
            "I need to provide:",
            "1. My reasoning chain (step-by-step analysis)",
            "2. My confidence level (0-1)",
            "3. Suggested actions to take",
            "4. A concise response summarizing my analysis",
            "",
            "I'll format my response as JSON with keys: reasoning_chain, confidence, suggested_actions, response_text"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_claude_response(self, response_data: Dict[str, Any], start_time: float) -> ReasoningResponse:
        """Parse Claude response"""
        try:
            content = response_data["content"][0]["text"]
            tokens_used = response_data.get("usage", {}).get("output_tokens", 0)
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                return ReasoningResponse(
                    success=True,
                    response_text=parsed.get("response_text", content),
                    reasoning_chain=parsed.get("reasoning_chain", [content]),
                    confidence=float(parsed.get("confidence", 0.7)),
                    suggested_actions=parsed.get("suggested_actions", []),
                    tokens_used=tokens_used,
                    processing_time=time.time() - start_time
                )
            except json.JSONDecodeError:
                # Fallback to treating entire content as response
                return ReasoningResponse(
                    success=True,
                    response_text=content,
                    reasoning_chain=[content],
                    confidence=0.7,
                    suggested_actions=["review_response"],
                    tokens_used=tokens_used,
                    processing_time=time.time() - start_time
                )
        
        except (KeyError, IndexError, TypeError) as e:
            return ReasoningResponse(
                success=False,
                response_text="",
                reasoning_chain=[],
                confidence=0.0,
                suggested_actions=[],
                tokens_used=0,
                processing_time=time.time() - start_time,
                error_message=f"Failed to parse response: {str(e)}"
            )


class LocalLLMClient(BaseLLMClient):
    """Local LLM client (for local models via API)"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"  # Default Ollama port
        self.model = config.model or "llama2"
    
    async def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Reason using local LLM"""
        start_time = time.time()
        
        try:
            prompt = self._build_prompt_common(request)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    content = response_data.get("response", "")
                    return ReasoningResponse(
                        success=True,
                        response_text=content,
                        reasoning_chain=[content],
                        confidence=0.6,  # Default for local models
                        suggested_actions=["review_local_response"],
                        tokens_used=len(content.split()),  # Approximate
                        processing_time=time.time() - start_time
                    )
                else:
                    return ReasoningResponse(
                        success=False,
                        response_text="",
                        reasoning_chain=[],
                        confidence=0.0,
                        suggested_actions=[],
                        tokens_used=0,
                        processing_time=time.time() - start_time,
                        error_message="Local LLM request failed"
                    )
        
        except Exception as e:
            return ReasoningResponse(
                success=False,
                response_text="",
                reasoning_chain=[],
                confidence=0.0,
                suggested_actions=[],
                tokens_used=0,
                processing_time=time.time() - start_time,
                error_message=f"Local LLM error: {str(e)}"
            )
    
    def _build_prompt_common(self, request: ReasoningRequest) -> str:
        """Build prompt for local LLM"""
        return f"""Analyze this data and provide reasoning:

SENSORY DATA: {json.dumps(request.sensory_data)}
INTERPRETATION: {json.dumps(request.interpretation_result)}
TASK: {request.task_type}
PRIORITY: {request.priority}

Provide your analysis and reasoning:"""


class ReasoningLayer:
    """
    Layer 3: Manages external LLM reasoning and provider selection
    """
    
    def __init__(self):
        self.providers: Dict[LLMProvider, BaseLLMClient] = {}
        self.primary_provider: Optional[LLMProvider] = None
        self.fallback_providers: List[LLMProvider] = []
        self.reasoning_history = []
        self.max_history = 50
    
    def add_provider(self, config: LLMConfig, is_primary: bool = False):
        """Add an LLM provider"""
        if config.provider == LLMProvider.OPENAI:
            client = OpenAIClient(config)
        elif config.provider == LLMProvider.CLAUDE:
            client = ClaudeClient(config)
        elif config.provider == LLMProvider.LOCAL:
            client = LocalLLMClient(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        self.providers[config.provider] = client
        
        if is_primary or self.primary_provider is None:
            self.primary_provider = config.provider
        else:
            if config.provider not in self.fallback_providers:
                self.fallback_providers.append(config.provider)
    
    async def reason(self, 
                    sensory_data: Dict[str, Any], 
                    interpretation_result: Dict[str, Any],
                    context: Optional[str] = None,
                    task_type: str = "general") -> ReasoningResponse:
        """
        Perform reasoning using available LLM providers
        
        Args:
            sensory_data: Raw sensory data from Layer 1
            interpretation_result: Interpretation from Layer 2
            context: Additional context for reasoning
            task_type: Type of reasoning task
            
        Returns:
            ReasoningResponse with LLM analysis
        """
        request = ReasoningRequest(
            sensory_data=sensory_data,
            interpretation_result=interpretation_result,
            context=context,
            task_type=task_type,
            priority=interpretation_result.get("reaction_level", "medium")
        )
        
        # Try primary provider first
        if self.primary_provider and self.primary_provider in self.providers:
            async with self.providers[self.primary_provider] as client:
                response = await client.reason(request)
                if response.success:
                    self._add_to_history(request, response, self.primary_provider)
                    return response
        
        # Try fallback providers
        for provider in self.fallback_providers:
            if provider in self.providers:
                try:
                    async with self.providers[provider] as client:
                        response = await client.reason(request)
                        if response.success:
                            self._add_to_history(request, response, provider)
                            return response
                except Exception:
                    continue
        
        # All providers failed
        return ReasoningResponse(
            success=False,
            response_text="",
            reasoning_chain=[],
            confidence=0.0,
            suggested_actions=["check_llm_providers"],
            tokens_used=0,
            processing_time=0.0,
            error_message="All LLM providers failed"
        )
    
    def _add_to_history(self, 
                       request: ReasoningRequest, 
                       response: ReasoningResponse, 
                       provider: LLMProvider):
        """Add reasoning interaction to history"""
        self.reasoning_history.append({
            "timestamp": time.time(),
            "provider": provider.value,
            "request": asdict(request),
            "response": asdict(response),
            "success": response.success
        })
        
        # Maintain history size
        if len(self.reasoning_history) > self.max_history:
            self.reasoning_history.pop(0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for providers"""
        if not self.reasoning_history:
            return {"total_requests": 0, "providers": {}}
        
        provider_stats = {}
        total_requests = len(self.reasoning_history)
        
        for entry in self.reasoning_history:
            provider = entry["provider"]
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "requests": 0,
                    "successes": 0,
                    "total_tokens": 0,
                    "total_time": 0.0
                }
            
            stats = provider_stats[provider]
            stats["requests"] += 1
            if entry["success"]:
                stats["successes"] += 1
            stats["total_tokens"] += entry["response"]["tokens_used"]
            stats["total_time"] += entry["response"]["processing_time"]
        
        # Calculate rates and averages
        for provider, stats in provider_stats.items():
            if stats["requests"] > 0:
                stats["success_rate"] = stats["successes"] / stats["requests"]
                stats["avg_tokens"] = stats["total_tokens"] / stats["requests"]
                stats["avg_time"] = stats["total_time"] / stats["requests"]
        
        return {
            "total_requests": total_requests,
            "providers": provider_stats,
            "primary_provider": self.primary_provider.value if self.primary_provider else None,
            "fallback_providers": [p.value for p in self.fallback_providers]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of reasoning layer"""
        return {
            "configured_providers": list(self.providers.keys()),
            "primary_provider": self.primary_provider.value if self.primary_provider else None,
            "fallback_providers": [p.value for p in self.fallback_providers],
            "performance_stats": self.get_performance_stats()
        }