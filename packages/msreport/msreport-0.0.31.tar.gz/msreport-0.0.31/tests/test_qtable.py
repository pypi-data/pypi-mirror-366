import numpy as np
import pandas as pd
import pytest

import msreport.qtable


@pytest.fixture
def example_data():
    design = pd.DataFrame(
        [
            ("Sample_A1", "Experiment_A", "1"),
            ("Sample_A2", "Experiment_A", "1"),
            ("Sample_B1", "Experiment_B", "1"),
            ("Sample_B2", "Experiment_B", "1"),
        ],
        columns=["Sample", "Experiment", "Replicate"],
    )

    data = pd.DataFrame(
        {
            "id": ["1", "2", "3"],
            "Total peptides": [2, 1, 2],
            "Representative protein": ["A", "B", "C"],
            "Valid": [True, True, False],
            # Note that one intensitiy must be above 64, otherwise it is assumed
            # that they are already log transformed and another log is prevented.
            "Intensity": [100, 0, np.nan],
            "Intensity Sample_A1": [100, np.nan, 60],
            "Intensity Sample_A2": [100, np.nan, 20],
            "Intensity Sample_B1": [150, np.nan, 00],  # <- 0 is considered missing
            "Intensity Sample_B2": [15, np.nan, 40],
            "Mean_Experiment_A1": [100, np.nan, 40],  # <- Adjust to Sample_A1/A2
        }
    )

    example_data = {
        "data": data,
        "design": design,
        "expression_tag": "Intensity",
        "intensity_columns": [
            "Intensity Sample_A1",
            "Intensity Sample_A2",
            "Intensity Sample_B1",
            "Intensity Sample_B2",
        ],
        "expression_columns": [
            "Expression Sample_A1",
            "Expression Sample_A2",
            "Expression Sample_B1",
            "Expression Sample_B2",
        ],
        "intensity_cols_to_samples": {
            "Intensity Sample_A1": "Sample_A1",
            "Intensity Sample_A2": "Sample_A2",
            "Intensity Sample_B1": "Sample_B1",
            "Intensity Sample_B2": "Sample_B2",
        },
        "expr_cols_to_samples": {
            "Expression Sample_A1": "Sample_A1",
            "Expression Sample_A2": "Sample_A2",
            "Expression Sample_B1": "Sample_B1",
            "Expression Sample_B2": "Sample_B2",
        },
    }
    return example_data


@pytest.fixture
def example_qtable(example_data):
    qtable = msreport.qtable.Qtable(example_data["data"], design=example_data["design"], id_column="id")  # fmt: skip
    qtable.set_expression_by_tag("Intensity")
    return qtable


class TestQtableInitialization:
    def test_data_is_added_to_qtable(self, example_data):
        qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip
        assert qtable.data.equals(example_data["data"])

    def test_design_is_added_to_qtable(self, example_data):
        qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip
        assert qtable.design.equals(example_data["design"])

    def test_id_column_is_added_to_qtable(self, example_data):
        qtable = msreport.qtable.Qtable(example_data["data"], design=example_data["design"], id_column="id")  # fmt: skip
        assert qtable._id_column == "id"

    def test_non_unique_data_index_raises_error(self, example_data):
        example_data["data"].index = [0 for _ in range(len(example_data["data"]))]
        with pytest.raises(ValueError):
            msreport.qtable.Qtable(example_data["data"], design=example_data["design"], id_column="Representative protein")  # fmt: skip

    def test_non_existing_id_column_raises_error(self, example_data):
        with pytest.raises(KeyError):
            msreport.qtable.Qtable(example_data["data"], design=example_data["design"], id_column="non_existing_column")  # fmt: skip

    def test_id_column_containing_non_unique_values_raises_error(self, example_data):
        example_data["data"]["id"] = "1"
        with pytest.raises(ValueError):
            msreport.qtable.Qtable(example_data["data"], design=example_data["design"], id_column="id")  # fmt: skip


def test_qtable_add_design(example_data):
    qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip
    qtable.add_design(example_data["design"])
    assert qtable.design.equals(example_data["design"])

    with pytest.raises(ValueError):
        qtable.add_design(pd.DataFrame(columns=["Sample"]))
    with pytest.raises(ValueError):
        qtable.add_design(pd.DataFrame(columns=["Experiment"]))


