"""
NC Root Cause Auto-Suggestion Model
NLP-based root cause suggestion using historical NC data

This model uses Natural Language Processing to:
- Analyze NC descriptions and identify patterns
- Find similar historical NCs using semantic similarity
- Suggest likely root causes based on historical data
- Provide confidence scores and supporting evidence
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import joblib
from pathlib import Path
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass


class NCRootCauseSuggestionModel:
    """NC root cause suggestion model using NLP."""

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize the model.

        Args:
            model_path: Path to saved model files
        """
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.sentence_model = None
        self.historical_data = None
        self.embeddings = None

        if model_path and model_path.exists():
            self.load_model()

    def preprocess_text(self, text: str) -> str:
        """Preprocess NC description text.

        Args:
            text: Raw NC description

        Returns:
            Cleaned and preprocessed text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep important ones
        text = re.sub(r'[^a-z0-9\s\-\.]', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def train(self, historical_ncs: pd.DataFrame):
        """Train the NC root cause suggestion model.

        Args:
            historical_ncs: DataFrame with columns:
                - nc_number: NC ID
                - description: NC description
                - nc_type: Type of NC
                - severity: Severity level
                - root_cause: Identified root cause
                - source: NC source
        """
        print("Training NC Root Cause Suggestion Model...")

        self.historical_data = historical_ncs.copy()

        # Preprocess descriptions
        self.historical_data['processed_description'] = self.historical_data['description'].apply(
            self.preprocess_text
        )

        # Fit TF-IDF vectorizer
        print("Fitting TF-IDF vectorizer...")
        self.vectorizer.fit(self.historical_data['processed_description'])

        # Optionally load sentence transformer for better semantic matching
        try:
            print("Loading sentence transformer model...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Generate embeddings for historical NCs
            print("Generating embeddings...")
            self.embeddings = self.sentence_model.encode(
                self.historical_data['processed_description'].tolist(),
                show_progress_bar=True
            )
            print("Embeddings generated!")

        except Exception as e:
            print(f"Could not load sentence transformer: {e}")
            print("Will use TF-IDF similarity instead")

        print("Model training complete!")

    def suggest_root_causes(
        self,
        nc_description: str,
        nc_type: Optional[str] = None,
        severity: Optional[str] = None,
        top_k: int = 5
    ) -> Dict:
        """Suggest root causes for a new NC.

        Args:
            nc_description: Description of the new NC
            nc_type: Type of NC (optional filter)
            severity: Severity level (optional filter)
            top_k: Number of similar cases to retrieve

        Returns:
            Dictionary with:
            - suggested_root_causes: List of suggested causes with confidence
            - similar_cases: List of similar historical NC numbers
            - confidence_score: Overall confidence (0-100)
        """
        if self.historical_data is None:
            return self._mock_suggestion(nc_description)

        # Preprocess input
        processed_input = self.preprocess_text(nc_description)

        # Find similar historical NCs
        similar_ncs = self._find_similar_ncs(
            processed_input, nc_type, severity, top_k
        )

        # Extract root causes from similar cases
        root_cause_suggestions = self._extract_root_causes(similar_ncs)

        # Calculate confidence based on similarity scores
        if similar_ncs:
            avg_similarity = np.mean([nc['similarity'] for nc in similar_ncs])
            confidence = min(95, avg_similarity * 100)
        else:
            confidence = 50

        return {
            "suggested_root_causes": root_cause_suggestions,
            "similar_cases": [nc['nc_number'] for nc in similar_ncs],
            "confidence_score": round(confidence, 2),
            "suggestion_date": datetime.now()
        }

    def _find_similar_ncs(
        self,
        processed_description: str,
        nc_type: Optional[str],
        severity: Optional[str],
        top_k: int
    ) -> List[Dict]:
        """Find similar historical NCs using semantic similarity.

        Args:
            processed_description: Preprocessed NC description
            nc_type: NC type filter
            severity: Severity filter
            top_k: Number of results

        Returns:
            List of similar NCs with similarity scores
        """
        # Filter historical data if type/severity provided
        filtered_data = self.historical_data.copy()

        if nc_type:
            filtered_data = filtered_data[filtered_data['nc_type'] == nc_type]

        if severity:
            filtered_data = filtered_data[filtered_data['severity'] == severity]

        if len(filtered_data) == 0:
            return []

        # Compute similarity
        if self.sentence_model is not None and self.embeddings is not None:
            # Use sentence transformer embeddings
            input_embedding = self.sentence_model.encode([processed_description])

            # Filter embeddings to match filtered data
            filtered_indices = filtered_data.index.tolist()
            filtered_embeddings = self.embeddings[filtered_indices]

            # Compute cosine similarity
            similarities = cosine_similarity(input_embedding, filtered_embeddings)[0]

        else:
            # Use TF-IDF similarity
            input_vector = self.vectorizer.transform([processed_description])
            historical_vectors = self.vectorizer.transform(filtered_data['processed_description'])
            similarities = cosine_similarity(input_vector, historical_vectors)[0]

        # Get top K similar NCs
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        similar_ncs = []
        for idx in top_indices:
            row = filtered_data.iloc[idx]
            similar_ncs.append({
                'nc_number': row['nc_number'],
                'description': row['description'],
                'root_cause': row.get('root_cause', 'Not identified'),
                'nc_type': row['nc_type'],
                'severity': row['severity'],
                'similarity': float(similarities[idx])
            })

        return similar_ncs

    def _extract_root_causes(self, similar_ncs: List[Dict]) -> List[Dict]:
        """Extract and rank root causes from similar NCs.

        Args:
            similar_ncs: List of similar NC dictionaries

        Returns:
            List of root cause suggestions with confidence
        """
        if not similar_ncs:
            return []

        # Count root causes weighted by similarity
        root_cause_scores = {}

        for nc in similar_ncs:
            root_cause = nc.get('root_cause', 'Unknown')
            if root_cause and root_cause != 'Not identified':
                similarity = nc['similarity']

                if root_cause not in root_cause_scores:
                    root_cause_scores[root_cause] = {
                        'cause': root_cause,
                        'score': 0,
                        'supporting_ncs': []
                    }

                root_cause_scores[root_cause]['score'] += similarity
                root_cause_scores[root_cause]['supporting_ncs'].append(nc['nc_number'])

        # Sort by score
        sorted_causes = sorted(
            root_cause_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # Normalize scores to 0-100 confidence
        if sorted_causes:
            max_score = sorted_causes[0]['score']
            for cause in sorted_causes:
                cause['confidence'] = round((cause['score'] / max_score) * 100, 2)

        return sorted_causes[:5]  # Return top 5

    def _mock_suggestion(self, nc_description: str) -> Dict:
        """Generate mock suggestions when model is not trained."""
        # Simple keyword-based suggestions
        description_lower = nc_description.lower()

        mock_causes = []

        if 'calibration' in description_lower or 'measurement' in description_lower:
            mock_causes.append({
                'cause': 'Inadequate calibration frequency',
                'confidence': 85.0,
                'supporting_ncs': ['NC-2024-001', 'NC-2024-015']
            })
            mock_causes.append({
                'cause': 'Equipment measurement error',
                'confidence': 75.0,
                'supporting_ncs': ['NC-2024-003']
            })

        if 'procedure' in description_lower or 'process' in description_lower:
            mock_causes.append({
                'cause': 'Inadequate procedure documentation',
                'confidence': 80.0,
                'supporting_ncs': ['NC-2024-007']
            })
            mock_causes.append({
                'cause': 'Process not followed correctly',
                'confidence': 70.0,
                'supporting_ncs': ['NC-2024-012']
            })

        if 'training' in description_lower or 'competency' in description_lower:
            mock_causes.append({
                'cause': 'Insufficient training',
                'confidence': 90.0,
                'supporting_ncs': ['NC-2024-005', 'NC-2024-018']
            })

        if not mock_causes:
            mock_causes = [
                {
                    'cause': 'Human error',
                    'confidence': 60.0,
                    'supporting_ncs': []
                },
                {
                    'cause': 'Process variation',
                    'confidence': 55.0,
                    'supporting_ncs': []
                }
            ]

        return {
            "suggested_root_causes": mock_causes[:3],
            "similar_cases": [cause['supporting_ncs'][0] for cause in mock_causes if cause['supporting_ncs']][:5],
            "confidence_score": mock_causes[0]['confidence'] if mock_causes else 50.0,
            "suggestion_date": datetime.now()
        }

    def save_model(self, path: Path):
        """Save model to disk."""
        path.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.vectorizer, path / "tfidf_vectorizer.pkl")

        if self.historical_data is not None:
            self.historical_data.to_pickle(path / "historical_data.pkl")

        if self.embeddings is not None:
            np.save(path / "embeddings.npy", self.embeddings)

        print(f"Model saved to {path}")

    def load_model(self):
        """Load model from disk."""
        if self.model_path:
            self.vectorizer = joblib.load(self.model_path / "tfidf_vectorizer.pkl")
            self.historical_data = pd.read_pickle(self.model_path / "historical_data.pkl")

            embeddings_path = self.model_path / "embeddings.npy"
            if embeddings_path.exists():
                self.embeddings = np.load(embeddings_path)

            # Load sentence model if available
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except:
                pass

            print(f"Model loaded from {self.model_path}")
