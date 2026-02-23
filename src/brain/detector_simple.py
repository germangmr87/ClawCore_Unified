#!/usr/bin/env python3
"""
DETECTOR SIMPLE PERO EFECTIVO
"""

def detect_language(text):
    """Detecta español vs inglés"""
    if not text:
        return "en", 0.5
    
    text_lower = text.lower()
    
    # Palabras clave
    es_words = ['hola', 'cómo', 'qué', 'dónde', 'cuándo', 'por qué', 'gracias', 'adiós']
    en_words = ['hello', 'how', 'what', 'where', 'when', 'why', 'thanks', 'goodbye']
    
    # Caracteres españoles
    es_chars = ['á', 'é', 'í', 'ó', 'ú', 'ñ', '¿', '¡']
    
    # Contar
    es_score = 0
    en_score = 0
    
    # Caracteres españoles
    for char in es_chars:
        if char in text:
            es_score += 3
    
    # Palabras clave
    for word in es_words:
        if word in text_lower:
            es_score += 2
    
    for word in en_words:
        if word in text_lower:
            en_score += 2
    
    # Decisión
    if es_score > en_score:
        confidence = min(0.95, es_score / 10)
        return "es", confidence
    elif en_score > es_score:
        confidence = min(0.95, en_score / 10)
        return "en", confidence
    else:
        # Empate → inglés por defecto
        return "en", 0.6

# Test
if __name__ == "__main__":
    tests = [
        "Hola mundo",
        "Hello world",
        "Cómo estás?",
        "How are you?",
        "El perro corre",
        "The dog runs"
    ]
    
    for text in tests:
        lang, conf = detect_language(text)
        print(f"'{text}' → {lang.upper()} ({conf:.0%})")