class TestQtableCopy:
    def test_copy(self, example_qtable):
        copied_qtable = example_qtable.copy()
        assert copied_qtable.data.equals(example_qtable.data)
        assert copied_qtable.design.equals(example_qtable.design)
        assert copied_qtable.id_column == example_qtable.id_column
        assert copied_qtable is not example_qtable


class TestQtableTempDesign:
    def test_design_is_changed_in_scope(self, example_qtable):
        with example_qtable.temp_design(pd.DataFrame(columns=["Sample", "Experiment", "Replicate"])):  # fmt: skip
            assert example_qtable.design.equals(pd.DataFrame(columns=["Sample", "Experiment", "Replicate"]))  # fmt:skip

    def test_design_is_restored_after_scope(self, example_qtable):
        original_design = example_qtable.design.copy()
        with example_qtable.temp_design(pd.DataFrame(columns=["Sample", "Experiment", "Replicate"])):  # fmt: skip
            ...
        assert example_qtable.design.equals(original_design)
        assert "Experiment_A" in example_qtable.design["Experiment"].tolist()
        assert "Experiment_B" in example_qtable.design["Experiment"].tolist()

    def test_exclude_experiments_removes_experiment(self, example_qtable):
        with example_qtable.temp_design(exclude_experiments=["Experiment_A"]):
            assert "Experiment_A" not in example_qtable.design["Experiment"].tolist()
            assert "Experiment_B" in example_qtable.design["Experiment"].tolist()

    def test_keep_experiments_keeps_only_selected_experiments(self, example_qtable):
        with example_qtable.temp_design(keep_experiments=["Experiment_A"]):
            assert "Experiment_A" in example_qtable.design["Experiment"].tolist()
            assert "Experiment_B" not in example_qtable.design["Experiment"].tolist()

    def test_exclude_samples_removes_experiment(self, example_qtable):
        with example_qtable.temp_design(exclude_samples=["Sample_A1"]):
            assert "Sample_A1" not in example_qtable.design["Sample"].tolist()
            assert "Sample_A2" in example_qtable.design["Sample"].tolist()

    def test_keep_samples_keeps_only_selected_experiments(self, example_qtable):
        with example_qtable.temp_design(keep_samples=["Sample_A1"]):
            assert "Sample_A1" in example_qtable.design["Sample"].tolist()
            assert "Sample_A2" not in example_qtable.design["Sample"].tolist()


class TestExcludeInvalid:
    def test_default(self):
        df = pd.DataFrame({"Value": ["valid", "excluded"], "Valid": [True, False]})
        filtered_df = msreport.qtable._exclude_invalid(df)
        assert filtered_df["Value"].tolist() == ["valid"]

    def test_raise_key_error(self):
        df = pd.DataFrame({"Value": ["valid", "excluded"]})
        with pytest.raises(KeyError):
            msreport.qtable._exclude_invalid(df)


class TestMatchSamplesToTagColumns:
    def test_match_samples_to_tag_columns(self):
        samples = ["SampleA_1", "SampleA_2", "SampleB_1"]
        columns = ["Tag SampleA_1", "Tag SampleA_2", "Tag SampleB_1"]
        true_mapping = {
            "SampleA_1": "Tag SampleA_1",
            "SampleA_2": "Tag SampleA_2",
            "SampleB_1": "Tag SampleB_1",
        }
        observed_mapping = msreport.qtable._match_samples_to_tag_columns(samples, columns, "Tag")  # fmt:skip
        assert observed_mapping == true_mapping

    def test_correct_mapping_with_samples_that_are_substrings(self):
        samples = ["B_1", "SampleB_1"]
        columns = ["Tag B_1", "Tag SampleB_1"]
        true_mapping = {"B_1": "Tag B_1", "SampleB_1": "Tag SampleB_1"}
        observed_mapping = msreport.qtable._match_samples_to_tag_columns(samples, columns, "Tag")  # fmt:skip
        assert observed_mapping == true_mapping


class TestQtableGetData:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_data):
        self.qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip

    def test_get_data(self, example_data):
        assert self.qtable.get_data().equals(example_data["data"])

    def test_filter_valid(self, example_data):
        data = self.qtable.get_data(exclude_invalid=True)

        valid_mask = example_data["data"]["Valid"]
        assert data.equals(example_data["data"][valid_mask])


