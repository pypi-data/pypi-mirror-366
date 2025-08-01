import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Sequence

from decouple import config
from rapidfuzz import fuzz
from sqlalchemy.orm import joinedload
from sqlmodel import Session, or_, select

from .exceptions import SnippetNotFoundError
from .models import Language, Snippet, SnippetTagLink, Tag

# threshold score for fuzzy search, tune it if needed
THRESHOLD: int = config("THRESHOLD", default=60, cast=int)


class SnippetRepository(ABC):  # pragma: no cover
    @abstractmethod
    def add(self, snippet: Snippet) -> None:
        pass

    @abstractmethod
    def list(self) -> Sequence[Snippet]:
        pass

    @abstractmethod
    def get(self, snippet_id: int) -> Snippet | None:
        pass

    @abstractmethod
    def delete(self, snippet_id: int) -> None:
        pass

    @abstractmethod
    def tag(
        self, snippet_id: int, /, *targs: str, remove: bool = False, sort: bool = True
    ) -> None:
        pass

    @abstractmethod
    def toggle_favorite(self, snippet_id: int) -> None:
        pass

    @abstractmethod
    def search(
        self, term: str, *, language: Language | None = None, fuzzy: bool = False
    ) -> Sequence[Snippet]:
        pass

    @staticmethod
    def _update_tags(
        snippet: Snippet,
        tag_names: set[str],
        get_or_create_tag: Callable[[str], Tag],
        remove: bool,
        sort: bool,
    ) -> None:
        if remove:
            snippet.tags = [tag for tag in snippet.tags if tag.name not in tag_names]
        else:
            existing_tag_names = {tag.name for tag in snippet.tags}
            for name in tag_names:
                if name not in existing_tag_names:
                    tag = get_or_create_tag(name)
                    snippet.tags.append(tag)

        if sort:
            snippet.tags.sort(key=lambda t: t.name)
        snippet.updated_at = datetime.now(UTC)

    @staticmethod
    def _update_favorite(snippet: Snippet) -> None:
        snippet.favorite = not snippet.favorite
        snippet.updated_at = datetime.now(UTC)

    # 🔍 Search Utilities
    @staticmethod
    def _validate_search_term(term: str) -> str:
        """
        Validates and normalizes a search term.

        Raises:
            ValueError: If the search term is empty.

        Returns:
            str: The lowercase search term for case-insensitive comparison.
        """
        if not term:
            raise ValueError("The term cannot be empty")
        return term.lower()

    @staticmethod
    def _build_searchable_text(snippet: Snippet) -> str:
        """
        Constructs a searchable text string from a Snippet.

        The result includes the snippet's title, code, description,
        and all associated tag names.

        Args:
            snippet (Snippet): The snippet to convert.

        Returns:
            str: A lowercased concatenated string of searchable fields.
        """
        parts = [
            snippet.title,
            snippet.code,
            snippet.description or "",
            " ".join(tag.name for tag in snippet.tags),
        ]
        return " ".join(parts).lower()

    @staticmethod
    def _filter_by_language(
        snippets: Sequence[Snippet], language: Language | None
    ) -> Sequence[Snippet]:
        """
        Filters a sequence of snippets by language, if specified.

        Args:
            snippets (Sequence[Snippet]): The list of snippets to filter.
            language (Language | None): The desired language, or None for no filtering.

        Returns:
            Sequence[Snippet]: Filtered list of snippets.
        """
        if not language:
            return snippets
        return [s for s in snippets if s.language == language]

    @staticmethod
    def _fuzzy_match(term_lower: str, snippets: Sequence[Snippet]) -> Sequence[Snippet]:
        """
        Performs a fuzzy match of snippets based on the partial_ratio metric.

        Snippets with a fuzzy score greater than or equal to THRESHOLD are included.
        Results are sorted by descending match score.

        Args:
            term_lower (str): The lowercased search term.
            snippets (Sequence[Snippet]): Candidate snippets to match.

        Returns:
            Sequence[Snippet]: Matched and ranked snippets.
        """
        results = []
        for snippet in snippets:
            searchable_text = SnippetRepository._build_searchable_text(snippet)
            score = fuzz.partial_ratio(term_lower, searchable_text)
            if score >= THRESHOLD:
                results.append((score, snippet))
        results.sort(key=lambda x: x[0], reverse=True)
        return [snippet for _, snippet in results]

    @staticmethod
    def _exact_match(term_lower: str, snippets: Sequence[Snippet]) -> Sequence[Snippet]:
        """
        Performs an exact (case-insensitive substring) match across snippet fields.

        Matches if the term appears in any of:
            - title
            - code
            - description
            - tag names

        Args:
            term_lower (str): The lowercased search term.
            snippets (Sequence[Snippet]): Candidate snippets.

        Returns:
            Sequence[Snippet]: All snippets that contain the term.
        """

        def matches(snippet: Snippet) -> bool:
            in_title = term_lower in snippet.title.lower()
            in_code = term_lower in snippet.code.lower()
            in_description = (
                bool(snippet.description) and term_lower in snippet.description.lower()
            )
            in_tags = any(term_lower in tag.name.lower() for tag in snippet.tags)
            return in_title or in_code or in_description or in_tags

        return [s for s in snippets if matches(s)]


