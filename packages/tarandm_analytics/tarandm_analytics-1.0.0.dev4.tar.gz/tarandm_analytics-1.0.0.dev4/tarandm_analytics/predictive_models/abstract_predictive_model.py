from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Union, Any

from pydantic import BaseModel, SerializerFunctionWrapHandler, model_serializer

from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType
from tarandm_analytics_utils.utils.parse import parse_value


class AbstractPredictiveModel(BaseModel, ABC):
    type: PredictiveModelType
    feature_names: List[str]
    intercept: Optional[float] = None
    intercept_name: Optional[str] = None

    @model_serializer(mode="wrap")
    def serialize_external_model(self, standard_serializer: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        return self.serialize_model(standard_serializer=standard_serializer)

    @abstractmethod
    def serialize_model(self, standard_serializer: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def predict(
        self, attribute_values: Dict[str, Union[int, float]], target_class: Optional[str] = None
    ) -> Optional[float]:
        raise NotImplementedError()

    @abstractmethod
    def predict_batch(
        self, attribute_values: Dict[str, List[Union[int, float]]], target_class: Optional[str] = None
    ) -> Optional[List[Optional[float]]]:
        raise NotImplementedError()

    def validate_target_class(self, target_class: str) -> None:
        # most mathematical models have this attribute
        if hasattr(self, "model") and hasattr(self.model, "classes_"):
            target_class_value = parse_value(target_class)
            available_classes = list(map(lambda x: parse_value(str(x)), self.model.classes_))
            if target_class_value not in available_classes:
                raise ValueError(
                    f"Argument 'target_class' of value {target_class} not found in classes '{self.model.classes_}'"
                )

    def _get_target_class_index(self, target_class: Optional[str]) -> int:
        class_index = None
        # the model return a vector of probabilities, search for probability of specific classes
        # most mathematical models have this attribute
        if hasattr(self, "model") and hasattr(self.model, "classes_"):
            if target_class is not None:
                target_class_value = parse_value(target_class)
            else:
                target_class_value = 1
            available_classes = list(map(lambda x: parse_value(str(x)), self.model.classes_))
            class_index = available_classes.index(target_class_value)

        if class_index is None:
            class_index = 0

        return class_index

    @property
    def coefficients(self) -> Optional[List[float]]:
        return None

    @property
    def best_iteration(self) -> Optional[int]:
        return None

    @property
    def number_of_trees(self) -> Optional[int]:
        return None

    @property
    def best_eval_metric(self) -> Optional[float]:
        return None

    @property
    def number_of_attributes(self) -> Optional[int]:
        return None