@pytest.mark.parametrize("key", ["Representative protein", ["Valid", "Total peptides"]])
def test_qtable_getitem(example_qtable, key):
    assert example_qtable[key].equals(example_qtable.data[key])


@pytest.mark.parametrize(
    "key, value",
    [["A", "1"], [["A", "B"], [1, 2]]],
)
def test_qtable_setitem(example_qtable, key, value):
    example_qtable[key] = value
    assert np.all(example_qtable.data[key] == value)


@pytest.mark.parametrize(
    "key, is_present",
    [["Representative protein", True], ["An absent column", False]],
)
def test_qtable_contains(example_qtable, key, is_present):
    assert (key in example_qtable) == is_present


def test_qtable_get_design(example_data):
    qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip
    assert qtable.get_design().equals(example_data["design"])


def test_qtable_get_samples(example_data, example_qtable):
    design = example_data["design"]

    samples = design["Sample"].tolist()
    assert example_qtable.get_samples() == samples

    for exp in design["Experiment"].unique():
        samples = design[design["Experiment"] == exp]["Sample"].tolist()
        assert example_qtable.get_samples(exp) == samples


def test_qtable_get_experiment(example_data, example_qtable):
    sample = example_data["design"].iloc[0]["Sample"]
    experiment = example_data["design"].iloc[0]["Experiment"]
    assert example_qtable.get_experiment(sample) == experiment


class TestQtableGetExperiments:
    def test_without_samples(self, example_data, example_qtable):
        experiment_set = set(example_data["design"]["Experiment"])
        assert set(example_qtable.get_experiments()) == experiment_set

    def test_with_samples(self, example_data, example_qtable):
        samples = example_data["design"].iloc[0:2].values[:, 0]
        expected_experiments = example_data["design"].iloc[0:2].values[:, 1]
        fetched_experiments = example_qtable.get_experiments(samples)
        assert set(fetched_experiments) == set(expected_experiments)


class TestQtableResetExpression:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_data):
        self.qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip

    def test_reset_of_parameters(self):
        self.qtable._expression_columns = ["test"]
        self.qtable._expression_features = ["test"]
        self.qtable._expression_sample_mapping = {"test": "test"}

        self.qtable._reset_expression()
        assert self.qtable._expression_columns == []
        assert self.qtable._expression_features == []
        assert self.qtable._expression_sample_mapping == {}

    def test_reset_of_data_columns(self, example_data):
        self.qtable._set_expression(example_data["intensity_cols_to_samples"])

        self.qtable._reset_expression()
        data_columns = self.qtable.data.columns
        all_expression_columns_absent_in_data = not any(
            c in data_columns for c in example_data["expression_columns"]
        )
        assert all_expression_columns_absent_in_data

    def test_reset_of_expression_features(self, example_data):
        new_feature = example_data["data"]["id"]
        new_feature.name = "Feature"

        self.qtable.add_expression_features(new_feature)
        assert "Feature" in self.qtable.data.columns

        self.qtable._reset_expression()
        assert "Feature" not in self.qtable.data.columns


