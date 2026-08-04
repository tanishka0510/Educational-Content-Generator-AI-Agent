from schemas.workflow import *

workflow = ExecutionPlan(

    routing=RoutingDecision(

        workflow_info=WorkflowInfo(

            intent=Intent.QUIZ,

            workflow=WorkflowCategory.EDUCATIONAL

        ),

        selected_agents=[
            AgentName.EDUCATIONAL
        ]

    ),

    execution_strategy=ExecutionStrategy.SINGLE

)

print(workflow.model_dump_json(indent=4))