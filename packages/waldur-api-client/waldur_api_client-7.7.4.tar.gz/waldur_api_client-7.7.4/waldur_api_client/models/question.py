from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.question_options import QuestionOptions


T = TypeVar("T", bound="Question")


@_attrs_define
class Question:
    """
    Attributes:
        uuid (UUID):
        category_uuid (UUID):
        question_options (list['QuestionOptions']):
        description (Union[Unset, str]):
        solution (Union[None, Unset, str]): Guidance shown when answer needs clarification
        image (Union[None, Unset, str]):
    """

    uuid: UUID
    category_uuid: UUID
    question_options: list["QuestionOptions"]
    description: Union[Unset, str] = UNSET
    solution: Union[None, Unset, str] = UNSET
    image: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        category_uuid = str(self.category_uuid)

        question_options = []
        for question_options_item_data in self.question_options:
            question_options_item = question_options_item_data.to_dict()
            question_options.append(question_options_item)

        description = self.description

        solution: Union[None, Unset, str]
        if isinstance(self.solution, Unset):
            solution = UNSET
        else:
            solution = self.solution

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "category_uuid": category_uuid,
                "question_options": question_options,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if solution is not UNSET:
            field_dict["solution"] = solution
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.question_options import QuestionOptions

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        category_uuid = UUID(d.pop("category_uuid"))

        question_options = []
        _question_options = d.pop("question_options")
        for question_options_item_data in _question_options:
            question_options_item = QuestionOptions.from_dict(question_options_item_data)

            question_options.append(question_options_item)

        description = d.pop("description", UNSET)

        def _parse_solution(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        solution = _parse_solution(d.pop("solution", UNSET))

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        question = cls(
            uuid=uuid,
            category_uuid=category_uuid,
            question_options=question_options,
            description=description,
            solution=solution,
            image=image,
        )

        question.additional_properties = d
        return question

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
