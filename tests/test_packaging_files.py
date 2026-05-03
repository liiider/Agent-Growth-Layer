from pathlib import Path


def test_dockerfile_installs_after_copying_source() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8").splitlines()

    install_index = dockerfile.index("RUN pip install --no-cache-dir .")
    server_copy_index = dockerfile.index("COPY server ./server")
    sdk_copy_index = dockerfile.index("COPY sdk ./sdk")

    assert server_copy_index < install_index
    assert sdk_copy_index < install_index


def test_dockerignore_excludes_generated_outputs() -> None:
    dockerignore = Path(".dockerignore").read_text(encoding="utf-8")

    assert "data" in dockerignore
    assert "sdk/javascript/node_modules" in dockerignore
    assert "sdk/javascript/dist" in dockerignore
    assert "__pycache__" in dockerignore
