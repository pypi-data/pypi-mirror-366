import os
import subprocess
import time
from pathlib import Path

from fastapi.testclient import TestClient

DATA_DIR = Path(__file__).parent / "data/geotiffs"


def test_setup_aligned_disp_s1_command(tmp_path):
    """Test that the setup-aligned-disp-s1 command creates a config file."""
    config_file = tmp_path / "bowser_rasters.json"

    # Run the setup command
    result = subprocess.run(
        ["bowser", "setup-aligned-disp-s1", str(DATA_DIR), "-o", config_file],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert Path(config_file).exists()
    assert Path(config_file).stat().st_size > 0


def test_fastapi_app_startup(tmp_path):
    """Test that the FastAPI app can start with the sample data."""
    config_file = tmp_path / "bowser_rasters.json"
    # Run the setup command
    subprocess.run(
        ["bowser", "setup-aligned-disp-s1", str(DATA_DIR), "-o", config_file],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    # Set up environment for test
    os.environ["BOWSER_DATASET_CONFIG_FILE"] = str(config_file)

    # Import after setting environment variables
    from bowser.main import app

    client = TestClient(app)

    # Test basic endpoints
    response = client.get("/mode")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data

    response = client.get("/datasets")
    assert response.status_code == 200


def test_bowser_cli_run_command(tmp_path):
    """Test that bowser run command doesn't crash immediately."""
    config_file = tmp_path / "bowser_rasters.json"
    # Run the setup command
    subprocess.run(
        ["bowser", "setup-aligned-disp-s1", str(DATA_DIR), "-o", config_file],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Start the server in background and kill it quickly
    proc = subprocess.Popen(
        ["bowser", "run", "-f", str(config_file), "--port", "8999"],
        cwd=Path(__file__).parent.parent,
    )

    # Give it a moment to start up
    time.sleep(2)

    # Kill the process
    proc.terminate()
    proc.wait(timeout=5)

    # Check it didn't crash immediately
    assert proc.returncode != 1, "Server crashed on startup"