class TestQtableSetExpression:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_data):
        self.qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip

    def test_correct_setting_of_private_variables(self, example_data):
        self.qtable._set_expression(example_data["intensity_cols_to_samples"])

        assert self.qtable._expression_columns == example_data["expression_columns"]
        assert (
            self.qtable._expression_sample_mapping
            == example_data["expr_cols_to_samples"]
        )

    def test_with_zerotonan_false(self, example_data):
        self.qtable._set_expression(
            example_data["intensity_cols_to_samples"], zerotonan=False
        )

        expr_table = self.qtable.data[example_data["expression_columns"]]
        num_zero = (expr_table == 0).sum().sum()
        num_nan = expr_table.isna().sum().sum()
        assert num_zero == 1
        assert num_nan == 4

    def test_with_zerotonan_true(self, example_data):
        self.qtable._set_expression(
            example_data["intensity_cols_to_samples"], zerotonan=True
        )

        expr_table = self.qtable.data[example_data["expression_columns"]]
        num_zero = (expr_table == 0).sum().sum()
        num_nan = expr_table.isna().sum().sum()
        assert num_zero == 0
        assert num_nan == 5

    def test_with_log2_true(self, example_data):
        self.qtable._set_expression(
            example_data["intensity_cols_to_samples"], log2=True
        )

        expr_table = self.qtable.data[example_data["expression_columns"]]
        expected = example_data["data"][example_data["intensity_columns"]]
        expected = np.log2(expected.replace({0: np.nan}))
        assert np.array_equal(
            expr_table.to_numpy(), expected.to_numpy(), equal_nan=True
        )

    def test_error_raised_when_column_mapping_empty(self, example_data):
        column_mapping = {}
        with pytest.raises(KeyError):
            self.qtable._set_expression(column_mapping)

    def test_error_raised_when_expression_columns_not_in_data(self, example_data):
        column_mapping = example_data["intensity_cols_to_samples"]
        column_mapping["column_not_present"] = "Sample_A1"
        with pytest.raises(KeyError):
            self.qtable._set_expression(column_mapping)

    def test_error_raised_when_samples_from_column_mapping_not_in_design(self, example_data):  # fmt: skip
        column_mapping = example_data["intensity_cols_to_samples"]
        column_mapping["Intensity Sample_A1"] = "sample not present"
        with pytest.raises(ValueError):
            self.qtable._set_expression(column_mapping)

    def test_error_raised_when_not_all_samples_from_design_in_column_mapping(self, example_data):  # fmt: skip
        column_mapping = example_data["intensity_cols_to_samples"]
        column_mapping.pop("Intensity Sample_A1")
        with pytest.raises(ValueError):
            self.qtable._set_expression(column_mapping)


class TestQtableSetExpressionByTag:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_data):
        self.qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip

    def test_set_expression_by_tag(self, example_data):
        self.qtable.set_expression_by_tag(example_data["expression_tag"])

        assert self.qtable._expression_columns == example_data["expression_columns"]
        assert (
            self.qtable._expression_sample_mapping
            == example_data["expr_cols_to_samples"]
        )

    def test_with_zerotonan(self, example_data):
        self.qtable.set_expression_by_tag(
            example_data["expression_tag"], zerotonan=True
        )

        expr_table = self.qtable.data[example_data["expression_columns"]]
        num_zero = (expr_table == 0).sum().sum()
        assert num_zero == 0

    def test_with_log2(self, example_data):
        self.qtable.set_expression_by_tag(example_data["expression_tag"], log2=True)

        expr_table = self.qtable.data[example_data["expression_columns"]]
        expected = example_data["data"][example_data["intensity_columns"]]
        expected = np.log2(expected.replace({0: np.nan}))
        assert np.array_equal(
            expr_table.to_numpy(), expected.to_numpy(), equal_nan=True
        )


class TestQtableSetExpressionByColumn:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_data):
        self.qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip

    def test_set_expression_by_column(self, example_data):
        self.qtable.set_expression_by_column(example_data["intensity_cols_to_samples"])
        assert self.qtable._expression_columns == example_data["expression_columns"]
        assert (
            self.qtable._expression_sample_mapping
            == example_data["expr_cols_to_samples"]
        )

    def test_with_zerotonan(self, example_data):
        self.qtable.set_expression_by_column(
            example_data["intensity_cols_to_samples"], zerotonan=True
        )

        expr_table = self.qtable.data[example_data["expression_columns"]]
        num_zero = (expr_table == 0).sum().sum()
        assert num_zero == 0

    def test_with_log2(self, example_data):
        self.qtable.set_expression_by_column(
            example_data["intensity_cols_to_samples"], log2=True
        )

        expr_table = self.qtable.data[example_data["expression_columns"]]
        expected = example_data["data"][example_data["intensity_columns"]]
        expected = np.log2(expected.replace({0: np.nan}))
        assert np.array_equal(
            expr_table.to_numpy(), expected.to_numpy(), equal_nan=True
        )


