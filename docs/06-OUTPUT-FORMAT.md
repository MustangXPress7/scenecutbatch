# 06 — Output Format (FCP7 XML)

## Goal

Produce an FCP7 XML (xmeml) that Premiere Pro imports into a bin containing:

1. A **master sequence** with all detected cuts in timeline order.
2. **Virtual subclips** — one per detected scene — that reference the original
   media file (no duplication).

## Structure (conceptual)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="5">
  <bin>
    <name>take_042</name>
    <children>
      <!-- master sequence -->
      <sequence id="seq_take_042">
        <name>take_042_master</name>
        <rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate>
        <media>
          <video><track>
            <!-- one clipitem per scene, in order -->
            <clipitem id="clip_0">
              <name>take_042_scene_0</name>
              <start>0</start>
              <end>45</end>
              <in>0</in>
              <out>45</out>
              <file id="file_take_042">
                <name>take_042.mov</name>
                <pathurl>file://localhost/D:/Footage/take_042.mov</pathurl>
                <rate>...</rate>
              </file>
            </clipitem>
            ...
          </track></video>
        </media>
      </sequence>

      <!-- virtual subclips -->
      <clip id="subclip_0">
        <name>take_042_scene_0</name>
        <duration>45</duration>
        <rate>...</rate>
        <media><video><track><clipitem>...</clipitem></track></video></media>
        <!-- optional markers -->
        <marker>
          <name>GREEN</name>
          <comment>score=0.92</comment>
          <in>0</in>
          <out>0</out>
        </marker>
      </clip>
      ...
    </children>
  </bin>
</xmeml>
```

## Implementation notes

- Prefer reusing EsqueletoEdit's `export/fcp7xml_exporter.py` (otio-fcp-adapter)
  if it can express virtual subclips. Otherwise build xmeml directly with
  `xml.etree.ElementTree` for full control.
- Frame-accurate: use rational timebase; handle NTSC (23.976, 29.97) via
  `<ntsc>TRUE</ntsc>` + timebase 24/30.
- `pathurl` must be `file://localhost/` + absolute path with forward slashes.
- Test import manually in Premiere Pro (smoke test) before declaring Phase 2 done.
- Keep a golden-file test (like EsqueletoEdit's `tests/golden/`).

## EDL (v2)

Optional. Defer.
