import argparse
import json
from collections.abc import Sequence
from pathlib import Path


def combine_bowser(
    bowser_paths: Sequence[Path], names: Sequence[str], out_suffix: str = "_combined"
):
    """Combine multiple bowser JSON files into a single output file.

    Parameters
    ----------
    bowser_paths : Sequence[Path]
        List of Path objects pointing to directories containing bowser_rasters.json
    names : Sequence[str]
        Name prefixes for each source (must be same length as bowser_paths)
    out_suffix : str
        Filename addition to use for the combined output file.
        Creates a new file names f"bowser_rasters{out_suffix}.json"
        Default is "_combined

    """
    if len(bowser_paths) != len(names):
        raise ValueError("bowser_paths and names must have the same length")
    parent_dirs = []
    json_paths = []
    for p in bowser_paths:
        if p.is_file():
            parent_dirs.append(p.parent)
            json_paths.append(p)
        else:
            parent_dirs.append(p)
            json_paths.append(p / "bowser_rasters.json")

    def adjust_paths(d, path):
        """Adjust file paths in the data dictionary to be relative to the given path."""
        file_list = []
        for fn in d["file_list"]:
            file_list.append(f"{path}/{fn}")
        d["file_list"] = file_list

        mask_file_list = []
        for fn in d["mask_file_list"]:
            mask_file_list.append(f"{path}/{fn}")
        d["mask_file_list"] = mask_file_list

    # Load and process data from each source
    all_data = []

    for parent, p, name_prefix in zip(parent_dirs, json_paths, names):
        # Read the JSON file
        d = json.loads(p.read_text())

        # Process each item in the data
        for item in d:
            item["name"] = f"{name_prefix}: {item['name']}"
            adjust_paths(item, parent)

        all_data.append(d)

    # Combine all data by interleaving items from each source
    outname = f"bowser_rasters{out_suffix}.json"
    out = []

    # Interleave items: first item from each source, then second item from each source
    max_length = max(len(data_source) for data_source in all_data)
    for i in range(max_length):
        for data_source in all_data:
            if i >= len(data_source):
                continue
            out.append(data_source[i])
    Path(outname).write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bowser-paths", nargs="*", type=Path)
    parser.add_argument("--names", nargs="*")
    parser.add_argument("--out-suffix", default="_combined")
    args = parser.parse_args()
    combine_bowser(args.bowser_paths, args.names, args.out_suffix)
