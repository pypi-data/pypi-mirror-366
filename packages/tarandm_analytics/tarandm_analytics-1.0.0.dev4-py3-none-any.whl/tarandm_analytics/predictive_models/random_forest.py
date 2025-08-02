from typing import Optional, List, Dict, Literal, Any, Union, TYPE_CHECKING

from tarandm_analytics.predictive_models.builder import PredictiveModelBuilder

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    import numpy as np
    from sklearn.tree._tree import Tree
else:
    # We must use Any here because without this line pydantic will load sklearn even though we don't really need it.
    RandomForestClassifier = Any

from tarandm_analytics.predictive_models.abstract_predictive_model import AbstractPredictiveModel
from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType
from pydantic import Field, SerializerFunctionWrapHandler, model_validator


class ModelRandomForest(AbstractPredictiveModel):
    """Internal representation of RandomForest model in TaranDM software. The class extends
    RandomForestClassifier class from sklearn.ensemble package with information about model type (
    random forest) and package version info.
    """

    model: Optional["RandomForestClassifier"] = Field(default=None, exclude=True)
    type: Literal[PredictiveModelType.RANDOM_FOREST]  # type: ignore[valid-type]
    package: Optional[str] = None
    package_version: Optional[str] = None
    random_forest_model: Dict[str, Any]

    @model_validator(mode="after")
    def deserialize_model(self) -> "ModelRandomForest":
        self.model = self.get_random_forest_from_dict(self.random_forest_model)
        return self

    def serialize_model(self, standard_serializer: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        return PredictiveModelBuilder().random_forest_model_dump(self.model)

    def predict(
        self, attribute_values: Dict[str, Union[int, float]], target_class: Optional[str] = None
    ) -> Optional[float]:
        """Compute prediction in form of probability of target for one scoring case.

        :param: attribute_values: list of attributes' values
        :return: predicted probability of target
        """
        if self.model is None:
            raise Exception("'predict' method of RANDOM_FOREST model was called, but the model object was not defined.")

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
        :return: list of predicted probabilities of target
        """
        if self.model is None:
            raise Exception(
                "'predict_batch' method of RANDOM_FOREST model was called, but the model object was not defined."
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

    @staticmethod
    def _get_tree_from_dict(
        tree_dict: Dict[str, Any], n_features: int, n_classes: "np.ndarray", n_outputs: int, version: str
    ) -> "Tree":
        tree_dict = tree_dict.copy()

        major, minor, patch = map(int, version.split("."))
        if major <= 1 and (minor <= 3 or (major == 4 and patch == 0)):
            # update format of values introduced in scikit 1.4.1
            new_values = []
            for value in tree_dict["values"]:
                sublist = []
                for item in value:
                    n_samples = int(sum(item))
                    sublist.append([value / n_samples for value in item])
                new_values.append(sublist)
            tree_dict["values"] = new_values

        from sklearn.tree._tree import Tree

        tree = Tree(n_features, n_classes, n_outputs)

        nodes = [tuple(n) for n in tree_dict["nodes_values"]]
        types = tree_dict["nodes_types"]

        import numpy as np

        tree_dict["nodes"] = np.array(nodes, types)

        remove_keys = ["nodes_types", "nodes_values"]
        for remove_key in remove_keys:
            if remove_key in tree_dict:
                del tree_dict[remove_key]

        tree_dict["values"] = np.array(tree_dict["values"])

        tree.__setstate__(tree_dict)

        return tree

    def _get_decision_tree_from_dict(
        self, decision_tree_dict: Dict[str, Any], version: str
    ) -> "DecisionTreeClassifier":
        from sklearn.tree import DecisionTreeClassifier

        decision_tree_dict = decision_tree_dict.copy()  # shallow copy only

        decision_tree = DecisionTreeClassifier()

        import numpy as np

        decision_tree_dict["classes_"] = np.array(decision_tree_dict["classes_"]).astype(str)

        decision_tree_dict["tree_"] = self._get_tree_from_dict(
            tree_dict=decision_tree_dict["tree_"],
            n_features=decision_tree_dict["n_features_in_"],
            n_classes=np.array([decision_tree_dict["n_classes_"]]),
            n_outputs=decision_tree_dict["n_outputs_"],
            version=version,
        )

        decision_tree.__setstate__(decision_tree_dict)

        if hasattr(decision_tree, "_sklearn_version"):
            del decision_tree._sklearn_version

        return decision_tree

    def get_random_forest_from_dict(self, random_forest_dict: Dict[str, Any]) -> "RandomForestClassifier":
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.ensemble import RandomForestClassifier

        random_forest_dict = random_forest_dict.copy()  # shallow copy only
        version = random_forest_dict["_sklearn_version"]

        major, minor, patch = map(int, version.split("."))
        if major <= 1 and (minor <= 3 or (major == 4 and patch == 0)):
            # update format of values introduced in scikit 1.4.1
            # first split has all values
            random_forest_dict["_n_samples"] = int(sum(random_forest_dict["estimators_"][0]["tree_"]["values"][0][0]))

        random_forest = RandomForestClassifier()

        random_forest_dict["estimator"] = DecisionTreeClassifier()
        random_forest_dict["_estimator"] = DecisionTreeClassifier()

        random_forest_dict["classes_"] = [str(cl) for cl in random_forest_dict["classes_"]]
        random_forest_dict["estimators_"] = [
            self._get_decision_tree_from_dict(e, version=version) for e in random_forest_dict["estimators_"]
        ]
        random_forest_dict["estimator_params"] = tuple(random_forest_dict["estimator_params"])

        if "feature_names_in_" in random_forest_dict:
            random_forest_dict["feature_names_in_"] = random_forest_dict["feature_names_in_"]

        random_forest.__setstate__(random_forest_dict)

        return random_forest
