"""
Document Classification & Auto-Tagging Model
NLP-based document classification and metadata extraction

Uses text classification to:
- Classify document type (Procedure, Form, Work Instruction, etc.)
- Extract key entities (dates, equipment IDs, document references)
- Generate relevant tags automatically
- Identify document category and metadata
"""

import numpy as np
import pandas as pd
import re
from typing import Dict, List, Optional
from datetime import datetime
import joblib
from pathlib import Path

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
except ImportError:
    pass


class DocumentClassifier:
    """Document classification and auto-tagging model."""

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize the model.

        Args:
            model_path: Path to saved model files
        """
        self.model_path = model_path
        self.classifier = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.label_encoder = LabelEncoder()
        self.tag_keywords = self._initialize_tag_keywords()

        if model_path and model_path.exists():
            self.load_model()

    def _initialize_tag_keywords(self) -> Dict[str, List[str]]:
        """Initialize keyword mapping for auto-tagging."""
        return {
            'calibration': ['calibration', 'calibrate', 'calibrated', 'accuracy', 'measurement'],
            'quality': ['quality', 'qms', 'iso', 'standard', 'audit', 'compliance'],
            'safety': ['safety', 'hazard', 'risk', 'ppe', 'emergency', 'accident'],
            'testing': ['test', 'testing', 'examination', 'analysis', 'laboratory'],
            'equipment': ['equipment', 'instrument', 'machine', 'device', 'apparatus'],
            'procedure': ['procedure', 'process', 'method', 'protocol', 'workflow'],
            'training': ['training', 'competency', 'skill', 'certification', 'qualification'],
            'document_control': ['revision', 'version', 'approval', 'control', 'distribution'],
            'nonconformance': ['nonconformance', 'deviation', 'defect', 'nc', 'capa'],
            'maintenance': ['maintenance', 'preventive', 'corrective', 'service', 'repair'],
            'solar_pv': ['solar', 'photovoltaic', 'pv', 'module', 'panel'],
            'iec': ['iec', '61215', '61730', '61701', 'standard'],
            'customer': ['customer', 'client', 'quotation', 'order', 'requirement']
        }

    def preprocess_text(self, text: str) -> str:
        """Preprocess document text.

        Args:
            text: Raw document text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters
        text = re.sub(r'[^a-z0-9\s]', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def extract_entities(self, text: str) -> Dict:
        """Extract named entities from document text.

        Args:
            text: Document text

        Returns:
            Dictionary of extracted entities
        """
        entities = {
            'dates': [],
            'equipment_ids': [],
            'document_numbers': [],
            'standards': [],
            'email_addresses': []
        }

        # Extract dates (various formats)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
        ]
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text))

        # Extract equipment IDs (EQP-YYYY-XXX pattern)
        entities['equipment_ids'] = re.findall(r'EQP-\d{4}-\d{3}', text, re.IGNORECASE)

        # Extract document numbers (QSF-YYYY-XXX pattern)
        entities['document_numbers'] = re.findall(r'QSF-\d{4}-\d{3}', text, re.IGNORECASE)

        # Extract IEC standards
        entities['standards'] = re.findall(r'IEC\s*\d{5}', text, re.IGNORECASE)

        # Extract email addresses
        entities['email_addresses'] = re.findall(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            text
        )

        return entities

    def generate_tags(self, text: str, max_tags: int = 10) -> List[str]:
        """Generate relevant tags for document.

        Args:
            text: Document text
            max_tags: Maximum number of tags to return

        Returns:
            List of relevant tags
        """
        text_lower = text.lower()
        tags = []

        # Check keyword matches
        for tag, keywords in self.tag_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if tag not in tags:
                        tags.append(tag)
                    break

        return tags[:max_tags]

    def train(self, training_data: pd.DataFrame):
        """Train the document classification model.

        Args:
            training_data: DataFrame with columns:
                - title: Document title
                - content: Document text content
                - doc_type: Document type (target label)
        """
        print("Training Document Classification Model...")

        # Preprocess content
        training_data['processed_content'] = training_data['content'].apply(
            self.preprocess_text
        )

        # Fit vectorizer
        X = self.vectorizer.fit_transform(training_data['processed_content'])

        # Encode labels
        y = self.label_encoder.fit_transform(training_data['doc_type'])

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train Multinomial Naive Bayes classifier
        print("Training classifier...")
        self.classifier = MultinomialNB(alpha=1.0)
        self.classifier.fit(X_train, y_train)

        # Evaluate
        train_acc = self.classifier.score(X_train, y_train)
        test_acc = self.classifier.score(X_test, y_test)

        print(f"Train Accuracy: {train_acc:.3f}")
        print(f"Test Accuracy: {test_acc:.3f}")
        print("Model training complete!")

    def classify(self, document_text: str, document_title: str = "") -> Dict:
        """Classify document and generate metadata.

        Args:
            document_text: Full document text
            document_title: Document title (optional)

        Returns:
            Dictionary with:
            - predicted_category: Document type
            - confidence_score: Confidence (0-100)
            - suggested_tags: List of tags
            - extracted_entities: Dictionary of entities
        """
        if self.classifier is None:
            return self._mock_classification(document_text, document_title)

        # Combine title and content
        full_text = f"{document_title} {document_text}"

        # Preprocess
        processed_text = self.preprocess_text(full_text)

        # Vectorize
        text_vector = self.vectorizer.transform([processed_text])

        # Predict
        predicted_label = self.classifier.predict(text_vector)[0]
        predicted_proba = self.classifier.predict_proba(text_vector)[0]

        # Decode label
        predicted_category = self.label_encoder.inverse_transform([predicted_label])[0]

        # Confidence (max probability)
        confidence = max(predicted_proba) * 100

        # Generate tags
        tags = self.generate_tags(full_text)

        # Extract entities
        entities = self.extract_entities(document_text)

        return {
            "predicted_category": predicted_category,
            "confidence_score": round(confidence, 2),
            "suggested_tags": tags,
            "extracted_entities": entities,
            "classification_date": datetime.now()
        }

    def _mock_classification(self, document_text: str, document_title: str) -> Dict:
        """Generate mock classification when model is not trained."""
        text_lower = (document_title + " " + document_text).lower()

        # Simple keyword-based classification
        if 'procedure' in text_lower or 'sop' in text_lower:
            category = 'Procedure'
            confidence = 85.0
        elif 'form' in text_lower or 'qsf' in text_lower:
            category = 'Form'
            confidence = 80.0
        elif 'work instruction' in text_lower or 'wi' in text_lower:
            category = 'Work Instruction'
            confidence = 75.0
        elif 'policy' in text_lower:
            category = 'Policy'
            confidence = 80.0
        elif 'manual' in text_lower:
            category = 'Manual'
            confidence = 70.0
        elif 'report' in text_lower or 'test' in text_lower:
            category = 'Report'
            confidence = 75.0
        else:
            category = 'Other'
            confidence = 60.0

        # Generate tags
        tags = self.generate_tags(document_text)

        # Extract entities
        entities = self.extract_entities(document_text)

        return {
            "predicted_category": category,
            "confidence_score": confidence,
            "suggested_tags": tags,
            "extracted_entities": entities,
            "classification_date": datetime.now()
        }

    def save_model(self, path: Path):
        """Save model to disk."""
        path.mkdir(parents=True, exist_ok=True)

        if self.classifier:
            joblib.dump(self.classifier, path / "classifier.pkl")

        joblib.dump(self.vectorizer, path / "vectorizer.pkl")
        joblib.dump(self.label_encoder, path / "label_encoder.pkl")
        joblib.dump(self.tag_keywords, path / "tag_keywords.pkl")

        print(f"Model saved to {path}")

    def load_model(self):
        """Load model from disk."""
        if self.model_path:
            self.classifier = joblib.load(self.model_path / "classifier.pkl")
            self.vectorizer = joblib.load(self.model_path / "vectorizer.pkl")
            self.label_encoder = joblib.load(self.model_path / "label_encoder.pkl")
            self.tag_keywords = joblib.load(self.model_path / "tag_keywords.pkl")
            print(f"Model loaded from {self.model_path}")
