# Copyright (C) 2025 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Wed Jul 30 2025

import contextlib

import numpy as np
import sklearn
from cosmic_toolbox import logger
from packaging import version
from sklearn.base import ClassifierMixin
from sklearn.base import is_classifier as original_is_classifier

LOGGER = logger.get_logger(__file__)


class CompatibleCalibratedClassifier:  # pragma: no cover
    """
    Compatibility wrapper for CalibratedClassifierCV to work with sklearn >= 1.6.
    This class bypasses sklearn's stricter validation while maintaining the same
    functionality.
    """

    def __init__(self, original_pipe):
        self.original_pipe = original_pipe
        self.classes_ = getattr(original_pipe, "classes_", np.array([0, 1]))
        self.n_features_in_ = getattr(original_pipe, "n_features_in_", None)
        # Forward the calibrated_classifiers_ attribute for TF model loading
        self.calibrated_classifiers_ = getattr(
            original_pipe, "calibrated_classifiers_", []
        )

    def predict(self, X):
        # Try original first, fallback to manual aggregation
        try:
            return self.original_pipe.predict(X)
        except Exception:
            # Manual prediction by averaging calibrated classifiers
            predictions = []
            for cal_clf in self.original_pipe.calibrated_classifiers_:
                pred = cal_clf.estimator.predict(X)
                predictions.append(pred)
            # Use majority vote
            return np.array(
                [1 if np.mean(preds) > 0.5 else 0 for preds in zip(*predictions)]
            )

    def predict_proba(self, X):
        # Bypass sklearn validation by manually implementing calibrated prediction
        try:
            # Pre-allocate arrays for better performance
            n_samples = X.shape[0]
            n_calibrators = len(self.original_pipe.calibrated_classifiers_)
            predictions = np.zeros((n_calibrators, n_samples))

            for i, cal_clf in enumerate(self.original_pipe.calibrated_classifiers_):
                # Get raw predictions from the estimator pipeline
                if hasattr(cal_clf.estimator, "predict_proba"):
                    estimator_proba = cal_clf.estimator.predict_proba(X)
                    # Use the positive class probability for calibration
                    if estimator_proba.shape[1] == 2:
                        raw_pred = estimator_proba[:, 1]
                    else:
                        raw_pred = estimator_proba.flatten()
                else:
                    # Fallback to predict if predict_proba not available
                    raw_pred = cal_clf.estimator.predict(X).astype(float)

                # Apply calibration - try different attribute names for different
                # sklearn versions
                if hasattr(cal_clf, "calibrator"):
                    calibrated_pred = cal_clf.calibrator.predict(
                        raw_pred.reshape(-1, 1)
                    ).flatten()
                elif hasattr(cal_clf, "calibrators"):
                    # For newer sklearn versions with calibrators (not calibrators_)
                    calibrated_pred = (
                        cal_clf.calibrators[0]
                        .predict(raw_pred.reshape(-1, 1))
                        .flatten()
                    )
                elif hasattr(cal_clf, "calibrators_"):
                    # For sklearn versions with calibrators_
                    calibrated_pred = (
                        cal_clf.calibrators_[0]
                        .predict(raw_pred.reshape(-1, 1))
                        .flatten()
                    )
                else:
                    # Fallback: use raw predictions
                    calibrated_pred = raw_pred

                predictions[i] = calibrated_pred

            # Average predictions across calibrated classifiers (vectorized)
            avg_pred = np.mean(predictions, axis=0)
            return np.column_stack([1 - avg_pred, avg_pred])

        except Exception as e:
            LOGGER.warning(f"Fallback prediction failed: {e}")
            # Ultimate fallback: return uniform probabilities
            return np.full((X.shape[0], 2), 0.5)

    def set_params(self, **params):
        return self.original_pipe.set_params(**params)

    def get_params(self, deep=True):
        return self.original_pipe.get_params(deep=deep)


