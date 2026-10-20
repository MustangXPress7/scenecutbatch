"""Tests for XML builder (Task 01-01-C)."""

from fractions import Fraction
from pathlib import Path

import xml.etree.ElementTree as ET

from scenecutbatch.core.models import DetectionResult, DetectConfig, Scene
from scenecutbatch.export.xml_builder import build_xml, write_xml


def _make_result(stem="take_042", num_scenes=3, fps=Fraction(30, 1)):
    scenes = []
    for i in range(num_scenes):
        start = i * 30
        end = start + 30
        scenes.append(
            Scene(
                index=i,
                start_frame=start,
                end_frame=end,
                start_time=start / 30.0,
                end_time=end / 30.0,
                start_tc=f"00:00:{start // 30:02d}:00",
                end_tc=f"00:00:{end // 30:02d}:00",
                duration_sec=(end - start) / 30.0,
                detection_score=0.0,
            )
        )
    return DetectionResult(
        clip_path=Path(f"/Footage/{stem}.mov"),
        fps=fps,
        scenes=scenes,
    )


def test_build_xml_contains_master_and_subclips():
    """build_xml output parses as XML, root xmeml version 5, master + subclips + pathurl."""
    result = _make_result()
    xml = build_xml(result, DetectConfig())
    root = ET.fromstring(xml)
    assert root.tag == "xmeml"
    assert root.get("version") == "5"

    bin_el = root.find("bin")
    assert bin_el is not None
    assert bin_el.find("name").text == "take_042"

    children = bin_el.find("children")
    assert children is not None

    # Master sequence
    seq = children.find("sequence")
    assert seq is not None
    assert seq.get("id") == "seq_take_042"
    rate = seq.find("rate")
    assert rate.find("timebase").text == "30"
    assert rate.find("ntsc").text == "FALSE"

    # clipitems in timeline order
    track = seq.find("media/video/track")
    clipitems = track.findall("clipitem")
    assert len(clipitems) == 3
    starts = [int(ci.find("start").text) for ci in clipitems]
    assert starts == [0, 30, 60]

    # Virtual subclips
    subclips = children.findall("clip")
    assert len(subclips) == 3
    for i, sc in enumerate(subclips):
        assert sc.get("id") == f"subclip_{i}"
        assert sc.find("name").text == f"take_042_scene_{i}"

    # pathurl present with file://localhost/ + forward slashes
    pathurls = root.iter("pathurl")
    pathurl_list = [pu.text for pu in pathurls]
    assert all(p.startswith("file://localhost/") for p in pathurl_list)
    assert all("/" in p and "\\" not in p for p in pathurl_list)


def test_write_xml_produces_file_on_disk(tmp_path):
    """write_xml produces {stem}_cuts.xml on disk."""
    result = _make_result()
    out = tmp_path / "take_042_cuts.xml"
    written = write_xml(result, out, DetectConfig())
    assert written == out
    assert out.exists()
    ET.parse(out)  # must be valid XML
