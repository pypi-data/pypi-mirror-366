"""
IsoPrompt - AI-powered prompt optimization tool.
Modes are the various ways IsoPrompt can optimize prompts.
"""

from typing import List

from .models import IsoPromptMode

DEFAULT_MODE = "simple"

ISOPROMPT_MODES = [
    # --- FOUNDATION MODES ---
    {
        "mode": "simple",
        "description": "Clear, direct prompts for straightforward tasks.",
        "usage": "Use for basic Q&A, instructions, or simple requests.",
        "capabilities": ["Directness", "Speed"],
        "strictness": "low",
        "require_citations": False,
        "output_formats": ["plain", "markdown"],
        "industries": ["all"],
        "topics": ["FAQ", "how-to", "summaries", "questions"],
    },
    {
        "mode": "reasoning",
        "description": "Step-by-step logical thinking and problem-solving.",
        "usage": "Use for math, logic, or multi-step reasoning tasks.",
        "capabilities": ["Logic", "Proof", "Calculation"],
        "strictness": "medium",
        "require_citations": False,
        "output_formats": ["list", "numbered_steps", "markdown"],
        "industries": ["education", "finance", "engineering", "all"],
        "topics": ["math problems", "case analysis", "root cause"],
    },
    {
        "mode": "chain_of_thought",
        "description": "Detailed, explicit reasoning steps before the answer.",
        "usage": "Use for complex analysis, diagnostics, or planning.",
        "capabilities": ["Structured Logic", "Transparency"],
        "strictness": "high",
        "require_citations": False,
        "output_formats": ["numbered_steps", "blockquote", "markdown"],
        "industries": ["consulting", "medicine", "software", "all"],
        "topics": ["diagnosis", "strategic planning", "debugging"],
    },
    {
        "mode": "creative",
        "description": "Innovative, imaginative, and out-of-the-box thinking.",
        "usage": "Use for brainstorming, ideation, or content creation.",
        "capabilities": ["Creativity", "Lateral Thinking"],
        "strictness": "variable",
        "require_citations": False,
        "output_formats": ["plain", "story", "list", "markdown"],
        "industries": ["marketing", "media", "product design", "education", "all"],
        "topics": ["ad copy", "storytelling", "campaign ideas"],
    },
    {
        "mode": "analytical",
        "description": "Thorough analysis and detailed examination.",
        "usage": "Use for reports, audits, or in-depth reviews.",
        "capabilities": ["Analysis", "Breakdown", "Structured Review"],
        "strictness": "high",
        "require_citations": True,
        "output_formats": ["report", "table", "list", "markdown"],
        "industries": [
            "finance",
            "research",
            "operations",
            "mathematics",
            "computer science",
            "business",
            "strategy",
            "product management",
            "law",
            "science",
            "engineering",
            "all",
        ],
        "topics": [
            "financial analysis",
            "market research",
            "process review",
            "scientific analysis",
        ],
    },
    {
        "mode": "instructional",
        "description": "Step-by-step guides and teaching content.",
        "usage": "Use for tutorials, onboarding, or training.",
        "capabilities": ["Teaching", "Process Decomposition"],
        "strictness": "medium",
        "require_citations": False,
        "output_formats": ["step_list", "numbered_steps", "markdown"],
        "industries": ["education", "HR", "customer support", "technology", "all"],
        "topics": ["tutorials", "onboarding", "user guides"],
    },
    {
        "mode": "conversational",
        "description": "Natural, human-like dialogue and chat.",
        "usage": "Use for chatbots, customer service, or interactive agents.",
        "capabilities": ["Dialogue", "Context Retention"],
        "strictness": "low",
        "require_citations": False,
        "output_formats": ["chat", "plain", "markdown"],
        "industries": ["customer support", "retail", "healthcare", "education", "all"],
        "topics": ["chatbots", "virtual assistants", "FAQ bots"],
    },
    {
        "mode": "persuasive",
        "description": "Prompts designed to convince or influence.",
        "usage": "Use for sales, negotiation, or marketing copy.",
        "capabilities": ["Rhetoric", "Sales", "Influence"],
        "strictness": "variable",
        "require_citations": False,
        "output_formats": ["plain", "ad_copy", "pitch", "markdown"],
        "industries": ["sales", "marketing", "politics", "business", "all"],
        "topics": ["sales pitches", "ad copy", "negotiation"],
    },
    {
        "mode": "summarization",
        "description": "Condense information into concise summaries.",
        "usage": "Use for executive summaries, abstracts, or TL;DRs.",
        "capabilities": ["Abstraction", "Compression", "Synthesis"],
        "strictness": "medium",
        "require_citations": True,
        "output_formats": ["summary", "table", "markdown", "bullet_list"],
        "industries": ["media", "research", "business", "all"],
        "topics": ["news summaries", "meeting notes", "research abstracts"],
    },
    {
        "mode": "critical_review",
        "description": "Critical analysis and constructive feedback.",
        "usage": "Use for peer review, code review, or editorial feedback.",
        "capabilities": ["Critical Thinking", "Evaluation"],
        "strictness": "high",
        "require_citations": True,
        "output_formats": ["review_report", "inline_comments", "markdown"],
        "industries": [
            "software",
            "publishing",
            "academia",
            "science",
            "engineering",
            "all",
        ],
        "topics": ["code review", "manuscript review", "product feedback"],
    },
    # --- RESEARCH, SCIENTIFIC & ADVANCED MODES ---
    {
        "mode": "socratic",
        "description": "Rigorous, question-driven exploration and adversarial thinking.",
        "usage": "Expose flaws, challenge assumptions, improve robustness.",
        "capabilities": ["Adversarial", "Philosophical", "Assumption Testing"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["dialogue", "qa", "markdown"],
        "industries": [
            "research",
            "academia",
            "policy",
            "science",
            "philosophy",
            "all",
        ],
        "topics": ["bias detection", "robustness", "debate", "risk analysis"],
    },
    {
        "mode": "comparative",
        "description": "Systematic comparison of alternatives with clear criteria.",
        "usage": "Technology, literature, product, policy comparisons.",
        "capabilities": ["Contrast", "Decision Making"],
        "strictness": "high",
        "require_citations": True,
        "output_formats": ["table", "pros_cons", "list", "markdown"],
        "industries": ["consulting", "research", "engineering", "product", "all"],
        "topics": ["literature reviews", "tech comparisons", "decision matrix"],
    },
    {
        "mode": "synthesis",
        "description": "Combine multiple sources or perspectives into unified insight.",
        "usage": "Meta-research, consensus building, integrated reviews.",
        "capabilities": ["Integration", "Big Picture", "Synthesis"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["integrated_report", "summary", "table", "markdown"],
        "industries": ["research", "product", "science", "strategy", "academia", "all"],
        "topics": ["meta-analysis", "state-of-the-art reports", "consensus finding"],
    },
    {
        "mode": "critical_appraisal",
        "description": "Formal evaluation of evidence using scientific frameworks (e.g., GRADE, PRISMA, CASP).",
        "usage": "Systematic reviews, risk assessments, scientific critique.",
        "capabilities": ["Evidence Evaluation", "Reliability Assessment"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["appraisal_table", "formal_report", "markdown"],
        "industries": ["medicine", "academia", "policy", "science", "all"],
        "topics": ["systematic review", "evidence appraisal", "quality scoring"],
    },
    {
        "mode": "data_extraction",
        "description": "Extract facts, statistics, and entities from complex text or data.",
        "usage": "Knowledge base building, entity extraction, data curation.",
        "capabilities": [
            "Fact Extraction",
            "Entity Mining",
            "Knowledge Graph Creation",
        ],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["table", "csv", "json", "markdown"],
        "industries": ["data science", "ml", "legal", "research", "academia", "all"],
        "topics": ["entity extraction", "statistical extraction", "literature mining"],
    },
    {
        "mode": "meta_analysis",
        "description": "Aggregate and statistically analyze results from multiple sources or studies.",
        "usage": "Scientific synthesis, medical trials, evidence integration.",
        "capabilities": ["Aggregation", "Statistical Synthesis"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["statistical_report", "table", "summary", "markdown"],
        "industries": [
            "medicine",
            "science",
            "social science",
            "market research",
            "all",
        ],
        "topics": ["meta-analysis", "study aggregation", "evidence synthesis"],
    },
    {
        "mode": "risk_analysis",
        "description": "Identify, articulate, and evaluate risks, uncertainties, and assumptions.",
        "usage": "Proposals, technical plans, research, strategy.",
        "capabilities": ["Risk Scanning", "Scenario Analysis"],
        "strictness": "high",
        "require_citations": True,
        "output_formats": ["risk_table", "list", "markdown"],
        "industries": ["engineering", "finance", "policy", "R&D", "science", "all"],
        "topics": [
            "risk assessment",
            "assumption mapping",
            "uncertainty quantification",
        ],
    },
    {
        "mode": "method_design",
        "description": "Design and critique research methods, study designs, and protocols.",
        "usage": "Research planning, experimental protocol development, grant writing.",
        "capabilities": ["Design", "Protocol", "Framework Evaluation"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["protocol_doc", "table", "markdown"],
        "industries": ["academia", "R&D", "clinical trials", "science", "all"],
        "topics": ["study design", "experimental protocols", "methodology review"],
    },
    {
        "mode": "hypothesis_generation",
        "description": "Generate, evaluate, and refine hypotheses or ideas for research and innovation.",
        "usage": "Scientific brainstorming, product R&D, invention.",
        "capabilities": ["Ideation", "Hypothesis Framing"],
        "strictness": "medium",
        "require_citations": False,
        "output_formats": ["list", "table", "markdown"],
        "industries": ["research", "science", "product", "startups", "all"],
        "topics": ["hypothesis", "ideation", "discovery"],
    },
    # --- META, SELF-IMPROVEMENT & GOVERNANCE MODES ---
    {
        "mode": "provenance_tracking",
        "description": "Track sources, confidence levels, and attributions for all facts and outputs.",
        "usage": "Research traceability, scientific rigor, regulatory compliance.",
        "capabilities": ["Traceability", "Source Attribution"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["annotated", "citation_list", "json", "markdown"],
        "industries": ["research", "law", "compliance", "science", "all"],
        "topics": ["source tracking", "evidence confidence", "regulatory evidence"],
    },
    {
        "mode": "reproducibility_check",
        "description": "Assess whether outputs are reproducible, verifiable, and based on transparent reasoning.",
        "usage": "Meta-research, peer review, quality assurance.",
        "capabilities": ["Reproducibility", "Verification"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["reproducibility_report", "table", "markdown"],
        "industries": ["academia", "science", "software", "all"],
        "topics": ["reproducibility", "verification", "replication"],
    },
    {
        "mode": "bias_audit",
        "description": "Surface and analyze potential sources of bias and hidden assumptions in data, models, or outputs.",
        "usage": "Bias detection, audit reports, trustworthiness analysis.",
        "capabilities": ["Bias Detection", "Assumption Mapping"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["bias_report", "list", "markdown"],
        "industries": ["research", "policy", "ethics", "science", "all"],
        "topics": ["bias", "audit", "assumption surfacing"],
    },
    {
        "mode": "self_critique",
        "description": "Automatically critiques and grades its own output for accuracy, completeness, and bias.",
        "usage": "Trustworthy superintelligent self-improvement and error catching.",
        "capabilities": ["Self-Evaluation", "Meta-Reasoning"],
        "strictness": "ultra",
        "require_citations": True,
        "output_formats": ["review_report", "score", "list", "markdown"],
        "industries": ["all"],
        "topics": ["output critique", "self-reflection", "model audit"],
    },
    {
        "mode": "redundancy_verification",
        "description": "Requires multiple independent output generations to converge before returning an answer (ensemble/consensus mode).",
        "usage": "Safety-critical, ensemble-verified outputs.",
        "capabilities": ["Redundancy", "Safety", "Consensus"],
        "strictness": "ultra",
        "require_citations": True,
        "output_formats": ["consensus_report", "table", "markdown"],
        "industries": [
            "critical infrastructure",
            "science",
            "safety",
            "compliance",
            "all",
        ],
        "topics": ["redundancy", "verification", "ensemble methods"],
    },
    {
        "mode": "confidence_quantification",
        "description": "Quantifies the model's confidence and uncertainty for every major claim or answer.",
        "usage": "Decision support, research, high-stakes automation.",
        "capabilities": ["Uncertainty Quantification", "Probability"],
        "strictness": "very_high",
        "require_citations": True,
        "output_formats": ["table", "json", "markdown"],
        "industries": ["research", "science", "medicine", "governance", "all"],
        "topics": ["confidence", "uncertainty", "probability estimation"],
    },
]


def get_available_modes() -> List[IsoPromptMode]:
    """Get a list of available modes.

    Returns:
        A list of IsoPromptMode objects.
    """
    return [IsoPromptMode.model_validate(mode) for mode in ISOPROMPT_MODES]


def get_default_mode() -> IsoPromptMode:
    """Get the default mode.

    Returns:
        A IsoPromptMode object.
    """
    modes = get_available_modes()
    default_mode = next((mode for mode in modes if mode.mode == DEFAULT_MODE), None)
    if default_mode is None:
        raise ValueError(f"Default mode '{DEFAULT_MODE}' not found in available modes.")
    return default_mode


def is_mode_valid(mode: str) -> bool:
    """
    Check if a mode is valid.

    Args:
        mode: The mode to check.

    Returns:
        True if the mode is valid, False otherwise.
    """
    modes = get_available_modes()
    return any(m.mode == mode for m in modes)


def get_available_mode_names() -> List[str]:
    """
    Get a list of available mode names.

    Args:
        None

    Returns:
        A list of mode names.
    """
    modes = get_available_modes()
    return [mode.mode for mode in modes]