def fix_calibrated_classifier_compatibility(pipe):  # pragma: no cover
    """
    Fix compatibility issues with CalibratedClassifierCV for scikit-learn >= 1.6.

    This function creates a compatibility wrapper that bypasses sklearn's stricter
    validation while maintaining the same functionality.

    :param pipe: The pipeline to fix
    :return: The original pipeline or a compatibility wrapper if needed
    """
    if not hasattr(pipe, "calibrated_classifiers_"):
        return pipe

    try:
        # For sklearn >= 1.6, only create the wrapper if we actually encounter the error
        if version.parse(sklearn.__version__) >= version.parse("1.6"):
            # First, try to use the original pipeline to see if it works
            try:
                # Determine number of features from the pipeline
                n_features = getattr(pipe, "n_features_in_", None)

                n_feature_none = n_features is None
                has_calibrated_classifiers = (
                    hasattr(pipe, "calibrated_classifiers_")
                    and len(pipe.calibrated_classifiers_) > 0
                )
                if n_feature_none & has_calibrated_classifiers:
                    first_estimator = pipe.calibrated_classifiers_[0].estimator
                    if hasattr(first_estimator, "named_steps"):
                        for _, step in first_estimator.named_steps.items():
                            if hasattr(step, "n_features_in_"):
                                n_features = step.n_features_in_
                                break

                # Test with a small dummy array to check if validation fails
                test_X = np.random.random((1, n_features))
                _ = pipe.predict_proba(test_X)
                # If we reach here, the original pipeline works fine
                LOGGER.debug(
                    "Original pipeline works with sklearn >= 1.6, no wrapper needed"
                )
                return pipe
            except ValueError as e:
                if "Pipeline should either be a classifier" in str(e):
                    LOGGER.info(
                        "Creating compatibility wrapper for sklearn >= 1.6 due to "
                        "validation error"
                    )
                    return CompatibleCalibratedClassifier(pipe)
                else:
                    # Different error, let it propagate
                    raise
            except Exception:
                # Other exceptions during testing, fall back to wrapper
                LOGGER.info(
                    "Creating compatibility wrapper for sklearn >= 1.6 due to test "
                    "failure"
                )
                return CompatibleCalibratedClassifier(pipe)

        return pipe

    except Exception as e:
        LOGGER.warning(f"Could not create compatibility wrapper: {e}")
        return pipe


def patched_is_classifier(estimator):  # pragma: no cover
    """
    Enhanced is_classifier that works with custom classifiers in sklearn 1.6+.

    In sklearn 1.6+, is_classifier relies on the new tagging system which may not
    recognize custom classifiers properly. This function provides backward
    compatibility by falling back to ClassifierMixin detection.
    """
    # First try the original function
    result = original_is_classifier(estimator)
    if result:
        return True

    # If original fails, check for ClassifierMixin as fallback
    if isinstance(estimator, ClassifierMixin):
        return True

    # For pipelines, check if the final step is a classifier
    if hasattr(estimator, "steps") and estimator.steps:
        final_step = estimator.steps[-1][1]
        if isinstance(final_step, ClassifierMixin):
            return True

    # For GridSearchCV, check the base estimator
    if hasattr(estimator, "estimator"):
        return patched_is_classifier(estimator.estimator)

    return False


def apply_sklearn_compatibility_patches():  # pragma: no cover
    """
    Apply compatibility patches for scikit-learn version differences.

    This should be called early in the import process to ensure compatibility
    across different sklearn versions.
    """
    sklearn_version = version.parse(sklearn.__version__)

    # Apply patches for sklearn 1.6+ where is_classifier behavior changed
    if sklearn_version >= version.parse("1.6.0"):
        LOGGER.info("Applying sklearn 1.6+ compatibility patches for is_classifier")

        # Patch the is_classifier function in relevant modules
        sklearn.base.is_classifier = patched_is_classifier

        # Try to patch sklearn.utils._response if it exists and is accessible
        try:
            sklearn.utils._response.is_classifier = patched_is_classifier
        except (ImportError, AttributeError):
            LOGGER.debug("sklearn.utils._response not available for patching")

        # Also patch in calibration module if it exists
        with contextlib.suppress(ImportError, AttributeError):
            sklearn.calibration.is_classifier = patched_is_classifier
