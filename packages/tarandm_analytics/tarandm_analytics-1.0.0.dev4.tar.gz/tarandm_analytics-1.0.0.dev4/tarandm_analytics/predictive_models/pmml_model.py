from io import StringIO, BytesIO, TextIOWrapper
from typing import Optional, Literal, List, Dict, Union, Any, TYPE_CHECKING

from pydantic import SerializerFunctionWrapHandler, model_validator, Field

from tarandm_analytics.predictive_models.abstract_predictive_model import AbstractPredictiveModel
from tarandm_analytics.predictive_models.builder import PredictiveModelBuilder
from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType

if TYPE_CHECKING:
    from sklearn_pmml_model.linear_model import PMMLLogisticRegression
    from sklearn_pmml_model.ensemble import PMMLForestClassifier
    from sklearn_pmml_model.ensemble.gb import PMMLGradientBoostingClassifier
else:
    # We must use Any here because without this line pydantic will load sklearn_pmml_model even though we don't really need it.
    PMMLLogisticRegression = PMMLForestClassifier = PMMLGradientBoostingClassifier = Any


class ModelPMML(AbstractPredictiveModel):
    pmml_model: str
    type: Literal[PredictiveModelType.PMML]  # type: ignore[valid-type]
    feature_names: List[str] = []
    model: Optional[Union["PMMLLogisticRegression", "PMMLForestClassifier", "PMMLGradientBoostingClassifier"]] = Field(
        default=None
    )

    @model_validator(mode="after")
    def deserialize_model(self) -> "ModelPMML":
        if self.model is not None or self.pmml_model is None:
            return self

        import xml.etree.ElementTree as ET
        from sklearn_pmml_model.linear_model import PMMLLogisticRegression
        from sklearn_pmml_model.ensemble import PMMLForestClassifier
        from sklearn_pmml_model.ensemble.gb import PMMLGradientBoostingClassifier

        model_readable: StringIO | TextIOWrapper[BytesIO] = StringIO(self.pmml_model)

        tree = ET.parse(model_readable)  # nosec
        root = tree.getroot()

        model_cls = None
        for r in root:
            root_attributes = r.attrib
            if "algorithmName" in root_attributes:
                if root_attributes["algorithmName"] == "sklearn.linear_model._logistic.LogisticRegression":
                    model_cls = PMMLLogisticRegression
                    break
                elif root_attributes["algorithmName"] == "sklearn.ensemble._forest.RandomForestClassifier":
                    model_cls = PMMLForestClassifier

                    # TODO! ugly hack until sklearn_pmml_model is fixed
                    # https://github.com/iamDecode/sklearn-pmml-model/issues/61
                    for node in tree.findall(".//Node"):
                        if "recordCount" in node.attrib:
                            count = node.attrib["recordCount"]
                            for distr in node.findall("./ScoreDistribution"):
                                distr.attrib["recordCount"] = str(float(distr.attrib["recordCount"]) / float(count))

                    new_tree = BytesIO()
                    tree.write(new_tree)
                    model_readable = TextIOWrapper(new_tree, encoding="US-ASCII")
                    self.pmml_model = model_readable.read()

                    break
                elif root_attributes["algorithmName"] == "XGBoost (GBTree)":
                    model_cls = PMMLGradientBoostingClassifier

        if model_cls is None:
            raise ValueError("Unable to load pmml model.")

        model_readable.seek(0)
        self.model = model_cls(pmml=model_readable)
        self.feature_names = self._get_feature_names()

        return self

    def serialize_model(self, standard_serializer: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        return PredictiveModelBuilder().pmml_model_dump(StringIO(self.pmml_model))

    def predict(
        self, attribute_values: Dict[str, Union[int, float]], target_class: Optional[str] = None
    ) -> Optional[float]:
        if self.model is None:
            raise Exception(f"'predict' method of {self.type} model was called, but the model object was not defined.")

        data_for_predict = []
        for feature in self.feature_names:
            val = attribute_values.get(feature, None)
            if val is None or type(val) not in [int, float]:
                raise TypeError(f"Model predict method was called with non-numerical value: {feature} = {val}.")
            data_for_predict.append(val)

        class_index = self._get_target_class_index(target_class)
        import numpy as np

        return float(self.model.predict_proba(np.expand_dims(np.array(data_for_predict), axis=0))[0, class_index])

    def predict_batch(
        self, attribute_values: Dict[str, List[Union[int, float]]], target_class: Optional[str] = None
    ) -> List[Optional[float]]:
        n_obs = len(attribute_values[list(attribute_values.keys())[0]])
        predictions = []
        for i in range(n_obs):
            attr_vals_single_row = {}
            for pred, vals in attribute_values.items():
                attr_vals_single_row[pred] = vals[i]
            predictions.append(self.predict(attribute_values=attr_vals_single_row, target_class=target_class))
        return predictions

    def _get_feature_names(self) -> List[str]:
        if self.model is not None:
            features_with_order = sorted(
                [
                    (k, v[0])
                    for k, v in self.model.field_mapping.items()
                    if v[0] is not None and self.model.fields[k].tag == "DataField"
                ],
                key=lambda x: x[1],
            )
            return [x[0] for x in features_with_order]
        else:
            return []
