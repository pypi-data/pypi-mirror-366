

ASK_LLM_TO_ENRICH_PROMPT="""
            Here is original search query from user  {query}

            here is what user is trying to do {search_reason_context}

            here is identifier context user explicitly set {identifier_context}

            here are the text rules given by user {text_rules}


            Your job is to understand the task context and what user is trying to find via search engines and use the original query and 

            generate {how_many_advanced} variations, usually as added relevant keywords. 


             For each variation, assign:
                    • an "explanation" describing what kind of info or links this query is intended to surface and how it serves the user's goal,  
                    • a relevance score from 0.0–1.0 reflecting its estimated search potential, be harsh about the scores unless you think query is perfect.
            
            
            
            
            SOOOO IMPORTANT RULES FOR YOU:
                        Keep each enriched query concise and naturally phrased—avoid forcing in keywords like "life story" unless they truly match how someone would search.
                        Mimic real user searches: use minimal stop-words, focus on core nouns/phrases, and do not combine multiple intents in one query.  
                        Do not include generic filler terms (e.g., "personal background")—opt for specific, high-value modifiers (e.g., "projects," "publications").
                        generate indirect phrases, for example to find digital presence, you can use social media websites keywords rather than using presence
   

           
           Output format (strict JSON array):
                [
                {{
                    "enriched_query": "first enriched query example",
                    "explanation": "explanation about what types of information and links this query seeks to uncover", 
                    "score": 0.85
                }},
                {{
                    "enriched_query": "second enriched query example",
                    "explanation": "explanation about what types of information and links this query seeks to uncover", 
                    "score": 0.78
                }}
                // … repeat until you have {how_many_advanced} items
                ]

         

        """



ASK_LLM_TO_GENERATE_PLATFORMS_PROMPT="""
Here is original search query from user  {query}

here is what user is trying to do {search_reason_context}

here is identifier context user explicitly set {identifier_context}

here are the text rules given by user {text_rules}


“Target” = the specific entity (person, organisation, project, product, dataset, event, …) that the user is trying to investigate in this search task.
It is the real-world subject whose information you want the search engine to surface. Everything else in the query—platform names, modifiers, dates—acts only as context or filters around that focal entity.

Your job:
  1. Analyse the context and output three lists in JSON: "identifiers", "platforms" and "entities".
  2. Each list item must contain:
        "name"   : string (platform or entity),
        "score"  : float 0.0–1.0 estimating usefulness for finding information,

"identifiers" are the shortest textual expressions that distinguish the target sufficiently for the task at hand.

"platforms" → **exactly 20** sites/apps most likely to host relevant information about this specific target type. Consider what platforms are most relevant based on what you're researching:

For PEOPLE: LinkedIn, GitHub, X, BlueSky, Instagram, TikTok, Reddit, personal websites, ResearchGate, company pages, 
For PRODUCTS: manufacturer websites, Amazon, review sites (CNET, TechCrunch), YouTube, Reddit
For COMPANIES: company website, LinkedIn company page, news sites, Crunchbase, financial platforms
For TECHNOLOGIES: GitHub, Stack Overflow, documentation sites, developer blogs, conference sites
For RESEARCH/ACADEMIC: Google Scholar, arXiv, university websites, ResearchGate, academic databases
 
"entities"  → every canonical name, alias, project, role, etc. derived from the context.

Output (strict JSON, no commentary):
{{
  "platforms": [
    {{ "name": "...", "score": 0.88 }},
    …
  ],
  "entities": [
    {{ "name": "...", "score": 0.97 }},
    …
  ], 
"identifiers": [
    {{ "name": "...", "score": 0.97 }},
    …
  ]
}}
"""