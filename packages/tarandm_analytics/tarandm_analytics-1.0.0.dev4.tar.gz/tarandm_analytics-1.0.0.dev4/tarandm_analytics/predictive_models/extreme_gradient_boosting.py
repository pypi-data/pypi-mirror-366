import json
from typing import Optional, List, Dict, Literal, Any, Union, TYPE_CHECKING

from tarandm_analytics.predictive_models.builder import PredictiveModelBuilder

if TYPE_CHECKING:
    from xgboost import Booster
else:
    # We must use Any here because without this line pydantic will load xgboost even though we don't really need it.
    Booster = Any

from tarandm_analytics.predictive_models.abstract_predictive_model import AbstractPredictiveModel
from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType
from pydantic import Field, SerializerFunctionWrapHandler, model_validator


class ModelXGBoost(AbstractPredictiveModel):
    """Internal representation of Extreme Gradient Boosting model in TaranDM software. The class extends
    Booster class from xgboost package with information about model type (XGB) and package version info.
    """

    model: Optional[Booster] = Field(default=None, exclude=True)
    type: Literal[PredictiveModelType.XGB]  # type: ignore[valid-type]
    package: Optional[str] = None
    package_version: Optional[str] = None
    xgb_model: Dict[str, Any]

    @model_validator(mode="after")
    def deserialize_model(self) -> "ModelXGBoost":
        model_bytearray = bytearray()
        model_bytearray.extend(json.dumps(self.xgb_model).encode("utf-8"))

        import xgboost as xgb

        model = xgb.Booster()
        model.load_model(model_bytearray)

        self.model = model
        return self

    def serialize_model(self, standard_serializer: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        if self.model is None:
            raise Exception("'serialize_model' method of XGB model was called, but the model object was not defined.")
        return PredictiveModelBuilder().xgb_model_dump(self.model)

    def predict(
        self, attribute_values: Dict[str, Union[int, float]], target_class: Optional[str] = None
    ) -> Optional[float]:
        """Compute prediction in form of probability of target for one scoring case.

        :param: attribute_values: list of attributes' values
        :return: predicted probability of target
        """
        if self.model is None:
            raise Exception("'predict' method of XGB model was called, but the model object was not defined.")

        data_for_predict = []
        for feature in self.feature_names:
            val = attribute_values.get(feature, None)
            if val is not None and type(val) not in [int, float]:
                raise TypeError(f"Model predict method was called with non-numerical value: {feature} = {val}.")
            data_for_predict.append(val)

        import xgboost as xgb

        return float(
            self.model.predict(
                xgb.DMatrix(
                    data=[data_for_predict],
                    feature_names=self.model.feature_names,
                )
            )[0]
        )

    def predict_batch(
        self, attribute_values: Dict[str, List[Union[int, float]]], target_class: Optional[str] = None
    ) -> Optional[List[Optional[float]]]:
        """Compute prediction in form of probability of target for multiple scoring cases.

        :param: attribute_values: attribute values - one row represents one case to be scored
        :return: list of predicted probabilities of target
        """
        if self.model is None:
            raise Exception("'predict_batch' method of XGB model was called, but the model object was not defined.")

        data_for_predict = []
        n_obs = None
        for feature in self.feature_names:
            values = attribute_values.get(feature, None)
            if not isinstance(values, list):
                raise TypeError(
                    f"'predict_batch' method expect values of each attribute provided in list. Values for "
                    f"{feature} was provided as {type(values)}."
                )
            elif not all(val is None or isinstance(val, (int, float)) for val in values):
                raise TypeError("Some of values provided to predict_batch method are not numerical or None.")
            elif n_obs is not None and n_obs != len(values):
                raise ValueError(
                    "Values provided to predict_batch method do not have the same size for all attributes."
                )
            data_for_predict.append(values)

        data_for_predict_transposed = list(map(list, zip(*data_for_predict)))

        import xgboost as xgb

        return list(
            self.model.predict(
                xgb.DMatrix(
                    data=data_for_predict_transposed,
                    feature_names=self.feature_names,
                )
            )
        )
