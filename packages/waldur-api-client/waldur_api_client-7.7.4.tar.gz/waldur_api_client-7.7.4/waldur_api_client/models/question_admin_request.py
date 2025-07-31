from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..models.blank_enum import BlankEnum
from ..models.operator_enum import OperatorEnum
from ..models.question_type_enum import QuestionTypeEnum
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="QuestionAdminRequest")


@_attrs_define
class QuestionAdminRequest:
    """
    Attributes:
        checklist (str):
        description (Union[Unset, str]):
        solution (Union[None, Unset, str]): Guidance shown when answer needs clarification
        image (Union[File, None, Unset]):
        order (Union[Unset, int]):
        required (Union[Unset, bool]):
        question_type (Union[Unset, QuestionTypeEnum]):
        operator (Union[BlankEnum, OperatorEnum, Unset]):
        review_answer_value (Union[Unset, Any]): Answer value that trigger review.
        always_requires_review (Union[Unset, bool]): This question always requires review regardless of answer
    """

    checklist: str
    description: Union[Unset, str] = UNSET
    solution: Union[None, Unset, str] = UNSET
    image: Union[File, None, Unset] = UNSET
    order: Union[Unset, int] = UNSET
    required: Union[Unset, bool] = UNSET
    question_type: Union[Unset, QuestionTypeEnum] = UNSET
    operator: Union[BlankEnum, OperatorEnum, Unset] = UNSET
    review_answer_value: Union[Unset, Any] = UNSET
    always_requires_review: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        checklist = self.checklist

        description = self.description

        solution: Union[None, Unset, str]
        if isinstance(self.solution, Unset):
            solution = UNSET
        else:
            solution = self.solution

        image: Union[None, Unset, types.FileTypes]
        if isinstance(self.image, Unset):
            image = UNSET
        elif isinstance(self.image, File):
            image = self.image.to_tuple()

        else:
            image = self.image

        order = self.order

        required = self.required

        question_type: Union[Unset, str] = UNSET
        if not isinstance(self.question_type, Unset):
            question_type = self.question_type.value

        operator: Union[Unset, str]
        if isinstance(self.operator, Unset):
            operator = UNSET
        elif isinstance(self.operator, OperatorEnum):
            operator = self.operator.value
        else:
            operator = self.operator.value

        review_answer_value = self.review_answer_value

        always_requires_review = self.always_requires_review

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "checklist": checklist,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if solution is not UNSET:
            field_dict["solution"] = solution
        if image is not UNSET:
            field_dict["image"] = image
        if order is not UNSET:
            field_dict["order"] = order
        if required is not UNSET:
            field_dict["required"] = required
        if question_type is not UNSET:
            field_dict["question_type"] = question_type
        if operator is not UNSET:
            field_dict["operator"] = operator
        if review_answer_value is not UNSET:
            field_dict["review_answer_value"] = review_answer_value
        if always_requires_review is not UNSET:
            field_dict["always_requires_review"] = always_requires_review

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        checklist = d.pop("checklist")

        description = d.pop("description", UNSET)

        def _parse_solution(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        solution = _parse_solution(d.pop("solution", UNSET))

        def _parse_image(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                image_type_0 = File(payload=BytesIO(data))

                return image_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

        image = _parse_image(d.pop("image", UNSET))

        order = d.pop("order", UNSET)

        required = d.pop("required", UNSET)

        _question_type = d.pop("question_type", UNSET)
        question_type: Union[Unset, QuestionTypeEnum]
        if isinstance(_question_type, Unset):
            question_type = UNSET
        else:
            question_type = QuestionTypeEnum(_question_type)

        def _parse_operator(data: object) -> Union[BlankEnum, OperatorEnum, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_0 = OperatorEnum(data)

                return operator_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            operator_type_1 = BlankEnum(data)

            return operator_type_1

        operator = _parse_operator(d.pop("operator", UNSET))

        review_answer_value = d.pop("review_answer_value", UNSET)

        always_requires_review = d.pop("always_requires_review", UNSET)

        question_admin_request = cls(
            checklist=checklist,
            description=description,
            solution=solution,
            image=image,
            order=order,
            required=required,
            question_type=question_type,
            operator=operator,
            review_answer_value=review_answer_value,
            always_requires_review=always_requires_review,
        )

        question_admin_request.additional_properties = d
        return question_admin_request

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
