from app.analysis.capabilities.schemas import BusinessPurpose, SemanticPrimitive
from app.investigation_framework.schemas import InvestigationStageName

from .schemas import BusinessGoal


def default_business_goals() -> list[BusinessGoal]:
    """
    Universal, domain-independent starting ontology for investigation intent.
    """

    shared_stages = [
        InvestigationStageName.UNDERSTAND,
        InvestigationStageName.OBSERVE,
        InvestigationStageName.EXPLAIN,
        InvestigationStageName.VALIDATE,
        InvestigationStageName.RECOMMEND,
    ]

    return [
        BusinessGoal(
            goal_id="goal_explain_decline",
            name="Explain Decline",
            description="Understand why performance reduced over time or across cohorts.",
            business_purpose=BusinessPurpose.DIAGNOSE,
            common_business_questions=[
                "Which factors are most associated with recent decline?",
                "Is decline concentrated in specific segments or periods?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_descriptive_statistics",
                "cap_correlation_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_regression_analysis",
                "cap_outlier_detection",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.CATEGORICAL,
                SemanticPrimitive.DATETIME,
            ],
            tags=["performance", "diagnosis", "decline"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_explain_growth",
            name="Explain Growth",
            description="Identify drivers behind observed performance improvement.",
            business_purpose=BusinessPurpose.DIAGNOSE,
            common_business_questions=[
                "What changed when growth accelerated?",
                "Which variables move most with growth outcomes?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_descriptive_statistics",
                "cap_correlation_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_regression_analysis",
                "cap_random_forest",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.CATEGORICAL,
                SemanticPrimitive.DATETIME,
            ],
            tags=["performance", "diagnosis", "growth"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_compare_performance",
            name="Compare Performance",
            description="Compare outcomes between groups, entities, or periods.",
            business_purpose=BusinessPurpose.COMPARE,
            common_business_questions=[
                "Are outcomes different between groups?",
                "Which segment outperforms peers consistently?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_descriptive_statistics",
                "cap_ttest_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_chi_square_analysis",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.CATEGORICAL,
            ],
            tags=["comparison", "benchmarking"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_rank_entities",
            name="Rank Entities",
            description="Rank entities using comparable performance measures.",
            business_purpose=BusinessPurpose.DESCRIBE,
            common_business_questions=[
                "Which entities are top and bottom performers?",
                "How stable is ranking across periods?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_descriptive_statistics",
            ],
            optional_analytical_capabilities=[
                "cap_frequency_distribution",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.IDENTIFIER,
                SemanticPrimitive.CATEGORICAL,
            ],
            tags=["ranking", "prioritization"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_segment_population",
            name="Segment Population",
            description="Split a mixed population into coherent groups for analysis.",
            business_purpose=BusinessPurpose.CLUSTER,
            common_business_questions=[
                "What natural segments exist in the population?",
                "How distinct are segment behaviors?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_frequency_distribution",
            ],
            optional_analytical_capabilities=[
                "cap_random_forest",
                "cap_correlation_analysis",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.CATEGORICAL,
                SemanticPrimitive.BOOLEAN,
            ],
            tags=["segmentation", "population"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_detect_anomalies",
            name="Detect Anomalies",
            description="Find atypical patterns that deserve investigation.",
            business_purpose=BusinessPurpose.DETECT_ANOMALY,
            common_business_questions=[
                "Which records are statistically unusual?",
                "Are anomalies concentrated by segment or time?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_outlier_detection",
            ],
            optional_analytical_capabilities=[
                "cap_descriptive_statistics",
                "cap_correlation_analysis",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.DATETIME,
                SemanticPrimitive.CATEGORICAL,
            ],
            tags=["risk", "quality", "anomaly"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_discover_relationships",
            name="Discover Relationships",
            description="Reveal associations between variables and entity traits.",
            business_purpose=BusinessPurpose.DISCOVER_ASSOCIATION,
            common_business_questions=[
                "Which variables move together?",
                "Are categorical features associated?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_correlation_analysis",
                "cap_chi_square_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_regression_analysis",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.CATEGORICAL,
                SemanticPrimitive.BOOLEAN,
            ],
            tags=["relationships", "associations"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_forecast_trends",
            name="Forecast Trends",
            description="Project likely future trajectory from historical signals.",
            business_purpose=BusinessPurpose.FORECAST,
            common_business_questions=[
                "What is the expected trajectory next period?",
                "Which factors most influence projected trend?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_regression_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_descriptive_statistics",
                "cap_random_forest",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.DATETIME,
            ],
            tags=["forecast", "trend"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_validate_hypothesis",
            name="Validate Hypothesis",
            description="Test whether a stated assumption is supported by data.",
            business_purpose=BusinessPurpose.VALIDATE_ASSUMPTION,
            common_business_questions=[
                "Is the observed effect statistically meaningful?",
                "Should we reject or retain the hypothesis?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_ttest_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_chi_square_analysis",
                "cap_outlier_detection",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.CATEGORICAL,
                SemanticPrimitive.BOOLEAN,
            ],
            tags=["hypothesis", "validation"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_measure_change",
            name="Measure Change",
            description="Quantify differences between baseline and comparison states.",
            business_purpose=BusinessPurpose.COMPARE,
            common_business_questions=[
                "How much did performance change?",
                "Is the change statistically defensible?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_descriptive_statistics",
                "cap_ttest_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_regression_analysis",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.DATETIME,
                SemanticPrimitive.CATEGORICAL,
            ],
            tags=["measurement", "change"],
            version="1.0.0",
        ),
        BusinessGoal(
            goal_id="goal_optimize_performance",
            name="Optimize Performance",
            description="Prioritize controllable factors that improve outcomes.",
            business_purpose=BusinessPurpose.DIAGNOSE,
            common_business_questions=[
                "Which levers have strongest association with outcomes?",
                "What combination of factors improves performance most?",
            ],
            applicable_investigation_stages=shared_stages,
            required_analytical_capabilities=[
                "cap_regression_analysis",
                "cap_correlation_analysis",
            ],
            optional_analytical_capabilities=[
                "cap_random_forest",
                "cap_outlier_detection",
            ],
            supported_semantic_primitives=[
                SemanticPrimitive.NUMERIC,
                SemanticPrimitive.CATEGORICAL,
                SemanticPrimitive.BOOLEAN,
                SemanticPrimitive.DATETIME,
            ],
            tags=["optimization", "performance"],
            version="1.0.0",
        ),
    ]