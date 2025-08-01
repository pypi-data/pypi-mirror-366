from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Type, TypeVar

from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

T = TypeVar("T", bound="Snippet")


class Language(StrEnum):
    PYTHON = "PYTHON"
    JAVA = "JAVA"
    RUST = "RUST"
    GO = "GO"


class SnippetTagLink(SQLModel, table=True):  # type: ignore[call-arg]
    snippet_id: int | None = Field(
        default=None, primary_key=True, foreign_key="snippet.id"
    )
    tag_id: int | None = Field(default=None, primary_key=True, foreign_key="tag.id")


class SnippetBase(SQLModel):
    title: str
    code: str = Field(sa_column=Column(Text))
    description: str | None = None
    language: Language
    favorite: bool = False


class Snippet(SnippetBase, table=True):  # type: ignore[call-arg]
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime | None = None

    tags: list["Tag"] = Relationship(
        back_populates="snippets",
        link_model=SnippetTagLink,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "order_by": "Tag.name",
        },
    )

    @classmethod
    def create(cls: Type[T], **kwargs: Any) -> T:
        snippet: Snippet = cls(**kwargs)
        return snippet


class SnippetCreate(SnippetBase):
    pass


class SnippetPublic(SnippetBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    tags: list["TagPublic"]


class TagBase(SQLModel):
    name: str = Field(min_length=1, max_length=20)


class Tag(TagBase, table=True):  # type: ignore[call-arg]
    id: int | None = Field(default=None, primary_key=True)

    snippets: list["Snippet"] = Relationship(
        back_populates="tags",
        link_model=SnippetTagLink,
    )


class TagPublic(TagBase):
    id: int


# Generic message
class Message(SQLModel):
    detail: str


class RunResult(SQLModel):
    output: str


def main() -> None:  # pragma: no cover
    # create engine
    engine = create_engine("sqlite:///snipster.db", echo=True)
    # populate db and table
    SQLModel.metadata.create_all(engine)
    # add a snippet
    with Session(engine) as session:
        fastapi_tag = Tag(name="fastapi")
        pydantic_tag = Tag(name="pydantic")
        uv_tag = Tag(name="uv")

        snippet = Snippet(
            title="Test create snippet",
            code="print('FastAPI, pydantic and uv are awesome')",
            description="This is an example of using SQLModel",
            language=Language.RUST,
            tags=[fastapi_tag, pydantic_tag, uv_tag],
        )
        session.add(snippet)
        session.commit()
        session.refresh(snippet)

    with Session(engine) as session:
        snippets = session.exec(select(Snippet)).all()
        for snippet in snippets:
            print(snippet)


if __name__ == "__main__":  # pragma: no cover
    main()
