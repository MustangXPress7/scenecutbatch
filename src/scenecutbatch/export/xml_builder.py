"""FCP7 XML builder for virtual subclips — Premiere Pro compatible."""

from __future__ import annotations

import uuid as uuid_mod
from fractions import Fraction
from pathlib import Path
from typing import Optional

import xml.etree.ElementTree as ET

from ..core.models import DetectionResult, DetectConfig


def _clean_text(text: str) -> str:
    """Return a safe text value for XML elements."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _pathurl(path: Path) -> str:
    """Build a Premiere-compatible file://localhost/ pathurl (forward slashes)."""
    absolute = path.resolve()
    return "file://localhost/" + absolute.as_posix()


def _timecode_frames(fps: Fraction, seconds: float) -> int:
    """Convert seconds to frame count using exact Fraction fps math (D-02)."""
    return int(round(seconds * float(fps)))


def _tc_string(frames: int, fps: Fraction) -> str:
    """Format frames as SMPTE timecode string HH:MM:SS:FF."""
    fps_val = float(fps)
    total_seconds = frames / fps_val
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    frames_remainder = int((total_seconds % 1) * fps_val)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames_remainder:02d}"


def build_xml(result: DetectionResult, config: Optional[DetectConfig] = None) -> str:
    """Return FCP7 xmeml v5 XML string compatible with Premiere Pro.

    Structure mirrors what Premiere Pro exports for scene-cut detection:
      <xmeml version="5">
        <bin>
          <name>{clean_name}</name>
          <labels><label2>[color]</label2></labels>
          <children>
            <clip id="masterclip-N" explodedTracks="true">
              <uuid>{uuid}</uuid>
              <masterclipid>masterclip-N</masterclipid>
              <ismasterclip>TRUE</ismasterclip>
              <duration>{frames}</duration>
              <rate><timebase>{fps}</timebase><ntsc>{ntsc}</ntsc></rate>
              <in>{start_frame}</in>
              <out>{end_frame}</out>
              <name>{clean_name}</name>
              <media>
                <video>
                  <track>
                    <clipitem id="clipitem-N">
                      <masterclipid>masterclip-N</masterclipid>
                      <name>{name}</name>
                      <duration>{frames}</duration>
                      <rate>...</rate>
                      <pproSoftStartOffset>{start_frame}</pproSoftStartOffset>
                      <pproSoftEndOffset>{pproSoftEndOffset}</pproSoftEndOffset>
                      <alphatype>none</alphatype>
                      <pixelaspectratio>square</pixelaspectratio>
                      <anamorphic>FALSE</anamorphic>
                      <file id="file-N">
                        <name>{name}</name>
                        <pathurl>{pathurl}</pathurl>
                        <rate>...</rate>
                        <duration>{total_frames}</duration>
                        <timecode>...</timecode>
                        <media>
                          <video>
                            <samplecharacteristics>
                              <rate>...</rate>
                              <width>1920</width>
                              <height>1080</height>
                              <anamorphic>FALSE</anamorphic>
                              <pixelaspectratio>square</pixelaspectratio>
                              <fielddominance>none</fielddominance>
                            </samplecharacteristics>
                          </video>
                          <audio>
                            <samplecharacteristics>
                              <depth>16</depth>
                              <samplerate>44100</samplerate>
                            </samplecharacteristics>
                            <channelcount>2</channelcount>
                          </audio>
                        </media>
                      </file>
                      <link>
                        <linkclipref>clipitem-N</linkclipref>
                        <mediatype>video</mediatype>
                        <trackindex>1</trackindex>
                        <clipindex>1</clipindex>
                      </link>
                      <link>
                        <linkclipref>clipitem-N</linkclipref>
                        <mediatype>audio</mediatype>
                        <trackindex>1</trackindex>
                        <clipindex>1</clipindex>
                        <groupindex>1</groupindex>
                      </link>
                    </clipitem>
                  </track>
                </video>
                <audio>
                  <track>
                    <clipitem id="clipitem-N">
                      ...
                    </clipitem>
                  </track>
                </audio>
              </media>
            </clip>
          </children>
          <logginginfo>
            <description></description>
            <scene></scene>
            <shottake></shottake>
            <lognote>{url}</lognote>
            <good></good>
            <originalvideofilename></originalvideofilename>
            <originalaudiofilename></originalaudiofilename>
          </logginginfo>
          <colorinfo>
            <lut></lut>
            <lut1></lut1>
            <asc_sop></asc_sop>
            <asc_sat></asc_sat>
            <lut2></lut2>
          </colorinfo>
          <labels>
            <label2>[color]</label2>
          </labels>
        </clip>
      </children>
    </bin>
  </xmeml>
    """
    config = config or DetectConfig()
    stem = result.clip_path.stem
    fps = result.fps if result.fps else Fraction(30, 1)
    fps_value = int(round(float(fps)))
    ntsc = "TRUE" if abs(float(fps) - round(float(fps))) > 1e-6 else "FALSE"

    total_frames = int(round(float(fps) * result.clip_path.stat().st_size / 100000)) if result.clip_path.exists() else 51678
    # Use a reasonable total duration based on the last scene end
    if result.scenes:
        total_frames = result.scenes[-1].end_frame

    xmeml = ET.Element("xmeml", version="5")
    bin_el = ET.SubElement(xmeml, "bin")

    name_el = ET.SubElement(bin_el, "name")
    name_el.text = stem

    labels_el = ET.SubElement(bin_el, "labels")
    label2_el = ET.SubElement(labels_el, "label2")
    label2_el.text = "Mango"

    children = ET.SubElement(bin_el, "children")

    for i, scene in enumerate(result.scenes, 1):
        masterclip_id = f"masterclip-{i}"
        clip_uuid = str(uuid_mod.uuid4())

        # ---------- Master clip ----------
        masterclip = ET.SubElement(children, "clip")
        masterclip.set("id", masterclip_id)
        masterclip.set("explodedTracks", "true")

        uuid_el = ET.SubElement(masterclip, "uuid")
        uuid_el.text = clip_uuid

        mc_id_el = ET.SubElement(masterclip, "masterclipid")
        mc_id_el.text = masterclip_id

        is_master = ET.SubElement(masterclip, "ismasterclip")
        is_master.text = "TRUE"

        duration_el = ET.SubElement(masterclip, "duration")
        duration_el.text = str(scene.end_frame - scene.start_frame)

        rate_el = ET.SubElement(masterclip, "rate")
        tb_el = ET.SubElement(rate_el, "timebase")
        tb_el.text = str(fps_value)
        ntsc_el = ET.SubElement(rate_el, "ntsc")
        ntsc_el.text = ntsc

        in_el = ET.SubElement(masterclip, "in")
        in_el.text = str(scene.start_frame)
        out_el = ET.SubElement(masterclip, "out")
        out_el.text = str(scene.end_frame)

        mc_name = ET.SubElement(masterclip, "name")
        mc_name.text = stem

        # Media
        media = ET.SubElement(masterclip, "media")

        # --- Video track ---
        video = ET.SubElement(media, "video")
        v_track = ET.SubElement(video, "track")

        v_clipitem = ET.SubElement(v_track, "clipitem")
        v_clipitem.set("id", f"clipitem-{2*i-1}")

        v_mc_id = ET.SubElement(v_clipitem, "masterclipid")
        v_mc_id.text = masterclip_id

        v_name = ET.SubElement(v_clipitem, "name")
        v_name.text = stem

        v_duration = ET.SubElement(v_clipitem, "duration")
        v_duration.text = str(scene.end_frame - scene.start_frame)

        v_rate = ET.SubElement(v_clipitem, "rate")
        v_tb = ET.SubElement(v_rate, "timebase")
        v_tb.text = str(fps_value)
        v_ntsc = ET.SubElement(v_rate, "ntsc")
        v_ntsc.text = ntsc

        v_soft_start = ET.SubElement(v_clipitem, "pproSoftStartOffset")
        v_soft_start.text = str(scene.start_frame)
        v_soft_end = ET.SubElement(v_clipitem, "pproSoftEndOffset")
        v_soft_end.text = str(total_frames)

        v_alpha = ET.SubElement(v_clipitem, "alphatype")
        v_alpha.text = "none"
        v_pixel = ET.SubElement(v_clipitem, "pixelaspectratio")
        v_pixel.text = "square"
        v_anamorphic = ET.SubElement(v_clipitem, "anamorphic")
        v_anamorphic.text = "FALSE"

        v_file = ET.SubElement(v_clipitem, "file")
        v_file.set("id", f"file-{i}")
        v_file_name = ET.SubElement(v_file, "name")
        v_file_name.text = stem
        v_file_pathurl = ET.SubElement(v_file, "pathurl")
        v_file_pathurl.text = _pathurl(result.clip_path)
        v_file_rate = ET.SubElement(v_file, "rate")
        v_file_tb = ET.SubElement(v_file_rate, "timebase")
        v_file_tb.text = str(fps_value)
        v_file_ntsc = ET.SubElement(v_file_rate, "ntsc")
        v_file_ntsc.text = ntsc
        v_file_duration = ET.SubElement(v_file, "duration")
        v_file_duration.text = str(total_frames)

        v_file_tc = ET.SubElement(v_file, "timecode")
        v_file_tc_rate = ET.SubElement(v_file_tc, "rate")
        v_file_tc_tb = ET.SubElement(v_file_tc_rate, "timebase")
        v_file_tc_tb.text = str(fps_value)
        v_file_tc_ntsc = ET.SubElement(v_file_tc_rate, "ntsc")
        v_file_tc_ntsc.text = ntsc
        v_file_tc_string = ET.SubElement(v_file_tc, "string")
        v_file_tc_string.text = _tc_string(scene.start_frame, fps)
        v_file_tc_frame = ET.SubElement(v_file_tc, "frame")
        v_file_tc_frame.text = str(scene.start_frame)
        v_file_tc_display = ET.SubElement(v_file_tc, "displayformat")
        v_file_tc_display.text = "NDF"

        v_file_media = ET.SubElement(v_file, "media")
        v_file_video = ET.SubElement(v_file_media, "video")
        v_file_sc = ET.SubElement(v_file_video, "samplecharacteristics")
        v_file_sc_rate = ET.SubElement(v_file_sc, "rate")
        v_file_sc_tb = ET.SubElement(v_file_sc_rate, "timebase")
        v_file_sc_tb.text = str(fps_value)
        v_file_sc_ntsc = ET.SubElement(v_file_sc_rate, "ntsc")
        v_file_sc_ntsc.text = ntsc
        v_file_sc_width = ET.SubElement(v_file_sc, "width")
        v_file_sc_width.text = "1920"
        v_file_sc_height = ET.SubElement(v_file_sc, "height")
        v_file_sc_height.text = "1080"
        v_file_sc_anamorphic = ET.SubElement(v_file_sc, "anamorphic")
        v_file_sc_anamorphic.text = "FALSE"
        v_file_sc_pixel = ET.SubElement(v_file_sc, "pixelaspectratio")
        v_file_sc_pixel.text = "square"
        v_file_sc_field = ET.SubElement(v_file_sc, "fielddominance")
        v_file_sc_field.text = "none"

        v_file_audio = ET.SubElement(v_file_media, "audio")
        v_file_audio_sc = ET.SubElement(v_file_audio, "samplecharacteristics")
        v_file_audio_depth = ET.SubElement(v_file_audio_sc, "depth")
        v_file_audio_depth.text = "16"
        v_file_audio_samplerate = ET.SubElement(v_file_audio_sc, "samplerate")
        v_file_audio_samplerate.text = "44100"
        v_file_audio_channelcount = ET.SubElement(v_file_audio, "channelcount")
        v_file_audio_channelcount.text = "2"

        # Video links
        v_link1 = ET.SubElement(v_clipitem, "link")
        v_link1_ref = ET.SubElement(v_link1, "linkclipref")
        v_link1_ref.text = f"clipitem-{2*i-1}"
        v_link1_mediatype = ET.SubElement(v_link1, "mediatype")
        v_link1_mediatype.text = "video"
        v_link1_trackindex = ET.SubElement(v_link1, "trackindex")
        v_link1_trackindex.text = "1"
        v_link1_clipindex = ET.SubElement(v_link1, "clipindex")
        v_link1_clipindex.text = "1"

        v_link2 = ET.SubElement(v_clipitem, "link")
        v_link2_ref = ET.SubElement(v_link2, "linkclipref")
        v_link2_ref.text = f"clipitem-{2*i}"
        v_link2_mediatype = ET.SubElement(v_link2, "mediatype")
        v_link2_mediatype.text = "audio"
        v_link2_trackindex = ET.SubElement(v_link2, "trackindex")
        v_link2_trackindex.text = "1"
        v_link2_clipindex = ET.SubElement(v_link2, "clipindex")
        v_link2_clipindex.text = "1"
        v_link2_groupindex = ET.SubElement(v_link2, "groupindex")
        v_link2_groupindex.text = "1"

        v_link3 = ET.SubElement(v_clipitem, "link")
        v_link3_ref = ET.SubElement(v_link3, "linkclipref")
        v_link3_ref.text = f"clipitem-{2*i+1}"
        v_link3_mediatype = ET.SubElement(v_link3, "mediatype")
        v_link3_mediatype.text = "audio"
        v_link3_trackindex = ET.SubElement(v_link3, "trackindex")
        v_link3_trackindex.text = "2"
        v_link3_clipindex = ET.SubElement(v_link3, "clipindex")
        v_link3_clipindex.text = "1"
        v_link3_groupindex = ET.SubElement(v_link3, "groupindex")
        v_link3_groupindex.text = "1"

        # --- Audio track 1 ---
        audio = ET.SubElement(media, "audio")
        a_track = ET.SubElement(audio, "track")

        a_clipitem = ET.SubElement(a_track, "clipitem")
        a_clipitem.set("id", f"clipitem-{2*i}")

        a_mc_id = ET.SubElement(a_clipitem, "masterclipid")
        a_mc_id.text = masterclip_id

        a_name = ET.SubElement(a_clipitem, "name")
        a_name.text = stem

        a_duration = ET.SubElement(a_clipitem, "duration")
        a_duration.text = str(scene.end_frame - scene.start_frame)

        a_rate = ET.SubElement(a_clipitem, "rate")
        a_tb = ET.SubElement(a_rate, "timebase")
        a_tb.text = str(fps_value)
        a_ntsc = ET.SubElement(a_rate, "ntsc")
        a_ntsc.text = ntsc

        a_soft_start = ET.SubElement(a_clipitem, "pproSoftStartOffset")
        a_soft_start.text = str(scene.start_frame)
        a_soft_end = ET.SubElement(a_clipitem, "pproSoftEndOffset")
        a_soft_end.text = str(total_frames)

        a_file = ET.SubElement(a_clipitem, "file")
        a_file.set("id", f"file-{i}")

        # Audio links
        a_link1 = ET.SubElement(a_clipitem, "link")
        a_link1_ref = ET.SubElement(a_link1, "linkclipref")
        a_link1_ref.text = f"clipitem-{2*i-1}"
        a_link1_mediatype = ET.SubElement(a_link1, "mediatype")
        a_link1_mediatype.text = "video"
        a_link1_trackindex = ET.SubElement(a_link1, "trackindex")
        a_link1_trackindex.text = "1"
        a_link1_clipindex = ET.SubElement(a_link1, "clipindex")
        a_link1_clipindex.text = "1"

        a_link2 = ET.SubElement(a_clipitem, "link")
        a_link2_ref = ET.SubElement(a_link2, "linkclipref")
        a_link2_ref.text = f"clipitem-{2*i}"
        a_link2_mediatype = ET.SubElement(a_link2, "mediatype")
        a_link2_mediatype.text = "audio"
        a_link2_trackindex = ET.SubElement(a_link2, "trackindex")
        a_link2_trackindex.text = "1"
        a_link2_clipindex = ET.SubElement(a_link2, "clipindex")
        a_link2_clipindex.text = "1"
        a_link2_groupindex = ET.SubElement(a_link2, "groupindex")
        a_link2_groupindex.text = "1"

        a_link3 = ET.SubElement(a_clipitem, "link")
        a_link3_ref = ET.SubElement(a_link3, "linkclipref")
        a_link3_ref.text = f"clipitem-{2*i+1}"
        a_link3_mediatype = ET.SubElement(a_link3, "mediatype")
        a_link3_mediatype.text = "audio"
        a_link3_trackindex = ET.SubElement(a_link3, "trackindex")
        a_link3_trackindex.text = "2"
        a_link3_clipindex = ET.SubElement(a_link3, "clipindex")
        a_link3_clipindex.text = "1"
        a_link3_groupindex = ET.SubElement(a_link3, "groupindex")
        a_link3_groupindex.text = "1"

        # --- Audio track 2 ---
        a2_track = ET.SubElement(audio, "track")

        a2_clipitem = ET.SubElement(a2_track, "clipitem")
        a2_clipitem.set("id", f"clipitem-{2*i+1}")

        a2_mc_id = ET.SubElement(a2_clipitem, "masterclipid")
        a2_mc_id.text = masterclip_id

        a2_name = ET.SubElement(a2_clipitem, "name")
        a2_name.text = stem

        a2_duration = ET.SubElement(a2_clipitem, "duration")
        a2_duration.text = str(scene.end_frame - scene.start_frame)

        a2_rate = ET.SubElement(a2_clipitem, "rate")
        a2_tb = ET.SubElement(a2_rate, "timebase")
        a2_tb.text = str(fps_value)
        a2_ntsc = ET.SubElement(a2_rate, "ntsc")
        a2_ntsc.text = ntsc

        a2_soft_start = ET.SubElement(a2_clipitem, "pproSoftStartOffset")
        a2_soft_start.text = str(scene.start_frame)
        a2_soft_end = ET.SubElement(a2_clipitem, "pproSoftEndOffset")
        a2_soft_end.text = str(total_frames)

        a2_file = ET.SubElement(a2_clipitem, "file")
        a2_file.set("id", f"file-{i}")

        # Audio2 links
        a2_link1 = ET.SubElement(a2_clipitem, "link")
        a2_link1_ref = ET.SubElement(a2_link1, "linkclipref")
        a2_link1_ref.text = f"clipitem-{2*i-1}"
        a2_link1_mediatype = ET.SubElement(a2_link1, "mediatype")
        a2_link1_mediatype.text = "video"
        a2_link1_trackindex = ET.SubElement(a2_link1, "trackindex")
        a2_link1_trackindex.text = "1"
        a2_link1_clipindex = ET.SubElement(a2_link1, "clipindex")
        a2_link1_clipindex.text = "1"

        a2_link2 = ET.SubElement(a2_clipitem, "link")
        a2_link2_ref = ET.SubElement(a2_link2, "linkclipref")
        a2_link2_ref.text = f"clipitem-{2*i}"
        a2_link2_mediatype = ET.SubElement(a2_link2, "mediatype")
        a2_link2_mediatype.text = "audio"
        a2_link2_trackindex = ET.SubElement(a2_link2, "trackindex")
        a2_link2_trackindex.text = "1"
        a2_link2_clipindex = ET.SubElement(a2_link2, "clipindex")
        a2_link2_clipindex.text = "1"
        a2_link2_groupindex = ET.SubElement(a2_link2, "groupindex")
        a2_link2_groupindex.text = "1"

        a2_link3 = ET.SubElement(a2_clipitem, "link")
        a2_link3_ref = ET.SubElement(a2_link3, "linkclipref")
        a2_link3_ref.text = f"clipitem-{2*i+1}"
        a2_link3_mediatype = ET.SubElement(a2_link3, "mediatype")
        a2_link3_mediatype.text = "audio"
        a2_link3_trackindex = ET.SubElement(a2_link3, "trackindex")
        a2_link3_trackindex.text = "2"
        a2_link3_clipindex = ET.SubElement(a2_link3, "clipindex")
        a2_link3_clipindex.text = "1"
        a2_link3_groupindex = ET.SubElement(a2_link3, "groupindex")
        a2_link3_groupindex.text = "1"

        # Logging info
        logginginfo = ET.SubElement(masterclip, "logginginfo")
        li_description = ET.SubElement(logginginfo, "description")
        li_scene = ET.SubElement(logginginfo, "scene")
        li_shottake = ET.SubElement(logginginfo, "shottake")
        li_lognote = ET.SubElement(logginginfo, "lognote")
        li_lognote.text = ""
        li_good = ET.SubElement(logginginfo, "good")
        li_ovf = ET.SubElement(logginginfo, "originalvideofilename")
        li_oaf = ET.SubElement(logginginfo, "originalaudiofilename")

        # Color info
        colorinfo = ET.SubElement(masterclip, "colorinfo")
        ci_lut = ET.SubElement(colorinfo, "lut")
        ci_lut1 = ET.SubElement(colorinfo, "lut1")
        ci_asc_sop = ET.SubElement(colorinfo, "asc_sop")
        ci_asc_sat = ET.SubElement(colorinfo, "asc_sat")
        ci_lut2 = ET.SubElement(colorinfo, "lut2")

        # Labels
        master_labels = ET.SubElement(masterclip, "labels")
        ml_label2 = ET.SubElement(master_labels, "label2")
        ml_label2.text = "Iris"

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
