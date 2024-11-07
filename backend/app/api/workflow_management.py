from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..schemas.workflow_schemas import (
    WorkflowNodeCoordinatesSchema,
    WorkflowCreateRequestSchema,
    WorkflowNodeSchema,
    WorkflowResponseSchema,
    WorkflowDefinitionSchema,
)
from ..database import get_db
from ..models.workflow_model import WorkflowModel as WorkflowModel

router = APIRouter()


def create_a_new_workflow_definition() -> WorkflowDefinitionSchema:
    return WorkflowDefinitionSchema(
        nodes=[
            WorkflowNodeSchema(
                id="input_node",
                node_type="InputNode",
                coordinates=WorkflowNodeCoordinatesSchema(x=100, y=100),
                config={},
            )
        ],
        links=[],
    )


@router.post(
    "/", response_model=WorkflowResponseSchema, description="Create a new workflow"
)
def create_workflow(
    workflow_request: WorkflowCreateRequestSchema, db: Session = Depends(get_db)
) -> WorkflowResponseSchema:
    if not workflow_request.definition:
        workflow_request.definition = create_a_new_workflow_definition()
    new_workflow = WorkflowModel(
        name=workflow_request.name or "Untitled Workflow",
        description=workflow_request.description,
        definition=(workflow_request.definition.model_dump()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)
    return new_workflow


@router.put(
    "/{workflow_id}/",
    response_model=WorkflowResponseSchema,
    description="Update a workflow",
)
def update_workflow(
    workflow_id: str,
    workflow_def: WorkflowDefinitionSchema,
    db: Session = Depends(get_db),
) -> WorkflowResponseSchema:
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    workflow.definition = workflow_def.model_dump()
    workflow.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(workflow)
    return workflow


@router.get(
    "/", response_model=List[WorkflowResponseSchema], description="List all workflows"
)
def list_workflows(db: Session = Depends(get_db)):
    workflows = db.query(WorkflowModel).all()
    return workflows


@router.get(
    "/{workflow_id}/",
    response_model=WorkflowResponseSchema,
    description="Get a workflow by ID",
)
def get_workflow(
    workflow_id: str, db: Session = Depends(get_db)
) -> WorkflowResponseSchema:
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
