"""
IsoPrompt - AI-powered prompt optimization tool.
Domains are the categories of knowledge that IsoPrompt can optimize prompts for.
"""

from typing import List

from .models import IsoPromptDomain

DEFAULT_DOMAIN = "general_knowledge"


ISOPROMPT_DOMAINS = [
    # Pure Sciences
    {
        "domain": "mathematics",
        "description": "Study of numbers, structures, patterns, and logical reasoning.",
        "fields": [
            "algebra",
            "geometry",
            "calculus",
            "statistics",
            "probability",
            "number_theory",
            "logic",
            "topology",
            "discrete_math",
            "analysis",
        ],
        "applications": [
            "data_analysis",
            "cryptography",
            "finance",
            "computer_science",
            "engineering",
        ],
    },
    {
        "domain": "physics",
        "description": "Study of matter, energy, forces, and the laws of nature.",
        "fields": [
            "mechanics",
            "quantum_physics",
            "thermodynamics",
            "optics",
            "astrophysics",
            "nuclear_physics",
            "particle_physics",
            "relativity",
            "condensed_matter",
        ],
        "applications": ["aerospace", "electronics", "energy", "materials_science"],
    },
    {
        "domain": "chemistry",
        "description": "Study of substances, their properties, reactions, and transformations.",
        "fields": [
            "organic_chemistry",
            "inorganic_chemistry",
            "physical_chemistry",
            "biochemistry",
            "analytical_chemistry",
            "theoretical_chemistry",
        ],
        "applications": ["pharma", "materials", "food_science", "biotechnology"],
    },
    {
        "domain": "biology",
        "description": "Science of life, living organisms, and ecosystems.",
        "fields": [
            "molecular_biology",
            "cell_biology",
            "genetics",
            "evolution",
            "zoology",
            "botany",
            "microbiology",
            "ecology",
            "physiology",
            "developmental_biology",
        ],
        "applications": ["medicine", "biotech", "agriculture", "environmental_science"],
    },
    {
        "domain": "astronomy",
        "description": "Study of celestial objects, space, and the universe.",
        "fields": [
            "astrophysics",
            "planetary_science",
            "cosmology",
            "observational_astronomy",
        ],
        "applications": ["space_science", "satellite_technology"],
    },
    {
        "domain": "earth_sciences",
        "description": "Study of Earth, its structure, processes, and environments.",
        "fields": [
            "geology",
            "geography",
            "meteorology",
            "oceanography",
            "climatology",
            "hydrology",
            "paleontology",
            "soil_science",
            "volcanology",
            "seismology",
        ],
        "applications": [
            "mining",
            "oil_and_gas",
            "environmental_policy",
            "urban_planning",
        ],
    },
    # Engineering & Technology
    {
        "domain": "computer_science",
        "description": "Theoretical and practical study of computation, software, and information systems.",
        "fields": [
            "algorithms",
            "data_structures",
            "software_engineering",
            "machine_learning",
            "artificial_intelligence",
            "data_science",
            "theoretical_cs",
            "cybersecurity",
            "networks",
            "operating_systems",
            "databases",
            "programming_languages",
        ],
        "applications": [
            "software_development",
            "web",
            "cloud",
            "mobile",
            "robotics",
            "automation",
        ],
    },
    {
        "domain": "engineering",
        "description": "Application of science and math to solve real-world problems.",
        "fields": [
            "mechanical_engineering",
            "electrical_engineering",
            "civil_engineering",
            "chemical_engineering",
            "aerospace_engineering",
            "biomedical_engineering",
            "systems_engineering",
            "materials_engineering",
            "environmental_engineering",
            "nuclear_engineering",
            "industrial_engineering",
            "petroleum_engineering",
            "automotive_engineering",
        ],
        "applications": [
            "product_design",
            "manufacturing",
            "infrastructure",
            "energy",
            "transport",
        ],
    },
    {
        "domain": "artificial_intelligence",
        "description": "Study and creation of intelligent systems and agents.",
        "fields": [
            "machine_learning",
            "deep_learning",
            "natural_language_processing",
            "computer_vision",
            "robotics",
            "multi-agent_systems",
            "explainable_ai",
            "ai_alignment",
        ],
        "applications": [
            "automation",
            "analytics",
            "personal_assistants",
            "autonomous_vehicles",
        ],
    },
    {
        "domain": "robotics",
        "description": "Design, construction, and use of robots.",
        "fields": [
            "robot_design",
            "robot_control",
            "swarm_robots",
            "humanoid_robots",
            "industrial_robots",
            "medical_robots",
        ],
        "applications": ["manufacturing", "surgery", "exploration", "service_robots"],
    },
    {
        "domain": "nanotechnology",
        "description": "Manipulation and application of matter at the nanoscale.",
        "fields": [
            "nanomaterials",
            "nanoelectronics",
            "nanomedicine",
            "nanofabrication",
        ],
        "applications": ["medicine", "materials", "electronics"],
    },
    # Medicine & Life Sciences
    {
        "domain": "medicine",
        "description": "Science and practice of diagnosis, treatment, and prevention of disease.",
        "fields": [
            "internal_medicine",
            "surgery",
            "pediatrics",
            "psychiatry",
            "neurology",
            "oncology",
            "immunology",
            "radiology",
            "anesthesiology",
            "pathology",
            "cardiology",
            "public_health",
            "genomics",
            "pharmacology",
            "epidemiology",
            "emergency_medicine",
        ],
        "applications": [
            "clinical_practice",
            "medical_research",
            "telemedicine",
            "biotechnology",
        ],
    },
    {
        "domain": "public_health",
        "description": "Promoting and protecting the health of populations.",
        "fields": [
            "epidemiology",
            "health_policy",
            "health_education",
            "global_health",
            "biostatistics",
            "occupational_health",
        ],
        "applications": ["disease_control", "health_education", "community_health"],
    },
    {
        "domain": "psychology",
        "description": "Study of mind, behavior, and mental processes.",
        "fields": [
            "clinical_psychology",
            "cognitive_psychology",
            "behavioral_psychology",
            "developmental_psychology",
            "neuropsychology",
            "social_psychology",
            "forensic_psychology",
            "organizational_psychology",
        ],
        "applications": ["therapy", "counseling", "organizational_behavior"],
    },
    {
        "domain": "biotechnology",
        "description": "Use of biological systems and organisms for technological advances.",
        "fields": [
            "synthetic_biology",
            "bioinformatics",
            "genomics",
            "proteomics",
            "bioprocessing",
        ],
        "applications": ["pharmaceuticals", "agriculture", "food_science"],
    },
    {
        "domain": "veterinary_medicine",
        "description": "Diagnosis, treatment, and prevention of diseases in animals.",
        "fields": [
            "companion_animals",
            "farm_animals",
            "zoological_medicine",
            "wildlife_medicine",
        ],
        "applications": ["animal_health", "public_health", "animal_research"],
    },
    # Social Sciences & Humanities
    {
        "domain": "economics",
        "description": "Study of production, consumption, and distribution of goods and services.",
        "fields": [
            "microeconomics",
            "macroeconomics",
            "behavioral_economics",
            "development_economics",
            "financial_economics",
            "international_economics",
        ],
        "applications": ["policy", "finance", "consulting"],
    },
    {
        "domain": "law",
        "description": "Systems of rules created and enforced through social institutions.",
        "fields": [
            "criminal_law",
            "civil_law",
            "international_law",
            "intellectual_property",
            "constitutional_law",
            "commercial_law",
        ],
        "applications": ["legal_practice", "compliance", "policy"],
    },
    {
        "domain": "political_science",
        "description": "Study of politics, government systems, and political behavior.",
        "fields": [
            "comparative_politics",
            "political_theory",
            "public_administration",
            "international_relations",
        ],
        "applications": ["governance", "diplomacy", "policy"],
    },
    {
        "domain": "sociology",
        "description": "Study of society, social relationships, and institutions.",
        "fields": [
            "urban_sociology",
            "sociology_of_family",
            "criminology",
            "education_sociology",
        ],
        "applications": ["social_research", "policy", "education"],
    },
    {
        "domain": "history",
        "description": "Study of past events, cultures, and civilizations.",
        "fields": [
            "ancient_history",
            "modern_history",
            "military_history",
            "history_of_science",
            "archaeology",
        ],
        "applications": ["teaching", "research", "documentary"],
    },
    {
        "domain": "philosophy",
        "description": "Study of fundamental questions about existence, values, knowledge, reason, and mind.",
        "fields": [
            "ethics",
            "epistemology",
            "metaphysics",
            "logic",
            "aesthetics",
            "philosophy_of_mind",
        ],
        "applications": ["bioethics", "critical_thinking", "research"],
    },
    {
        "domain": "linguistics",
        "description": "Scientific study of language, structure, and meaning.",
        "fields": [
            "syntax",
            "semantics",
            "phonology",
            "morphology",
            "pragmatics",
            "sociolinguistics",
            "computational_linguistics",
        ],
        "applications": ["translation", "NLP", "communication"],
    },
    # Business & Management
    {
        "domain": "business",
        "description": "Organization, operation, and management of enterprises.",
        "fields": [
            "finance",
            "accounting",
            "marketing",
            "management",
            "operations",
            "strategy",
            "human_resources",
            "supply_chain",
        ],
        "applications": ["corporate_management", "entrepreneurship", "consulting"],
    },
    {
        "domain": "finance",
        "description": "Management of money, investments, and financial systems.",
        "fields": [
            "banking",
            "investment_management",
            "insurance",
            "quantitative_finance",
            "fintech",
        ],
        "applications": ["wealth_management", "trading", "personal_finance"],
    },
    {
        "domain": "marketing",
        "description": "Promotion, selling, and distribution of products or services.",
        "fields": [
            "digital_marketing",
            "branding",
            "market_research",
            "advertising",
            "consumer_behavior",
        ],
        "applications": ["sales", "campaigns", "market_analysis"],
    },
    {
        "domain": "supply_chain",
        "description": "Management of the flow of goods, services, and information.",
        "fields": [
            "logistics",
            "procurement",
            "inventory_management",
            "distribution",
            "sourcing",
        ],
        "applications": ["retail", "manufacturing", "transportation"],
    },
    {
        "domain": "human_resources",
        "description": "Management of people within organizations.",
        "fields": [
            "recruitment",
            "talent_management",
            "organizational_development",
            "labor_relations",
        ],
        "applications": ["employee_engagement", "training", "workplace_policy"],
    },
    # Arts & Culture
    {
        "domain": "arts",
        "description": "Creative expression in visual, musical, and performing arts.",
        "fields": [
            "visual_arts",
            "music",
            "theater",
            "dance",
            "film",
            "literature",
            "photography",
            "design",
        ],
        "applications": ["creative_industries", "media", "education"],
    },
    {
        "domain": "media",
        "description": "Production and dissemination of information, news, and entertainment.",
        "fields": ["journalism", "broadcasting", "digital_media", "publishing"],
        "applications": ["content_creation", "public_relations", "news"],
    },
    {
        "domain": "cultural_studies",
        "description": "Examination of cultural practices, beliefs, and institutions.",
        "fields": [
            "anthropology",
            "folklore",
            "religious_studies",
            "gender_studies",
            "ethnic_studies",
        ],
        "applications": ["social_policy", "diversity_initiatives", "museum_curation"],
    },
    # Environment, Sustainability, and Practical Life
    {
        "domain": "environmental_science",
        "description": "Study and management of the natural environment.",
        "fields": [
            "ecology",
            "conservation",
            "climatology",
            "oceanography",
            "sustainability",
        ],
        "applications": [
            "environmental_policy",
            "renewable_energy",
            "resource_management",
        ],
    },
    {
        "domain": "agriculture",
        "description": "Science and practice of cultivating plants and livestock.",
        "fields": [
            "crop_science",
            "horticulture",
            "animal_husbandry",
            "agronomy",
            "agroecology",
        ],
        "applications": ["food_production", "farming_technology", "agribusiness"],
    },
    {
        "domain": "food_science",
        "description": "Study of food production, processing, safety, and nutrition.",
        "fields": [
            "nutrition",
            "food_technology",
            "food_chemistry",
            "sensory_analysis",
        ],
        "applications": ["food_safety", "product_development", "health"],
    },
    # Everyday, Emerging, and Cross-Disciplinary
    {
        "domain": "personal_development",
        "description": "Strategies and tools for self-improvement and well-being.",
        "fields": ["self_help", "meditation", "mindfulness", "coaching", "counseling"],
        "applications": ["therapy", "workshops", "self-education"],
    },
    {
        "domain": "sports",
        "description": "Physical activities, games, and athletics.",
        "fields": [
            "sports_science",
            "coaching",
            "athlete_development",
            "sports_medicine",
        ],
        "applications": ["training", "team_management", "fitness"],
    },
    {
        "domain": "parenting",
        "description": "Raising and nurturing children.",
        "fields": [
            "child_development",
            "education",
            "family_counseling",
            "child_psychology",
        ],
        "applications": ["parenting_advice", "early_education", "family_support"],
    },
    {
        "domain": "travel",
        "description": "Movement of people between distant locations.",
        "fields": ["tourism", "hospitality", "logistics"],
        "applications": ["trip_planning", "travel_advisory", "tourism_management"],
    },
    # Frontier & Bleeding Edge
    {
        "domain": "quantum_computing",
        "description": "Computational systems based on quantum mechanics.",
        "fields": ["quantum_algorithms", "quantum_hardware", "quantum_cryptography"],
        "applications": ["computation", "encryption", "simulation"],
    },
    {
        "domain": "blockchain",
        "description": "Distributed ledger technology and decentralized systems.",
        "fields": ["cryptocurrencies", "smart_contracts", "decentralized_finance"],
        "applications": ["finance", "supply_chain", "digital_identity"],
    },
    {
        "domain": "space_science",
        "description": "Study and exploration of outer space.",
        "fields": ["space_exploration", "planetary_science", "astrophysics"],
        "applications": ["space_missions", "satellite_tech", "astrophysics_research"],
    },
    {
        "domain": "consciousness_studies",
        "description": "Interdisciplinary study of the mind, awareness, and subjective experience.",
        "fields": [
            "philosophy_of_mind",
            "neuroscience",
            "psychology",
            "artificial_consciousness",
        ],
        "applications": ["AI_research", "cognitive_science", "mindfulness"],
    },
    # Meta and General
    {
        "domain": "interdisciplinary",
        "description": "Cross-domain and integrative approaches to knowledge.",
        "fields": [
            "systems_thinking",
            "complexity_science",
            "knowledge_management",
            "policy_design",
        ],
        "applications": ["innovation", "systems_engineering", "meta_research"],
    },
    {
        "domain": "general_knowledge",
        "description": "All cross-disciplinary or uncategorized knowledge.",
        "fields": [],
        "applications": ["trivia", "interdisciplinary_research", "knowledge_bases"],
    },
]


def get_available_domains() -> List[IsoPromptDomain]:
    """Get a list of available domains."""
    return [IsoPromptDomain.model_validate(domain) for domain in ISOPROMPT_DOMAINS]


def get_default_domain() -> IsoPromptDomain:
    """Get the default domain."""
    domains = get_available_domains()
    default_domain = next(
        (domain for domain in domains if domain.domain == DEFAULT_DOMAIN), None
    )
    if default_domain is None:
        raise ValueError(
            f"Default domain '{DEFAULT_DOMAIN}' not found in available domains."
        )
    return default_domain


def is_domain_valid(domain: str) -> bool:
    """Check if a domain is valid."""
    domains = get_available_domains()
    return any(d.domain == domain for d in domains)


def get_available_domain_names() -> List[str]:
    """Get a list of available domain names."""
    domains = get_available_domains()
    return [domain.domain for domain in domains]
