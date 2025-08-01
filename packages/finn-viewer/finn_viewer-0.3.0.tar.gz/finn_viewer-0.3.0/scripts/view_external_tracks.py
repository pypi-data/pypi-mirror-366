import pandas as pd

import finn
from finn.track_application_menus import MainApp
from finn.track_data_views.views_coordinator.tracks_viewer import TracksViewer
from finn.track_import_export.load_tracks import tracks_from_df
from finn_builtins.example_data import Fluo_N2DL_HeLa

if __name__ == "__main__":
    # load the example data
    raw_layer_info, labels_layer_info, points_layer_info = Fluo_N2DL_HeLa()
    segmentation_arr = labels_layer_info[0]
    # the segmentation ids in this file correspond to the segmentation ids in the
    # example segmentation data, loaded above
    csvfile = "scripts/hela_example_tracks.csv"
    selected_columns = {
        "time": "t",
        "y": "y",
        "x": "x",
        "id": "id",
        "parent_id": "parent_id",
        "seg_id": "id",
    }

    df = pd.read_csv(csvfile)

    # Create new columns for each feature based on the original column values
    for feature, column in selected_columns.items():
        df[feature] = df[column]

    tracks = tracks_from_df(
        df=df,
        segmentation=segmentation_arr,
        scale=[1, 1, 1],
        features={"area": "Recompute"},
    )

    viewer = finn.Viewer()
    raw_data, raw_kwargs, _ = raw_layer_info
    viewer.add_image(raw_data, **raw_kwargs)
    labels_data, labels_kwargs, _ = labels_layer_info
    viewer.add_labels(labels_data, **labels_kwargs)
    widget = MainApp(viewer)
    viewer.window.add_dock_widget(widget)
    TracksViewer.get_instance(viewer).tracks_list.add_tracks(tracks, "example")

    # Start the finn GUI event loop
    finn.run()
