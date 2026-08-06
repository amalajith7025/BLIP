from app.investigation_framework.schemas import InvestigationStageName
from app.investigation_framework.services import (
    build_universal_stages,
    create_universal_investigation,
)


def test_build_universal_stages_has_canonical_order():
    stages = build_universal_stages()

    assert len(stages) == 6
    assert [stage.execution_order for stage in stages] == [1, 2, 3, 4, 5, 6]
    assert [stage.name for stage in stages] == [
        InvestigationStageName.UNDERSTAND,
        InvestigationStageName.OBSERVE,
        InvestigationStageName.EXPLAIN,
        InvestigationStageName.VALIDATE,
        InvestigationStageName.RECOMMEND,
        InvestigationStageName.LEARN,
    ]


def test_create_universal_investigation_hydrates_stage_inputs():
    investigation = create_universal_investigation(
        name="Q4 Revenue Drop",
        stage_inputs={
            InvestigationStageName.UNDERSTAND: {"dataset_name": "finance_q4.csv"},
        },
    )

    assert investigation.name == "Q4 Revenue Drop"
    assert len(investigation.stages) == 6
    assert investigation.stages[0].inputs == {"dataset_name": "finance_q4.csv"}
    assert investigation.stages[1].inputs == {}