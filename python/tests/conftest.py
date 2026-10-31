from pathlib import Path

import pytest

from openhead.client import Head
from openhead.sim import SimServer
from openhead.tokens import TokenStore

REPO = Path(__file__).resolve().parents[2]
FACE_BUILT = (REPO / "face" / "dist" / "index.html").exists()

needs_face = pytest.mark.skipif(not FACE_BUILT, reason="face/dist missing: npm run build in face/")


@pytest.fixture
def store(tmp_path: Path) -> TokenStore:
    return TokenStore(tmp_path / "tokens.json")


@pytest.fixture
async def sim():
    """Headless simulator on a free port; fails the test if it sent anything off-schema."""
    if not FACE_BUILT:
        pytest.skip("face/dist missing: npm run build in face/")
    server = SimServer(host="127.0.0.1", port=0, mdns=False, validate_outgoing=True)
    await server.start()
    yield server
    await server.stop()
    assert server.violations == []


@pytest.fixture
async def head(sim: SimServer, store: TokenStore):
    """Paired client connected to the simulator."""
    h = await Head.connect("127.0.0.1", sim.port, client="pytest", store=store)
    await h.pair("0000")
    yield h
    await h.close()