class InMemorySnippetRepo(SnippetRepository):
    def __init__(self) -> None:
        self._snippets: dict[int, Snippet] = {}
        self._tags_by_name: dict[str, Tag] = {}
        self._next_id = 1

    def add(self, snippet: Snippet) -> None:
        if snippet.id is None:
            snippet.id = self._next_id
            self._next_id += 1
        self._snippets[snippet.id] = snippet

    def list(self) -> Sequence[Snippet]:
        return list(self._snippets.values())

    def get(self, snippet_id: int) -> Snippet | None:
        return self._snippets.get(snippet_id)

    def delete(self, snippet_id: int) -> None:
        if snippet_id not in self._snippets:
            raise SnippetNotFoundError
        self._snippets.pop(snippet_id)

    def tag(
        self, snippet_id: int, /, *targs: str, remove: bool = False, sort: bool = True
    ) -> None:
        snippet = self.get(snippet_id)
        if snippet is None:
            raise SnippetNotFoundError

        tag_names = {t.strip() for t in targs if t.strip()}
        if not tag_names:
            return

        def get_or_create(name: str) -> Tag:
            tag = self._tags_by_name.get(name)
            if tag is None:
                tag = Tag(name=name)
                self._tags_by_name[name] = tag
            return tag

        self._update_tags(snippet, tag_names, get_or_create, remove, sort)

    def toggle_favorite(self, snippet_id: int) -> None:
        snippet = self.get(snippet_id)
        if snippet is None:
            raise SnippetNotFoundError
        self._update_favorite(snippet)

    def search(
        self, term: str, *, language: Language | None = None, fuzzy: bool = False
    ) -> Sequence[Snippet]:
        term_lower = self._validate_search_term(term)
        candidates = list(self._snippets.values())
        candidates = self._filter_by_language(candidates, language)

        if fuzzy:
            return self._fuzzy_match(term_lower, candidates)
        return self._exact_match(term_lower, candidates)


