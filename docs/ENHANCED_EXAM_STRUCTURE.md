# Enhanced Exam Structure with Tags and Learning Paths

## 🎯 **New Features Added**

Your SMS-Agent now extracts **tags** and **learning paths (prerequisites)** for both exams and exercise series, providing richer educational metadata.

## 📋 **Enhanced Exam Structure**

### **Complete Exam JSON Schema**
```json
{
  "type_document": "examen",
  "source_details": {
    "nom_source": "Science made simple",
    "est_interne_sms": true
  },
  "titre_examen": "Examen Final - Mathématiques Appliquées",
  "matiere": "Mathématiques, Statistiques",
  "tags": [
    "mathématiques",
    "statistiques", 
    "probabilités",
    "analyse",
    "examen final"
  ],
  "learning_path": [
    {
      "module_name": "Analyse Mathématique",
      "prerequisites": [
        "Calcul différentiel et intégral",
        "Fonctions à plusieurs variables",
        "Séries et suites"
      ],
      "topics": [
        "Dérivées partielles",
        "Intégrales multiples",
        "Équations différentielles"
      ],
      "difficulty": "avancé"
    },
    {
      "module_name": "Statistiques et Probabilités",
      "prerequisites": [
        "Statistiques descriptives",
        "Théorie des probabilités de base",
        "Variables aléatoires"
      ],
      "topics": [
        "Tests d'hypothèses",
        "Régression linéaire",
        "Distributions de probabilité"
      ],
      "difficulty": "intermédiaire"
    }
  ],
  "nombre_sections": 3,
  "points_total": 100,
  "duree": "3 heures",
  "instructions_generales": "Répondez à toutes les questions. Calculatrice autorisée.",
  "exercices": [
    {
      "id_exercice_ou_titre": "Exercice 1 - Analyse",
      "enonce_exercice": "Soit f(x,y) = x²y + xy². Calculez les dérivées partielles et analysez les points critiques.",
      "points_exercice": 25,
      "questions": [
        {
          "id_question_ou_numero": "1a",
          "texte_question": "Calculez ∂f/∂x et ∂f/∂y. Montrez tous les calculs intermédiaires et vérifiez vos résultats en calculant les dérivées secondes mixtes.",
          "options_reponse": [],
          "type_reponse_attendu": "calcul détaillé avec justification"
        }
      ]
    }
  ]
}
```

## 📚 **Enhanced Exercise Series Structure**

### **Complete Exercise Series JSON Schema**
```json
{
  "type_document": "serie_exercices",
  "source_details": {
    "nom_source": "Université de Paris",
    "est_interne_sms": false
  },
  "sujet_principal": "Travaux Dirigés - Mécanique Quantique",
  "tags": [
    "mécanique quantique",
    "physique",
    "équations de schrödinger",
    "travaux dirigés"
  ],
  "learning_path": [
    {
      "module_name": "Fondements de la Mécanique Quantique",
      "prerequisites": [
        "Mécanique classique",
        "Électromagnétisme",
        "Mathématiques avancées (équations différentielles)"
      ],
      "topics": [
        "Principe d'incertitude",
        "Fonction d'onde",
        "Équation de Schrödinger"
      ],
      "difficulty": "avancé"
    }
  ],
  "exercices": [
    {
      "id_exercice_ou_titre": "Exercice 1 - Particule dans une boîte",
      "enonce_exercice": "Considérez une particule libre dans une boîte unidimensionnelle de longueur L.",
      "questions": [
        {
          "id_question_ou_numero": "1a",
          "texte_question": "Établissez l'équation de Schrödinger pour cette situation. Quelles sont les conditions aux limites appropriées ? Résolvez l'équation et trouvez les niveaux d'énergie quantifiés.",
          "options_reponse": [],
          "type_reponse_attendu": "résolution complète avec justification physique"
        }
      ]
    }
  ]
}
```

## 🔧 **What the AI Extracts**

### **Tags (Mots-clés)**
- **Subject keywords** from content
- **Document type indicators** (examen, exercices, etc.)
- **Topic-specific terms** (mathématiques, physique, etc.)
- **Level indicators** (débutant, avancé, etc.)

### **Learning Path / Prerequisites**
- **Module organization** by topic/chapter
- **Required knowledge** for each section
- **Topic coverage** within each module  
- **Difficulty assessment** (débutant, intermédiaire, avancé)

## 🎯 **Benefits of Enhanced Structure**

### **For Course Organization**
```json
{
  "tags": ["algèbre", "géométrie", "niveau licence"],
  "learning_path": [
    {
      "module_name": "Algèbre Linéaire",
      "prerequisites": ["Mathématiques de base", "Calcul matriciel"],
      "topics": ["Espaces vectoriels", "Applications linéaires"],
      "difficulty": "intermédiaire"
    }
  ]
}
```

### **For Prerequisite Tracking**
- **Identify required knowledge** before attempting exam
- **Map learning progression** through topics
- **Assess difficulty levels** for proper preparation
- **Organize content** by subject areas

### **For Content Discovery**
- **Search by tags** to find related content
- **Filter by difficulty** level
- **Group by prerequisites** for learning paths
- **Categorize by topics** for curriculum planning

## 🚀 **Usage Examples**

### **API Call for Enhanced Extraction**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-slides" \
  -F "slides=@exam_math.pdf" \
  -F "ai_provider=google" \
  -F "analysis_depth=comprehensive" \
  -F "target_audience=advanced"
```

### **Python Code for Enhanced Analysis**
```python
from app.tools.slide_analyzer import SlideAnalyzerTool

tool = SlideAnalyzerTool()
result = await tool.execute({
    'slide_images': ['exam_physics.pdf'],
    'ai_provider': 'google',
    'analysis_depth': 'comprehensive',
    'target_audience': 'advanced'
})

# Access enhanced data
data = result.data
tags = data.get('tags', [])
learning_path = data.get('learning_path', [])

print(f"Tags: {', '.join(tags)}")
for module in learning_path:
    print(f"Module: {module['module_name']}")
    print(f"Prerequisites: {', '.join(module['prerequisites'])}")
```

## 📊 **Expected Output**

When you analyze an exam or exercise series, you'll now see:

```
📝 Complete Document Analysis:
   Total exercises found: 3
   Tags: mathématiques, analyse, examen final, niveau avancé
   Learning modules: 2

🎯 Learning Path / Prerequisites:
   Module 1: Analyse Mathématique
     Prerequisites: Calcul différentiel, Fonctions à plusieurs variables
     Topics: Dérivées partielles, Intégrales multiples
     Difficulty: avancé
   
   Module 2: Statistiques et Probabilités  
     Prerequisites: Statistiques descriptives, Théorie des probabilités
     Topics: Tests d'hypothèses, Régression linéaire
     Difficulty: intermédiaire
```

## 💡 **Pro Tips**

1. **Tags help with content organization** - use them for search and categorization
2. **Prerequisites show learning dependencies** - essential for curriculum planning  
3. **Difficulty levels guide preparation** - match student level to content
4. **Topics provide content overview** - quick understanding of coverage
5. **Module structure aids navigation** - logical content organization

Your SMS-Agent now provides **comprehensive educational metadata** for better content management! 🎉 