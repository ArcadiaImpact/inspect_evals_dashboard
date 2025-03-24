from inspect_evals.metadata import load_listing


def test_load_listing():
    listing = load_listing()
    assert len(listing.evals) > 0
