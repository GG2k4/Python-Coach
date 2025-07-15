import random
from dotenv import load_dotenv  # type: ignore
import os
import faiss  # type: ignore
import numpy as np  # type: ignore
import json
from App.Commons.constants import topics_dimensions
from App.Services.attempted_question_service import AttemptedQuestionService
from App.Commons.schemas import AttemptedQuestionCreate, UserID
from sqlalchemy.orm import Session  # type: ignore

attempted_question_service = AttemptedQuestionService()

class queryDB:
    def __init__(self, metadata_path="App/DB/questions_metadata4.json", index_path="App/DB/questions_vector_database4.index"):
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "r") as meta_file:
            self.metadata = json.load(meta_file)
        self.embedding_dim = 384
        self.custom_dim = 115
        self.total_dim = self.custom_dim + self.embedding_dim
        self.topics_dimensions = topics_dimensions
        self.attempted_question_service = attempted_question_service

    @staticmethod
    def normalize(vec: np.array):
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    @staticmethod
    def create_topic_vector(topic_weights: dict):
        topic_vector = np.zeros(len(topics_dimensions))
        for topic, weight in topic_weights.items():
            if topic in topics_dimensions:
                topic_vector[topics_dimensions[topic]] = float(weight)
        return topic_vector

    @staticmethod
    def activation(x):
        return x + 0.05 * (1 - x)**2

    def get_question(self, user_id, db: Session, query_weights_vector: list, to_activate=True, add_noise=True, k=5, similarity_threshold=0.9):
        query_weights_vector = np.array(query_weights_vector)
        if to_activate:
            activated = np.array([self.activation(x) for x in query_weights_vector])
            query_weights_vector = self.normalize(activated)

        zeros = np.zeros(self.embedding_dim)
        query_weights_vector = np.concatenate((zeros, query_weights_vector)).reshape(1, -1)

        if add_noise:
            noise_level = 0.05
            noise = np.random.normal(-noise_level, noise_level, query_weights_vector.shape)
            query_weights_vector = query_weights_vector + noise
        
        distances, indices = self.index.search(query_weights_vector, k)
        
        attempted_questions = {aq.question for aq in self.attempted_question_service.get_all_attempted_questions(
            user_id=UserID(user_id=user_id), db=db
        )}
        
        candidates = []
        for i in range(k):
            idx = int(indices[0][i])
            candidate_question = self.metadata[idx]["question"]
            if candidate_question in attempted_questions:
                continue
            retrieved_vector = self.index.reconstruct(idx)[384:]
            q_vec = query_weights_vector[0, 384:]
            r_vec = retrieved_vector
            norm_q = np.linalg.norm(q_vec)
            norm_r = np.linalg.norm(r_vec)
            if norm_q == 0 or norm_r == 0:
                sim = 0
            else:
                sim = np.dot(q_vec, r_vec) / (norm_q * norm_r)
            
            num_topics = len(self.metadata[idx]["topics"])
            bonus = 1 - 0.05 * num_topics  
            adjusted_sim = sim * bonus + random.uniform(0, 0.01)
            if adjusted_sim < similarity_threshold:
                candidates.append((idx, adjusted_sim))
        
        if not candidates:
            candidates = [(int(indices[0][i]), None) for i in range(min(k, len(indices[0])))]
        
        candidates.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))
        selected_idx = candidates[0][0]

        retrieved_vector = self.index.reconstruct(selected_idx)[384:]
        question = self.metadata[selected_idx]["question"]
        topics = self.metadata[selected_idx]["topics"]
        python_vector = [float(x) for x in retrieved_vector]
        
        self.attempted_question_service.create_new_attempted_question(
            attempted_question=AttemptedQuestionCreate(
                user_id=user_id, question=question, elo_value=python_vector, topics=topics
            ),
            db=db
        )

        return retrieved_vector, question, topics

    def get_question_by_topic(self, user_id: int, topic_weights: dict, db: Session):
        query_weights_vector = self.create_topic_vector(topic_weights)
        return self.get_question(user_id=user_id, query_weights_vector=query_weights_vector, db=db, to_activate=False, add_noise=False), query_weights_vector