class DBSnippetRepo(SnippetRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, snippet: Snippet) -> None:
        self._session.add(snippet)
        self._session.commit()
        self._session.refresh(snippet)

    def list(self) -> Sequence[Snippet]:
        snippets = self._session.exec(select(Snippet)).all()
        return snippets

    def get(self, snippet_id: int) -> Snippet | None:
        snippet = self._session.get(Snippet, snippet_id)
        return snippet

    def delete(self, snippet_id: int) -> None:
        snippet = self._session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError
        self._session.delete(snippet)
        self._session.commit()

    def tag(
        self, snippet_id: int, /, *targs: str, remove: bool = False, sort: bool = True
    ) -> None:
        snippet = self._session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError

        tag_names = {t.strip() for t in targs if t.strip()}
        if not tag_names:
            return

        # Efficiently fetch all existing tags
        stmt = select(Tag).where(Tag.name.in_(tag_names))  # type: ignore[attr-defined]
        result = self._session.exec(stmt).all()
        existing_tags = {tag.name: tag for tag in result}

        def get_or_create(name: str) -> Tag:
            tag = existing_tags.get(name)
            if tag is None:
                tag = Tag(name=name)
                self._session.add(tag)
                self._session.flush()
                existing_tags[name] = tag
            return tag

        # noinspection PyTypeChecker
        self._update_tags(snippet, tag_names, get_or_create, remove, sort)

        # noinspection PyTypeChecker
        self.add(snippet)

    def toggle_favorite(self, snippet_id: int) -> None:
        snippet = self.get(snippet_id)
        if snippet is None:
            raise SnippetNotFoundError
        self._update_favorite(snippet)
        self.add(snippet)

    def search(
        self,
        term: str,
        *,
        language: Language | None = None,  # still kept here for interface compatibility
        fuzzy: bool = False,
    ) -> Sequence[Snippet]:
        term_lower = self._validate_search_term(term)
        term_like = f"%{term_lower}%"

        # Base SQL query with joinedload for tags
        # noinspection PyTypeChecker
        stmt = select(Snippet).options(joinedload(Snippet.tags))

        if not fuzzy:
            # noinspection PyTypeChecker
            stmt = stmt.where(
                or_(
                    Snippet.title.ilike(term_like),  # type: ignore[attr-defined]
                    Snippet.code.ilike(term_like),  # type: ignore[attr-defined]
                    Snippet.description.ilike(term_like),  # type: ignore[attr-defined]
                    Snippet.id.in_(  # type: ignore[attr-defined]
                        select(SnippetTagLink.snippet_id)
                        .join(Tag, Tag.id == SnippetTagLink.tag_id)
                        .where(Tag.name.ilike(term_like))  # type: ignore[attr-defined]
                    ),
                )
            )

        if language:
            stmt = stmt.where(Snippet.language == language)

        # Run query
        candidates = self._session.exec(stmt).unique().all()

        if not fuzzy:
            return candidates

        # Fuzzy match using rapidfuzz
        return self._fuzzy_match(term_lower, candidates)


class JSONSnippetRepo(SnippetRepository):
    def __init__(self, json_file_path: Path) -> None:
        self._path = json_file_path
        self._snippets: dict[int, Snippet] = {}
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return

        with open(self._path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            tag_names = item.pop("tags", [])
            snippet = Snippet.model_validate(item)
            snippet.tags = [Tag(name=name) for name in tag_names]
            self._snippets[snippet.id] = snippet
            self._next_id = max(self._next_id, snippet.id + 1)

    def _save(self) -> None:
        data = []
        for snippet in self._snippets.values():
            snippet_dict = snippet.model_dump(mode="json", exclude={"tags"})
            snippet_dict["tags"] = [tag.name for tag in snippet.tags]
            data.append(snippet_dict)

        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def add(self, snippet: Snippet) -> None:
        if snippet.id is None:
            snippet.id = self._next_id
            self._next_id += 1
        self._snippets[snippet.id] = snippet
        self._save()

    def list(self) -> Sequence[Snippet]:
        return list(self._snippets.values())

    def get(self, snippet_id: int) -> Snippet | None:
        return self._snippets.get(snippet_id)

    def delete(self, snippet_id: int) -> None:
        if snippet_id not in self._snippets:
            raise SnippetNotFoundError
        del self._snippets[snippet_id]
        self._save()

    def tag(
        self, snippet_id: int, /, *targs: str, remove: bool = False, sort: bool = True
    ) -> None:
        snippet = self.get(snippet_id)
        if snippet is None:
            raise SnippetNotFoundError

        tag_names = {t.strip() for t in targs if t.strip()}
        if not tag_names:
            return

        def get_or_create(name: str) -> Tag:
            # Tags are not deduplicated globally in JSONRepo, so just create on the fly
            return Tag(name=name)

        self._update_tags(snippet, tag_names, get_or_create, remove, sort)
        self._save()

    def toggle_favorite(self, snippet_id: int) -> None:
        snippet = self.get(snippet_id)
        if snippet is None:
            raise SnippetNotFoundError
        self._update_favorite(snippet)
        self._save()

    def search(
        self, term: str, *, language: Language | None = None, fuzzy: bool = False
    ) -> Sequence[Snippet]:
        term_lower = self._validate_search_term(term)
        candidates = list(self._snippets.values())
        candidates = self._filter_by_language(candidates, language)

        if fuzzy:
            return self._fuzzy_match(term_lower, candidates)
        return self._exact_match(term_lower, candidates)
