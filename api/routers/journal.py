from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from api.db.postgres_sante import get_session_sante
from api.schemas.auth import CurrentUser
from api.schemas.sante import JournalCreate, JournalRead

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post("", response_model=JournalRead, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    body: JournalCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_session_sante),
):
    id_anonyme = str(current_user.id_anonyme)
    row = db.execute(
        text(
            """
            INSERT INTO journal_alimentaire
                (id_anonyme, horodatage, nom_repas, type_repas, total_calories, total_proteines, total_glucides, total_lipides)
            VALUES
                (:id_anonyme, :horodatage, :nom_repas, :type_repas, :total_calories, :total_proteines, :total_glucides, :total_lipides)
            RETURNING id_repas, id_anonyme, horodatage, nom_repas, type_repas, total_calories, total_proteines, total_glucides, total_lipides
            """
        ),
        {
            "id_anonyme": id_anonyme,
            "horodatage": body.horodatage,
            "nom_repas": body.nom_repas,
            "type_repas": body.type_repas,
            "total_calories": body.total_calories,
            "total_proteines": body.total_proteines,
            "total_glucides": body.total_glucides,
            "total_lipides": body.total_lipides,
        },
    ).fetchone()
    db.commit()
    return JournalRead.model_validate(dict(row._mapping))

