"""Tests for XML builder (Plan 01-04-C)."""

from fractions import Fraction
from pathlib import Path

import xml.etree.ElementTree as ET

from scenecutbatch.core.models import DetectionResult, DetectConfig, Scene
from scenecutbatch.export.xml_builder import build_xml, write_xml


def _make_result(tmp_path, stem="take_042", num_scenes=2, fps=Fraction(30, 1)):
    clip_path = (tmp_path / f"{stem}.mov").resolve()
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
    return DetectionResult(clip_path=clip_path, fps=fps, scenes=scenes)


def test_build_xml_contains_master_and_subclips(tmp_path):
    """build_xml output: xmeml v5, bin name = clip stem, master sequence has
    clipitems in order, subclips present, pathurl file://localhost/ + abs path."""
    stem = "take_042"
    num_scenes = 2
    result = _make_result(tmp_path, stem=stem, num_scenes=num_scenes)
    xml = build_xml(result, DetectConfig())
    root = ET.fromstring(xml)
    assert root.tag == "xmeml"
    assert root.get("version") == "5"

    bin_el = root.find("bin")
    assert bin_el is not None
    assert bin_el.find("name").text == stem

    children = bin_el.find("children")
    assert children is not None

    # Master sequence
    seq = children.find("sequence")
    assert seq is not None
    assert seq.get("id") == f"seq_{stem}"
    rate = seq.find("rate")
    assert rate.find("timebase").text == "30"
    assert rate.find("ntsc").text == "FALSE"

    # clipitems in timeline order
    track = seq.find("media/video/track")
    clipitems = track.findall("clipitem")
    assert len(clipitems) == num_scenes
    starts = [int(ci.find("start").text) for ci in clipitems]
    assert starts == [i * 30 for i in range(num_scenes)]
    ends = [int(ci.find("end").text) for ci in clipitems]
    assert ends == [(i + 1) * 30 for i in range(num_scenes)]

    # Virtual subclips
    subclips = children.findall("clip")
    assert len(subclips) == num_scenes
    for i, sc in enumerate(subclips):
        assert sc.get("id") == f"subclip_{i}"
        assert sc.find("name").text == f"{stem}_scene_{i}"
        assert sc.find("duration").text == "30"

    # pathurl present with file://localhost/ + absolute forward-slash path
    pathurls = [pu.text for pu in root.iter("pathurl")]
    assert len(pathurls) >= 1
    assert all(p.startswith("file://localhost/") for p in pathurls)
    assert all("/" in p and "\\" not in p for p in pathurls)
    assert str(result.clip_path.resolve().as_posix()) in pathurls[0]


def test_write_xml_writes_file(tmp_path):
    """write_xml creates {stem}_cuts.xml on disk under tmp output dir, file parses."""
    result = _make_result(tmp_path)
    out = tmp_path / f"{result.clip_path.stem}_cuts.xml"
    written = write_xml(result, out, DetectConfig())
    assert written == out
    assert out.exists()
    ET.parse(out)  # must be valid XML
