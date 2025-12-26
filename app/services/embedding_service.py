from typing import List, Tuple, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.models.conversation import Message, MessageEmbedding
from app.services.openai_service import openai_service
import json


class EmbeddingService:
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_and_store_embedding(
        self,
        message_id: str,
        content: str
    ) -> bool:
        """Generate embedding for message and store it"""
        try:
            # Generate embedding
            embedding_vector = await openai_service.generate_embedding(content)
            
            # Check if embedding already exists
            existing = self.db.query(MessageEmbedding).filter(
                MessageEmbedding.message_id == message_id
            ).first()
            
            if existing:
                existing.embedding = json.dumps(embedding_vector)
            else:
                new_embedding = MessageEmbedding(
                    message_id=message_id,
                    embedding=json.dumps(embedding_vector)
                )
                self.db.add(new_embedding)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Embedding storage error: {str(e)}")
            self.db.rollback()
            return False
    
    def cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def search_similar_messages(
        self,
        query: str,
        user_id: int,
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Tuple[Message, float]]:
        """Search for similar messages using embeddings"""
        try:
            # Generate query embedding
            query_embedding = await openai_service.generate_embedding(query)
            
            # Get all user's message embeddings
            embeddings = self.db.query(
                MessageEmbedding, Message
            ).join(
                Message, MessageEmbedding.message_id == Message.id
            ).join(
                Message.conversation
            ).filter(
                Message.conversation.has(user_id=user_id)
            ).all()
            
            # Calculate similarities
            results = []
            for emb, msg in embeddings:
                stored_embedding = json.loads(emb.embedding)
                similarity = self.cosine_similarity(query_embedding, stored_embedding)
                
                if similarity >= min_similarity:
                    results.append((msg, similarity))
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
        
        except Exception as e:
            print(f"Similarity search error: {str(e)}")
            return []