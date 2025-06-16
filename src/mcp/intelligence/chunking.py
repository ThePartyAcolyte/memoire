"""
Semantic chunking capabilities for intelligent content fragmentation.

Handles both legacy content analysis and new semantic chunking with context awareness.
"""

import logging
import json
from typing import Dict, Any, List
from google import genai

logger = logging.getLogger(__name__)


class SemanticChunker:
    """Handles semantic content chunking using Gemini."""
    
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        
        # Get chunk size from config
        from ...config import config
        self.min_chunk_words = config.get("chunking.min_chunk_words", 20)
        self.max_chunk_words = config.get("chunking.max_chunk_words", 150)
    
    def _call_gemini(self, prompt: str, temperature: float = None) -> str:
        """Helper to call Gemini with config settings."""
        from ...config import config
        
        model = config.get("processing.model", "gemini-2.5-flash-preview-05-20")
        if temperature is None:
            temperature = config.get("processing.temperature", 0.3)
        
        response = self.gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config={"temperature": temperature}
        )
        return response.text.strip()
    
    def analyze_content_legacy(self, content: str, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy content analysis for backward compatibility.
        
        Maintains the same interface as the original intelligent_middleware.py
        """
        prompt = f"""Analyze this project information and determine how to organize it:

CONTENT TO ANALYZE:
{content}

PROJECT CONTEXT:
- Project: {project_state.get('project_name', 'Unknown')}
- Description: {project_state.get('description', 'No description')}
- Existing clusters: {[c.get('name') for c in project_state.get('clusters', [])]}

ANALYZE AND RESPOND WITH JSON:
{{
    "content_type": "decision|pattern|task|context|reference",
    "target_cluster": "suggested_cluster_name", 
    "creates_cluster": true|false,
    "reasoning": "why this classification",
    "confidence": 0.0-1.0
}}

Focus on practical project organization. Keep cluster names simple and descriptive."""
        
        try:
            analysis_text = self._call_gemini(prompt)
            analysis_text = self._extract_json(analysis_text)
            analysis = json.loads(analysis_text)
            
            logger.info(f"Legacy analysis: {analysis['target_cluster']} ({analysis['confidence']})")
            return analysis
            
        except Exception as e:
            logger.error(f"Legacy analysis failed: {e}")
            return {
                "content_type": "context",
                "target_cluster": "general",
                "creates_cluster": False,
                "reasoning": "Fallback due to analysis error",
                "confidence": 0.5
            }
    
    async def chunk_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Divide content into semantically coherent chunks.
        
        Args:
            content: Text content to chunk
            
        Returns:
            List of chunk dictionaries with semantic metadata
        """
        word_count = len(content.split())
        
        # Don't chunk if content is already optimal size
        if word_count <= self.max_chunk_words:
            return [{
                "content": content,
                "semantic_summary": await self._extract_summary(content),
                "key_concepts": await self._extract_concepts(content),
                "chunk_type": "atomic",
                "word_count": word_count
            }]
        
        # Perform semantic chunking for longer content
        return await self._semantic_chunking(content)
    
    async def _semantic_chunking(self, content: str) -> List[Dict[str, Any]]:
        """Use Gemini for intelligent semantic chunking."""
        
        prompt = f"""
        Divide este contenido en fragmentos semánticamente coherentes:
        
        CONTENIDO:
        {content}
        
        CRITERIOS:
        - Cada fragmento debe ser una unidad semántica completa ({self.min_chunk_words}-{self.max_chunk_words} palabras)
        - Mantén contexto suficiente para comprensión independiente
        - Respeta límites conceptuales naturales
        - Optimiza para búsqueda en lenguaje natural
        
        RESPONDE JSON:
        {{
            "chunks": [
                {{
                    "content": "texto completo del fragmento",
                    "semantic_summary": "resumen en 1 frase de qué trata",
                    "key_concepts": ["concepto1", "concepto2", "concepto3"],
                    "answers_question": "¿qué pregunta natural respondería este fragmento?",
                    "word_count": 85
                }}
            ]
        }}
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": 0.3}
            )
            
            result_text = response.text.strip()
            result_text = self._extract_json(result_text)
            result = json.loads(result_text)
            
            chunks = result.get("chunks", [])
            logger.info(f"Semantic chunking produced {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Semantic chunking failed: {e}")
            return await self._fallback_chunking(content)
    
    async def _extract_summary(self, content: str) -> str:
        """Extract a concise summary for short content."""
        if len(content.split()) <= 30:
            return content[:100] + "..." if len(content) > 100 else content
        
        try:
            prompt = f"Resumen en 1 frase: {content}"
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": 0.1}
            )
            return response.text.strip()
        except:
            return content[:100] + "..."
    
    async def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content."""
        try:
            prompt = f"Extrae 3-5 conceptos clave de: {content}"
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": 0.1}
            )
            
            concepts_text = response.text.strip()
            concepts = [c.strip().replace("•", "").replace("-", "") 
                       for c in concepts_text.split(",") if c.strip()]
            return concepts[:5]
            
        except:
            words = content.split()[:10]
            return [w for w in words if len(w) > 3][:3]
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from Gemini response."""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            return text[start:end].strip()
        return text
    
    async def _fallback_chunking(self, content: str) -> List[Dict[str, Any]]:
        """Simple fallback chunking when Gemini fails."""
        sentences = content.split(". ")
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + ". " + sentence if current_chunk else sentence
            if len(test_chunk.split()) > self.max_chunk_words and current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "semantic_summary": current_chunk[:50] + "...",
                    "key_concepts": [],
                    "chunk_type": "fallback",
                    "word_count": len(current_chunk.split())
                })
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "semantic_summary": current_chunk[:50] + "...",
                "key_concepts": [],
                "chunk_type": "fallback",
                "word_count": len(current_chunk.split())
            })
        
        return chunks


class ContextualChunker:
    """Chunker that considers existing project contexts (Perspective 2 approach)."""
    
    def __init__(self, gemini_client, memory_service):
        self.gemini_client = gemini_client
        self.memory_service = memory_service
        self.semantic_chunker = SemanticChunker(gemini_client)
        
    async def chunk_with_context_awareness(self, content: str, project_id: str) -> List[Dict[str, Any]]:
        """
        Chunk content considering existing project contexts.
        
        Implements the "Hybrid Suggested" approach from Perspective 2.
        """
        # Get existing project contexts
        existing_contexts = await self._get_project_contexts(project_id)
        
        # If no contexts exist, use basic semantic chunking
        if not existing_contexts:
            basic_chunks = await self.semantic_chunker.chunk_content(content)
            return [self._add_context_suggestions(chunk, []) for chunk in basic_chunks]
        
        # Perform context-aware chunking
        return await self._context_guided_chunking(content, existing_contexts)
    
    async def _context_guided_chunking(self, content: str, existing_contexts: List) -> List[Dict[str, Any]]:
        """Perform chunking guided by existing project contexts."""
        
        context_descriptions = {
            getattr(ctx, 'name', f'context_{i}'): getattr(ctx, 'description', 'No description')
            for i, ctx in enumerate(existing_contexts)
        }
        
        prompt = f"""
        Divide este contenido en fragmentos semánticamente coherentes, considerando los 
        patrones organizacionales que han emergido en este proyecto.
        
        CONTENIDO A FRAGMENTAR:
        {content}
        
        CONTEXTOS EXISTENTES EN EL PROYECTO:
        {json.dumps(context_descriptions, indent=2)}
        
        INSTRUCCIONES:
        1. Cada fragmento debe ser semánticamente coherente (20-150 palabras)
        2. Si el contenido se alinea con contextos existentes, menciónalo
        3. Si surge un tema nuevo, identifícalo como nuevo contexto potencial
        4. Un fragmento PUEDE pertenecer a múltiples contextos
        5. Prioriza utilidad para búsqueda natural sobre categorización perfecta
        
        RESPONDE JSON:
        {{
            "fragments": [
                {{
                    "content": "texto del fragmento completo",
                    "semantic_summary": "resumen en 1 frase",
                    "key_concepts": ["concepto1", "concepto2"],
                    "suggested_contexts": ["contexto_existente", "nuevo_contexto"],
                    "context_reasoning": "por qué pertenece a estos contextos",
                    "context_confidence": 0.8
                }}
            ]
        }}
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": 0.3}
            )
            
            result_text = response.text.strip()
            result_text = self._extract_json(result_text)
            result = json.loads(result_text)
            
            fragments = result.get("fragments", [])
            logger.info(f"Context-aware chunking produced {len(fragments)} fragments")
            return fragments
            
        except Exception as e:
            logger.error(f"Context-aware chunking failed: {e}")
            # Fallback to basic semantic chunking
            basic_chunks = await self.semantic_chunker.chunk_content(content)
            return [self._add_context_suggestions(chunk, existing_contexts) for chunk in basic_chunks]
    
    def _add_context_suggestions(self, chunk: Dict[str, Any], contexts: List) -> Dict[str, Any]:
        """Add basic context suggestions when advanced analysis fails."""
        chunk["suggested_contexts"] = ["general"]
        chunk["context_reasoning"] = "Fallback categorization"
        chunk["context_confidence"] = 0.5
        return chunk
    
    async def _get_project_contexts(self, project_id: str) -> List:
        """Retrieve existing contexts for the project."""
        try:
            # Use real context retrieval from memory service
            contexts = self.memory_service.list_contexts_by_project(project_id)
            logger.info(f"Retrieved {len(contexts)} existing contexts for project {project_id}")
            return contexts
        except Exception as e:
            logger.error(f"Failed to get project contexts: {e}")
            return []
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from Gemini response."""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            return text[start:end].strip()
        return text
