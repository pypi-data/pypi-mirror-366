#   Exercise of exclusive rights to this Software belongs to Taran Advisory and distribution,
#   duplication or any other usage without previous written agreement of Taran Advisory is
#   prohibited.

from typing import List, Optional, Dict, Any, Literal, Union, TYPE_CHECKING, cast

from tarandm_analytics.predictive_models.builder import PredictiveModelBuilder

if TYPE_CHECKING:
    from sklearn.linear_model import LogisticRegression
else:
    # We must use Any here because without this line pydantic will load sklearn even though we don't really need it.
    LogisticRegression = Any

from tarandm_analytics.predictive_models.abstract_predictive_model import AbstractPredictiveModel
from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType
from pydantic import Field, SerializerFunctionWrapHandler, model_validator


class ModelLogisticRegression(AbstractPredictiveModel):
    """Internal representation of Logistic regression model in TaranDM software. The class extends
    LogisticRegression class from sklearn.linear_model package with information about model type (logistic
    regression) and package version info.
    """

    model: Optional["LogisticRegression"] = Field(default=None)
    type: Literal[PredictiveModelType.LOGISTIC_REGRESSION]  # type: ignore[valid-type]
    package: Optional[str] = None
    package_version: Optional[str] = None
    logreg_model_params: Dict[str, Any]
    init_params: Dict[str, Any]

    @model_validator(mode="after")
    def deserialize_model(self) -> "ModelLogisticRegression":
        import numpy as np
        from sklearn.linear_model import LogisticRegression

        logistic_regression = LogisticRegression(**self.init_params)

        for parameter_name, parameter_value in self.logreg_model_params.items():
            setattr(logistic_regression, parameter_name, np.array(parameter_value))

        logistic_regression.feature_names_in_ = self.feature_names

        self.model = logistic_regression

        self.intercept = self.get_intercept()
        self.intercept_name = self.get_intercept_name()

        return self

    def serialize_model(self, standard_serializer: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        return PredictiveModelBuilder().logreg_model_dump(self.model)

    def predict(
        self, attribute_values: Dict[str, Union[int, float]], target_class: Optional[str] = None
    ) -> Optional[float]:
        """Compute prediction in form of probability of target for one scoring case.

        :param: attribute_values: list of attributes' values
        :return: predicted probability of target
        """
        if self.model is None:
            raise Exception(
                "'predict' method of LOGISTIC_REGRESSION model was called, but the model object was not defined."
            )

        data_for_predict = []
        for feature in self.feature_names:
            val = attribute_values.get(feature, None)
            if val is None or type(val) not in [int, float]:
                raise TypeError(f"Model predict method was called with non-numerical value: {feature} = {val}.")
            data_for_predict.append(val)

        class_index = self._get_target_class_index(target_class)
        return float(self.model.predict_proba([data_for_predict])[0, class_index])

    def predict_batch(
        self, attribute_values: Dict[str, List[Union[int, float]]], target_class: Optional[str] = None
    ) -> Optional[List[Optional[float]]]:
        """Compute prediction in form of probability of target for multiple scoring cases.

        :param: attribute_values: attribute values - one row represents one case to be scored
        :return: list of predicted probabilities of target.
        """
        if self.model is None:
            raise Exception(
                "'predict_batch' method of LOGISTIC_REGRESSION model was called, but the model object was not defined."
            )

        data_for_predict = []
        n_obs = None
        for feature in self.feature_names:
            values = attribute_values.get(feature, None)
            if not isinstance(values, list):
                raise TypeError(
                    f"'predict_batch' method expect values of each attribute provided in list. Values for "
                    f"{feature} was provided as {type(values)}."
                )
            elif not all(isinstance(val, (int, float)) for val in values):
                raise TypeError("Some of values provided to predict_batch method are not numerical.")
            elif n_obs is not None and n_obs != len(values):
                raise ValueError(
                    "Values provided to predict_batch method do not have the same size for all attributes."
                )
            data_for_predict.append(values)

        data_for_predict = [list(row) for row in zip(*data_for_predict)]

        class_index = self._get_target_class_index(target_class)
        return self.model.predict_proba(data_for_predict)[:, class_index]

    @property
    def coefficients(self) -> Optional[List[float]]:
        try:
            return cast(List[float], self.logreg_model_params["coef_"][0])
        except KeyError:
            return None

    def get_intercept(self) -> float:
        try:
            return cast(float, self.logreg_model_params["intercept_"][0])
        except KeyError:
            return 0

    def get_intercept_name(self) -> Optional[str]:
        try:
            return cast(str, self.init_params["intercept_name"])
        except KeyError:
            return None
