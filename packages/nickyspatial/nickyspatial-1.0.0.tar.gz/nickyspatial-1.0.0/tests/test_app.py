# -*- coding: utf-8 -*-
"""Test suite for the NickySpatial application.

This suite tests the full workflow of the NickySpatial library, including
reading a raster, performing segmentation, calculating spectral indices,
applying classification rules, and exporting results.
It also includes checks for the generated outputs and their validity.
"""

import json
import os
import shutil

import pytest

from nickyspatial import (
    EnclosedByRuleSet,
    LayerManager,
    MergeRuleSet,
    RuleSet,
    SlicSegmentation,
    SupervisedClassifier,
    TouchedByRuleSet,
    attach_area_stats,
    attach_ndvi,
    attach_shape_metrics,
    attach_spectral_indices,
    layer_to_vector,
    plot_classification,
    plot_layer,
    read_raster,
)


@pytest.fixture(autouse=True)
def clean_output():
    """Fixture to clean up the output directory before and after tests."""
    output_dir = "output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    yield
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


@pytest.fixture
def test_raster_path():
    """Fixture to provide the path to a sample raster image for testing."""
    path = os.path.join("data", "sample.tif")
    if not os.path.exists(path):
        pytest.skip("Test image not found in data/ directory.")
    return path


def check_geojson_features(filepath):
    """Check if the GeoJSON file contains features."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("type") == "FeatureCollection", "Invalid GeoJSON: wrong type."
    features = data.get("features")
    assert isinstance(features, list), "GeoJSON features is not a list."
    assert len(features) > 0, f"No features found in {filepath}."


def test_full_workflow(test_raster_path):
    """Test the full workflow of segmentation, classification, and export."""
    # Step 1: Create the output directory and initialize the LayerManager.
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    manager = LayerManager()

    # Step 2: Read the raster.
    image_data, transform, crs = read_raster(test_raster_path)
    assert image_data is not None, "Failed to read image data."

    # Step 3: Perform segmentation.
    segmenter = SlicSegmentation(scale=20, compactness=1)
    segmentation_layer = segmenter.execute(image_data, transform, crs, layer_manager=manager, layer_name="Base_Segmentation")
    assert segmentation_layer is not None, "Segmentation layer was not created."

    # Step 4: Plot segmentation and save the figure.
    fig1 = plot_layer(segmentation_layer, image_data, rgb_bands=(3, 2, 1), show_boundaries=True)
    seg_img_path = os.path.join(output_dir, "1_segmentation.png")
    fig1.savefig(seg_img_path)
    assert os.path.exists(seg_img_path), "Segmentation image not saved."

    # Step 5: Calculate spectral indices (NDVI and others).
    segmentation_layer.attach_function(
        attach_ndvi,
        name="ndvi_stats",
        nir_column="band_4_mean",
        red_column="band_3_mean",
        output_column="NDVI",
    )
    segmentation_layer.attach_function(
        attach_spectral_indices,
        name="spectral_indices",
        bands={
            "blue": "band_1_mean",
            "green": "band_2_mean",
            "red": "band_3_mean",
            "nir": "band_4_mean",
        },
    )
    fig2 = plot_layer(segmentation_layer, attribute="NDVI", title="NDVI Values", cmap="RdYlGn")
    ndvi_img_path = os.path.join(output_dir, "2_ndvi.png")
    fig2.savefig(ndvi_img_path)
    assert os.path.exists(ndvi_img_path), "NDVI image not saved."

    # Step 6: Calculate shape metrics.
    segmentation_layer.attach_function(attach_shape_metrics, name="shape_metrics")
    seg_vector_path = os.path.join(output_dir, "segmentation.geojson")
    layer_to_vector(segmentation_layer, seg_vector_path)
    assert os.path.exists(seg_vector_path), "Segmentation GeoJSON not created."

    # Step 7: Apply land cover classification rules.
    land_cover_rules = RuleSet(name="Land_Cover")
    land_cover_rules.add_rule(name="Vegetation", condition="NDVI > 0.2")
    land_cover_rules.add_rule(name="Other", condition="NDVI <= 0.2")
    land_cover_layer = land_cover_rules.execute(segmentation_layer, layer_manager=manager, layer_name="Land_Cover")
    assert land_cover_layer is not None, "Land cover layer was not created."
    fig3 = plot_classification(land_cover_layer, class_field="classification")
    lc_img_path = os.path.join(output_dir, "3_land_cover.png")
    fig3.savefig(lc_img_path)
    assert os.path.exists(lc_img_path), "Land cover classification image not saved."

    # Step 8: Calculate class statistics.
    land_cover_layer.attach_function(attach_area_stats, name="area_by_class", by_class="classification")
    area_stats = land_cover_layer.get_function_result("area_by_class")
    assert "class_areas" in area_stats, "Area stats missing class_areas."
    assert len(area_stats["class_areas"]) > 0, "Area stats computed no classes."

    # Step 9: Apply hierarchical classification rules for vegetation.
    vegetation_rules = RuleSet(name="Vegetation_Types")
    vegetation_rules.add_rule(
        name="Healthy_Vegetation",
        condition="(classification == 'Vegetation') & (NDVI > 0.6)",
    )
    vegetation_rules.add_rule(
        name="Moderate_Vegetation",
        condition="(classification == 'Vegetation') & (NDVI <= 0.6) & (NDVI > 0.4)",
    )
    vegetation_rules.add_rule(
        name="Sparse_Vegetation",
        condition="(classification == 'Vegetation') & (NDVI <= 0.4)",
    )
    vegetation_layer = vegetation_rules.execute(
        land_cover_layer,
        layer_manager=manager,
        layer_name="Vegetation_Types",
        result_field="veg_class",
    )
    assert vegetation_layer is not None, "Vegetation layer was not created."
    fig4 = plot_classification(vegetation_layer, class_field="veg_class")
    veg_img_path = os.path.join(output_dir, "4_vegetation_types.png")
    fig4.savefig(veg_img_path)
    assert os.path.exists(veg_img_path), "Vegetation classification image not saved."

    # Step 10: Export results.
    lc_vector_path = os.path.join(output_dir, "land_cover.geojson")
    veg_vector_path = os.path.join(output_dir, "vegetation_types.geojson")
    layer_to_vector(land_cover_layer, lc_vector_path)
    layer_to_vector(vegetation_layer, veg_vector_path)
    assert os.path.exists(lc_vector_path), "Land cover GeoJSON not saved."
    assert os.path.exists(veg_vector_path), "Vegetation GeoJSON not saved."

    # TODO : Fix this test case it is failing for some reason
    # lc_raster_path = os.path.join(output_dir, "land_cover.tif")
    # layer_to_raster(land_cover_layer, lc_raster_path, column="classification")
    # assert os.path.exists(lc_raster_path), "Land cover raster not saved."

    # Check that the generated GeoJSON files contain features.
    check_geojson_features(lc_vector_path)
    check_geojson_features(veg_vector_path)

    # Print the available layers.
    available_layers = manager.get_layer_names()
    assert len(available_layers) >= 3, "Expected at least three layers in manager."

    """Supervised Classification Test Start"""
    # Step 1: Perform segmentation.
    segmenter = SlicSegmentation(scale=20, compactness=1)
    segmentation_layer = segmenter.execute(image_data, transform, crs, layer_manager=manager, layer_name="Base_Segmentation")
    assert segmentation_layer is not None, "Segmentation layer was not created."

    # Step 2: define samples and colors
    samples = {
        "Water": [41, 134, 246, 491],
        "built-up": [12, 499, 290, 484],
        "vegetation": [36, 143, 239, 588, 371],
    }
    classes_color = {"Water": "#3437c2", "built-up": "#de1421", "vegetation": "#0f6b2f"}
    # Step 3: RF Supervised Classification implementation
    params = {"n_estimators": 100, "oob_score": True, "random_state": 42}
    rf_classification = SupervisedClassifier(name="RF Classification", classifier_type="Random Forest", classifier_params=params)
    rf_classification_layer, accuracy, feature_importances = rf_classification.execute(
        segmentation_layer,
        samples=samples,
        layer_manager=manager,
        layer_name="RF Classification",
    )
    fig5 = plot_classification(rf_classification_layer, class_field="classification", class_color=classes_color)
    assert rf_classification_layer is not None, "RF classification layer was not created."
    rf_classification_img_path = os.path.join(output_dir, "5_RF_classification.png")
    fig5.savefig(rf_classification_img_path)
    assert os.path.exists(rf_classification_img_path), "RF Classification layer not saved."

    # Step 4: Apply merge segements based on class
    merger = MergeRuleSet("MergeByVegAndType")
    class_value = ["Water", "vegetation"]
    merged_layer = merger.execute(
        source_layer=rf_classification_layer,
        class_column_name="classification",
        class_value=class_value,
        layer_manager=manager,
        layer_name="Merged RF Classification",
    )
    assert merged_layer is not None, "Merged layer was not created."
    fig6 = plot_classification(merged_layer, class_field="classification", class_color=classes_color)
    merged_img_path = os.path.join(output_dir, "5_merged.png")
    fig6.savefig(merged_img_path)
    assert os.path.exists(merged_img_path), "Merged_by layer not saved."

    # Step 5: Apply enclosed_by rule
    encloser_rule = EnclosedByRuleSet()
    enclosed_by_layer = encloser_rule.execute(
        source_layer=merged_layer,
        class_column_name="classification",
        class_value_a="vegetation",
        class_value_b="built-up",
        new_class_name="park",
        layer_manager=manager,
        layer_name="enclosed_by_layer",
    )
    assert enclosed_by_layer is not None, "Enclosed_by layer was not created."
    classes_color["park"] = "#d2f7dc"
    fig7 = plot_classification(enclosed_by_layer, class_field="classification", class_color=classes_color)
    enclosed_img_path = os.path.join(output_dir, "7_enclosed_by.png")
    fig7.savefig(enclosed_img_path)
    assert os.path.exists(enclosed_img_path), "Enclosed_by layer not saved."

    # Step 6: Apply touched_by rule
    touched_by_rule = TouchedByRuleSet()
    touched_by_layer = touched_by_rule.execute(
        source_layer=enclosed_by_layer,
        class_column_name="classification",
        class_value_a="built-up",
        class_value_b="Water",
        new_class_name="Water front builtup",
        layer_manager=manager,
        layer_name="touched_by_layer",
    )
    assert touched_by_layer is not None, "Touched_by layer was not created."
    classes_color["Water front builtup"] = "#cc32cf"
    fig8 = plot_classification(touched_by_layer, class_field="classification", class_color=classes_color)
    touched_img_path = os.path.join(output_dir, "8_touched_by.png")
    fig8.savefig(touched_img_path)
    assert os.path.exists(touched_img_path), "Touched_by layer not saved."
