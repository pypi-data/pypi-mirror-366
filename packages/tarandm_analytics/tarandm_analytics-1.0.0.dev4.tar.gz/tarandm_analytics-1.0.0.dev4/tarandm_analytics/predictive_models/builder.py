import ast
import datetime
import io
from typing import Callable, List, Dict, Union, Optional, Any, Tuple, TYPE_CHECKING, cast
from pydantic import BaseModel

import structlog
from tarandm_analytics_utils.predictive_models.attribute_preprocessing.attribute_binning import (
    AttributeBinCategorical,
    AttributeBinNumerical,
    AttributeBinning,
    AttributeDataType,
    PredictiveModelBinName,
)
from tarandm_analytics_utils.predictive_models.attribute_preprocessing.attribute_preprocessing import (
    AttributePreprocessing,
    PredictiveModelDummyEncoding,
    PredictiveModelDummyEncodingSingleValue,
)
from tarandm_analytics_utils.predictive_models.attribute_preprocessing.attribute_transformation import (
    AttributeTransformation,
)
from tarandm_analytics_utils.predictive_models.extended_predictive_model import PredictiveModelType
from tarandm_analytics_utils.predictive_models.model_description.model_description import (
    AttachedImage,
    PredictiveModelDescription,
)
from tarandm_analytics_utils.predictive_models.model_description.sample_decription import (
    ClassFrequency,
    SampleDescription,
)
from tarandm_analytics_utils.predictive_models.model_monitoring.model_monitoring import PredictiveModelMonitoring
from tarandm_analytics_utils.predictive_models.model_performance.model_performance import (
    PredictiveModelPerformance,
)
from tarandm_analytics_utils.predictive_models.model_performance.sample_performance import (
    PerformanceMetrics,
    SamplePerformance,
    SampleType,
)

from tarandm_analytics.predictive_models.expert_score import ModelExpertScore

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.tree._tree import Tree
    from xgboost import Booster
    import pandas as pd
    import polars as pl
    import numpy as np
    from tarandm_analytics.predictive_models.extended_predictive_model import ExtendedPredictiveModel
else:
    RandomForestClassifier = Any
    LogisticRegression = Any
    DecisionTreeClassifier = Any
    Tree = Any
    Booster = Any

from tarandm_analytics.export_predictive_model.model_visualization import (
    shap_summary_plot_logistic_regression,
    shap_summary_plot_xgboost,
    shap_summary_plot_random_forest,
    learning_curves_plot,
)
from tarandm_analytics.utils.formatting import get_number_formatting

logger = structlog.get_logger(__name__)

ModelType = Union["LogisticRegression", "RandomForestClassifier", "Booster", "pl.DataFrame", io.StringIO]
ModelTypeWithPandas = Union[
    "LogisticRegression", "RandomForestClassifier", "Booster", "pl.DataFrame", "pd.DataFrame", io.StringIO
]


class RequestData(BaseModel):
    model_type: PredictiveModelType
    target_class: Optional[str] = None
    label_name: Optional[str] = None
    predictors: List[str]
    attribute_binning: Optional[Dict] = None
    monitoring_data: PredictiveModelMonitoring
    description: PredictiveModelDescription
    model_performance: PredictiveModelPerformance
    attribute_transformation: List[AttributeTransformation]
    dummy_encoding: List[PredictiveModelDummyEncoding]


