import os
import pytest

from gemf import GEMF


def test_gemf(tmpdir):
    example_file = "tests/map_data.gemf"

    outdir_example_tiles = os.path.join(tmpdir, "parsed")
    outfile_rewritten = os.path.join(outdir_example_tiles, "rewritten.gemf")

    # read example file and save tiles
    gemf = GEMF.from_file(example_file, lazy=False)
    gemf_dict_in = gemf.to_dict()
    gemf.save_tiles(outdir_example_tiles)


    # rewrite gemf file
    gemf.write(outfile_rewritten)
    gemf = GEMF.from_file(outfile_rewritten, lazy=False)
    gemf_dict_out = gemf.to_dict()


    # read from tiles
    gemf = GEMF.from_tiles(outdir_example_tiles, lazy=False)
    gemf_dict_tile = gemf.to_dict()

    for key in ['header_info', 'source_data', 'range_data', 'range_details']:
        assert gemf_dict_in["header"][key] == gemf_dict_out["header"][key], f"Input .gemf does not equal rewritten .gemf @ {key}"
        assert gemf_dict_in["header"][key] == gemf_dict_tile["header"][key], f"Input .gemf does not equal .gemf from tiles @ {key}"

    assert len(gemf_dict_in["data"]) == len(gemf_dict_out["data"]), "Data @ Input .gemf does not equal rewritten .gemf."
    assert len(gemf_dict_in["data"]) == len(gemf_dict_tile["data"]), "Data @ Input .gemf does not equal .gemf from tiles."