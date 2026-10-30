from app.routes.defects import ALLOWED

def test_cannot_close_defect_directly_from_open():
    # A bug cannot skip straight to closed. It must be verified first.
    assert "Closed" not in ALLOWED["Open"]

def test_closed_requires_verified():
    # A bug can only close if it is currently in "Verified" status
    assert "Closed" in ALLOWED["Verified"]