# stdlib
from typing import Any, Generic, TypeVar
from uuid import UUID

# thirdparty
from beanie import Document
from beanie.odm.enums import SortDirection
from pydantic import BaseModel

# project
from documents.reaction import LikeValue

DocumentType = TypeVar("DocumentType", bound=Document)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[DocumentType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[DocumentType]) -> None:
        self.model = model

    async def create(self, obj_in: CreateSchemaType) -> DocumentType:
        document = self.model(**obj_in.model_dump())
        await document.insert()
        return document

    async def get(self, document_id: UUID, filters: dict | None = None) -> DocumentType:
        query = self._create_query(filters=filters)
        query["_id"] = document_id
        document = await self.model.find_one(query)
        if document is None:
            raise DocumentNotFoundException(f"Not found. {self.model.Settings.name}: {document_id}")
        return document

    async def update(self, document_id: UUID, update_data: UpdateSchemaType) -> DocumentType:
        document = await self.get(document_id)
        await document.update(update_data.model_dump())
        return document

    async def delete(self, document_id: UUID) -> None:
        document = await self.get(document_id)
        await document.delete()

    async def list(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_field: str | None = None,
        sort_order: SortDirection = SortDirection.ASCENDING,
        filters: dict[str, Any] | None = None,
    ) -> list[DocumentType]:
        """
        Возвращает список документов, удовлетворяющих переданным фильтрам.

        Args:
            skip: Сколько документов пропустить в выдаче.
            limit: Сколько документов возвращать.
            sort_field: Название поля, по которому производить сортировку.
            sort_order: Направление сортировки.
            filters: Модель с фильтрами. Если None, то возвращаются все документы.

        Returns:
            Список документов
        """

        query = self._create_query(filters=filters)

        sort = []
        if sort_field:
            sort.append((sort_field, sort_order))

        documents = await self.model.find(query, skip=skip, limit=limit).sort(*sort).to_list()
        return documents

    def _create_query(self, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Создает словарь запроса для фильтрации на основе переданных фильтров.

        Args:
            filters: Словарь с фильтрами. Если None, возвращается пустой словарь.

        Returns:
            Словарь с условиями для запроса.
        """
        if filters is None:
            return {}

        query: dict[str, Any] = {}

        for filter_field, filter_value in filters.items():
            if filter_value is None:
                continue

            if "__" in filter_field:
                field, comparator = filter_field.split("__")
                self.__add_comparator_to_query(query, field, comparator, filter_value)
            else:
                query[filter_field] = filter_value

        return query

    @staticmethod
    def __add_comparator_to_query(query: dict[str, Any], field: str, comparator: str, value: Any) -> None:
        """
        Добавляет условие с компаратором в словарь запроса.

        Args:
            query: Словарь запроса, который будет изменен.
            field: Поле для фильтрации (например, "rating").
            comparator: Компаратор (например, "gte").
            value: Значение для сравнения.
        """
        if query.get(field) is None:
            query[field] = {}

        query[field][f"${comparator}"] = value


class RatingRepository(BaseRepository[DocumentType, CreateSchemaType, UpdateSchemaType]):
    async def update_rating_count(self, document_id: UUID, like_value: LikeValue | int) -> DocumentType:
        document = await self.get(document_id)
        document.rating += like_value
        await document.save()
        return document


class DocumentNotFoundException(Exception):
    pass


class DocumentAlreadyExistsException(Exception):
    pass