class PredictiveModelBuilder:
    def prepare_predictive_model_data(
        self,
        model: ModelType,
        attributes: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        data: Optional["pd.DataFrame"] = None,
        label_name: Optional[str] = None,
        target_class: Optional[str] = None,
        attribute_binning: Optional[Dict] = None,
        attribute_transformation: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        dummy_encoding: Optional[
            Union[
                List[Dict[str, Union[str, Dict[str, Union[str, bool]]]]], Dict[str, List[Dict[str, Union[str, bool]]]]
            ]
        ] = None,
        monitoring_data: Optional[Dict[str, List[Dict]]] = None,
        hyperparameters: Optional[Dict] = None,
        general_notes: Optional[Dict[str, Any]] = None,
        attribute_description: Optional[Dict[str, str]] = None,
        column_name_sample: Optional[str] = None,
        column_name_date: Optional[str] = None,
        column_name_prediction: Optional[str] = None,
        evaluate_performance: Optional[Dict[str, Union[str, List[str]]]] = None,
        learning_curves_data: Optional[Dict] = None,
        created_date: Optional[datetime.date] = None,
    ) -> RequestData:
        # 1. Restructure dummy encoding and transformations into new format if provided in old format
        dummy_encoding_formatted = self._format_dummy_encoding(dummy_encoding)
        transformations_formatted = self._format_transformations(attribute_transformation)

        model_type_final = self._validate_model_type(model_type, model)
        model_name_final = self._validate_model_name(model_name, model_type_final)
        if model_type_final == PredictiveModelType.PMML:
            # TODO: add validation that StringIO in model can be parsed?
            model_attributes_orig = attributes
        else:
            model_attributes_orig = self._validate_feature_names(
                attributes=attributes,
                transformations=transformations_formatted,
                attribute_binning=attribute_binning,
                dummy_encoding=dummy_encoding_formatted,
                model=model,
            )

        # 2. Get descriptive data about data samples used in model development
        sample_description_data = self._get_data_sample_description(
            data=data,
            column_name_label=label_name,
            column_name_sample=column_name_sample,
            column_name_date=column_name_date,
        )

        # 3. Get model performance over different samples
        model_performance = self._get_predictive_model_performance(
            data=data,
            column_name_sample=column_name_sample,
            column_name_prediction=column_name_prediction,
            evaluate_performance=evaluate_performance,
        )

        # 4. Generate images
        images = self._generate_images(
            data=data,
            model=model,
            model_type=model_type_final,
            target_class=target_class,
            learning_curves_data=learning_curves_data,
        )

        # 5. Prepare request data
        return RequestData(
            model_type=model_type_final,
            target_class=target_class,
            label_name=label_name,
            predictors=model_attributes_orig or [],
            attribute_binning=attribute_binning,
            monitoring_data=PredictiveModelMonitoring.model_validate(monitoring_data or {}),
            description=PredictiveModelDescription.model_validate(
                {
                    "predictive_model_name": model_name_final,
                    "sample_metadata": sample_description_data,
                    "attribute_description": attribute_description,
                    "hyperparameters": hyperparameters,
                    "number_of_trainable_parameters": None,
                    "general_notes": general_notes,
                    "predictive_model_created": self._validate_model_created_value(created_date),
                    "attached_images": images,
                }
            ),
            model_performance=model_performance,
            attribute_transformation=transformations_formatted or [],
            dummy_encoding=dummy_encoding_formatted or [],
        )

    def _get_data_sample_description(
        self,
        data: Optional["pd.DataFrame"],
        column_name_label: Optional[str] = None,
        column_name_sample: Optional[str] = None,
        column_name_date: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Function evaluates different descriptive information about model development data sample, such as what time range
        was used, what are the frequencies of label classes and other.

        :param data: Dataset to be used for descriptive info evaluation.
        :param column_name_label: Name of the column inside 'data' that stores labels.
        :param column_name_sample: Name of the column inside 'data' that distinguishes type of data samples. Column can
               contain for instance values 'train', 'valid', 'test'. This will define which observations belong to train
               set, validation set and test set.
        :param column_name_date: Name of the column inside 'data' that stores dates related to observations.
        :return: Dictionary with descriptive info data.
        """
        if data is None:
            logger.warning(
                "Preparing sample descriptions: No dataset was provided. Cannot evaluate sample description " "data."
            )
            return None
        elif len(data) == 0:
            logger.warning(
                "Preparing sample descriptions: Provided dataset has 0 observations. Cannot evaluate sample "
                "description data."
            )
            return None

        if column_name_sample is None:
            logger.warning(
                "Preparing sample descriptions: Column name with sample type was not provided. All observations will "
                "be treated as training data."
            )
            # _generate_sample_type_column_name makes sure that it does not overwrite existing column
            column_name_sample = self._generate_sample_type_column_name(data=data)
            data[column_name_sample] = "train"
        elif column_name_sample not in data.columns:
            logger.warning(
                f"Preparing sample descriptions: Provided column name with sample type '{column_name_sample}' does not "
                f"exist in data. All observations will be treated as training data."
            )
            # _generate_sample_type_column_name makes sure that it does not overwrite existing column
            column_name_sample = self._generate_sample_type_column_name(data=data)
            data[column_name_sample] = "train"

        date_available = True
        if column_name_date is None:
            logger.warning(
                "Preparing sample descriptions: Date column name (parameter 'column_name_date') was not provided. Time "
                "related metadata will not be evaluated."
            )
            date_available = False
        elif column_name_date not in data.columns:
            logger.warning(
                f"Preparing sample descriptions: Provided date column name '{column_name_date}' does not exist in "
                f"data. Time related metadata will not be evaluated."
            )
            date_available = False
        elif data[column_name_date].dtype != "<M8[ns]":
            logger.warning(
                f"Preparing sample descriptions: Provided date column name '{column_name_date}' is of type "
                f"{data[column_name_date].dtype.__str__()}. Required type is '<M8[ns]'. Time related metadata will not "
                f"be evaluated."
            )
            date_available = False

        label_available = True
        label_binary = True
        if column_name_label is None:
            logger.warning(
                "Preparing sample descriptions: Label column name was not provided. Label related metadata "
                "will not be evaluated."
            )
            label_available = False
        elif column_name_label not in data.columns:
            logger.warning(
                f"Preparing sample descriptions: Provided label column name '{column_name_label}' does not exist in "
                f"data. Label related metadata will not be evaluated."
            )
            label_available = False
        elif data[column_name_label].nunique() != 2:
            label_binary = False

        included_sample_types = data[column_name_sample].unique()

        result = []
        for sample_type in included_sample_types:
            sample_meta = {"sample_type": sample_type.upper()}
            mask = data[column_name_sample] == sample_type
            sample_meta["number_of_observations"] = len(data[mask])

            if date_available:
                sample_meta["first_date"] = data[mask][column_name_date].min().strftime(format="%Y-%m-%d")
                sample_meta["last_date"] = data[mask][column_name_date].max().strftime(format="%Y-%m-%d")

            if label_available and label_binary:
                sample_meta["label_class_frequency"] = []
                for label_class in data[column_name_label].unique().tolist():
                    sample_meta["label_class_frequency"].append(
                        {
                            "label_class": label_class,
                            "number_of_observations": len(data[mask & (data[column_name_label] == label_class)]),
                        }
                    )
            result.append(sample_meta)

        return result

    def _get_model_type(self, model: Any) -> PredictiveModelType:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from xgboost import Booster
        import polars as pl

        if isinstance(model, io.StringIO):
            logger.info("Automatically added model type PMML.")
            return PredictiveModelType.PMML
        elif isinstance(model, LogisticRegression):
            logger.info("Automatically assigned model type LOGISTIC_REGRESSION.")
            return PredictiveModelType.LOGISTIC_REGRESSION
        elif isinstance(model, RandomForestClassifier):
            logger.info("Automatically added model type RANDOM_FOREST.")
            return PredictiveModelType.RANDOM_FOREST
        elif isinstance(model, Booster):
            logger.info("Automatically added model type XGB.")
            return PredictiveModelType.XGB
        elif isinstance(model, pl.DataFrame):
            logger.info("Automatically added model type EXPERT_SCORE.")
            return PredictiveModelType.EXPERT_SCORE
        else:
            raise TypeError(
                f"Model type was not provided and neither could not be detected detected automatically. Available model "
                f"types are: {PredictiveModelType.__members__.keys()}"
            )

    def _validate_model_type(
        self,
        model_type: Optional[str],
        model: Union["LogisticRegression", "RandomForestClassifier", "Booster", "pd.DataFrame"],
    ) -> str:
        if model_type is None:
            model_type_final = self._get_model_type(model=model)
        else:
            model_type_final = model_type

        return model_type_final

    def _validate_model_created_value(self, model_created: Optional[datetime.date]) -> datetime.date:
        if model_created is None:
            logger.info(
                "Request data 'model_created_date' was not provided. Current date will be used as a date when the "
                "model was created."
            )
            return datetime.date.today()

        return model_created

    def _prepare_attribute_binning(
        self, attribute_binning: Optional[Dict[str, Dict[str, Any]]]
    ) -> List[AttributeBinning]:
        if attribute_binning is not None:
            binning = AttributePreprocessing.add_attribute_binning(attribute_binning)
        else:
            binning = []

        return binning

    def _add_intercept_indicator_column(self, dt: "pl.DataFrame") -> "pl.DataFrame":
        if "is_intercept" not in dt.columns:
            import polars as pl

            dt = dt.with_columns(
                pl.when(
                    (pl.col("bin_from").is_null())
                    & (pl.col("bin_to").is_null())
                    & (pl.col("categories").is_null())
                    & (pl.col("missing") == 0)
                    & (pl.col("default") == 0)
                )
                .then(1)
                .otherwise(0)
                .alias("is_intercept")
            )

        if dt["is_intercept"].sum() > 1:
            raise ValueError("Found multiple rows defined as intercept. Only one row can be defined as intercept.")

        return dt

    def get_unique_values_from_df_col(self, dt: "pl.DataFrame", extract_values_from: str) -> List[str]:
        """This function will extract unique values from polars DataFrame into list in deterministic order."""
        attributes_in_df = dt[extract_values_from].to_list()
        seen_attr = set()
        unique_attributes = []
        for attr in attributes_in_df:
            if attr not in seen_attr:
                unique_attributes.append(attr)
                seen_attr.add(attr)

        return unique_attributes

    def prepare_binning_categorical(
        self, expert_score_attr: "pl.DataFrame", default_score: float = 0.0, null_score: float = 0.0
    ) -> List[AttributeBinCategorical]:
        binning = []
        default_bin_name = PredictiveModelBinName.SYSTEM_DEFAULT

        for i in range(len(expert_score_attr)):
            special_bin = False
            if expert_score_attr["missing"][i] == 1:
                null_score = expert_score_attr["value"][i]
                special_bin = True
            elif expert_score_attr["default"][i] == 1:
                default_score = float(expert_score_attr["value"][i])
                default_bin_name = PredictiveModelBinName.DEFINED_DEFAULT
                special_bin = True

            if special_bin:
                continue

            categories = ast.literal_eval(expert_score_attr["categories"][i])
            if not isinstance(categories, list):
                categories = [categories]
            binning.append(
                AttributeBinCategorical(
                    categories=categories,
                    id=i + 2,
                    value=expert_score_attr["value"][i],
                )
            )
        binning.append(AttributeBinCategorical(name=default_bin_name, id=0, value=default_score))
        binning.append(AttributeBinCategorical(name=PredictiveModelBinName.NULL, id=1, value=null_score))

        return binning

    def prepare_binning_numerical(
        self,
        expert_score_attr: "pl.DataFrame",
        negative_infinity_representation: List[str],
        positive_infinity_representation: List[str],
        default_score: float = 0.0,
        null_score: float = 0.0,
    ) -> List[AttributeBinNumerical]:
        binning = []
        default_bin_name = PredictiveModelBinName.SYSTEM_DEFAULT

        for i in range(len(expert_score_attr)):
            special_bin = False
            if expert_score_attr["missing"][i] == 1:
                null_score = expert_score_attr["value"][i]
                special_bin = True
            elif expert_score_attr["default"][i] == 1:
                default_score = expert_score_attr["value"][i]
                default_bin_name = PredictiveModelBinName.DEFINED_DEFAULT
                special_bin = True

            if special_bin:
                continue

            if (
                isinstance(expert_score_attr["bin_from"][i], str)
                and expert_score_attr["bin_from"][i].upper() in negative_infinity_representation
            ):
                lower_bound = float("-inf")
            else:
                lower_bound = float(expert_score_attr["bin_from"][i])

            if (
                isinstance(expert_score_attr["bin_to"][i], str)
                and expert_score_attr["bin_to"][i].upper() in positive_infinity_representation
            ):
                upper_bound = float("inf")
            else:
                upper_bound = float(expert_score_attr["bin_to"][i])

            binning.append(
                AttributeBinNumerical(
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    id=i + 2,
                    value=expert_score_attr["value"][i],
                )
            )
        binning.append(AttributeBinNumerical(name=default_bin_name, id=0, value=default_score))
        binning.append(AttributeBinNumerical(name=PredictiveModelBinName.NULL, id=1, value=null_score))

        return binning

    def create_model_from_data_frame(self, df: "pl.DataFrame") -> "ExtendedPredictiveModel":
        from tarandm_analytics.predictive_models.extended_predictive_model import ExtendedPredictiveModel

        mandatory_columns = ["attribute", "bin_from", "bin_to", "categories", "value"]
        if any([p not in df.columns for p in mandatory_columns]):
            raise TypeError(f"Expert score csv missing one of the following columns: {mandatory_columns}.")

        import polars as pl

        if "missing" not in df.columns:
            df = df.with_columns(pl.lit(0).alias("missing"))
        else:
            df = df.with_columns(pl.col("missing").fill_null(0).alias("missing_filled"))
            df = df.drop("missing").rename({"missing_filled": "missing"})

        if "default" not in df.columns:
            df = df.with_columns(pl.lit(0).alias("default"))
        else:
            df = df.with_columns(pl.col("default").fill_null(0).alias("default_filled"))
            df = df.drop("default").rename({"default_filled": "default"})

        # Add intercept column if not included in df
        df = self._add_intercept_indicator_column(df)

        unique_attributes = self.get_unique_values_from_df_col(df, "attribute")
        unique_attributes_no_intercept = self.get_unique_values_from_df_col(
            df.filter(pl.col("is_intercept") == 0), "attribute"
        )

        attr_binnings = []

        if df["value"].is_null().sum() > 0:
            raise ValueError("Column 'value' must be always filled. Found missing values in 'value'.")

        cannot_determine_attr_type = df.with_columns(
            pl.when(
                (pl.col("is_intercept") == 0)
                & (pl.col("missing") == 0)
                & (pl.col("default") == 0)
                & (pl.col("bin_from").is_not_null())
                & (pl.col("bin_to").is_not_null())
                & (pl.col("categories").is_not_null())
            )
            .then(1)
            .otherwise(0)
            .alias("invalid_line")
        )
        if cannot_determine_attr_type["invalid_line"].sum() > 0:
            raise ValueError(
                "DataFrame contains attributes that have both interval borders and categories defined. Cannot determine "
                "if the attribute is NUMERICAL or CATEGORICAL."
            )

        undefined_binning = df.with_columns(
            pl.when(
                (pl.col("is_intercept") == 0)
                & (pl.col("missing") == 0)
                & (pl.col("default") == 0)
                & (pl.col("bin_from").is_null())
                & (pl.col("bin_to").is_null())
                & (pl.col("categories").is_null())
            )
            .then(1)
            .otherwise(0)
            .alias("invalid_line")
        )
        if undefined_binning["invalid_line"].sum() > 0:
            raise ValueError(
                "Some rows do not define neither interval borders nor categories and value in 'missing' is 0. Bin is "
                "insufficiently defined."
            )

        incomplete_numerical_binning = df.with_columns(
            pl.when(
                (pl.col("is_intercept") == 0)
                & (pl.col("missing") == 0)
                & (pl.col("default") == 0)
                & (pl.col("categories").is_null())
                & ((pl.col("bin_from").is_null()) | (pl.col("bin_to").is_null()))
            )
            .then(1)
            .otherwise(0)
            .alias("invalid_line")
        )
        if incomplete_numerical_binning["invalid_line"].sum() > 0:
            raise ValueError("Numerical attributes must have defined both 'bin_from' and 'bin_to' columns.")

        if not df["value"].dtype.is_numeric():
            raise ValueError(
                f"Column 'value' must contain numeric values. Provided column value is of type {df['value'].dtype}."
            )

        intercept = None
        intercept_name = None
        for attr in unique_attributes:
            expert_score_attr = df.filter(pl.col("attribute") == attr)
            null_score = 0.0
            default_score = 0.0

            if (expert_score_attr["is_intercept"] == 1).sum() > 0:
                intercept = expert_score_attr["value"].to_list()[0]
                intercept_name = expert_score_attr["attribute"].to_list()[0]
                continue
            elif (
                expert_score_attr.filter((pl.col("missing") == 0) & (pl.col("default") == 0))["categories"]
                .is_null()
                .sum()
                == 0
            ):
                attr_dtype = AttributeDataType.CATEGORICAL
                binning_definition = self.prepare_binning_categorical(
                    expert_score_attr=expert_score_attr, default_score=default_score, null_score=null_score
                )
            else:
                attr_dtype = AttributeDataType.NUMERICAL
                neg_inf_repr, pos_inf_repr = ModelExpertScore.get_allowed_infinity_representation()
                binning_definition = self.prepare_binning_numerical(
                    expert_score_attr=expert_score_attr,
                    negative_infinity_representation=neg_inf_repr,
                    positive_infinity_representation=pos_inf_repr,
                    default_score=default_score,
                    null_score=null_score,
                )

            attr_binnings.append(
                AttributeBinning(attribute=attr, attribute_data_type=attr_dtype, attribute_binning=binning_definition)
            )

        extended_predictive_model = ExtendedPredictiveModel(
            external_model=ModelExpertScore(
                type=PredictiveModelType.EXPERT_SCORE,
                feature_names=unique_attributes_no_intercept,
                intercept=intercept,
                intercept_name=intercept_name,
            ),
            attributes=unique_attributes_no_intercept,
        )
        extended_predictive_model.attribute_preprocessing.binning = attr_binnings
        extended_predictive_model.attributes = unique_attributes_no_intercept
        extended_predictive_model.predictive_model_type = PredictiveModelType.EXPERT_SCORE

        return extended_predictive_model

    def create_model_from_csv(
        self, filename: Union[io.StringIO, str], delimiter: str = ","
    ) -> "ExtendedPredictiveModel":
        """Expert score model can be defined by csv file. Function 'create_model_from_csv' loads expert score model from csv
        and create internal representation of the model compatible with TaranDM.

        csv file must contain following columns: 'predictor', 'bin_from', 'bin_to', 'categories', 'value'

        Numerical attributes in expert score model must have values 'bin_from' and 'bin_to' filled. Categorical attributes
        must have 'categories' column filled. Column 'value' should be always filled.

        For numerical attributes, values in 'bin_from' and 'bin_to' represent interval ('bin_from' ; 'bin_to'].
        """
        import polars as pl

        expert_score = pl.read_csv(source=filename, separator=delimiter)
        return self.create_model_from_data_frame(expert_score)

    def _validate_binning_defined_for_valid_attributes(
        self, attributes: List[str], attribute_binning: List[AttributeBinning]
    ) -> List[Dict[str, Any]]:
        unknown_attributes = set([b.attribute for b in attribute_binning]) - set(attributes)
        if len(unknown_attributes) > 0:
            logger.warning(
                f"Encountered binning for following attributes that are not available after transformations: "
                f"{unknown_attributes}. Binning of not those attributes will be ignored."
            )

        return [b for b in attribute_binning if b.attribute not in unknown_attributes]

    def _build_predictive_model(
        self, predictive_model: ModelType, request_data: RequestData
    ) -> "ExtendedPredictiveModel":
        from tarandm_analytics.predictive_models.extended_predictive_model import ExtendedPredictiveModel

        if request_data.model_type == PredictiveModelType.EXPERT_SCORE:
            extended_model = self.create_model_from_data_frame(df=cast("pl.DataFrame", predictive_model))
            extended_model.target = request_data.label_name
            extended_model.target_class = request_data.target_class
            extended_model.description = request_data.description
            extended_model.performance = request_data.model_performance
        else:
            serialized_model = self._get_dumped_model(
                model=predictive_model, model_type=request_data.model_type, attributes=request_data.predictors
            )
            if request_data.model_type == PredictiveModelType.PMML and "feature_names" not in serialized_model:
                serialized_model["feature_names"] = request_data.predictors

            # 1. basic validation of provided data
            if request_data.model_type == PredictiveModelType.RANDOM_FOREST and request_data.target_class is None:
                try:
                    request_data.target_class = serialized_model["random_forest_model"]["classes_"][-1]
                    logger.warning(
                        f"Parameter 'target_class' was not provided for RandomForest model. Value was automatically set "
                        f"to '{request_data.target_class}'"
                    )
                except Exception as e:
                    raise ValueError(
                        f"Parameter 'target_class' was not provided for random forest model and could not be "
                        f"auto-detected (Error in auto-detection: {e})."
                    )

            # 2. Prepare attribute preprocessing data
            # for validating if the binning is defined for valid attribute, we first need to get available attributes
            # (original attributes + attributes created in transformations)
            attribute_binning_preprocessed = self._prepare_attribute_binning(
                attribute_binning=request_data.attribute_binning
            )

            # Detect attributes if not provided
            if request_data.model_type != PredictiveModelType.PMML and len(request_data.predictors) == 0:
                request_data.predictors = self.automated_attribute_detection(
                    model=predictive_model,
                    transformations=request_data.attribute_transformation,
                    binnings=attribute_binning_preprocessed,
                    dummy_encoding=request_data.dummy_encoding,
                )

            attribute_after_transformations = request_data.predictors.copy()
            if request_data.attribute_transformation is not None:
                for transformation in request_data.attribute_transformation:
                    transformed_attribute_name = transformation.transformed_attribute_name
                    if (
                        transformed_attribute_name is not None
                        and transformed_attribute_name != transformation.attribute
                    ):
                        attribute_after_transformations.append(transformed_attribute_name)

            attribute_binning_preprocessed = self._validate_binning_defined_for_valid_attributes(
                attributes=attribute_after_transformations, attribute_binning=attribute_binning_preprocessed
            )

            attribute_preprocessing = AttributePreprocessing.model_validate(
                {
                    "transformations": request_data.attribute_transformation or [],
                    "binning": attribute_binning_preprocessed or [],
                    "dummy_encoding": request_data.dummy_encoding or [],
                }
            )
            if request_data.model_type == PredictiveModelType.PMML:
                extended_model_dict = {
                    "external_model": serialized_model,
                    "attributes": request_data.predictors,
                    "predictive_model_type": request_data.model_type,
                    "target": request_data.label_name,
                }

                extended_model = ExtendedPredictiveModel.model_validate(extended_model_dict)
            else:
                extended_model_dict = {
                    "external_model": serialized_model,
                    "predictive_model_type": request_data.model_type,
                    "attributes": request_data.predictors,
                    "target": request_data.label_name,
                    "target_class": request_data.target_class,
                    "attribute_preprocessing": attribute_preprocessing,
                    "description": request_data.description,
                    "performance": request_data.model_performance,
                    "monitoring": request_data.monitoring_data,
                }
                extended_model = ExtendedPredictiveModel.model_validate(extended_model_dict)
        return extended_model

    def build(
        self,
        model: ModelTypeWithPandas,
        attributes: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        data: Optional["pd.DataFrame"] = None,
        label_name: Optional[str] = None,
        target_class: Optional[str] = None,
        attribute_binning: Optional[Dict] = None,
        attribute_transformation: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        dummy_encoding: Optional[
            Union[
                List[Dict[str, Union[str, Dict[str, Union[str, bool]]]]], Dict[str, List[Dict[str, Union[str, bool]]]]
            ]
        ] = None,
        monitoring_data: Optional[Dict[str, List[Dict]]] = None,
        hyperparameters: Optional[Dict] = None,
        general_notes: Optional[Dict[str, Any]] = None,
        attribute_description: Optional[Dict[str, str]] = None,
        column_name_sample: Optional[str] = None,
        column_name_date: Optional[str] = None,
        column_name_prediction: Optional[str] = None,
        evaluate_performance: Optional[Dict[str, Union[str, List[str]]]] = None,
        learning_curves_data: Optional[Dict] = None,
        created_date: Optional[datetime.date] = None,
    ) -> "ExtendedPredictiveModel":
        """
        Function prepares input data for build model zip file, that is ready to be implemented in TaranDM software.
        Created input data will be sent to the TaranDM endpoint, through which final model zip file is returned.

        :param model: Trained predictive model. One of from "sklearn.ensemble.RandomForestClassifier",
        "sklearn.linear_model.LogisticRegression", "xgboost.Booster", "pd.DataFrame". "pd.DataFrame" represents expert
        scorecard model, where user manually defines values for predictor bins.
        :param attributes: List of model predictors before transformation or binning. For example if 'age' is binned
        into 'age_binned' and binned version enters the model, list of predictors should include 'age' (rather than
        'age_binned') and binning for age should be provided in 'attribute_binning' parameter.
        :param model_name: Name of the model (will be visible in TaranDM GUI).
        :param model_type: Type of the model. One of "XGB", "LOGISTIC_REGRESSION", "RANDOM_FOREST", "EXPERT_SCORE".
        :param data: Dataset used for model training. Required to calculate model performance, and descriptive
        statistics about development sample. Should contain all the predictors as they enter the model (after binning).
        :param label_name: Name of the target variable. Should be included in data to properly evaluate model
        performance.
        :param target_class: Target class predicted by the model.
        :param attribute_binning: Attribute binning (if applied). In inference phase, we first apply predictor
        transformation (if defined), then binning and dummy encoding. Resulting value is passed to model predict method.

        Binning should be provided as a dictionary with following structure:
        binning = {
            'numerical_predictor1': {
                'dtype': 'NUMERICAL',
                'bins': [-np.inf, 20, 35, 50, np.inf],
                'bin_vals': [1, 2, 3, 4, 1000],
                'null_val': 0,
                'binned_attribute_name': 'name_after_binning'
            },
            'categorical_predictor1': {
                'dtype': 'CATEGORICAL',
                'bins': [['M'], ['F']]',
                'bin_vals': [1, 2, 3, 4, 1000],
                'null_val': 0
            },
            ...
        }
        Keys of provided dictionary are names of the predictors. TaranDM supports 'NUMERICAL' and 'CATEGORICAL' data
        types of predictors. For numerical predictors, binning is defined by providing list of bin borders. For
        categorical predictors, binning is defined by providing list of lists. Inner lists define values that belong
        to each group. Both 'NUMERICAL' and 'CATEGORICAL' data types contain attributes 'bin_vals' and
        'null_val'. Those are values used for encoding the bins. 'null_val' is an encoding value for null values
        (missings).

        :param attribute_transformation: Transformation of the predictors. Transformation is applied before binning. If
        both transformation and binning are defined, predictor is first transformed and binning is applied on values
        obtained after transformation.

        Transformation should be provided as a dictionary with following structure:
        transformation = {
            'numerical_predictor1': '{numerical_predictor1} + 1'
            ...
        }
        In transformation formula, anything in "{}" is considered as predictor and will be replaced with predictor value
        during formula evaluation.

        :param dummy_encoding: Dummy encoding of predictors. Following for is required:
        dummy_encoding = {
            'feature_name': [
                {
                    'value': 'first_value_to_be_encoded',
                    'encoded_feature_name': 'name_of_created_dummy_feature_val1',
                    'use_for_undefined': False
                },
                {
                    'value': 'second_value_to_be_encoded',
                    'encoded_feature_name': 'name_of_created_dummy_feature_val1',
                    'use_for_undefined': True
                },
            ]
        }
        'use_for_undefined' is a boolean value - if True, then created dummy variable will have value 1 for unknown
        values (values not defined in other dummies).
        :param monitoring_data: Data for monitoring, including attribute's binning with bin frequency and bin target
        rate. Those data are used in monitoring for evaluation of stability in time (PSI).
        :param hyperparameters: Model hyperparameters.
        :param general_notes: Dictionary of general notes about the model. Notes will be displayed in GUI.
        :param attribute_description: Dictionary with description of predictors.
        :param column_name_sample: Name of the column in data, that defines different data sample types (train, test,
        etc.). If provided, sample statistics will be stored in model metadata.
        :param column_name_date: Name of the column in data, that defines time dimension. If provided, information about
        time range used in development sample data will be stored in model metadata.
        :param column_name_prediction: Name of the column in data, that holds model prediction. This column is used to
        evaluate model performance.
        :param evaluate_performance: Dictionary that defines performance to be evaluated - which target and over which
        sample types. Use following structure:

        evaluate_performance = {
            'label_3M': 'AUC',
            'label_12M': ['AUC', 'GINI']
        }
        :param learning_curves_data: Data for plotting learning curves plot in following structure:

        learning_curves_data = {
            'sample1': {
                'metric1': [
                    0.5,
                    0.4,
                    0.3
                ]
            },
            'sample2': {
                'metric1': [
                    0.6,
                    0.5,
                    0.4
                ]
            }
        }
        :return:

        ----------------------------

        Export predictive model as a zip file ready to import in TaranDM.

        :param request_data: Request data in the same form as output of `prepare_predictive_model_data` method. In fact,
        mentioned method provides a tuple, with request data on the first position and images on the second position.
        :param filename: File name of exported zip file
        :param images: Images to be exported with the model. Images are displayed in GUI with the model and they are
        returned by `prepare_predictive_model_data` method.
        :return:
        """
        import pandas as pd

        if isinstance(model, pd.DataFrame):
            import polars as pl

            model = pl.from_pandas(model)

        request_data = self.prepare_predictive_model_data(
            model=model,
            attributes=attributes,
            model_name=model_name,
            model_type=model_type,
            data=data,
            label_name=label_name,
            target_class=target_class,
            attribute_binning=attribute_binning,
            attribute_transformation=attribute_transformation,
            dummy_encoding=dummy_encoding,
            monitoring_data=monitoring_data,
            hyperparameters=hyperparameters,
            general_notes=general_notes,
            attribute_description=attribute_description,
            column_name_sample=column_name_sample,
            column_name_date=column_name_date,
            column_name_prediction=column_name_prediction,
            evaluate_performance=evaluate_performance,
            learning_curves_data=learning_curves_data,
            created_date=created_date,
        )
        return self._build_predictive_model(predictive_model=model, request_data=request_data)

    # def build(
    #     self,
    #     model: ModelTypeWithPandas,
    #     attributes: Optional[List[str]] = None,
    #     model_name: Optional[str] = None,
    #     model_type: Optional[PredictiveModelType] = None,
    #     data: Optional["pd.DataFrame"] = None,
    #     label_name: Optional[str] = None,
    #     target_class: Optional[str] = None,
    #     attribute_binning: Optional[Dict] = None,
    #     attribute_transformation: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
    #     dummy_encoding: Optional[
    #         Union[
    #             List[Dict[str, Union[str, Dict[str, Union[str, bool]]]]], Dict[str, List[Dict[str, Union[str, bool]]]]
    #         ]
    #     ] = None,
    #     monitoring_data: Optional[Dict[str, List[Dict]]] = None,
    #     hyperparameters: Optional[Dict] = None,
    #     general_notes: Optional[Dict[str, Any]] = None,
    #     attribute_description: Optional[Dict[str, str]] = None,
    #     column_name_sample: Optional[str] = None,
    #     column_name_date: Optional[str] = None,
    #     column_name_prediction: Optional[str] = None,
    #     evaluate_performance: Optional[Dict[str, Union[str, List[str]]]] = None,
    #     learning_curves_data: Optional[Dict] = None,
    # ) -> ExtendedPredictiveModel:
    #     """
    #     Function prepares input data for build model zip file, that is ready to be implemented in TaranDM software.
    #     Created input data will be sent to the TaranDM endpoint, through which final model zip file is returned.

    #     :param model: Trained predictive model. One of from "sklearn.ensemble.RandomForestClassifier",
    #     "sklearn.linear_model.LogisticRegression", "xgboost.Booster", "pd.DataFrame". "pd.DataFrame" represents expert
    #     scorecard model, where user manually defines values for predictor bins.
    #     :param attributes: List of model predictors before transformation or binning. For example if 'age' is binned
    #     into 'age_binned' and binned version enters the model, list of predictors should include 'age' (rather than
    #     'age_binned') and binning for age should be provided in 'attribute_binning' parameter.
    #     :param model_name: Name of the model (will be visible in TaranDM GUI).
    #     :param model_type: Type of the model.
    #     :param data: Dataset used for model training. Required to calculate model performance, and descriptive
    #     statistics about development sample. Should contain all the predictors as they enter the model (after binning).
    #     :param label_name: Name of the target variable. Should be included in data to properly evaluate model
    #     performance.
    #     :param target_class: Target class predicted by the model.
    #     :param attribute_binning: Attribute binning (if applied). In inference phase, we first apply predictor
    #     transformation (if defined), then binning and dummy encoding. Resulting value is passed to model predict method.

    #     Binning should be provided as a dictionary with following structure:
    #     binning = {
    #         'numerical_predictor1': {
    #             'dtype': 'NUMERICAL',
    #             'bins': [-np.inf, 20, 35, 50, np.inf],
    #             'bin_vals': [1, 2, 3, 4, 1000],
    #             'null_val': 0,
    #             'binned_attribute_name': 'name_after_binning'
    #         },
    #         'categorical_predictor1': {
    #             'dtype': 'CATEGORICAL',
    #             'bins': [['M'], ['F']]',
    #             'bin_vals': [1, 2, 3, 4, 1000],
    #             'null_val': 0
    #         },
    #         ...
    #     }
    #     Keys of provided dictionary are names of the predictors. TaranDM supports 'NUMERICAL' and 'CATEGORICAL' data
    #     types of predictors. For numerical predictors, binning is defined by providing list of bin borders. For
    #     categorical predictors, binning is defined by providing list of lists. Inner lists define values that belong
    #     to each group. Both 'NUMERICAL' and 'CATEGORICAL' data types contain attributes 'bin_vals' and
    #     'null_val'. Those are values used for encoding the bins. 'null_val' is an encoding value for null values
    #     (missings).

    #     :param attribute_transformation: Transformation of the predictors. Transformation is applied before binning. If
    #     both transformation and binning are defined, predictor is first transformed and binning is applied on values
    #     obtained after transformation.

    #     Transformation should be provided as a dictionary with following structure:
    #     transformation = {
    #         'numerical_predictor1': '{numerical_predictor1} + 1'
    #         ...
    #     }
    #     In transformation formula, anything in "{}" is considered as predictor and will be replaced with predictor value
    #     during formula evaluation.

    #     :param dummy_encoding: Dummy encoding of predictors. Following for is required:
    #     dummy_encoding = {
    #         'feature_name': [
    #             {
    #                 'value': 'first_value_to_be_encoded',
    #                 'encoded_feature_name': 'name_of_created_dummy_feature_val1',
    #                 'use_for_undefined': False
    #             },
    #             {
    #                 'value': 'second_value_to_be_encoded',
    #                 'encoded_feature_name': 'name_of_created_dummy_feature_val1',
    #                 'use_for_undefined': True
    #             },
    #         ]
    #     }
    #     'use_for_undefined' is a boolean value - if True, then created dummy variable will have value 1 for unknown
    #     values (values not defined in other dummies).
    #     :param monitoring_data: Data for monitoring, including attribute's binning with bin frequency and bin target
    #     rate. Those data are used in monitoring for evaluation of stability in time (PSI).
    #     :param hyperparameters: Model hyperparameters.
    #     :param general_notes: Dictionary of general notes about the model. Notes will be displayed in GUI.
    #     :param attribute_description: Dictionary with description of predictors.
    #     :param column_name_sample: Name of the column in data, that defines different data sample types (train, test,
    #     etc.). If provided, sample statistics will be stored in model metadata.
    #     :param column_name_date: Name of the column in data, that defines time dimension. If provided, information about
    #     time range used in development sample data will be stored in model metadata.
    #     :param column_name_prediction: Name of the column in data, that holds model prediction. This column is used to
    #     evaluate model performance.
    #     :param evaluate_performance: Dictionary that defines performance to be evaluated - which target and over which
    #     sample types. Use following structure:

    #     evaluate_performance = {
    #         'label_3M': 'AUC',
    #         'label_12M': ['AUC', 'GINI']
    #     }
    #     :param learning_curves_data: Data for plotting learning curves plot in following structure:

    #     learning_curves_data = {
    #         'sample1': {
    #             'metric1': [
    #                 0.5,
    #                 0.4,
    #                 0.3
    #             ]
    #         },
    #         'sample2': {
    #             'metric1': [
    #                 0.6,
    #                 0.5,
    #                 0.4
    #             ]
    #         }
    #     }
    #     :return:
    #     """

    #     # Convert pandas to polars
    #     import pandas as pd

    #     if isinstance(model, pd.DataFrame):
    #         import polars as pl

    #         model = pl.from_pandas(model)

    #     predictive_model_type = self._get_model_type(model_type=model_type, model=model)

    #     # Restructure dummy encoding and transformations into new format if provided in old format
    #     dummy_encoding_formatted = self._format_dummy_encoding(dummy_encoding=dummy_encoding)
    #     transformations_formatted = self._format_transformations(transformations=attribute_transformation)

    #     external_model = self._get_dumped_model(model=model, model_type=predictive_model_type, attributes=attributes)
    #     feature_names = self._validate_feature_names(
    #         attributes=attributes,
    #         transformations=transformations_formatted,
    #         attribute_binning=attribute_binning,
    #         dummy_encoding=dummy_encoding_formatted,
    #         model=model,
    #     )
    #     attribute_preprocessing = self._prepare_attribute_preprocessing(
    #         model=model,
    #         predictive_model_type=predictive_model_type,
    #         feature_names=feature_names,
    #         attribute_binning=attribute_binning,
    #         transformations=transformations_formatted,
    #         dummy_encoding=dummy_encoding_formatted,
    #     )

    #     images = self._generate_images(
    #         data=data,
    #         model=model,
    #         model_type=predictive_model_type,
    #         target_class=target_class,
    #         learning_curves_data=learning_curves_data,
    #     )
    #     sample_metadata = self._get_sample_metadata(
    #         data=data,
    #         column_name_label=label_name,
    #         column_name_sample=column_name_sample,
    #         column_name_date=column_name_date,
    #     )
    #     description = PredictiveModelDescription(
    #         predictive_model_name=model_name,
    #         predictive_model_created=datetime.date.today(),
    #         sample_metadata=sample_metadata,
    #         attribute_description=attribute_description,
    #         hyperparameters=hyperparameters,
    #         number_of_trainable_parameters=None,  # TODO: Not supported here
    #         general_notes=general_notes,
    #         attached_images=images,
    #     )
    #     performance = self._get_predictive_model_performance(
    #         data=data,
    #         column_name_sample=column_name_sample,
    #         column_name_prediction=column_name_prediction,
    #         evaluate_performance=evaluate_performance,
    #     )

    #     if monitoring_data is None:
    #         monitoring_data = {}

    #     return ExtendedPredictiveModel(
    #         external_model=external_model,
    #         attributes=feature_names,
    #         predictive_model_type=predictive_model_type,
    #         target=label_name,
    #         target_class=target_class,
    #         attribute_preprocessing=attribute_preprocessing,
    #         description=description,
    #         performance=performance,
    #         monitoring=(PredictiveModelMonitoring.model_validate(monitoring_data)),
    #     )

    def automated_attribute_detection(
        self,
        model: ModelType,
        transformations: Optional[List[AttributeTransformation]],
        binnings: Optional[List[AttributeBinning]],
        dummy_encoding: Optional[List[PredictiveModelDummyEncoding]],
    ) -> List[str]:
        from sklearn.base import BaseEstimator
        from xgboost import Booster

        if isinstance(model, Booster):
            model_attributes = list(model.feature_names or [])
        elif isinstance(model, BaseEstimator):
            if hasattr(model, "feature_names_in_"):
                model_attributes = list(model.feature_names_in_)
            else:
                raise ValueError(
                    "Model attribute names were not provided and could not be detected automatically. Model "
                    "was recognized as scikit-learn estimator. Tried to collect model attribute names from "
                    "property 'feature_names_in_'. This property is available in scikit-learn since version "
                    "0.24."
                )
        else:
            raise ValueError("Model attribute names were not provided and could not be detected automatically.")

        # We detected feature that enters the model. First, we detect features as they were before dummy encoding
        names_encoded_to_orig = {}
        if dummy_encoding is not None:
            for encoding in dummy_encoding:
                for e in encoding.encoding:
                    names_encoded_to_orig[e.encoded_feature_name] = encoding.attribute

            model_attributes = list(set([names_encoded_to_orig.get(a, a) for a in model_attributes]))

        # After getting attributes before dummy encoding we extract attributes before binning
        if binnings is not None:
            for binning in binnings:
                binned_attribute_name = binning.binned_attribute_name
                if binned_attribute_name is not None and binned_attribute_name != binning.attribute:
                    if binned_attribute_name not in model_attributes:
                        raise ValueError(
                            "Model attribute names were not provided and could not be detected automatically."
                        )
                    model_attributes = [a for a in model_attributes if a != binned_attribute_name]
                    if binning.attribute not in model_attributes:
                        # there can be an attribute x and x_squared -> both used in model -> if we would append, we
                        # would have age twice in model attributes
                        model_attributes.append(binning.attribute)

        # Finally, we extract original attribute names by extracting names before transformations; there could be multiple
        # transformations applied over one predictor
        if transformations is not None:
            for transformation in transformations:
                transformed_attribute_name = transformation.transformed_attribute_name
                if transformed_attribute_name is not None and transformed_attribute_name != transformation.attribute:
                    if transformed_attribute_name not in model_attributes:
                        raise ValueError(
                            "Model attribute names were not provided and could not be detected automatically."
                        )
                    model_attributes = [a for a in model_attributes if a != transformed_attribute_name]
                    if transformation.attribute not in model_attributes:
                        model_attributes.append(transformation.attribute)

        logger.info("Model attributes were detected automatically.")
        return model_attributes

    def _prepare_attribute_preprocessing(
        self,
        model: ModelType,
        predictive_model_type: PredictiveModelType,
        feature_names: Optional[List[str]],
        attribute_binning: Optional[Dict[str, Any]],
        transformations: Optional[List[AttributeTransformation]],
        dummy_encoding: Optional[List[PredictiveModelDummyEncoding]],
    ) -> AttributePreprocessing:
        if feature_names is None:
            logger.warning("No feature names provided. Will use empty list.")
            feature_names = []

        if attribute_binning is None:
            logger.warning("No attribute binning provided. Will use empty list.")
            attribute_binning = {}

        binning = self._prepare_binning(feature_names=feature_names, attribute_binning=attribute_binning)

        if predictive_model_type != PredictiveModelType.EXPERT_SCORE:
            if len(feature_names) == 0:
                feature_names = self.automated_attribute_detection(
                    model=model,
                    transformations=transformations,
                    binnings=binning,
                    dummy_encoding=dummy_encoding,
                )
        else:
            return AttributePreprocessing()

        if transformations is None:
            transformations = []

        if dummy_encoding is None:
            dummy_encoding = []

        return AttributePreprocessing(
            transformations=transformations,
            binning=binning,
            dummy_encoding=dummy_encoding,
        )

    def _prepare_binning(self, feature_names: List[str], attribute_binning: Dict[str, Any]) -> List[AttributeBinning]:
        binning = AttributePreprocessing.add_attribute_binning(attributes_binning=attribute_binning)

        unknown_attributes = set([b.attribute for b in binning]) - set(feature_names)
        if len(unknown_attributes) > 0:
            logger.warning(
                f"Encountered binning for following attributes that are not available after transformations: "
                f"{unknown_attributes}. Binning of not those attributes will be ignored."
            )

        return [b for b in binning if b.attribute not in unknown_attributes]

    def _format_transformations(
        self,
        transformations: Optional[Union[Dict[str, str], List[Dict[str, str]]]],
    ) -> Optional[List[AttributeTransformation]]:
        if transformations is None:
            return None

        try:
            if isinstance(transformations, dict):
                transformations_formatted = []
                for attr, transformation in transformations.items():
                    transformations_formatted.append(
                        AttributeTransformation(attribute=attr, transformation=transformation)
                    )
                return transformations_formatted
            elif isinstance(transformations, list):
                return [AttributeTransformation.model_validate(item) for item in transformations]
        except Exception:
            message = """
            Transformations were provided in incorrect format. We support two formats:
            example_transformation_format_1 = [
                {
                    "attribute": "age",
                    "transformation": "{age} * {age}"
                    "transformed_attribute_name": "age_squared"
                }
            ]

            example_transformation_format_2 = {
                "age": "{age} * {age}" # age squared values will rewrite values in age attribute
            }
            """
            raise ValueError(message)

    def _format_dummy_encoding(
        self,
        dummy_encoding: Optional[
            Union[
                List[Dict[str, Union[str, Dict[str, Union[str, bool]]]]], Dict[str, List[Dict[str, Union[str, bool]]]]
            ]
        ],
    ) -> Optional[List[PredictiveModelDummyEncoding]]:
        if dummy_encoding is None:
            return None

        try:
            if isinstance(dummy_encoding, dict):
                dummy_encoding_formatted = []
                for attr, enc in dummy_encoding.items():
                    dummy_encoding_formatted.append(
                        PredictiveModelDummyEncoding(
                            attribute=attr,
                            encoding=[PredictiveModelDummyEncodingSingleValue.model_validate(item) for item in enc],
                        )
                    )
                return dummy_encoding_formatted
            elif isinstance(dummy_encoding, list):
                return [PredictiveModelDummyEncoding.model_validate(item) for item in dummy_encoding]

        except Exception:
            message = """
            Dummy encoding was provided in incorrect format. We support two formats:
            example_encoding_format_1 = [
                {
                    "attribute": "education",
                    "encoding": [
                        {
                            "value": "UNIVERSITY",
                            "encoded_feature_name": "education_university",
                            "use_for_undefined": False
                        },
                        {
                            "value': 'HIGH_SCHOOL",
                            "encoded_feature_name": "education_high_school",
                            "use_for_undefined": True
                        },
                    ]
                }
            ]

            example_encoding_format_2 = {
                "education": [
                    {
                        "value": "UNIVERSITY",
                        "encoded_feature_name": "education_university",
                        "use_for_undefined": False
                    },
                    {
                        "value': 'HIGH_SCHOOL",
                        "encoded_feature_name": "education_high_school",
                        "use_for_undefined": True
                    },
                ]
            }
            """
            raise ValueError(message)

    def _evaluate_auc(self, label: "np.ndarray", prediction: "np.ndarray") -> Optional[float]:
        if len(set(label)) == 1:
            logger.warning(
                "Evaluating model AUC: Only one class present in y_true. ROC AUC score is not defined in " "that case"
            )
            return None
        elif len(set(label)) > 2:
            logger.warning(
                f"Evaluating model AUC: AUC evaluation supports only binary labels. Provided label contains "
                f"{len(set(label))} unique values."
            )
            return None

        from sklearn.metrics import roc_auc_score

        try:
            return roc_auc_score(y_true=label, y_score=prediction)
        except Exception as e:
            logger.warning(f"Evaluating model AUC: Failed to evaluate 'roc_auc_score' function with error: {e}.")
            return None

    def _evaluate_gini(self, label: "np.ndarray", prediction: "np.ndarray") -> Optional[float]:
        auc = self._evaluate_auc(label, prediction)
        if auc is None:
            return None
        else:
            return 2 * auc - 1

    def _get_predictive_model_performance(
        self,
        data: Optional["pd.DataFrame"],
        column_name_sample: Optional[str],
        column_name_prediction: Optional[str],
        evaluate_performance: Optional[Dict[str, Union[str, List[str]]]],
    ) -> PredictiveModelPerformance:
        """
        Function calculates different performance metrics of predictive model.

        :param data: Dataset to be used for evaluating performance.
        :param column_name_sample: Name of the column inside 'data' that distinguishes type of data samples. Column can
               contain for instance values 'train', 'valid', 'test'. This will define which observations belong to train
               set, validation set and test set.
        :param column_name_prediction: Name of the column inside 'data' that holds values of predictive model prediction.
        :param evaluate_performance: Dictionary that defines what metrics should be evaluated. Keys in dictionary must refer
               to columns in 'data' that will be used as true label. Multiple true label columns can be defined. This can be
               useful for instance in situations when we have binary labels (indicators of an event) calculated over
               different time windows. In values under each key, metrics to be evaluated are defined.

               Example:
               evaluate_performance = {
                   'label_3M': 'AUC',
                   'label_12M': ['AUC', 'GINI']
               }
        :return: Dictionary with calculated performance metrics.
        """
        if data is None:
            logger.warning(
                "Preparing model performance data: No dataset was provided. Cannot evaluate model " "performance."
            )
            return PredictiveModelPerformance()
        if len(data) == 0:
            logger.warning(
                "Preparing model performance data: Provided dataset has 0 observations. Cannot evaluate "
                "model performance."
            )
            return PredictiveModelPerformance()

        message_common_part = (
            "Evaluating model performance: To evaluate model performance, provided dataset "
            "should contain a column with generated model predictions. Name of prediction column "
            "should be provided through 'column_name_prediction' parameter of "
            "'prepare_predictive_model_data' method."
        )
        if column_name_prediction is None or column_name_prediction not in data.columns:
            logger.warning(
                f"{message_common_part} Provided name of the column that holds predictions ('{column_name_prediction}')"
                f" is not in provided dataset. Cannot evaluate model performance."
            )
            return PredictiveModelPerformance()

        if column_name_sample is None:
            logger.warning(
                "Evaluating model performance: Column name with sample type was not provided. All observations will be "
                "treated as training data."
            )
            column_name_sample = self._generate_sample_type_column_name(data=data)
            data[column_name_sample] = "train"
        elif column_name_sample not in data.columns:
            logger.warning(
                f"Evaluating model performance: Provided column name with sample type '{column_name_sample}' does not "
                f"exist in data. All observations will be treated as training data."
            )
            # _generate_sample_type_column_name makes sure that it does not overwrite existing column
            column_name_sample = self._generate_sample_type_column_name(data=data)
            data[column_name_sample] = "train"

        implemented_performance_metrics: Dict[
            PerformanceMetrics, Callable[[np.ndarray, np.ndarray], Optional[float]]
        ] = {
            PerformanceMetrics.AUC: self._evaluate_auc,
            PerformanceMetrics.GINI: self._evaluate_gini,
        }

        performance = []
        included_sample_types = data[column_name_sample].unique()
        if evaluate_performance is None:
            evaluate_performance = {}

        for label, metrics in evaluate_performance.items():
            if isinstance(metrics, str):
                metrics = [metrics]

            for sample in included_sample_types:
                mask = data[column_name_sample] == sample
                performance_by_metric = {}
                for metric_str in metrics:
                    metric = PerformanceMetrics(metric_str.upper())
                    if metric not in implemented_performance_metrics:
                        logger.warning(
                            f"Evaluating model performance: Requested metric '{metric_str}' is not supported. Cannot "
                            f"evaluate '{metric}' for '{sample}' data sample. Supported performance metrices are: "
                            f"{', '.join(implemented_performance_metrics)}"
                        )
                        continue

                    if label not in data.columns:
                        logger.warning(
                            f"Evaluating model performance: Label '{label}' was not found in provided dataset. Cannot "
                            f"evaluate '{metric}' for '{sample}' data sample."
                        )
                        continue

                    evaluated_metric = implemented_performance_metrics[metric](
                        data[mask][label], data[mask][column_name_prediction]
                    )
                    if evaluated_metric is None:
                        continue
                    performance_by_metric[metric] = evaluated_metric

                if performance_by_metric:
                    performance.append(
                        SamplePerformance(
                            target=label,
                            sample=SampleType(sample.upper()),
                            performance=performance_by_metric,
                        )
                    )

        return PredictiveModelPerformance(
            sample_performance=performance,
            performance_metrics=sorted(list(implemented_performance_metrics.keys())),
        )

    def _generate_sample_type_column_name(self, data: "pd.DataFrame") -> str:
        if "sample" not in data.columns:
            return "sample"
        else:
            for i in range(1, 10000):
                if f"sample_{i}" not in data.columns:
                    return f"sample_{i}"
        return "column_with_sample_type"

    def _get_sample_metadata(
        self,
        data: Optional["pd.DataFrame"],
        column_name_label: Optional[str] = None,
        column_name_sample: Optional[str] = None,
        column_name_date: Optional[str] = None,
    ) -> Optional[List[SampleDescription]]:
        """
        Function evaluates different descriptive information about model development data sample, such as what time range
        was used, what are the frequencies of label classes and other.

        :param data: Dataset to be used for descriptive info evaluation.
        :param column_name_label: Name of the column inside 'data' that stores labels.
        :param column_name_sample: Name of the column inside 'data' that distinguishes type of data samples. Column can
               contain for instance values 'train', 'valid', 'test'. This will define which observations belong to train
               set, validation set and test set.
        :param column_name_date: Name of the column inside 'data' that stores dates related to observations.
        :return: Dictionary with descriptive info data.
        """
        if data is None:
            logger.warning(
                "Preparing sample descriptions: No dataset was provided. Cannot evaluate sample description " "data."
            )
            return None
        elif len(data) == 0:
            logger.warning(
                "Preparing sample descriptions: Provided dataset has 0 observations. Cannot evaluate sample "
                "description data."
            )
            return None

        if column_name_sample is None:
            logger.warning(
                "Preparing sample descriptions: Column name with sample type was not provided. All observations will "
                "be treated as training data."
            )
            # _generate_sample_type_column_name makes sure that it does not overwrite existing column
            column_name_sample = self._generate_sample_type_column_name(data=data)
            data[column_name_sample] = "train"
        elif column_name_sample not in data.columns:
            logger.warning(
                f"Preparing sample descriptions: Provided column name with sample type '{column_name_sample}' does not "
                f"exist in data. All observations will be treated as training data."
            )
            # _generate_sample_type_column_name makes sure that it does not overwrite existing column
            column_name_sample = self._generate_sample_type_column_name(data=data)
            data[column_name_sample] = "train"

        date_available = True
        if column_name_date is None:
            logger.warning(
                "Preparing sample descriptions: Date column name (parameter 'column_name_date') was not provided. Time "
                "related metadata will not be evaluated."
            )
            date_available = False
        elif column_name_date not in data.columns:
            logger.warning(
                f"Preparing sample descriptions: Provided date column name '{column_name_date}' does not exist in "
                f"data. Time related metadata will not be evaluated."
            )
            date_available = False
        elif data[column_name_date].dtype != "<M8[ns]":
            logger.warning(
                f"Preparing sample descriptions: Provided date column name '{column_name_date}' is of type "
                f"{data[column_name_date].dtype.__str__()}. Required type is '<M8[ns]'. Time related metadata will not "
                f"be evaluated."
            )
            date_available = False

        label_available = True
        label_binary = True
        if column_name_label is None:
            logger.warning(
                "Preparing sample descriptions: Label column name was not provided. Label related metadata "
                "will not be evaluated."
            )
            label_available = False
        elif column_name_label not in data.columns:
            logger.warning(
                f"Preparing sample descriptions: Provided label column name '{column_name_label}' does not exist in "
                f"data. Label related metadata will not be evaluated."
            )
            label_available = False
        elif data[column_name_label].nunique() != 2:
            label_binary = False

        included_sample_types = data[column_name_sample].unique()

        result = []
        for sample_type in included_sample_types:
            sample_meta = SampleDescription(sample_type=SampleType(sample_type.upper()))
            mask = data[column_name_sample] == sample_type
            sample_meta.number_of_observations = len(data[mask])

            if date_available:
                sample_meta.first_date = data[mask][column_name_date].min().strftime(format="%Y-%m-%d")
                sample_meta.last_date = data[mask][column_name_date].max().strftime(format="%Y-%m-%d")

            if label_available and label_binary:
                sample_meta.label_class_frequency = []
                for label_class in data[column_name_label].unique().tolist():
                    sample_meta.label_class_frequency.append(
                        ClassFrequency(
                            label_class=label_class,
                            number_of_observations=len(data[mask & (data[column_name_label] == label_class)]),
                        )
                    )
            result.append(sample_meta)

        return result

    def _generate_model_name(self, model_type: str) -> str:
        return f"{model_type.lower()}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _generate_images(
        self,
        data: "pd.DataFrame",
        model: ModelType,
        model_type: PredictiveModelType,
        target_class: Optional[str] = None,
        learning_curves_data: Optional[Dict] = None,
    ) -> List[AttachedImage]:
        images = []
        try:
            img = None
            if model_type == PredictiveModelType.LOGISTIC_REGRESSION:
                img = shap_summary_plot_logistic_regression(model=model, data=data)
            elif model_type == PredictiveModelType.XGB:
                img = shap_summary_plot_xgboost(model=cast(Booster, model), data=data)
            elif model_type == PredictiveModelType.RANDOM_FOREST:
                img = shap_summary_plot_random_forest(model=model, data=data, target_class=target_class)
            if img is not None:
                img.seek(0)
                images.append(AttachedImage(filename="shap_summary.svg", type="shap_summary", image=img.read()))
        except Exception as e:
            logger.warning(f"Failed to generate Shap summary plot: {e}")

        if model_type == PredictiveModelType.XGB:
            if learning_curves_data is None or len(learning_curves_data) == 0:
                logger.warning("Skipping learning curves plot - no data provided.")
            else:
                try:
                    img = learning_curves_plot(
                        model=cast(Booster, model), evaluations_result=learning_curves_data, metric=None
                    )
                    img.seek(0)
                    images.append(
                        AttachedImage(filename="learning_curves.svg", type="learning_curves", image=img.read())
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate learning curves plot: {e}")

        return images

    def get_monitoring_data(
        self,
        data: "pd.DataFrame",
        attributes: List[str],
        label_name: str,
        model_output_name: Optional[str] = None,
        binning: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[AttributeBinning] | AttributeBinning | None]:
        """
        Method prepares monitoring data to be exported with the model. They are important for monitoring stability of
        predictors and predictions. Predictor binning can be provided. If not, then it is created automatically
        (using percentiles for numerical predictors and n most frequent categories for categorical predictors).

        :param data: Data used for creating binning and calculating bin frequency and target rate.
        :param attributes: Attributes for which monitoring data will be prepared.
        :param label_name: Name of the target column in `data`.
        :param model_output_name: Name of the column with model prediction. If provided, monitoring data for prediction
        are prepared.
        :param binning: Pre-defined binning. If provided, monitoring will use this binning instead of automatic binning.
        Should be of following form:
        binning = {
            'numerical_predictor1': {
                'dtype': 'NUMERICAL',
                'bins': [-np.inf, 20, 35, 50, np.inf],
                'bin_vals': [1, 2, 3, 4, 1000],
                'null_val': 0,
                'binned_attribute_name': 'name_after_binning'
            },
            'categorical_predictor1': {
                'dtype': 'CATEGORICAL',
                'bins': [['M'], ['F']]',
                'bin_vals': [1, 2, 3, 4, 1000],
                'null_val': 0
            },
            ...
        }
        :return: Dictionary with monitoring data.
        """

        if binning is None:
            binning = {}

        import pandas as pd

        monitoring_data = []
        for attr in attributes:
            if attr not in data.columns:
                logger.warning(
                    f"Attribute {attr} was not found in provided dataset. Skipping preparation of monitoring "
                    f"data for this attribute."
                )
            if pd.api.types.is_numeric_dtype(data[attr].dtype):
                monitoring_data.append(
                    self.create_numerical_attribute_binning(
                        data=data,
                        col_attribute=attr,
                        col_target=label_name,
                        bins=binning.get(attr, {}).get("bins", None),
                    )
                )
            else:
                monitoring_data.append(
                    self.create_categorical_attribute_binning(
                        data=data,
                        col_attribute=attr,
                        col_target=label_name,
                        categories=binning.get(attr, {}).get("categories", None),
                    )
                )

        model_output_monitoring_data = None
        if model_output_name is not None:
            if model_output_name not in data.columns:
                logger.warning(
                    f"Model output column {model_output_name} was not found in provided dataset. Skipping preparation of monitoring "
                    f"data for model output."
                )
            else:
                if pd.api.types.is_numeric_dtype(data[model_output_name].dtype):
                    model_output_monitoring_data = self.create_numerical_attribute_binning(
                        data=data,
                        col_attribute=model_output_name,
                        col_target=label_name,
                        bins=binning.get(model_output_name, {}).get("bins", None),
                        n_bins=10,
                    )
                else:
                    logger.warning(
                        f"Model output column {model_output_name} is expected to be numerical. Non-numerical type"
                        f"{data[model_output_name].dtype} was provided."
                    )

        return {"binning": monitoring_data, "predictive_model_output_binning": model_output_monitoring_data}

    def create_numerical_attribute_binning(
        self,
        data: "pd.DataFrame",
        col_attribute: str,
        col_target: str,
        n_bins: int = 7,
        bins: Optional[List[Union[int, float]]] = None,
    ) -> AttributeBinning:
        """Create attribute binning for monitoring purposes. Bins are established to contain similar share of population
        (based on percentiles).

        :param: data: Data sample to be used for binning creation.
        :param: col_attribute: Attribute's name.
        :param: col_target: Name of the target.
        :param: n_bins: Number of bins to be created.
        :return: AttributeBinning object
        """

        # for numerical attributes, n same frequent bins are defined
        import numpy as np

        if bins is None:
            if len(data[col_attribute].unique()) > n_bins:
                bins = list(
                    np.unique(
                        np.percentile(
                            data[data[col_attribute].notnull()][col_attribute], np.linspace(0, 100, n_bins + 1)
                        )
                    )
                )
                bins[0] = -np.inf
                bins[-1] = np.inf
            else:
                bins = sorted(data[col_attribute].unique().tolist())
                bins.insert(0, -np.inf)
                bins.append(np.inf)

        frequency_null, target_rate_null = self._get_numerical_bin_frequency_and_target_rate(
            data=data, col_attribute=col_attribute, col_target=col_target, lower_bound=None, upper_bound=None
        )
        attribute_bins: List[AttributeBinNumerical | AttributeBinCategorical] = [
            AttributeBinNumerical(
                lower_bound=None,
                upper_bound=None,
                frequency=0.0,
                target_rate=0.0,
                id=0,
                name="0_default",
            ),
            AttributeBinNumerical(
                lower_bound=None,
                upper_bound=None,
                frequency=frequency_null,
                target_rate=target_rate_null,
                id=1,
                name="1_null",
            ),
        ]
        for i in range(len(bins) - 1):
            lower_bound = bins[i]
            upper_bound = bins[i + 1]

            frequency, target_rate = self._get_numerical_bin_frequency_and_target_rate(
                data=data,
                col_attribute=col_attribute,
                col_target=col_target,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )
            binning = AttributeBinNumerical(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                frequency=frequency,
                target_rate=target_rate,
                id=i + 2,
                name=f"{i + 2}_({get_number_formatting(lower_bound)};{get_number_formatting(upper_bound)})",
            )
            attribute_bins.append(binning)

        return AttributeBinning(
            attribute=col_attribute,
            attribute_data_type=AttributeDataType.NUMERICAL,
            attribute_binning=attribute_bins,
        )

    def create_categorical_attribute_binning(
        self,
        data: "pd.DataFrame",
        col_attribute: str,
        col_target: str,
        n_bins: int = 7,
        categories: Optional[List[List[str]]] = None,
    ) -> AttributeBinning:
        """Create attribute binning for monitoring purposes. First n_bins - 1 most frequent categories will have
        separate bin, the remaining categories will be joint in another bin.

        :param: data: Data sample to be used for binning creation.
        :param: col_attribute: Attribute's name.
        :param: col_target: Name of the target.
        :param: n_bins: Number of bins to be created.
        :return: AttributeBinning object
        """

        # for numerical attributes, n same frequent bins are defined

        if categories is None:
            categories_raw = [
                "null" if str(cat) == "nan" else cat
                for cat in data[col_attribute].value_counts(sort=True, ascending=False, dropna=True).index
            ]

            categories = []
            for i in range(min(n_bins - 1, len(categories_raw))):
                categories.append([categories_raw[i]])

            if len(categories_raw) >= n_bins:
                categories.append(categories_raw[n_bins:])

        frequency_null, target_rate_null = self._get_categorical_bin_frequency_and_target_rate(
            data=data, col_attribute=col_attribute, col_target=col_target, bin_categories=None
        )
        attribute_bins: List[AttributeBinNumerical | AttributeBinCategorical] = [
            AttributeBinCategorical(
                categories=None,
                frequency=0,
                target_rate=0,
                id=0,
                name="0_default",
            ),
            AttributeBinCategorical(
                categories=["null"],
                frequency=frequency_null,
                target_rate=target_rate_null,
                id=1,
                name="1_null",
            ),
        ]
        for i in range(len(categories)):
            frequency, target_rate = self._get_categorical_bin_frequency_and_target_rate(
                data=data, col_attribute=col_attribute, col_target=col_target, bin_categories=categories[i]
            )

            categories_str = ",".join(categories[i])
            binning = AttributeBinCategorical(
                categories=categories[i],
                frequency=frequency,
                target_rate=target_rate,
                id=i + 2,
                name=f"{i + 2}_{{{categories_str}}}",
            )
            attribute_bins.append(binning)

        return AttributeBinning(
            attribute=col_attribute,
            attribute_data_type=AttributeDataType.CATEGORICAL,
            attribute_binning=attribute_bins,
        )

    def _get_numerical_bin_frequency_and_target_rate(
        self,
        data: "pd.DataFrame",
        col_attribute: str,
        col_target: str,
        lower_bound: Optional[Union[int, float]],
        upper_bound: Optional[Union[int, float]],
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate frequency and target rate for given bin of numerical attribute.

        :param: data: Data for calculating bin frequencies and respective target rate.
        :param: col_attribute: Name of the attribute.
        :param: col_target: Name of the target.
        :param: lower_bound: Lower bound of a bin.
        :param: upper_bound: Upper bound of a bin.
        :return:
        """
        total_count = len(data)
        if total_count == 0:
            logger.warning(
                f"Cannot calculate bin frequency and target rate for {col_attribute}. Provided data contains "
                f"no observations."
            )
            return None, None

        if lower_bound is None and upper_bound is None:
            mask_bin = data[col_attribute].isnull()
        else:
            mask_bin = (data[col_attribute] > lower_bound) & (data[col_attribute] <= upper_bound)

        bin_frequency = mask_bin.sum()
        bin_target_frequency = (mask_bin & (data[col_target] == 1)).sum()

        if bin_target_frequency == 0:
            if lower_bound is None and upper_bound is None:
                logger.info(f"Target rate for column {col_attribute} and bin 'null' is zero.")
            else:
                logger.info(f"Target rate for column {col_attribute} and bin ({lower_bound};{upper_bound}] is zero.")
            return bin_frequency / total_count, 0.0

        return bin_frequency / total_count, bin_target_frequency / bin_frequency

    def _get_categorical_bin_frequency_and_target_rate(
        self, data: "pd.DataFrame", col_attribute: str, col_target: str, bin_categories: Optional[List[str]]
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate frequency and target rate for given bin of categorical attribute.

        :param: data: Data for calculating bin frequencies and respective target rate.
        :param: col_attribute: Name of the attribute.
        :param: col_target: Name of the target.
        :param: bin_categories: Categories included in bin.
        :return: Category frequency and target rate.
        """
        total_count = len(data)
        if total_count == 0:
            logger.warning(
                f"Cannot calculate bin frequency and target rate for {col_attribute}. Provided data contains "
                f"no observations."
            )
            return None, None

        if bin_categories is None:
            mask_bin = data[col_attribute].isnull()
            categories_str = "null"
        else:
            mask_bin = data[col_attribute].isin(bin_categories)
            categories_str = ",".join(bin_categories)

        bin_frequency = mask_bin.sum()
        bin_target_frequency = (mask_bin & (data[col_target] == 1)).sum()

        if bin_target_frequency == 0:
            if len(categories_str) > 30:
                categories_str = categories_str[0:27] + "..."
            logger.info(
                f"Target rate for attribute {col_attribute} and group of categories {{{categories_str}}} is zero."
            )
            return bin_frequency / total_count, 0.0

        return bin_frequency / total_count, bin_target_frequency / bin_frequency

    def _validate_model_name(self, model_name: Optional[str], model_type_final: str) -> str:
        if model_name is None:
            model_name_final = self._generate_model_name(model_type=model_type_final)
            logger.warning(f"Model name was not provided. Generated model name: '{model_name_final}'.")
        else:
            model_name_final = model_name

        return model_name_final

    def _validate_feature_names(  # noqa: C901
        self,
        attributes: Optional[List[str]],
        transformations: Optional[List[AttributeTransformation]],
        attribute_binning: Optional[Dict],
        dummy_encoding: Optional[List[PredictiveModelDummyEncoding]],
        model: ModelType,
    ) -> List[str]:
        if isinstance(model, io.StringIO):
            # PMML model does not support feature names, so we use attributes without processing
            return attributes or []

        model_attrs = self._get_feature_names_in(model=model)

        # 1. First reverse attributes created in dummy encoding
        attrs_before_dummy_encoding = model_attrs.copy()
        if dummy_encoding:
            for encoding in dummy_encoding:
                attr = encoding.attribute
                for single_dummy in encoding.encoding:
                    encoded_feature_name = single_dummy.encoded_feature_name
                    if encoded_feature_name not in model_attrs:
                        logger.warning(
                            f"Dummy encoding for attribute {attr} defines feature {encoded_feature_name}. This "
                            f"feature is not used in model. Please check dummy encoding for typos."
                        )
                    else:
                        if attr not in attrs_before_dummy_encoding:
                            attrs_before_dummy_encoding.append(attr)
                        del attrs_before_dummy_encoding[attrs_before_dummy_encoding.index(encoded_feature_name)]

        # 2. Second, reverse attribute created in attribute binning
        attrs_before_binning = attrs_before_dummy_encoding.copy()
        if attribute_binning:
            for attribute, binning in attribute_binning.items():
                binned_attribute_name = binning.get("binned_attribute_name", None)
                if binned_attribute_name is not None and binned_attribute_name != attribute:
                    if binned_attribute_name not in attrs_before_dummy_encoding:
                        logger.warning(
                            f"Binning defines attribute '{binned_attribute_name}'. This feature is not used in model. "
                            f"Please check binning for typos."
                        )
                    else:
                        if attribute not in attrs_before_binning:
                            attrs_before_binning.append(attribute)
                        del attrs_before_binning[attrs_before_binning.index(binned_attribute_name)]

        # 3. Finally, reverse attributes created in transformations
        orig_attrs = attrs_before_binning.copy()
        if transformations:
            for transformation in transformations:
                transformed_attribute_name = transformation.transformed_attribute_name
                original_attribute_name = transformation.attribute
                if transformed_attribute_name is not None and transformed_attribute_name != original_attribute_name:
                    if (
                        transformed_attribute_name not in attrs_before_binning
                        and transformed_attribute_name not in attrs_before_dummy_encoding
                        and transformed_attribute_name not in model_attrs
                    ):
                        logger.warning(
                            f"Transformations defines attribute '{transformed_attribute_name}'. This feature is not "
                            f"used in model or later phases attribute preprocessing (binning and dummy encoding). "
                            f"Please check transformations for typos."
                        )
                    else:
                        if original_attribute_name not in orig_attrs:
                            orig_attrs.append(original_attribute_name)
                        del orig_attrs[orig_attrs.index(transformed_attribute_name)]

        if attributes is None:
            logger.info(f"Expected original features (features before transformation and encodings) are: {orig_attrs}.")
        elif set(attributes) != set(orig_attrs):
            logger.warning(
                f"Expected original features (features before transformation and encodings) are different "
                f"from attributes provided in 'attributes' parameter. Expected: {orig_attrs};   Provided: "
                f"{attributes}. Expected original features will be used in exported model. Please check "
                f"that this is a correct behavior."
            )

        return orig_attrs

    def _get_feature_names_in(self, model: ModelType) -> List[str]:
        from xgboost import Booster
        import polars as pl

        if isinstance(model, Booster):
            return list(model.feature_names) if model.feature_names is not None else []
        elif isinstance(model, pl.DataFrame):
            return []
        else:
            if hasattr(model, "feature_names_in_"):
                return list(model.feature_names_in_)
            else:
                raise ValueError(
                    "Unable to detect feature names that enters the model. Please add property "
                    "'feature_names_in_' to your model object. 'feature_names_in_' will contain names of "
                    "features as they enter the model, i.e. after applying transformations, encodings and "
                    "dummy encodings."
                )

    def _get_dumped_model(
        self,
        model: ModelType,
        model_type: PredictiveModelType,
        attributes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if model_type == PredictiveModelType.PMML:
            serialized_model = self.pmml_model_dump(cast(io.StringIO, model))
            if "feature_names" not in serialized_model:
                serialized_model["feature_names"] = attributes
            return serialized_model
        elif model_type == PredictiveModelType.LOGISTIC_REGRESSION:
            return self.logreg_model_dump(cast("LogisticRegression", model))
        elif model_type == PredictiveModelType.XGB:
            return self.xgb_model_dump(cast("Booster", model))
        elif model_type == PredictiveModelType.EXPERT_SCORE:
            return self.expert_score_model_dump(cast("pl.DataFrame", model))
        elif model_type == PredictiveModelType.RANDOM_FOREST:
            return self.random_forest_model_dump(cast("RandomForestClassifier", model))
        return {}

    def logreg_model_dump(self, model: "LogisticRegression") -> Dict[str, Any]:
        import sklearn

        result = {"type": PredictiveModelType.LOGISTIC_REGRESSION, "package_version": sklearn.__version__}
        if model is not None:
            result["package"] = str(model.__class__)
            result["feature_names"] = list(model.feature_names_in_)
            result["init_params"] = model.get_params()
            result["logreg_model_params"] = mp = {}
            for p in ("coef_", "intercept_", "classes_", "n_iter_"):
                mp[p] = getattr(model, p).tolist()

        return result

    def xgb_model_dump(self, model: "Booster") -> Dict[str, Any]:
        import xgboost as xgb
        import json

        result: Dict[str, Any] = {"type": PredictiveModelType.XGB, "package_version": xgb.__version__}
        if model is not None:
            result["feature_names"] = list(model.feature_names) if model.feature_names is not None else []
            result["package"] = str(model.__class__)
            result["xgb_model"] = json.loads(model.save_raw(raw_format="json").decode("utf-8"))
        return result

    def _get_unique_values_from_df_col(self, dt: "pl.DataFrame", extract_values_from: str) -> List[str]:
        """This function will extract unique values from polars DataFrame into list in deterministic order."""
        attributes_in_df = dt[extract_values_from].to_list()
        seen_attr = set()
        unique_attributes = []
        for attr in attributes_in_df:
            if attr not in seen_attr:
                unique_attributes.append(attr)
                seen_attr.add(attr)

        return unique_attributes

    def expert_score_model_dump(self, model: "pl.DataFrame") -> Dict[str, Any]:
        import polars as pl

        unique_attributes = self._get_unique_values_from_df_col(model, "attribute")
        feature_names = self._get_unique_values_from_df_col(model.filter(pl.col("is_intercept") == 0), "attribute")

        intercept = None
        intercept_name = None
        for attr in unique_attributes:
            expert_score_attr = model.filter(pl.col("attribute") == attr)
            if (expert_score_attr["is_intercept"] == 1).sum() > 0:
                intercept = expert_score_attr["value"].to_list()[0]
                intercept_name = expert_score_attr["attribute"].to_list()[0]

        return {
            "type": PredictiveModelType.EXPERT_SCORE,
            "feature_names": feature_names,
            "intercept": intercept,
            "intercept_name": intercept_name,
        }

    def random_forest_model_dump(self, model: "RandomForestClassifier") -> Dict[str, Any]:
        import sklearn

        result = {"type": PredictiveModelType.RANDOM_FOREST, "package_version": sklearn.__version__}
        if model is not None:
            result["feature_names"] = list(model.feature_names_in_)
            result["package"] = str(model.__class__)
            result["random_forest_model"] = self._random_forest_to_dict(model)

        return result

    def pmml_model_dump(self, model: io.StringIO) -> Dict[str, Any]:
        import sklearn_pmml_model

        result = {"type": PredictiveModelType.PMML, "package_version": sklearn_pmml_model.__version__}
        if model is not None:
            result["pmml_model"] = model.getvalue()

            return result

    def _random_forest_to_dict(self, random_forest: "RandomForestClassifier") -> Dict[str, Any]:
        random_forest_dict = random_forest.__getstate__()

        random_forest_dict["classes_"] = [str(cl) for cl in random_forest_dict["classes_"]]
        random_forest_dict["estimators_"] = [self._decision_tree_to_dict(e) for e in random_forest_dict["estimators_"]]
        random_forest_dict["estimator_params"] = list(random_forest_dict["estimator_params"])

        if "feature_names_in_" in random_forest_dict:
            random_forest_dict["feature_names_in_"] = list(random_forest_dict["feature_names_in_"])

        remove_keys = ["estimator", "_estimator", "estimator_"]
        for remove_key in remove_keys:
            if remove_key in random_forest_dict:
                del random_forest_dict[remove_key]

        return random_forest_dict

    def _decision_tree_to_dict(self, decision_tree: "DecisionTreeClassifier") -> Dict[str, Any]:
        decision_tree_dict = decision_tree.__getstate__()

        decision_tree_dict["tree_"] = self._tree_to_dict(decision_tree.tree_)
        decision_tree_dict["classes_"] = decision_tree_dict["classes_"].astype(str).tolist()
        decision_tree_dict["n_classes_"] = int(decision_tree_dict["n_classes_"])

        if "_sklearn_version" in decision_tree_dict.keys():
            del decision_tree_dict["_sklearn_version"]

        return decision_tree_dict

    def _tree_to_dict(self, tree: "Tree") -> Dict[str, Any]:
        # TODO - resolve base_estimator, drop it somehow ...
        tree_dict = tree.__getstate__()

        tree_dict["nodes_types"] = self._get_structured_nparray_types(tree_dict["nodes"])
        tree_dict["nodes_values"] = tree_dict["nodes"].tolist()
        tree_dict["values"] = tree_dict["values"].tolist()

        # compatibility for  scikit <1.3
        from packaging import version
        import sklearn

        if version.parse(sklearn.__version__) < version.parse("1.4.0"):
            if "missing_go_to_left" not in tree_dict["nodes_types"]["names"]:
                tree_dict["nodes_types"]["names"].append("missing_go_to_left")
                tree_dict["nodes_types"]["formats"].append("uint8")
                tree_dict["nodes_types"]["offsets"].append(56)
                tree_dict["nodes_types"]["itemsize"] = 64

                updated_values = [(*t, 0) for t in tree_dict["nodes_values"]]
                tree_dict["nodes_values"] = updated_values
            else:
                updated_values = [(*t[:-1], 0) for t in tree_dict["nodes_values"]]
                tree_dict["nodes_values"] = updated_values

        del tree_dict["nodes"]

        return tree_dict

    def _get_structured_nparray_types(self, array: "np.ndarray") -> Dict[str, Any]:
        result = {"names": [], "formats": [], "offsets": [], "itemsize": array.dtype.itemsize}
        for field_name, field_info in array.dtype.fields.items():
            result["names"].append(field_name)
            result["formats"].append(field_info[0].__str__())
            result["offsets"].append(field_info[1])

        return result

    def create_numerical_attribute_binning_dmupto5_5_2(
        self,
        data: "pd.DataFrame",
        col_attribute: str,
        col_target: str,
        n_bins: int = 7,
        bins: Optional[List[Union[int, float]]] = None,
    ) -> Dict[str, Any]:
        """Create attribute binning for monitoring purposes. Bins are established to contain similar share of population
        (based on percentiles).

        :param: data: Data sample to be used for binning creation.
        :param: col_attribute: Attribute's name.
        :param: col_target: Name of the target.
        :param: n_bins: Number of bins to be created.
        :return: AttributeBinning object
        """

        # for numerical attributes, n same frequent bins are defined
        attribute_binning: Dict[str, Any] = {"dtype": "NUMERICAL"}

        import numpy as np

        if bins is None:
            if len(data[col_attribute].unique()) > n_bins:
                bins = list(
                    np.unique(
                        np.percentile(
                            data[data[col_attribute].notnull()][col_attribute], np.linspace(0, 100, n_bins + 1)
                        )
                    )
                )
                bins[0] = -np.inf
                bins[-1] = np.inf
            else:
                bins = sorted(data[col_attribute].unique().tolist())
                bins.insert(0, -np.inf)
                bins.append(np.inf)

        attribute_binning["bins"] = [-np.inf] + bins[1:-1] + [np.inf]

        frequency_null, target_rate_null = self._get_numerical_bin_frequency_and_target_rate(
            data=data, col_attribute=col_attribute, col_target=col_target, lower_bound=None, upper_bound=None
        )

        attribute_binning["null_frequency"] = frequency_null
        attribute_binning["null_target_rate"] = target_rate_null

        frequencies = []
        target_rates = []
        for i in range(len(bins) - 1):
            lower_bound = bins[i]
            upper_bound = bins[i + 1]

            frequency, target_rate = self._get_numerical_bin_frequency_and_target_rate(
                data=data,
                col_attribute=col_attribute,
                col_target=col_target,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )

            frequencies.append(frequency)
            target_rates.append(target_rate)

        attribute_binning["bin_frequencies"] = frequencies
        attribute_binning["bin_target_rates"] = target_rates

        return attribute_binning

    def create_categorical_attribute_binning_dmupto5_5_2(
        self,
        data: "pd.DataFrame",
        col_attribute: str,
        col_target: str,
        n_bins: int = 7,
        categories: Optional[List[List[str]]] = None,
    ) -> Dict[str, Any]:
        # for numerical attributes, n same frequent bins are defined
        attribute_binning: Dict[str, Any] = {"dtype": "CATEGORICAL"}

        if categories is None:
            categories_raw = [
                cat for cat in data[col_attribute].value_counts(sort=True, ascending=False, dropna=True).index
            ]

            categories = []
            for i in range(min(n_bins - 1, len(categories_raw))):
                categories.append([categories_raw[i]])

            if len(categories_raw) >= n_bins:
                categories.append(categories_raw[n_bins:])

        attribute_binning["bins"] = categories

        frequency_null, target_rate_null = self._get_categorical_bin_frequency_and_target_rate(
            data=data, col_attribute=col_attribute, col_target=col_target, bin_categories=None
        )

        attribute_binning["null_target_rate"] = target_rate_null
        attribute_binning["null_frequency"] = frequency_null

        frequencies = []
        target_rates = []
        for i in range(len(categories)):
            frequency, target_rate = self._get_categorical_bin_frequency_and_target_rate(
                data=data, col_attribute=col_attribute, col_target=col_target, bin_categories=categories[i]
            )

            frequencies.append(frequency)
            target_rates.append(target_rate)

        attribute_binning["bin_frequencies"] = frequencies
        attribute_binning["bin_target_rates"] = target_rates

        return attribute_binning

    def get_monitoring_data_old(
        self, data: "pd.DataFrame", attributes: List[str], label_name: str, binning: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        if binning is None:
            binning = {}

        import pandas as pd

        monitoring_data = {}
        for attr in attributes:
            if attr not in data.columns:
                logger.warning(
                    f"Attribute {attr} was not found in provided dataset. Skipping preparation of monitoring "
                    f"data for this attribute."
                )
            if pd.api.types.is_numeric_dtype(data[attr].dtype):
                monitoring_data[attr] = self.create_numerical_attribute_binning_dmupto5_5_2(
                    data=data, col_attribute=attr, col_target=label_name, bins=binning.get(attr, {}).get("bins", None)
                )
            else:
                monitoring_data[attr] = self.create_categorical_attribute_binning_dmupto5_5_2(
                    data=data,
                    col_attribute=attr,
                    col_target=label_name,
                    categories=binning.get(attr, {}).get("categories", None),
                )
        return monitoring_data
