"""FCP7 XML builder for virtual subclips."""

from __future__ import annotations

import urllib.parse
from fractions import Fraction
from pathlib import Path
from typing import Optional

import xml.etree.ElementTree as ET

from ..core.models import DetectionResult, DetectConfig


def _pathurl(path: Path) -> str:
    """Build a Premiere-compatible file://localhost/ pathurl (forward slashes)."""
    absolute = path.resolve()
    # as_posix() gives forward slashes even on Windows (C:/...).
    return "file://localhost/" + absolute.as_posix()


def _timecode_frames(fps: Fraction, seconds: float) -> int:
    """Convert seconds to frame count using exact Fraction fps math (D-02)."""
    return int(round(seconds * float(fps)))


def build_xml(result: DetectionResult, config: Optional[DetectConfig] = None) -> str:
    """Return FCP7 xmeml v5 XML string for a detection result.

    Structure:
      <xmeml version="5">
        <bin>
          <name>{stem}</name>
          <children>
            <sequence id="seq_{stem}">  (master sequence)
              <name>{stem}_master</name>
              <rate><timebase>{fps denominator}</timebase><ntsc>FALSE</ntsc></rate>
              <media><video><track>
                one <clipitem> per scene (start/end/in/out as frames, file ref w/ pathurl)
              </track></video></media>
            </sequence>
            one virtual <clip id="subclip_N"> per scene referencing same <file> pathurl
          </children>
        </bin>
      </xmeml>
    """
    config = config or DetectConfig()
    stem = result.clip_path.stem
    fps = result.fps if result.fps else Fraction(30, 1)
    # FCP7 <timebase> is frames-per-second (e.g. 30); ntsc TRUE for 23.976/29.97.
    fps_value = int(round(float(fps)))
    ntsc = "TRUE" if abs(float(fps) - round(float(fps))) > 1e-6 else "FALSE"

    xmeml = ET.Element("xmeml", version="5")
    bin_el = ET.SubElement(xmeml, "bin")

    name_el = ET.SubElement(bin_el, "name")
    name_el.text = stem

    children = ET.SubElement(bin_el, "children")

    # Shared <file> referenced by master clipitems and virtual subclips (no media duplication).
    file_el = ET.Element("file")
    file_el.set("id", f"file_{stem}")
    file_name = ET.SubElement(file_el, "name")
    file_name.text = result.clip_path.name
    pathurl_el = ET.SubElement(file_el, "pathurl")
    pathurl_el.text = _pathurl(result.clip_path)
    file_rate = ET.SubElement(file_el, "rate")
    file_timebase = ET.SubElement(file_rate, "timebase")
    file_timebase.text = str(fps_value)
    file_ntsc = ET.SubElement(file_rate, "ntsc")
    file_ntsc.text = ntsc

    # ---------- Master sequence ----------
    sequence = ET.SubElement(children, "sequence")
    sequence.set("id", f"seq_{stem}")
    seq_name = ET.SubElement(sequence, "name")
    seq_name.text = f"{stem}_master"

    rate = ET.SubElement(sequence, "rate")
    timebase = ET.SubElement(rate, "timebase")
    timebase.text = str(fps_value)
    seq_ntsc = ET.SubElement(rate, "ntsc")
    seq_ntsc.text = ntsc

    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    track = ET.SubElement(video, "track")

    for scene in result.scenes:
        clipitem = ET.SubElement(track, "clipitem")
        clipitem.set("id", f"clip_{scene.index}")
        cname = ET.SubElement(clipitem, "name")
        cname.text = f"{stem}_scene_{scene.index}"
        start_el = ET.SubElement(clipitem, "start")
        start_el.text = str(scene.start_frame)
        end_el = ET.SubElement(clipitem, "end")
        end_el.text = str(scene.end_frame)
        in_el = ET.SubElement(clipitem, "in")
        in_el.text = str(scene.start_frame)
        out_el = ET.SubElement(clipitem, "out")
        out_el.text = str(scene.end_frame)

        # File ref referencing the shared file (no duplication).
        fileref = ET.SubElement(clipitem, "file")
        fileref.set("id", f"file_{stem}")
        ref_name = ET.SubElement(fileref, "name")
        ref_name.text = result.clip_path.name
        ref_pathurl = ET.SubElement(fileref, "pathurl")
        ref_pathurl.text = _pathurl(result.clip_path)
        ref_rate = ET.SubElement(fileref, "rate")
        ref_tb = ET.SubElement(ref_rate, "timebase")
        ref_tb.text = str(fps_value)
        ref_ntsc = ET.SubElement(ref_rate, "ntsc")
        ref_ntsc.text = ntsc

    # ---------- Virtual subclips ----------
    for scene in result.scenes:
        subclip = ET.SubElement(children, "clip")
        subclip.set("id", f"subclip_{scene.index}")
        sname = ET.SubElement(subclip, "name")
        sname.text = f"{stem}_scene_{scene.index}"
        duration = ET.SubElement(subclip, "duration")
        duration.text = str(scene.end_frame - scene.start_frame)
        srate = ET.SubElement(subclip, "rate")
        stb = ET.SubElement(srate, "timebase")
        stb.text = str(fps_value)
        sntsc = ET.SubElement(srate, "ntsc")
        sntsc.text = ntsc

        sub_media = ET.SubElement(subclip, "media")
        sub_video = ET.SubElement(sub_media, "video")
        sub_track = ET.SubElement(sub_video, "track")
        sub_clipitem = ET.SubElement(sub_track, "clipitem")
        sub_clipitem.set("id", f"subclip_{scene.index}_item")
        sub_item_name = ET.SubElement(sub_clipitem, "name")
        sub_item_name.text = f"{stem}_scene_{scene.index}"
        sub_start = ET.SubElement(sub_clipitem, "start")
        sub_start.text = "0"
        sub_end = ET.SubElement(sub_clipitem, "end")
        sub_end.text = str(scene.end_frame - scene.start_frame)
        sub_in = ET.SubElement(sub_clipitem, "in")
        sub_in.text = "0"
        sub_out = ET.SubElement(sub_clipitem, "out")
        sub_out.text = str(scene.end_frame - scene.start_frame)

        sub_fileref = ET.SubElement(sub_clipitem, "file")
        sub_fileref.set("id", f"file_{stem}")
        sub_ref_name = ET.SubElement(sub_fileref, "name")
        sub_ref_name.text = result.clip_path.name
        sub_ref_pathurl = ET.SubElement(sub_fileref, "pathurl")
        sub_ref_pathurl.text = _pathurl(result.clip_path)
        sub_ref_rate = ET.SubElement(sub_fileref, "rate")
        sub_ref_tb = ET.SubElement(sub_ref_rate, "timebase")
        sub_ref_tb.text = str(fps_value)
        sub_ref_ntsc = ET.SubElement(sub_ref_rate, "ntsc")
        sub_ref_ntsc.text = ntsc

    ET.indent(xmeml, space="  ")
    xml_str = ET.tostring(xmeml, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


def write_xml(result: DetectionResult, output_path: Path,
              config: Optional[DetectConfig] = None) -> Path:
    """Write XML to disk and return path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_xml(result, config)
    output_path.write_text(content, encoding="utf-8")
    return output_path
