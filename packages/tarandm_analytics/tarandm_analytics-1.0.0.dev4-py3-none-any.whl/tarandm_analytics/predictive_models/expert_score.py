from typing import Literal, List, Optional, Dict, Union, Any, Tuple

from pydantic import SerializerFunctionWrapHandler
from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType
from tarandm_analytics.predictive_models.abstract_predictive_model import AbstractPredictiveModel


class ModelExpertScore(AbstractPredictiveModel):
    """Internal representation of expertly defined score. Expert score defines binning of attributes and assigns a value
    to every bin. Prediction is simple sum of assigned values.
    """

    type: Literal[PredictiveModelType.EXPERT_SCORE]  # type: ignore[valid-type]
    feature_names: List[str] = []

    def serialize_model(self, standard_serializer: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        return standard_serializer(self)

    def predict(
        self, attribute_values: Dict[str, Union[int, float]], target_class: Optional[str] = None
    ) -> Optional[float]:
        """Compute prediction for one scoring case.

        :param: attribute_values: list of attributes' values
        :return: predicted probability of target
        """
        data_for_predict = []
        for feature in self.feature_names:
            val = attribute_values.get(feature, None)
            if val is None or type(val) not in [int, float]:
                raise TypeError(f"Model predict method was called with non-numerical value: {feature} = {val}.")
            data_for_predict.append(val)

        intercept = self.intercept or 0.0
        return float(intercept + sum(data_for_predict))

    def predict_batch(
        self, attribute_values: Dict[str, List[Union[int, float]]], target_class: Optional[str] = None
    ) -> Optional[List[Optional[float]]]:
        """Compute prediction for multiple scoring cases.

        :param: attribute_values: attribute values - one row represents one case to be scored
        :return: list of predicted probabilities of target
        """
        data_for_predict = []
        n_obs = len(attribute_values.get(self.feature_names[0], []))
        for feature in self.feature_names:
            values = attribute_values.get(feature, None)
            if not isinstance(values, list):
                raise TypeError(
                    f"'predict_batch' method expect values of each attribute provided in list. Values for "
                    f"{feature} was provided as {type(values)}."
                )
            elif not all(isinstance(val, (int, float)) for val in values):
                raise TypeError("Some of values provided to predict_batch method are not numerical.")
            elif n_obs != len(values):
                raise ValueError("Number of values provided to predict_batch is inconsistent across attributes.")
            data_for_predict.append(values)

        intercept = self.intercept or 0.0
        return [sum(row) + intercept for row in zip(*data_for_predict)]

    @classmethod
    def get_allowed_infinity_representation(cls) -> Tuple[List[str], List[str]]:
        negative_inf_representation = ["NEGINFINITY", "NEGINF", "NEG_INF"]
        positive_inf_representation = ["INFINITY", "INF"]

        return negative_inf_representation, positive_inf_representation