class TestQtableAddExpressionFeature:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_data):
        self.qtable = msreport.qtable.Qtable(example_data["data"], example_data["design"], id_column="Representative protein")  # fmt: skip

    def test_with_series(self):
        new_data = self.qtable.data["id"].copy()
        new_data.name = "Feature"
        self.qtable.add_expression_features(new_data)

        qtable_columns = self.qtable.data.columns.to_list()
        assert "Feature" in qtable_columns
        assert "Feature" in self.qtable._expression_features

    def test_with_dataframe(self):
        new_data = self.qtable.data[["id", "id"]].copy()
        new_data.columns = ["Feature 1", "Feature 2"]
        self.qtable.add_expression_features(new_data)

        qtable_columns = self.qtable.data.columns.to_list()
        for new_column in new_data.columns:
            assert new_column in qtable_columns
            assert new_column in self.qtable._expression_features

    def test_qtable_data_integrity(self):
        old_columns = self.qtable.data.columns.to_list()
        old_shape = self.qtable.data.shape

        new_data = self.qtable.data["id"].copy()
        new_data.name = "Feature"
        self.qtable.add_expression_features(new_data)

        assert [column in self.qtable.data for column in old_columns]
        assert self.qtable.data.shape[0] == old_shape[0]
        assert self.qtable.data.shape[1] == old_shape[1] + 1


def test_qtable_get_expression_column(example_data, example_qtable):
    expected_columns = [c for c in example_data["expr_cols_to_samples"]]
    samples = [example_data["expr_cols_to_samples"][e] for e in expected_columns]
    columns = [example_qtable.get_expression_column(s) for s in samples]
    assert expected_columns == columns


class TestQtableMakeSampleTable:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_qtable):
        self.qtable = example_qtable

    def test_default_args(self, example_data):
        expected = example_data["data"][example_data["intensity_columns"]]
        tag = example_data["expression_tag"]

        expr_table = self.qtable.make_sample_table(tag)
        assert np.array_equal(
            expr_table.to_numpy(), expected.to_numpy(), equal_nan=True
        )

    def test_with_samples_as_columns(self, example_data):
        sample_names = example_data["design"]["Sample"].tolist()
        tag = example_data["expression_tag"]

        expr_table = self.qtable.make_sample_table(tag, samples_as_columns=True)
        expr_table_columns = expr_table.columns.tolist()
        assert expr_table_columns == sample_names


class TestQtableMakeExpressionTable:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_qtable):
        self.qtable = example_qtable

    def test_default_args(self, example_data):
        expected = example_data["data"][example_data["intensity_columns"]]

        # Test for correct values in dataframe
        expr_table = self.qtable.make_expression_table()
        assert np.array_equal(
            expr_table.to_numpy(), expected.to_numpy(), equal_nan=True
        )

    def test_with_samples_as_columns(self, example_data):
        expr_table = self.qtable.make_expression_table(samples_as_columns=True)
        expr_table_columns = expr_table.columns.tolist()

        sample_names = example_data["design"]["Sample"].tolist()
        assert expr_table_columns == sample_names

    def test_with_additional_features(self, example_data):
        expr_table = self.qtable.make_expression_table(features=["id"])
        assert "id" in expr_table.columns
        assert example_data["data"]["id"].equals(expr_table["id"])

    def test_with_all_arguments(self, example_data):
        expr_table_by_qtable = self.qtable.make_expression_table(
            features=["id"], samples_as_columns=True
        )
        assert isinstance(expr_table_by_qtable, pd.DataFrame)


class TestQtableSafeLoad:
    @pytest.fixture(autouse=True)
    def _init_qtable(self, example_qtable):
        # Need to refactor to not rely on the FragPipeReader
        # Note that it is import to test missing values / empty strings in object cols
        from msreport.reader import FragPipeReader

        reader = FragPipeReader("./tests/testdata/fragpipe", contaminant_tag="contam_")
        proteins = reader.import_proteins()
        proteins["Unique ID"] = range(len(proteins))
        design = pd.DataFrame(
            [
                ("SampleA_1", "Experiment_A", "1"),
                ("SampleB_1", "Experiment_B", "1"),
            ],
            columns=["Sample", "Experiment", "Replicate"],
        )
        self.qtable = msreport.qtable.Qtable(proteins, design, id_column="Unique ID")
        self.qtable.set_expression_by_tag("Intensity", log2=True)

    def test_data_is_equal_after_safe_and_load(self, tmp_path):
        self.qtable.save(tmp_path, "test_qtable")
        loaded_qtable = self.qtable.load(tmp_path, "test_qtable")
        pd.testing.assert_frame_equal(self.qtable.data, loaded_qtable.data)
        pd.testing.assert_frame_equal(self.qtable.design, loaded_qtable.design)
        assert self.qtable.id_column == loaded_qtable.id_column
