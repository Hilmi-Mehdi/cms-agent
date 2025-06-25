"""
Slide Analyzer Tool: Analyze course slides to extract structured course information
"""

import asyncio
import json
import re
import time
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult, AIProvider
from app.utils.ai_client import ai_client
from app.utils.pdf_processor import pdf_processor, PDF_SUPPORT_AVAILABLE


class SlideAnalyzerTool(BaseTool):
    """Tool that analyzes course slides to extract structured course information."""
    
    def get_definition(self) -> ToolDefinition:
        description = "Analyze course slides to extract title, descriptions, tags, and learning path"
        if PDF_SUPPORT_AVAILABLE:
            description += " (supports images and PDF files)"
        
        return ToolDefinition(
            name="slide_analyzer",
            description=description,
            parameters=[
                ToolParameter(
                    name="slide_images",
                    type="array",
                    description="List of slide image file paths, PDF file paths, or base64 encoded images",
                    required=True
                ),
                ToolParameter(
                    name="ai_provider",
                    type="string",
                    description="AI provider to use for analysis",
                    required=False,
                    default="openai",
                    enum=["openai", "google"]
                ),
                ToolParameter(
                    name="analysis_depth",
                    type="string",
                    description="Depth of analysis to perform",
                    required=False,
                    default="comprehensive",
                    enum=["basic", "detailed", "comprehensive"]
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="Target audience for the course",
                    required=False,
                    default="general",
                    enum=["beginner", "intermediate", "advanced", "general"]
                ),
                ToolParameter(
                    name="subject_area",
                    type="string",
                    description="Subject area hint for better analysis",
                    required=False,
                    default="auto-detect"
                ),
                ToolParameter(
                    name="max_pdf_pages",
                    type="integer",
                    description="Maximum number of pages to process from PDF files (default: 50)",
                    required=False,
                    default=50
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the slide analysis."""
        start_time = time.monotonic()
        try:
            slide_images = parameters.get("slide_images", [])
            ai_provider = parameters.get("ai_provider", "openai")
            analysis_depth = parameters.get("analysis_depth", "comprehensive")
            target_audience = parameters.get("target_audience", "general")
            subject_area = parameters.get("subject_area", "auto-detect")
            max_pdf_pages = parameters.get("max_pdf_pages", 50)
            
            if not slide_images:
                return ToolResult(
                    success=False,
                    error="No slide images provided"
                )
            
            # Validate and prepare images (including PDF conversion)
            validated_images = await self._validate_images(slide_images, max_pdf_pages, analysis_depth)
            if not validated_images:
                return ToolResult(
                    success=False,
                    error="No valid images found in the provided list"
                )
            
            # Determine AI provider
            provider = AIProvider.OPENAI if ai_provider.lower() == "openai" else AIProvider.GOOGLE
            
            # Analyze slides
            analysis_result = await self._analyze_slides(
                validated_images, 
                provider, 
                analysis_depth,
                target_audience,
                subject_area
            )
            print(f"DEBUG: Raw analysis from vision model ({provider.value}):\n{json.dumps(analysis_result, indent=2)}") # Log vision output
            
            # Extract structured information
            structured_result = await self._extract_structured_info(
                analysis_result,
                provider,
                analysis_depth
            )
            
            # Suggest next tools based on analysis
            next_tools = self._suggest_next_tools(analysis_depth, structured_result)
            
            end_time = time.monotonic()
            execution_time = round(end_time - start_time, 2)
            
            return ToolResult(
                success=True,
                data=structured_result,
                execution_time=execution_time,
                suggested_next_tools=next_tools,
                agent_notes=f"Analyzed {len(validated_images)} slides using {provider.value} with {analysis_depth} depth"
            )
            
        except Exception as e:
            end_time = time.monotonic()
            execution_time = round(end_time - start_time, 2)
            return ToolResult(
                success=False,
                error=f"Slide analysis failed: {str(e)}",
                execution_time=execution_time
            )
    
    async def _validate_images(self, slide_images: List[Union[str, bytes]], max_pdf_pages: int = 50, analysis_depth: str = "comprehensive") -> List[Union[str, bytes]]:
        """Validate and filter image inputs, including PDF conversion."""
        validated = []
        
        for img in slide_images:
            if isinstance(img, str):
                # Check if it's a file path
                if Path(img).exists():
                    file_path = Path(img)
                    ext = file_path.suffix.lower()
                    
                    # Handle PDF files
                    if ext == '.pdf':
                        if not PDF_SUPPORT_AVAILABLE:
                            print(f"WARNING: PDF support not available. Skipping {img}")
                            continue
                        
                        try:
                            print(f"Converting PDF to images: {img}")
                            # Use ultra-high DPI for complete text extraction
                            dpi = 350 if analysis_depth == "comprehensive" else 300
                            pdf_images = pdf_processor.pdf_to_images(img, dpi=dpi, max_pages=max_pdf_pages)
                            validated.extend(pdf_images)
                            print(f"Successfully converted {len(pdf_images)} pages from PDF at {dpi} DPI")
                        except Exception as e:
                            print(f"ERROR: Failed to convert PDF {img}: {e}")
                            continue
                    
                    # Handle image files
                    elif ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                        validated.append(img)
                    
                elif img.startswith('data:image/') or len(img) > 100:
                    # Assume it's base64 encoded
                    validated.append(img)
            elif isinstance(img, bytes):
                # Check if it's PDF bytes by trying to convert
                if PDF_SUPPORT_AVAILABLE and pdf_processor.validate_pdf(img):
                    try:
                        print("Converting PDF bytes to images")
                        # Use ultra-high DPI for complete text extraction
                        dpi = 350 if analysis_depth == "comprehensive" else 300
                        pdf_images = pdf_processor.pdf_to_images(img, dpi=dpi, max_pages=max_pdf_pages)
                        validated.extend(pdf_images)
                        print(f"Successfully converted {len(pdf_images)} pages from PDF bytes at {dpi} DPI")
                    except Exception as e:
                        print(f"ERROR: Failed to convert PDF bytes: {e}")
                        continue
                else:
                    # Assume it's image bytes
                    validated.append(img)
        
        return validated
    
    async def _analyze_slides(
        self, 
        images: List[Union[str, bytes]], 
        provider: AIProvider,
        analysis_depth: str,
        target_audience: str,
        subject_area: str
    ) -> Dict[str, Any]:
        """Analyze slides using AI vision models."""
        
        # Create comprehensive analysis prompt
        prompt = self._create_analysis_prompt(analysis_depth, target_audience, subject_area)
        
        try:
            response = await ai_client.analyze_images(
                images=images,
                prompt=prompt,
                provider=provider,
                temperature=0.3  # Lower temperature for structured analysis
            )
            
            return {
                "analysis_text": response["content"],
                "provider": response["provider"],
                "model": response["model"],
                "usage": response.get("usage", {}),
                "images_analyzed": response.get("images_analyzed", len(images))
            }
            
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, depth: str, audience: str, subject: str) -> str:
        """Create a comprehensive analysis prompt based on parameters."""
        
        common_instructions = """
RÈGLE ABSOLUE : EXTRACTION EXACTE UNIQUEMENT
Votre tâche est d'analyser attentivement l'ENSEMBLE des diapositives fournies pour en déterminer la nature globale, puis de structurer les informations extraites en un objet JSON unique.

INSTRUCTIONS CRITIQUES POUR L'EXTRACTION :
1. COPIEZ EXACTEMENT le texte visible - mot pour mot, caractère pour caractère
2. CONSERVEZ la structure originale - numérotation, formatage, ponctuation
3. NE MODIFIEZ JAMAIS le contenu - pas de reformulation, pas de résumé, pas d'amélioration
4. NE COMPLÉTEZ JAMAIS les phrases incomplètes ou tronquées
5. NE CORRIGEZ JAMAIS les fautes d'orthographe ou de grammaire
6. RESPECTEZ l'ordre exact des éléments comme ils apparaissent
7. Si le texte est partiellement visible ou coupé, copiez uniquement la partie visible

Toute votre analyse DOIT être basée strictement et exclusivement sur le contenu visible dans les diapositives. N'inférez, n'ajoutez, ou ne supposez AUCUNE information non explicitement présente.
Tous les champs textuels de l'objet JSON doivent être en FRANÇAIS et reproduire EXACTEMENT le texte source.

ÉTAPE 1: Classification Globale du Document
Après avoir examiné TOUTES les diapositives, déterminez le type de document principal parmi les suivants. Soyez très attentif aux titres principaux, aux en-têtes/pieds de page et à la structure globale du contenu pour faire votre choix. Une attention particulière doit être portée aux indicateurs d'évaluation.

- 'examen': **Priorité haute si des indicateurs clairs sont présents.** Si le document est un examen formel, un test, ou une évaluation. Recherchez des mots-clés proéminents dans les titres ou en début de document comme "Examen" (par exemple, "Examen Final", "Examen 2022"), "Test", "Évaluation Sommative", "Contrôle Continu". La présence d'une page de titre d'examen, une structure avec des points clairement attribués par question/section, des instructions spécifiques à un examen (temps limité, matériel autorisé), ou des sections typiques d'examen renforcent ce choix. Si "Examen" est mentionné, ce type doit être privilégié même si d'autres éléments pourraient suggérer un cours ou des exercices simples.

- 'serie_exercices': Si le document n'est pas classé comme 'examen' mais est principalement une collection d'exercices, de problèmes à résoudre, ou d'études de cas. Cela peut inclure des feuilles d'exercices, des travaux dirigés (TD), des travaux pratiques (TP) où le contenu principal est une liste de tâches/questions. Les diapositives peuvent contenir plusieurs exercices, chacun avec son énoncé ou des questions numérotées. L'absence d'un cadre formel d'examen (pas de points globaux, pas de durée limitée clairement énoncée pour l'ensemble) distingue ce type de l'examen.

- 'courses': Si le document n'est PAS un 'examen' ou une 'serie_exercices' et qu'il est structuré comme du matériel pédagogique pour enseigner un sujet. Il doit contenir principalement des explications, des définitions, des exemples, des discussions de concepts. La présence de "Science made simple" ou "SMS" (cas-insensible, même avec typos) ou un nom d'institution peut indiquer la source, mais le contenu doit être majoritairement explicatif et démonstratif pour être classé 'courses'. Un document contenant uniquement des exercices et leurs solutions, même s'il est étiqueté "Science made simple", devrait être classé 'serie_exercices' ou 'examen' si le mot "Examen" est présent.

Si, et seulement si, le document ne correspond clairement à AUCUN de ces trois types après une analyse attentive, utilisez 'autre'.

ÉTAPE 2: Extraction et Structuration JSON Conditionnelle
En fonction du type de document identifié à l'ÉTAPE 1, structurez votre réponse JSON EXACTEMENT comme décrit ci-dessous pour ce type. Ne retournez QUE l'objet JSON, sans texte avant ou après.

"""

        # JSON Schema for Courses
        course_schema = """
Si le type de document est 'courses':
{
  "type_document": "courses",
  "source_details": {
    "nom_source": "string (ex: 'Science made simple', 'Université de Paris', 'Source non spécifiée' - identifié même si le type n'est pas 'courses', en français)",
    "est_interne_sms": boolean (true si 'Science made simple' ou 'SMS' détecté, applicable même si ce n'est pas un 'courses')
  },
  "course_title": "string (titre du cours ou sujet principal si ce n'est pas un cours, en français)",
  "detailed_description": "string (description du contenu si c'est un cours; si c'est un examen ou une série d'exercices, décrivez brièvement le type d'exercices et les sujets couverts, en français)",
  "short_description": "string (description courte, adaptée au type de document, en français)",
  "tags": ["tag1 (directement extrait, en français)", "tag2", ...],
  "learning_path": [
    {
      "module_name": "string (nom du module si cours; ou section principale de l'examen/série d'exercices, en français)",
      "objectives": ["objectif1 (en français)", "objectif2", ...],
      "topics": ["sujet1 (en français)", "sujet2", ...],
      "estimated_duration": "string (durée estimée, en français, si explicite, sinon 'Non spécifié')",
      "difficulty": "string (difficulté, en français, si explicite, sinon 'Non spécifié')"
    }
  ],
  "target_audience_analysis": "string (analyse de l'audience cible, en français, si explicite)",
  "course_difficulty_progression": "string (progression de la difficulté, en français, si explicite)",
  "tools_required": ["outil1 (en français, si explicite)", "outil2", ...],
  "practical_applications": ["app1 (en français, si explicite)", "app2", ...],
  "key_concepts": ["concept1 (en français, si explicite)", "concept2", ...]
}
Pour 'tags', n'incluez que des mots-clés ou phrases courtes DIRECTEMENT EXTRAITS ou CLAIREMENT REPRÉSENTÉS dans le contenu des diapositives.
Les champs facultatifs (durée, difficulté, etc.) doivent être remplis UNIQUEMENT si l'information est explicite. Sinon, utilisez "Non spécifié" ou omettez pour les listes vides.
"""

        # JSON Schema for Exams (examen) - Enhanced with tags and learning path
        exam_schema = """
Si le type de document est 'examen':
{
  "type_document": "examen",
  "source_details": {
    "nom_source": "string (ex: 'Science made simple', 'Université de Paris', 'Source non spécifiée' - en français)",
    "est_interne_sms": boolean (true si 'Science made simple' ou 'SMS' détecté)
  },
  "titre_examen": "string (titre de l'examen, en français)",
  "matiere": "string (matière(s) principale(s) couverte(s), en français)",
  "tags": ["tag1 (mots-clés extraits du contenu, en français)", "tag2", ...],
  "learning_path": [
    {
      "module_name": "string (section ou chapitre de l'examen, en français)",
      "prerequisites": ["prérequis1 (connaissances nécessaires inférées, en français)", "prérequis2", ...],
      "topics": ["sujet1 (sujets couverts dans cette section, en français)", "sujet2", ...],
      "difficulty": "string (niveau de difficulté inféré: 'débutant', 'intermédiaire', 'avancé', en français)"
    }
  ],
  "nombre_sections": "integer (nombre de sections si applicable/visible, sinon null)",
  "points_total": "string | number (points totaux si applicable/visible, sinon null)",
  "duree": "string (durée si applicable/visible, en français, sinon null)",
  "instructions_generales": "string (instructions générales de l'examen, en français, si présentes)",
  "exercices": [ 
    {
      "id_exercice_ou_titre": "string (EXACTEMENT comme écrit, ex: 'Exercice 1', 'Ex. 2', 'Question A', etc.)",
      "enonce_exercice": "string (COPIE EXACTE de l'énoncé global, mot pour mot, si présent)",
      "points_exercice": "string | number (EXACTEMENT comme écrit, si visible)",
      "questions": [ 
        {
          "id_question_ou_numero": "string (EXACTEMENT comme écrit, ex: '1a', '1)', 'Question 1', etc.)",
          "texte_question": "string (COPIE EXACTE du texte de la question, mot pour mot, sans modification)",
          "options_reponse": ["string (COPIE EXACTE de chaque option, dans l'ordre exact d'apparition)"], 
          "type_reponse_attendu": "string (inféré selon le format visible: 'choix multiple', 'réponse libre', 'vrai/faux', etc.)"
        }
      ]
    }
  ]
}
"""

        # JSON Schema for Exercise Series (serie_exercices) - Enhanced with tags and learning path
        exercises_schema = """
Si le type de document est 'serie_exercices':
{
  "type_document": "serie_exercices",
  "source_details": {
    "nom_source": "string (ex: 'Science made simple', 'Université de Paris', 'Source non spécifiée' - en français)",
    "est_interne_sms": boolean (true si 'Science made simple' ou 'SMS' détecté)
  },
  "sujet_principal": "string (sujet général des exercices, en français)",
  "tags": ["tag1 (mots-clés extraits du contenu, en français)", "tag2", ...],
  "learning_path": [
    {
      "module_name": "string (thème ou chapitre des exercices, en français)",
      "prerequisites": ["prérequis1 (connaissances nécessaires inférées, en français)", "prérequis2", ...],
      "topics": ["sujet1 (sujets couverts dans cette série, en français)", "sujet2", ...],
      "difficulty": "string (niveau de difficulté inféré: 'débutant', 'intermédiaire', 'avancé', en français)"
    }
  ],
  "exercices": [ 
    {
      "id_exercice_ou_titre": "string (EXACTEMENT comme écrit, ex: 'Exercice 1', 'Ex. 2', 'Question A', etc.)",
      "enonce_exercice": "string (COPIE EXACTE de l'énoncé global, mot pour mot, si présent)",
      "points_exercice": "string | number (EXACTEMENT comme écrit, si visible)",
      "questions": [ 
        {
          "id_question_ou_numero": "string (EXACTEMENT comme écrit, ex: '1a', '1)', 'Question 1', etc.)",
          "texte_question": "string (COPIE EXACTE du texte de la question, mot pour mot, sans modification)",
          "options_reponse": ["string (COPIE EXACTE de chaque option, dans l'ordre exact d'apparition)"], 
          "type_reponse_attendu": "string (inféré selon le format visible: 'choix multiple', 'réponse libre', 'vrai/faux', etc.)"
        }
      ]
    }
  ]
}
"""
        
        # JSON Schema for Other (autre) - last resort
        other_schema = """
Si, et seulement si, le document ne peut être classé dans 'courses', 'examen', ou 'serie_exercices':
{
  "type_document": "autre",
  "description_contenu": "string (brève description du contenu général observé, en français)",
  "raison_classification_autre": "string (expliquez pourquoi il n'a pas pu être classé comme cours, examen ou série d'exercices, en français)"
}
"""

        specific_guidance = f"""
Informations contextuelles pour cette analyse (utilisez-les pour affiner la classification et l'extraction) :
Profondeur d'analyse demandée : {depth}
Public cible indiqué : {audience}
Domaine sujet (indice) : {subject}

Adaptez le niveau de détail en fonction de la profondeur demandée, mais respectez TOUJOURS la consigne de vous baser UNIQUEMENT sur le contenu explicite des diapositives. Votre réponse doit être un JSON valide unique.
"""

        final_prompt = (
            common_instructions
            + course_schema
            + exam_schema
            + exercises_schema
            + other_schema
            + specific_guidance
        )
        return final_prompt
    
    async def _extract_structured_info(
        self, 
        analysis_result: Dict[str, Any],
        provider: AIProvider,
        depth: str
    ) -> Dict[str, Any]:
        """Extract and structure the course information from AI analysis."""
        
        analysis_text = analysis_result.get("analysis_text", "Aucun texte d'analyse produit.")
        
        # Try to extract JSON from the response
        structured_data = self._extract_json_from_text(analysis_text)
        
        if not structured_data:
            # If JSON extraction fails, use AI to structure the data
            structured_data = await self._structure_with_ai(analysis_text, provider)

        # If still no valid structured_data or type_document is missing, use fallback
        if not structured_data or not structured_data.get("type_document"):
            structured_data = self._create_fallback_structure(analysis_text)
        
        # IMPORTANT: Extract raw slide contents for quiz generation
        # This is what the quiz generator needs to find exercises
        slide_contents = await self._extract_slide_contents(analysis_result, provider)
        structured_data["slide_contents"] = slide_contents
        
        # Ensure the original depth parameter is available for metadata, especially if fallback occurred
        structured_data["analysis_depth_param"] = depth
        # Stash original provider and model from analysis_result if not already in structured_data (e.g. from fallback)
        if "provider" not in structured_data:
            structured_data["provider"] = analysis_result.get("provider")
        if "model" not in structured_data:
            structured_data["model"] = analysis_result.get("model")
        if "images_analyzed" not in structured_data:
             structured_data["images_analyzed"] = analysis_result.get("images_analyzed", 0)
        if "usage" not in structured_data:
             structured_data["usage"] = analysis_result.get("usage", {})

        # Add metadata about the analysis, ensuring not to overwrite agent_notes from fallback
        current_agent_notes = structured_data.get("agent_notes")
        structured_data["analysis_metadata"] = {
            "provider": analysis_result.get("provider", "unknown"),
            "model": analysis_result.get("model", "unknown"),
            "images_analyzed": analysis_result.get("images_analyzed", 0),
            "analysis_depth": depth, # depth is a parameter of _extract_structured_info
            "usage_stats": analysis_result.get("usage", {})
        }
        if current_agent_notes:
            structured_data["agent_notes"] = current_agent_notes # Preserve fallback notes if any
        
        # Validate and clean the structured data based on its identified type
        structured_data = self._validate_and_clean_data(structured_data)
        
        return structured_data
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from text response."""
        try:
            # Look for JSON block in the text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return None
    
    async def _structure_with_ai(self, analysis_text: str, provider: AIProvider) -> Dict[str, Any]:
        """Attempt to structure the analysis text using another AI call."""
        print(f"DEBUG: Attempting to structure text with AI ({provider.value}). Input text:\n{analysis_text[:1000]}...") # Log input to fallback
        
        # Determine which model to use for structuring (prefer OpenAI for complex JSON)
        structuring_provider = AIProvider.OPENAI 
        
        structure_prompt = f"""
Le texte d'analyse suivant a été généré à partir de diapositives. Votre tâche est de le convertir en un objet JSON unique et correctement formaté, en FRANÇAIS.

Texte d'analyse brut :
{analysis_text}

Instructions importantes :
1.  Identifiez d'abord le type de document principal implicite dans le texte d'analyse. Les types possibles sont : 'courses', 'examen', 'serie_exercices'. Si aucun de ces types ne correspond clairement, utilisez 'autre'.
2.  Ensuite, structurez les informations UNIQUEMENT à partir du texte d'analyse fourni dans le format JSON approprié pour ce type. N'ajoutez ou n'inférez aucune information.
3.  COPIEZ EXACTEMENT le texte tel qu'il apparaît dans l'analyse - pas de reformulation, pas de correction, pas d'amélioration.
4.  Tous les champs textuels du JSON doivent être en FRANÇAIS et reproduire EXACTEMENT le texte source.

Schémas JSON cibles (choisissez celui qui correspond le mieux au texte d'analyse) :

Format pour 'courses':
{{ 
  "type_document": "courses",
  "source_details": {{ "nom_source": "string", "est_interne_sms": boolean }},
  "course_title": "string", ... (autres champs de cours comme définis dans l'invite principale)
}}

Format pour 'examen':
{{ 
  "type_document": "examen",
  "titre_examen": "string",
  "matiere": "string",
  "exercices": [ {{ "id_exercice_ou_titre": "string", "questions": [{{...}}] }} ], ... (autres champs d'examen comme définis dans l'invite principale)
}}

Format pour 'serie_exercices':
{{ 
  "type_document": "serie_exercices",
  "sujet_principal": "string",
  "exercices": [ {{ "id_exercice_ou_titre": "string", "questions": [{{...}}] }} ]
}}

Format pour 'autre' (dernier recours):
{{ 
  "type_document": "autre",
  "description_contenu": "string",
  "raison_classification_autre": "string"
}}

(Remarque: les "... (autres champs...)" font référence aux schémas détaillés de l'invite de génération principale. Utilisez la structure complète pour le type de document identifié.)

Répondez UNIQUEMENT avec l'objet JSON. Pas de texte supplémentaire avant ou après.
"""
        
        try:
            response = await ai_client.generate_response(
                messages=[{"role": "user", "content": structure_prompt}],
                provider=structuring_provider,
                temperature=0.1
            )
            
            parsed_json = self._extract_json_from_text(response["content"])
            if not parsed_json or not parsed_json.get("type_document"):
                # If parsing fails or doc type is missing, return a fallback that includes original text for context
                return self._create_fallback_structure(analysis_text) 
            return parsed_json
            
        except Exception as e:
            print(f"ERROR in _structure_with_ai: {e}")
            return self._create_fallback_structure(analysis_text)
    
    def _create_fallback_structure(self, analysis_text: Optional[str] = None) -> Dict[str, Any]:
        """Create a fallback structure if extraction fails, now simplified."""
        description = "L'analyse détaillée et la classification ont échoué."
        if analysis_text and analysis_text != "Aucun texte d'analyse produit.":
            description += f" Fragment du texte d'analyse non structuré : {analysis_text[:250]}..."
        
        return {
            "type_document": "autre",
            "description_contenu": description,
            "raison_classification_autre": "Impossible de classifier ou de structurer le contenu de manière fiable.",
            "agent_notes": "L'outil est revenu à une structure de secours."
        }
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch to specific validation functions based on document type."""
        doc_type = data.get("type_document")

        if not doc_type: # Should always have doc_type if parsing worked at all
            data = self._create_fallback_structure(data.get("analysis_text"))
            doc_type = data.get("type_document")

        # Ensure analysis_metadata is present, even if it was a fallback initially
        if "analysis_metadata" not in data:
            # analysis_result might not be in data if we went straight to fallback
            # and fallback didn't have these. So we use .get on data itself.
            analysis_result_provider = data.get("provider", "unknown")
            analysis_result_model = data.get("model", "unknown")
            analysis_result_images_analyzed = data.get("images_analyzed", 0)
            analysis_result_usage = data.get("usage", {})
            analysis_depth_param = data.get("analysis_depth_param", "unknown") # Need to ensure this is passed if not in analysis_result

            data["analysis_metadata"] = {
                "provider": analysis_result_provider,
                "model": analysis_result_model,
                "images_analyzed": analysis_result_images_analyzed,
                "analysis_depth": analysis_depth_param, # This was `depth` before, ensure it's available
                "usage_stats": analysis_result_usage
            }

        if doc_type == "courses":
            return self._validate_course_data(data)
        elif doc_type == "examen":
            return self._validate_exam_data(data)
        elif doc_type == "serie_exercices":
            return self._validate_exercises_data(data)
        elif doc_type == "autre":
            return self._validate_other_data(data)
        else: # Unknown type, return as is with a note or basic validation
            data["agent_notes"] = f"Type de document non reconnu: {doc_type}. Validation minimale."
            if "description_contenu" not in data:
                 data["description_contenu"] = "Contenu non classifié."
            return data

    def _validate_course_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean structured data for courses."""
        data.setdefault("type_document", "courses") 
        source_details = data.get("source_details", {})
        if not isinstance(source_details, dict): source_details = {}
        source_details.setdefault("nom_source", "Source non spécifiée")
        source_details.setdefault("est_interne_sms", False)
        data["source_details"] = source_details

        data.setdefault("course_title", "Titre du Cours (Généré)")
        data.setdefault("detailed_description", "Description Détaillée (Générée)")
        data.setdefault("short_description", "Description Courte (Générée)")
        data.setdefault("tags", ["cours"])
        data.setdefault("learning_path", [{
            "module_name": "Module Principal (Généré)",
            "objectives": ["Objectif à définir"],
            "topics": ["Sujet à définir"],
            "estimated_duration": "N/A",
            "difficulty": "N/A"
        }])
        data.setdefault("target_audience_analysis", "Analyse de l'audience à compléter")
        data.setdefault("course_difficulty_progression", "Progression à décrire")
        data.setdefault("tools_required", ["N/A"])
        data.setdefault("practical_applications", ["N/A"])
        data.setdefault("key_concepts", ["N/A"])

        if isinstance(data["tags"], list):
            data["tags"] = list(set(tag.strip().lower() for tag in data["tags"] if isinstance(tag, str) and tag.strip()))
        else:
            data["tags"] = ["cours"]

        if isinstance(data["learning_path"], list):
            for module in data["learning_path"]:
                if isinstance(module, dict):
                    module.setdefault("module_name", "Module (Généré)")
                    module.setdefault("objectives", ["Objectif à définir"])
                    module.setdefault("topics", ["Sujet à définir"])
                    module.setdefault("estimated_duration", "N/A")
                    module.setdefault("difficulty", "N/A")
        else:
            data["learning_path"] = [self._validate_course_data({})["learning_path"][0]] # get default module
        return data

    def _validate_exam_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean structured data for exams."""
        data.setdefault("type_document", "examen")
        
        source_details = data.get("source_details", {})
        if not isinstance(source_details, dict): source_details = {}
        source_details.setdefault("nom_source", "Source non spécifiée")
        source_details.setdefault("est_interne_sms", False)
        data["source_details"] = source_details
        
        data.setdefault("titre_examen", "Examen (Généré)")
        data.setdefault("matiere", "Non spécifiée")
        data.setdefault("instructions_generales", "Aucune instruction générale fournie.")
        
        # Add tags and learning path for exams
        data.setdefault("tags", ["examen"])
        data.setdefault("learning_path", [{
            "module_name": "Évaluation Principale (Généré)",
            "prerequisites": ["Connaissances de base à définir"],
            "topics": ["Sujets à identifier"],
            "difficulty": "intermédiaire"
        }])
        
        data.setdefault("exercices", [])

        # Validate tags
        if isinstance(data["tags"], list):
            data["tags"] = list(set(tag.strip().lower() for tag in data["tags"] if isinstance(tag, str) and tag.strip()))
        else:
            data["tags"] = ["examen"]

        # Validate learning path
        if isinstance(data["learning_path"], list):
            for module in data["learning_path"]:
                if isinstance(module, dict):
                    module.setdefault("module_name", "Module (Généré)")
                    module.setdefault("prerequisites", ["Prérequis à définir"])
                    module.setdefault("topics", ["Sujets à définir"])
                    module.setdefault("difficulty", "intermédiaire")
        else:
            data["learning_path"] = [data["learning_path"][0]] if data.get("learning_path") else [{
                "module_name": "Évaluation Principale (Généré)",
                "prerequisites": ["Connaissances de base à définir"],
                "topics": ["Sujets à identifier"],
                "difficulty": "intermédiaire"
            }]

        if isinstance(data["exercices"], list):
            for ex in data["exercices"]:
                if isinstance(ex, dict):
                    ex.setdefault("id_exercice_ou_titre", "Exercice (Généré)")
                    ex.setdefault("enonce_exercice", "Énoncé à définir.")
                    ex.setdefault("questions", [])
                    if isinstance(ex["questions"], list):
                        for q in ex["questions"]:
                            if isinstance(q, dict):
                                q.setdefault("id_question_ou_numero", "Question (Générée)")
                                q.setdefault("texte_question", "Texte de la question à définir.")
                                q.setdefault("options_reponse", [])
                                q.setdefault("type_reponse_attendu", "Non spécifié")
                    else:
                        ex["questions"] = [] # Ensure it's a list
        else:
            data["exercices"] = [] # Ensure it's a list
        return data

    def _validate_exercises_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean structured data for exercise series."""
        data.setdefault("type_document", "serie_exercices")

        source_details = data.get("source_details", {})
        if not isinstance(source_details, dict): source_details = {}
        source_details.setdefault("nom_source", "Source non spécifiée")
        source_details.setdefault("est_interne_sms", False)
        data["source_details"] = source_details

        data.setdefault("sujet_principal", "Série d'exercices (Généré)")
        
        # Add tags and learning path for exercise series
        data.setdefault("tags", ["exercices"])
        data.setdefault("learning_path", [{
            "module_name": "Série d'Exercices Principale (Généré)",
            "prerequisites": ["Connaissances de base à définir"],
            "topics": ["Sujets à identifier"],
            "difficulty": "intermédiaire"
        }])
        
        data.setdefault("exercices", [])

        # Validate tags
        if isinstance(data["tags"], list):
            data["tags"] = list(set(tag.strip().lower() for tag in data["tags"] if isinstance(tag, str) and tag.strip()))
        else:
            data["tags"] = ["exercices"]

        # Validate learning path
        if isinstance(data["learning_path"], list):
            for module in data["learning_path"]:
                if isinstance(module, dict):
                    module.setdefault("module_name", "Module (Généré)")
                    module.setdefault("prerequisites", ["Prérequis à définir"])
                    module.setdefault("topics", ["Sujets à définir"])
                    module.setdefault("difficulty", "intermédiaire")
        else:
            data["learning_path"] = [{
                "module_name": "Série d'Exercices Principale (Généré)",
                "prerequisites": ["Connaissances de base à définir"],
                "topics": ["Sujets à identifier"],
                "difficulty": "intermédiaire"
            }]

        # Validate exercises using similar logic to exam validation
        if isinstance(data["exercices"], list):
            for ex in data["exercices"]:
                if isinstance(ex, dict):
                    ex.setdefault("id_exercice_ou_titre", "Exercice (Généré)")
                    ex.setdefault("enonce_exercice", "Énoncé à définir.")
                    ex.setdefault("questions", [])
                    if isinstance(ex["questions"], list):
                        for q in ex["questions"]:
                            if isinstance(q, dict):
                                q.setdefault("id_question_ou_numero", "Question (Générée)")
                                q.setdefault("texte_question", "Texte de la question à définir.")
                                q.setdefault("options_reponse", [])
                                q.setdefault("type_reponse_attendu", "Non spécifié")
                    else:
                        ex["questions"] = []
        else:
            data["exercices"] = []
            
        return data

    def _validate_other_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean structured data for 'other' type."""
        data.setdefault("type_document", "autre")
        data.setdefault("description_contenu", "Description du contenu non disponible.")
        data.setdefault("raison_classification_autre", "Non spécifiée.")
        return data

    def _suggest_next_tools(self, analysis_depth: str, structured_data: Dict[str, Any]) -> List[str]:
        """Suggest appropriate next tools based on analysis results."""
        suggestions = []
        
        # Always suggest content analyzer for deeper text analysis
        suggestions.append("contentanalyzer")
        
        # Suggest content generator based on analysis depth
        if analysis_depth in ["detailed", "comprehensive"]:
            suggestions.append("contentgenerator")
        
        # Suggest file processor if course has materials
        if structured_data.get("tools_required") or structured_data.get("practical_applications"):
            suggestions.append("fileprocessor")
        
        return suggestions 

    async def _extract_slide_contents(self, analysis_result: Dict[str, Any], provider: AIProvider) -> List[Dict[str, Any]]:
        """Extract raw slide contents for quiz generation."""
        
        analysis_text = analysis_result.get("analysis_text", "")
        images_analyzed = analysis_result.get("images_analyzed", 0)
        
        if not analysis_text or images_analyzed == 0:
            return []
        
        # Create a specific prompt to extract slide-by-slide content
        content_extraction_prompt = f"""
You analyzed {images_analyzed} slide images. Now extract the RAW TEXT CONTENT from each slide separately.

For each slide, provide EXACTLY the text content visible on that slide, preserving:
- Question numbers (like "Question 4", "4a", "4b", etc.)
- Problem statements word-for-word
- Mathematical formulas and equations
- All visible text in original language (French/English)
- Original formatting and structure

Return the result as a JSON array with this exact format:
[
  {{
    "slide_number": 1,
    "content": "EXACT text content from slide 1..."
  }},
  {{
    "slide_number": 2, 
    "content": "EXACT text content from slide 2..."
  }},
  ...
]

Original analysis text for reference:
{analysis_text}

IMPORTANT: Extract the text content EXACTLY as it appears on each slide. Do not summarize, rephrase, or modify. This is critical for quiz generation.
"""
        
        try:
            response = await ai_client.generate_response(
                messages=[{"role": "user", "content": content_extraction_prompt}],
                provider=provider,
                temperature=0.1  # Very low temperature for exact extraction
            )
            
            # Try to extract JSON array from response
            import re
            json_match = re.search(r'\[[\s\S]*\]', response["content"])
            if json_match:
                json_str = json_match.group()
                slide_contents = json.loads(json_str)
                
                # Validate the structure
                if isinstance(slide_contents, list):
                    validated_contents = []
                    for slide in slide_contents:
                        if isinstance(slide, dict) and "slide_number" in slide and "content" in slide:
                            validated_contents.append({
                                "slide_number": slide["slide_number"],
                                "content": slide["content"]
                            })
                    
                    print(f"✅ Extracted content from {len(validated_contents)} slides")
                    return validated_contents
            
            # If JSON extraction fails, create basic slide contents from analysis text
            print("⚠️ Failed to extract structured slide contents, creating basic structure")
            return self._create_basic_slide_contents(analysis_text, images_analyzed)
            
        except Exception as e:
            print(f"❌ Error extracting slide contents: {e}")
            return self._create_basic_slide_contents(analysis_text, images_analyzed)
    
    def _create_basic_slide_contents(self, analysis_text: str, num_slides: int) -> List[Dict[str, Any]]:
        """Create basic slide contents when extraction fails."""
        
        if not analysis_text or num_slides == 0:
            return []
        
        # Split analysis text by potential slide breaks
        # Look for patterns that might indicate slide boundaries
        slide_markers = [
            r'slide\s*\d+',
            r'diapositive\s*\d+', 
            r'page\s*\d+',
            r'\n\n\n+',  # Multiple line breaks
        ]
        
        # Try to split the text
        import re
        text_parts = [analysis_text]  # Start with full text
        
        for marker in slide_markers:
            new_parts = []
            for part in text_parts:
                splits = re.split(marker, part, flags=re.IGNORECASE)
                new_parts.extend([s.strip() for s in splits if s.strip()])
            text_parts = new_parts
        
        # Ensure we have the right number of parts
        if len(text_parts) > num_slides:
            text_parts = text_parts[:num_slides]
        elif len(text_parts) < num_slides:
            # Distribute text evenly if we have fewer parts than slides
            while len(text_parts) < num_slides:
                if text_parts:
                    text_parts.append(text_parts[-1][:len(text_parts[-1])//2])
                else:
                    text_parts.append(analysis_text)
        
        # Create slide contents
        slide_contents = []
        for i in range(num_slides):
            content = text_parts[i] if i < len(text_parts) else analysis_text
            slide_contents.append({
                "slide_number": i + 1,
                "content": content
            })
        
        print(f"📄 Created basic slide contents for {len(slide_contents)} slides")
        return slide_contents 