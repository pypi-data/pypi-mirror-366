"""
ROS QA System - A simple chatbot for answering ROS and ROS2 questions
"""

import logging
from typing import Dict, Any, List, Optional
import openai
import requests
import json
import os
import re

from .config import (
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION,
    OPENAI_API_KEY, RETRIEVAL_API_BASE_URL
)

from .tools import ROSToolSystem

logger = logging.getLogger(__name__)

class ROSQASystem:
    """A QA system specialized in answering ROS and ROS2 questions"""
    
    def __init__(self, use_retrieval: bool = True, collection_name: str = "ros_oorb_docs", 
                 enable_tools: bool = True, retrieval_api_url: str = RETRIEVAL_API_BASE_URL):
        """
        Initialize the ROS QA System
        
        Args:
            use_retrieval: Whether to use retrieval augmented generation
            collection_name: Collection name for retrieval
            enable_tools: Whether to enable OpenAI function calling tools
            retrieval_api_url: Base URL for the retrieval API
        """
        self.use_retrieval = use_retrieval
        self.retrieval_api_url = retrieval_api_url
        self.collection_name = collection_name
        self.enable_tools = enable_tools
        self.openai_client = None
        self.tool_system = None
        self.model_name = None
        
        # Initialize OpenAI client (prefer Azure OpenAI)
        if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
            self.openai_client = openai.AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_version=AZURE_OPENAI_API_VERSION
            )
            # Initialize tool system if enabled
            if self.enable_tools:
                try:
                    self.tool_system = ROSToolSystem(AZURE_OPENAI_API_KEY, use_azure=True)
                except Exception as e:
                    logger.error(f"Failed to initialize tool system: {e}")
                    self.tool_system = None
                    
        elif OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Initialize tool system if enabled
            if self.enable_tools:
                try:
                    self.tool_system = ROSToolSystem(OPENAI_API_KEY, use_azure=False)
                except Exception as e:
                    logger.error(f"Failed to initialize tool system: {e}")
                    self.tool_system = None
        
        # Initialize retrieval system via API if enabled
        if self.use_retrieval:
            logger.info("Retrieval system enabled - will use API endpoints directly")
            # No initialization needed - API calls will be made directly
        
    def _get_ros_system_prompt(self) -> str:
        """Generate system prompt for ROS2"""
        
        return """You are OORB, a knowledgeable ROS2 expert assistant. Help users with ROS2 questions, providing accurate and practical information.

Key expertise:
- ROS2 concepts (nodes, topics, services, actions, parameters)
- Package development with colcon/ament
- Launch files and configuration
- Debugging and troubleshooting
- Best practices and design patterns
- Hardware integration and simulation
- Navigation2 and perception

Guidelines:
1. Provide clear, step-by-step instructions
2. Include relevant code examples with proper language tags
3. Mention important considerations and pitfalls
4. Suggest best practices
5. Be specific about ROS2 distributions when relevant
6. Include package names and dependencies
7. Provide debugging tips when appropriate

"""

    def _get_ros_system_prompt_for_tools(self) -> str:
        """Generate system prompt optimized for tool usage"""
        
        base_prompt = """You are OORB, an expert ROS2 assistant with file manipulation tools.

🔧 AVAILABLE TOOLS:
- run_command (use 'tree' to explore directories)
- read_file, write_file, edit_file_lines
- search_in_files, list_directory, analyze_code

� EFFICIENT WORKFLOW:
1. 🌳 START with 'tree' command to locate files
2. 📖 Read target files to understand structure  
3. 🔍 Search for specific patterns if needed
4. ✏️ Make changes with edit_file_lines
5. ✅ Verify changes with read_file

⚡ KEY RULES:
- Always use 'tree' first to find files efficiently
- Use edit_file_lines for ALL file modifications
- Complete tasks fully - don't just explore
- Progress logically toward the goal

🎯 EXAMPLE WORKFLOW (rate change):
1. run_command: "tree -I '__pycache__' ." 
2. read_file: examine target file
3. search_in_files: find rate pattern
4. edit_file_lines: change the rate value
5. read_file: verify the change

Be concise, efficient, and task-focused."""
        
        return base_prompt

    def _get_enhanced_system_prompt(self, context_info: Dict[str, Any] = None, 
                                   use_tools: bool = False, 
                                   selected_distro: str = None) -> str:
        """
        Generate enhanced system prompt with context for different usage scenarios.
        
        Args:
            context_info: Context information from retrieval
            use_tools: Whether this prompt is for tool usage
            selected_distro: Specific ROS2 distro for distro-aware responses
            
        Returns:
            Enhanced system prompt with context
        """
        # Determine base prompt based on usage scenario
        if use_tools:
            base_prompt = self._get_ros_system_prompt_for_tools()
        elif selected_distro:
            base_prompt = f"""You are OORB, a knowledgeable ROS2 expert assistant specialized in {selected_distro.upper()} distro. Your role is to help users with ROS2-related questions, providing accurate, practical, and helpful information specifically for the {selected_distro} distribution.

Key areas of expertise for ROS2 {selected_distro}:
- ROS2 concepts (nodes, topics, services, actions, parameters)
- Package development with colcon and ament
- Launch files and configuration specific to {selected_distro}
- Debugging and troubleshooting
- Best practices and design patterns for {selected_distro}
- Hardware integration and DDS configuration
- Navigation2 and motion planning
- Sensor integration and perception
- Quality of Service (QoS) policies

Guidelines for responses:
1. Focus specifically on ROS2 {selected_distro} unless stated otherwise
2. Provide clear, step-by-step instructions when applicable
3. Include relevant code examples and command-line usage for {selected_distro}
4. Mention important considerations and potential pitfalls specific to this distro
5. Suggest best practices for {selected_distro}
6. Include relevant package names and dependencies available in {selected_distro}
7. Provide debugging tips specific to this distribution
8. Format code blocks with appropriate language tags (```python, ```bash, ```xml, etc.)
9. When relevant, mention differences from other ROS2 distros
"""
        else:
            base_prompt = self._get_ros_system_prompt()
        
        # If no context provided, return base prompt
        if not context_info or not context_info.get('context'):
            return base_prompt
        
        # Create context section header based on scenario
        if selected_distro:
            context_header = f"RELEVANT {selected_distro.upper()} DOCUMENTATION CONTEXT:"
            context_description = f"The following context has been retrieved from official ROS2 {selected_distro} documentation and repositories to help answer your question."
        elif use_tools:
            context_header = "RELEVANT DOCUMENTATION CONTEXT:"
            context_description = "The following context has been retrieved from official ROS documentation and repositories to inform your responses and tool usage."
        else:
            context_header = "RELEVANT DOCUMENTATION CONTEXT:"
            context_description = "The following context has been retrieved from official ROS documentation, tutorials, and code repositories to help answer the user's question."
        
        # Build context section
        context_section = f"""

{context_header}
{context_description} Use this information as the primary source for your response.

{context_info['context']}

CONTEXT SOURCES SUMMARY:
- Total chunks: {context_info.get('total_chunks', 0)}
- Average quality: {context_info.get('avg_quality', 0):.2f}
- Repositories: {', '.join(context_info.get('metadata', {}).get('repositories', []))}
- Languages: {', '.join(context_info.get('metadata', {}).get('languages', []))}"""
        
        # Add tool-specific context details
        if use_tools:
            context_section += """

CONTEXT-AWARE TOOL USAGE:
1. Use the provided context as authoritative reference
2. Generate code that follows patterns from the context
3. Reference specific files and examples when appropriate
4. Ensure compatibility with versions and patterns shown in context
5. Use context to inform package dependencies and structure"""
        
        # Add distro-specific context details
        elif selected_distro:
            context_section += f"""
- Selected distro: {selected_distro}
- Sources from {selected_distro} documentation and code

INSTRUCTIONS FOR USING CONTEXT:
1. PRIORITIZE the provided {selected_distro}-specific context
2. Use specific examples and code snippets from the context when available
3. Reference source files when providing information (e.g., "According to the {selected_distro} documentation...")
4. Ensure all recommendations are compatible with ROS2 {selected_distro}
5. If context doesn't fully answer the question, supplement with general ROS2 knowledge while noting distro compatibility
6. Clearly indicate when you're drawing from the provided context vs. general knowledge
7. Highlight any {selected_distro}-specific features or limitations"""
        
        # Add general context usage instructions
        else:
            # Add detailed metadata if available
            if context_info.get('metadata'):
                metadata = context_info['metadata']
                context_section += f"""
- Code chunks: {metadata.get('code_chunks', 0)}
- Documentation chunks: {metadata.get('doc_chunks', 0)}"""
            
            # Add source details
            if context_info.get('sources'):
                context_section += "\n\nSOURCE DETAILS:\n"
                for i, source in enumerate(context_info['sources'], 1):
                    context_section += f"{i}. {source['file_name']}"
                    if source.get('repo_name'):
                        context_section += f" (from {source['repo_owner']}/{source['repo_name']})"
                    context_section += f" - Language: {source.get('language', 'N/A')}, Score: {source.get('score', 0):.3f}\n"
                    if source.get('source_link'):
                        context_section += f"   Link: {source['source_link']}\n"
            
            context_section += """

INSTRUCTIONS FOR USING CONTEXT:
1. PRIORITIZE the provided context - it contains official, up-to-date information
2. Use specific examples and code snippets from the context when available
3. Reference source files when providing information (e.g., "According to [filename]...")
4. If the context doesn't fully answer the question, supplement with your general ROS knowledge
5. Always verify that code examples match the user's target ROS version
6. Mention relevant source links when providing detailed explanations
7. If there are conflicts between context and your training data, prefer the context
8. Clearly indicate when you're drawing from the provided context vs. general knowledge"""
        
        return base_prompt + context_section 
                    
    def ask_question(self, question: str, model_name: str = "gpt-4",
                    temperature: float = 0.3, llm_backend: str = "azure", 
                    use_context: bool = None, context_filters: Optional[Dict[str, Any]] = None,
                    max_context_chunks: int = 5, expand_query: bool = False,
                    enable_tools: bool = False, max_tool_iterations: int = 5,
                    distro: str = None) -> Dict[str, Any]:
        """
        Ask a question to the ROS QA system with unified functionality.
        
        Args:
            question: The user's question about ROS
            model_name: The model to use for generation
            temperature: Temperature for response generation
            llm_backend: Backend to use ("azure", "openai", "ollama")
            use_context: Whether to use retrieval (overrides instance setting)
            context_filters: Filters for retrieval (e.g., {'language': 'python'})
            max_context_chunks: Maximum number of context chunks to retrieve
            expand_query: Whether to expand the query with related terms
            enable_tools: Whether to use OpenAI function calling tools
            max_tool_iterations: Maximum number of tool calling iterations (when tools enabled)
            distro: Specific ROS2 distro for distro-aware responses
            
        Returns:
            Dictionary containing the answer and metadata
        """
        
        # Check if tools are requested but not available
        if enable_tools and (not self.openai_client or not self.tool_system):
            return {
                "answer": "Tool-assisted responses require OpenAI API access and tool system initialization. Please check your OPENAI_API_KEY configuration.",
                "error": "Tools not available",
                "used_tools": False,
                "enable_tools_requested": True
            }
        
        # Determine if we should use context
        should_use_context = (use_context if use_context is not None 
                             else self.use_retrieval)
        
        # Generate system prompt and context
        context_info = None
        selected_distro = distro  # Use provided distro directly
        
        if should_use_context:
            try:
                # Prepare filters including distro if specified
                enhanced_filters = context_filters.copy() if context_filters else {}
                if distro:
                    enhanced_filters['distro'] = distro
                
                # Get relevant context from API
                context_info = self._get_relevant_context(
                    question, 
                    enhanced_filters, 
                    max_context_chunks,
                    expand_query
                )
                
                # Generate system prompt based on scenario
                system_prompt = self._get_enhanced_system_prompt(
                    context_info=context_info,
                    use_tools=enable_tools,
                    selected_distro=selected_distro
                )
                
            except Exception as e:
                logger.error(f"Context retrieval failed: {e}")
                # Fallback to base prompts
                if enable_tools:
                    system_prompt = self._get_ros_system_prompt_for_tools()
                else:
                    system_prompt = self._get_ros_system_prompt()
                context_info = None
                selected_distro = None
        else:
            # No context - use base prompts
            if enable_tools:
                system_prompt = self._get_ros_system_prompt_for_tools()
            else:
                system_prompt = self._get_ros_system_prompt()
            selected_distro = None
        
        try:
            # Handle tool-assisted responses
            if enable_tools:
                # Use the tool system's chat_with_tools method
                if should_use_context and context_info:
                    # Include context in the question for better tool awareness
                    enhanced_question = f"""Context from ROS documentation:
{context_info.get('context', '')[:2000]}...

User Question: {question}

Please use the available tools to help answer this question and generate any necessary files or code."""
                else:
                    enhanced_question = question
                
                tool_result = self.tool_system.chat_with_tools(
                    question=enhanced_question,
                    model=model_name,
                    max_iterations=max_tool_iterations
                )
                
                if tool_result.get("error"):
                    return {
                        "answer": f"I encountered an error while processing your ROS question: {tool_result['error']}",
                        "error": tool_result["error"],
                        "used_tools": False,
                        "model_used": model_name,
                        "backend_used": llm_backend
                    }
                
                result = {
                    "answer": tool_result.get("final_response", "No response generated"),
                    "model_used": model_name,
                    "backend_used": llm_backend,
                    "used_retrieval": should_use_context,
                    "used_tools": True,
                    "tool_calls": tool_result.get("tool_results", []),
                    "conversation": tool_result.get("conversation", []),
                    "iterations_used": tool_result.get("iterations_used", 0)
                }
                
            else:
                # Handle regular responses (with or without context)
                if llm_backend in ["azure", "openai"] and self.openai_client:
                    response = self._query_openai(question, system_prompt, model_name, temperature)
                elif llm_backend == "ollama":
                    response = self._query_ollama(question, system_prompt, model_name, temperature)
                else:
                    raise Exception(f"Backend '{llm_backend}' not available or not configured")
                
                result = {
                    "answer": response,
                    "model_used": model_name,
                    "backend_used": llm_backend,
                    "used_retrieval": should_use_context,
                    "used_tools": False
                }
            
            # Add context information if available
            if context_info:
                result.update({
                    "context_sources": context_info.get('sources', []),
                    "context_metadata": context_info.get('metadata', {}),
                    "total_context_chunks": context_info.get('total_chunks', 0),
                    "context_quality": context_info.get('avg_quality', 0.0)
                })
            
            # Add distro information if available
            if selected_distro:
                result.update({
                    "selected_distro": selected_distro,
                    "distro_detected": context_info.get('metadata', {}).get('distro_detected', False) if context_info else False
                })
            
            return result
            
        except Exception as e:
            error_msg = f"I encountered an error while processing your ROS question: {str(e)}."
            if enable_tools:
                error_msg += " You may want to try without tools or check your configuration."
            
            return {
                "answer": error_msg,
                "error": str(e),
                "used_retrieval": should_use_context,
                "used_tools": enable_tools,
                "backend_used": llm_backend
            }
    
    def _query_openai(self, question: str, system_prompt: str, model_name: str, temperature: float) -> str:
        """Query OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=temperature,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _query_ollama(self, question: str, system_prompt: str, model_name: str, temperature: float) -> str:
        """Query Ollama local API"""
        try:
            url = "http://localhost:11434/api/generate"
            
            # Combine system prompt and question for Ollama
            full_prompt = f"{system_prompt}\n\nUser question: {question}\n\nAssistant:"
            
            payload = {
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 2048
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "No response generated")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
    def _get_relevant_context(
        self,
        question: str,
        filters: Optional[Dict[str, Any]],
        max_chunks: int,
        expand_query: bool
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context from the API using /retrieve endpoint.
        
        Args:
            question: User's question
            filters: Optional filters for context retrieval
            max_chunks: Maximum number of chunks to retrieve
            expand_query: Whether to expand the query with related terms
            
        Returns:
            Context information dictionary
        """
        if not self.use_retrieval:
            return {}

        try:
            # Detect distro from query if not already specified in filters
            detected_distro = self._detect_distro_from_query(question)
            distro_to_use = filters.get('distro') if filters else detected_distro
            
            # Construct the payload for /retrieve endpoint
            payload = {
                "query": question,
                "n_results": max_chunks,
                "filters": filters or {},
                "include_metadata": True,
                "rerank": True,
                "distro": distro_to_use  # Add distro field
            }

            response = requests.post(f"{self.retrieval_api_url}/retrieve", json=payload, timeout=30)
            response.raise_for_status()

            retrieve_result = response.json()

            results = retrieve_result.get("results", [])
            if not results:
                return {
                    'context': '',
                    'sources': [],
                    'total_chunks': 0,
                    'avg_quality': 0.0,
                    'metadata': {}
                }

            # Format results from API response
            context_parts = []
            sources = []
            total_quality = 0
            languages = set()
            file_types = set()
            repos = set()

            for i, hit in enumerate(results):
                doc = hit.get("document", "")
                metadata = hit.get("metadata", {})

                source_info = f"[Source {i+1}: {metadata.get('file_name', 'Unknown')}]"
                context_parts.append(f"{source_info}\n{doc}")

                source = {
                    'file_name': metadata.get('file_name', 'Unknown'),
                    'file_path': metadata.get('file_path', ''),
                    'source_link': metadata.get('source_link', ''),
                    'repo_name': metadata.get('repo_name', ''),
                    'repo_owner': metadata.get('repo_owner', ''),
                    'language': metadata.get('language', ''),
                    'score': hit.get('score', 0.0),
                    'chunk_index': metadata.get('chunk_index', 0),
                    'has_code': metadata.get('has_code', False),
                    'has_documentation': metadata.get('has_documentation', False),
                    'distro': metadata.get('distro', '')
                }
                sources.append(source)

                total_quality += metadata.get('content_quality_score', 0.5)
                if metadata.get('language'):
                    languages.add(metadata['language'])
                if metadata.get('file_type'):
                    file_types.add(metadata['file_type'])
                if metadata.get('repo_name'):
                    repos.add(metadata['repo_name'])

            context = "\n\n---\n\n".join(context_parts)
            avg_quality = total_quality / len(results) if results else 0.0

            metadata_summary = {
                'repositories': list(repos),
                'languages': list(languages),
                'file_types': list(file_types),
                'avg_quality_score': avg_quality,
                'code_chunks': sum(1 for s in sources if s.get('has_code')),
                'doc_chunks': sum(1 for s in sources if s.get('has_documentation')),
                'selected_distro': distro_to_use or '',
                'distro_detected': bool(detected_distro),
                'distro_source': 'filter' if filters and filters.get('distro') else 'query' if detected_distro else 'none'
            }

            return {
                'context': context,
                'sources': sources,
                'total_chunks': len(results),
                'avg_quality': avg_quality,
                'metadata': metadata_summary,
                'expanded_query': question if expand_query else None,
                'processing_time': retrieve_result.get('processing_time', 0.0)
            }

        except Exception as e:
            return {}
    
    def _detect_distro_from_query(self, query: str) -> Optional[str]:
        """
        Detect ROS2 distro name from user query.
        
        Args:
            query: User's question
            
        Returns:
            Detected distro name or None
        """
        # Known ROS2 distro names (in order of release)
        ros2_distros = [
            'rolling', 'jazzy', 'iron', 'humble', 'galactic', 'foxy', 
            'eloquent', 'dashing', 'crystal', 'bouncy', 'ardent'
        ]
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Look for distro names in the query
        for distro in ros2_distros:
            # Check for exact word matches to avoid false positives
            if re.search(r'\b' + distro + r'\b', query_lower):
                return distro
                
        return None
    
    def search_documentation(self, query: str, filters: Optional[Dict[str, Any]] = None,
                           n_results: int = 10) -> Dict[str, Any]:
        """
        Search the documentation directly without generating a response.
        
        Args:
            query: Search query
            filters: Optional filters for search
            n_results: Number of results to return
            
        Returns:
            Search results with metadata
        """
        if not self.use_retrieval:
            return {
                "error": "Retrieval system not available",
                "results": []
            }
        
        try:
            # Detect distro from query if not already specified in filters
            detected_distro = self._detect_distro_from_query(query)
            distro_to_use = filters.get('distro') if filters else detected_distro
            
            # Use the same /retrieve endpoint for searching
            payload = {
                "query": query,
                "n_results": n_results,
                "filters": filters or {},
                "include_metadata": True,
                "rerank": True,
                "distro": distro_to_use  # Add distro field
            }
            
            response = requests.post(f"{self.retrieval_api_url}/retrieve", json=payload, timeout=30)
            response.raise_for_status()
            
            retrieve_result = response.json()
            results = retrieve_result.get("results", [])
            
            formatted_results = []
            for hit in results:
                formatted_results.append({
                    'content': hit.get("document", ""),
                    'metadata': hit.get("metadata", {}),
                    'score': hit.get('score', 0.0)
                })
            
            return {
                "query": query,
                "total_results": len(formatted_results),
                "results": formatted_results,
                "filters_applied": filters,
                "distro_detected": detected_distro,
                "distro_used": distro_to_use,
                "processing_time": retrieve_result.get('processing_time', 0.0)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "results": []
            }

