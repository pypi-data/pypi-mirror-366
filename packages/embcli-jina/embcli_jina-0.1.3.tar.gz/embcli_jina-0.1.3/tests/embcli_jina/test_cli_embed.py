import json
import os
from importlib.resources import files

import pytest
from click.testing import CliRunner
from embcli_core.cli import embed

skip_if_no_api_key = pytest.mark.skipif(
    not os.environ.get("JINA_API_KEY") or not os.environ.get("RUN_JINA_MULTIMODAL_TESTS") == "1",
    reason="JINA_API_KEY and RUN_JINA_MULTIMODAL_TESTS environment variables not set",
)


@skip_if_no_api_key
def test_embed_command_text(plugin_manager, mocker):
    mocker.patch("embcli_jina.jina.TIMEOUT_SEC", 30)
    mocker.patch("embcli_core.cli._pm", plugin_manager)
    runner = CliRunner()
    result = runner.invoke(embed, ["--model", "jina-v3", "flying cat"])
    assert result.exit_code == 0

    embeddings = json.loads(result.output)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 1024
    assert all(isinstance(val, float) for val in embeddings)


@skip_if_no_api_key
def test_embed_command_image(plugin_manager, mocker):
    mocker.patch("embcli_jina.jina_multimodal.TIMEOUT_SEC", 60)
    mocker.patch("embcli_core.cli._pm", plugin_manager)
    runner = CliRunner()
    image_path = files("tests.embcli_jina").joinpath("flying_cat.jpeg")
    result = runner.invoke(embed, ["--model", "jina-clip-v2", "--image", str(image_path)])
    assert result.exit_code == 0

    embeddings = json.loads(result.output)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 1024
    assert all(isinstance(val, float) for val in embeddings)
