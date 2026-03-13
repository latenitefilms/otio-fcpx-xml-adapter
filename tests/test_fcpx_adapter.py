# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
from unittest import mock
import xml.etree.ElementTree as ET

import opentimelineio as otio
import pytest

from otio_fcpx_xml_adapter.fcpx_xml import META_NAMESPACE, format_name


TEST_DIR = Path(__file__).resolve().parent
ROOT_DIR = TEST_DIR.parent
SAMPLE_DIR = TEST_DIR / "sample_data"
DTD_PATH = ROOT_DIR / "llm-resources" / "DTDs" / "FCPXMLv1_14.dtd"

SAMPLE_LIBRARY_XML = SAMPLE_DIR / "fcpx_library.fcpxml"
SAMPLE_PROJECT_XML = SAMPLE_DIR / "fcpx_project.fcpxml"
SAMPLE_EVENT_XML = SAMPLE_DIR / "fcpx_event.fcpxml"
SAMPLE_CLIPS_XML = SAMPLE_DIR / "fcpx_clips.fcpxml"
SAMPLE_VERSION_1_14_XML = SAMPLE_DIR / "fcpx_version_1_14.fcpxml"
SAMPLE_MULTI_EVENT_LIBRARY_XML = SAMPLE_DIR / "fcpx_multi_event_library.fcpxml"
SAMPLE_TRANSITIONS_XML = SAMPLE_DIR / "fcpx_transitions.fcpxml"

DRAGGED_EVENT_XML = ROOT_DIR / "llm-resources" / "Dragged FCP Event.fcpxml"
DRAGGED_LIBRARY_XML = ROOT_DIR / "llm-resources" / "Dragged FCP Library.fcpxml"
DRAGGED_PROJECT_XML = ROOT_DIR / "llm-resources" / "Dragged FCP Project.fcpxml"
DRAGGED_CLIPS_XML = ROOT_DIR / "llm-resources" / "Dragged FCPXML Clips.fcpxml"
DRAGGED_EVENTS_XML = ROOT_DIR / "llm-resources" / "Dragged FCPXML Events.fcpxml"
COMPLEX_LIBRARY_XML = (
    ROOT_DIR / "llm-resources" / "Example of Complex Library FCPXML.fcpxml"
)

EXPECTED_VIDEO_SIGNATURES = [
    [
        ("Clip", "IMG_0715"),
        ("Transition", "Cross Dissolve"),
        ("Stack", "compound_clip_1"),
        ("Clip", "IMG_0233"),
        ("Clip", "IMG_0687"),
        ("Clip", "IMG_0268"),
        ("Stack", "compound_clip_1"),
    ],
    [
        ("Clip", "IMG_0513"),
        ("Transition", "Cross Dissolve"),
        ("Clip", "IMG_0268"),
        ("Transition", "Cross Dissolve"),
        ("Clip", "IMG_0740"),
    ],
    [("Clip", "IMG_0857")],
]
EXPECTED_AUDIO_SIGNATURES = [
    [
        ("Clip", "IMG_0715"),
        ("Clip", "IMG_0513"),
        ("Clip", "IMG_0687"),
        ("Clip", "IMG_0233"),
        ("Clip", "IMG_0687"),
        ("Stack", "compound_clip_1"),
    ]
]


def read_fcpx_file(path):
    return otio.adapters.read_from_file(str(path))


def read_fcpx_string(xml_string):
    return otio.adapters.read_from_string(xml_string, "fcpx_xml")


def write_fcpx(obj, **kwargs):
    return otio.adapters.write_to_string(obj, "fcpx_xml", **kwargs)


def first_timeline(obj):
    if isinstance(obj, otio.schema.Timeline):
        return obj
    timelines = list(obj.find_children(descended_from_type=otio.schema.Timeline))
    assert timelines
    return timelines[0]


def track_signature(track):
    return [
        (type(item).__name__, getattr(item, "name", ""))
        for item in track
        if not isinstance(item, otio.schema.Gap)
    ]


def first_non_gap(track):
    return next(item for item in track if not isinstance(item, otio.schema.Gap))


def assert_v114_valid(xml_string):
    xmllint = shutil.which("xmllint")
    if not xmllint:
        pytest.skip("xmllint is required for DTD validation")

    with tempfile.NamedTemporaryFile(
        "w", suffix=".fcpxml", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(xml_string)
        temp_path = Path(handle.name)

    try:
        result = subprocess.run(
            [xmllint, "--noout", "--dtdvalid", str(DTD_PATH), str(temp_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        temp_path.unlink(missing_ok=True)

    assert result.returncode == 0, result.stderr


def make_external_clip(name, duration_frames=48, rate=24, target_url=None):
    duration = otio.opentime.RationalTime(duration_frames, rate)
    source_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(0, rate),
        duration=duration,
    )
    return otio.schema.Clip(
        name=name,
        media_reference=otio.schema.ExternalReference(
            target_url=target_url or "file:///tmp/{}.mov".format(name),
            available_range=source_range,
        ),
        source_range=source_range,
    )


def make_video_timeline(name, *items):
    track = otio.schema.Track(kind=otio.schema.TrackKind.Video)
    for item in items:
        track.append(item)
    timeline = otio.schema.Timeline(name=name)
    timeline.tracks.append(track)
    return timeline


@pytest.fixture(scope="module")
def complex_library():
    return read_fcpx_file(COMPLEX_LIBRARY_XML)


@pytest.fixture(scope="module")
def dragged_library():
    return read_fcpx_file(DRAGGED_LIBRARY_XML)


def test_format_name():
    with mock.patch.object(subprocess, "check_output", return_value=b"640x360\n"):
        with mock.patch("os.path.exists", return_value=True):
            assert format_name(25, "file:///dummy.mov") == "FFVideoFormat640x360p25"


@pytest.mark.parametrize(
    "fixture_path",
    [SAMPLE_PROJECT_XML, SAMPLE_EVENT_XML, SAMPLE_LIBRARY_XML],
)
def test_project_style_fixtures_roundtrip_and_validate(fixture_path):
    obj = read_fcpx_file(fixture_path)
    timeline = first_timeline(obj)

    assert timeline.name == "OpenTimeline_Project"
    assert len(timeline.tracks) == 4
    assert len(timeline.video_tracks()) == 3
    assert len(timeline.audio_tracks()) == 1
    assert [track_signature(track) for track in timeline.video_tracks()] == (
        EXPECTED_VIDEO_SIGNATURES
    )
    assert [track_signature(track) for track in timeline.audio_tracks()] == (
        EXPECTED_AUDIO_SIGNATURES
    )

    xml_string = write_fcpx(obj)
    assert_v114_valid(xml_string)

    roundtrip = read_fcpx_string(xml_string)
    roundtrip_timeline = first_timeline(roundtrip)
    assert roundtrip_timeline.name == timeline.name
    assert len(roundtrip_timeline.video_tracks()) == 3
    assert len(roundtrip_timeline.audio_tracks()) == 1
    assert sum(
        1
        for track in roundtrip_timeline.video_tracks()
        for item in track
        if isinstance(item, otio.schema.Transition)
    ) == 3
    assert any(
        isinstance(item, otio.schema.Stack) and item.name == "compound_clip_1"
        for track in roundtrip_timeline.video_tracks()
        for item in track
    )


def test_clips_collection_roundtrip_preserves_metadata_and_shape():
    collection = read_fcpx_file(SAMPLE_CLIPS_XML)

    assert [type(item).__name__ for item in collection] == ["Stack", "Clip", "Clip"]
    assert [item.name for item in collection] == [
        "compound_clip_1",
        "IMG_0857",
        "IMG_0858",
    ]
    assert collection[0].metadata[META_NAMESPACE]["container"] == "ref-clip"

    clip = collection[1]
    fcpx_metadata = clip.metadata[META_NAMESPACE]
    assert fcpx_metadata["note"] == "Truck in snow"
    assert [keyword["value"] for keyword in fcpx_metadata["keywords"]] == [
        "snow",
        "truck",
    ]
    assert fcpx_metadata["metadata"][0]["key"] == "com.apple.proapps.studio.angle"

    xml_string = write_fcpx(collection)
    assert_v114_valid(xml_string)

    roundtrip = read_fcpx_string(xml_string)
    assert [type(item).__name__ for item in roundtrip] == ["Stack", "Clip", "Clip"]
    assert [item.name for item in roundtrip] == [
        "compound_clip_1",
        "IMG_0857",
        "IMG_0858",
    ]
    roundtrip_clip = roundtrip[1]
    assert roundtrip_clip.metadata[META_NAMESPACE]["note"] == "Truck in snow"
    assert [keyword["value"] for keyword in roundtrip_clip.metadata[META_NAMESPACE]["keywords"]] == [
        "snow",
        "truck",
    ]


def test_version_1_14_media_rep_enabled_and_v14_write():
    timeline = read_fcpx_file(SAMPLE_VERSION_1_14_XML)
    track = timeline.video_tracks()[0]
    first_clip = track[0]

    assert timeline.name == "Version_Test_Project"
    assert first_clip.media_reference.target_url.endswith("TestClip_A.mov")
    assert first_clip.media_reference.metadata[META_NAMESPACE]["asset"]["media_reps"]
    assert track[0].enabled is True
    assert track[1].enabled is False

    xml_string = write_fcpx(timeline)
    assert_v114_valid(xml_string)
    root = ET.fromstring(xml_string)
    assert root.get("version") == "1.14"
    for asset in root.findall("./resources/asset"):
        assert "src" not in asset.attrib
        assert asset.findall("./media-rep")

    roundtrip = read_fcpx_string(xml_string)
    assert roundtrip.video_tracks()[0][1].enabled is False


def test_write_rejects_non_v114_versions():
    timeline = read_fcpx_file(SAMPLE_VERSION_1_14_XML)
    with pytest.raises(NotImplementedError):
        write_fcpx(timeline, fcpxml_version="1.11")


def test_multi_event_library_structure_roundtrip_and_validate():
    collection = read_fcpx_file(SAMPLE_MULTI_EVENT_LIBRARY_XML)
    events = list(collection)

    assert [event.name for event in events] == ["Event_One", "Event_Two"]
    assert [first_timeline(event).name for event in events] == [
        "Project_In_Event1",
        "Project_In_Event2",
    ]

    xml_string = write_fcpx(collection)
    assert_v114_valid(xml_string)

    roundtrip = read_fcpx_string(xml_string)
    roundtrip_events = list(roundtrip)
    assert [event.name for event in roundtrip_events] == ["Event_One", "Event_Two"]
    assert [first_timeline(event).name for event in roundtrip_events] == [
        "Project_In_Event1",
        "Project_In_Event2",
    ]


def test_transition_metadata_order_and_roundtrip():
    timeline = read_fcpx_file(SAMPLE_TRANSITIONS_XML)
    track = timeline.video_tracks()[0]
    transitions = [item for item in track if isinstance(item, otio.schema.Transition)]

    assert track_signature(track) == [
        ("Clip", "Clip_A"),
        ("Transition", "Cross Dissolve"),
        ("Clip", "Clip_B"),
        ("Transition", "Cross Dissolve"),
        ("Clip", "Clip_C"),
    ]
    assert len(transitions) == 2
    assert transitions[0].transition_type == otio.schema.TransitionTypes.SMPTE_Dissolve
    assert transitions[0].in_offset.value == 15
    assert transitions[0].out_offset.value == 15
    assert transitions[0].metadata[META_NAMESPACE]["filter_video"]["name"] == (
        "Cross Dissolve"
    )
    assert "filter_audio" in transitions[0].metadata[META_NAMESPACE]

    xml_string = write_fcpx(timeline)
    assert_v114_valid(xml_string)
    roundtrip = read_fcpx_string(xml_string)
    roundtrip_transitions = [
        item
        for item in roundtrip.video_tracks()[0]
        if isinstance(item, otio.schema.Transition)
    ]
    assert len(roundtrip_transitions) == 2
    assert roundtrip_transitions[0].metadata[META_NAMESPACE]["filter_video"]["name"] == (
        "Cross Dissolve"
    )


def test_title_generator_read_from_complex_sample(complex_library):
    title_clips = [
        clip
        for clip in complex_library.find_children(descended_from_type=otio.schema.Clip)
        if isinstance(clip.media_reference, otio.schema.GeneratorReference)
        and clip.media_reference.generator_kind == "fcpx.title"
    ]

    assert title_clips
    title_clip = title_clips[0]
    assert title_clip.media_reference.parameters["effect_name"]
    assert "text_xml" in title_clip.media_reference.parameters


def test_title_generator_write_roundtrip_and_validate():
    title_clip = otio.schema.Clip(
        name="Title Card",
        media_reference=otio.schema.GeneratorReference(
            name="Basic Title",
            generator_kind="fcpx.title",
            parameters={
                "effect_name": "Basic Title",
                "effect_uid": "basic-title",
                "effect_src": "file:///Applications/Final Cut Pro.app/Basic%20Title.moti",
                "text_xml": [
                    '<text><text-style ref="ts1">Hello</text-style></text>'
                ],
                "text_style_def_xml": [
                    '<text-style-def id="ts1"><text-style font="Helvetica" fontSize="64"/></text-style-def>'
                ],
            },
        ),
        source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 24),
            duration=otio.opentime.RationalTime(48, 24),
        ),
    )
    timeline = make_video_timeline("TitleTest", title_clip)

    xml_string = write_fcpx(timeline)
    assert_v114_valid(xml_string)
    root = ET.fromstring(xml_string)
    assert root.findall(".//title")
    assert root.findall("./resources/effect")

    roundtrip = read_fcpx_string(xml_string)
    clip = roundtrip.video_tracks()[0][0]
    assert isinstance(clip.media_reference, otio.schema.GeneratorReference)
    assert clip.media_reference.generator_kind == "fcpx.title"


def test_sync_clip_read_from_complex_sample(complex_library):
    sync_clips = [
        stack
        for stack in complex_library.find_children(descended_from_type=otio.schema.Stack)
        if stack.metadata.get(META_NAMESPACE, {}).get("container") == "sync-clip"
    ]

    assert sync_clips
    assert sync_clips[0].name
    assert len(sync_clips[0]) >= 1


def test_sync_clip_write_roundtrip_and_validate():
    inner_track = otio.schema.Track(kind=otio.schema.TrackKind.Video)
    inner_track.append(make_external_clip("Inner"))
    sync_clip = otio.schema.Stack(
        name="SyncClip",
        source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 24),
            duration=otio.opentime.RationalTime(48, 24),
        ),
        metadata={
            META_NAMESPACE: {
                "container": "sync-clip",
                "sync_clip": {"attrs": {"name": "SyncClip"}},
            }
        },
    )
    sync_clip.append(inner_track)
    timeline = make_video_timeline("SyncTest", sync_clip)

    xml_string = write_fcpx(timeline)
    assert_v114_valid(xml_string)
    assert "<sync-clip" in xml_string

    roundtrip = read_fcpx_string(xml_string)
    item = roundtrip.video_tracks()[0][0]
    assert isinstance(item, otio.schema.Stack)
    assert item.metadata[META_NAMESPACE]["container"] == "sync-clip"


def test_direct_adjustments_and_filters_read_from_complex_sample(complex_library):
    matching_clip = None
    for clip in complex_library.find_children(descended_from_type=otio.schema.Clip):
        effect_tags = {
            effect.metadata.get(META_NAMESPACE, {}).get("element")
            for effect in clip.effects
        }
        if {"adjust-transform", "filter-video"}.issubset(effect_tags):
            matching_clip = clip
            break

    assert matching_clip is not None
    assert any(
        effect.metadata[META_NAMESPACE]["element"] == "adjust-transform"
        for effect in matching_clip.effects
    )
    assert any(
        effect.metadata[META_NAMESPACE]["element"] == "filter-video"
        for effect in matching_clip.effects
    )


def test_effect_write_roundtrip_and_validate():
    clip = make_external_clip("FxClip")
    clip.effects.append(
        otio.schema.Effect(
            name="adjust-transform",
            effect_name="adjust-transform",
            metadata={
                META_NAMESPACE: {
                    "element": "adjust-transform",
                    "attrs": {"position": "10 20", "scale": "1.1 1.1"},
                    "params": [],
                    "raw_children": [],
                }
            },
        )
    )
    clip.effects.append(
        otio.schema.Effect(
            name="Gaussian",
            effect_name="Gaussian",
            metadata={
                META_NAMESPACE: {
                    "element": "filter-video",
                    "attrs": {"name": "Gaussian"},
                    "params": [{"name": "Amount", "key": "1", "value": "0.5"}],
                    "resource": {"name": "Gaussian", "uid": "gaussian-filter"},
                }
            },
        )
    )
    timeline = make_video_timeline("FxTest", clip)

    xml_string = write_fcpx(timeline)
    assert_v114_valid(xml_string)
    roundtrip = read_fcpx_string(xml_string)
    effect_tags = [
        effect.metadata[META_NAMESPACE]["element"]
        for effect in roundtrip.video_tracks()[0][0].effects
    ]
    assert effect_tags == ["adjust-transform", "filter-video"]


def test_conform_rate_is_mapped_to_linear_time_warp(complex_library):
    warped_clip = None
    for clip in complex_library.find_children(descended_from_type=otio.schema.Clip):
        if any(
            isinstance(effect, otio.schema.LinearTimeWarp)
            and effect.metadata.get(META_NAMESPACE, {}).get("conform_rate")
            for effect in clip.effects
        ):
            warped_clip = clip
            break

    assert warped_clip is not None


def test_linear_time_map_and_freeze_frame_roundtrip_and_validate():
    linear_clip = make_external_clip("Linear")
    linear_clip.effects.append(
        otio.schema.LinearTimeWarp(
            name="LinearTimeWarp",
            time_scalar=2.0,
            metadata={
                META_NAMESPACE: {
                    "time_map": {
                        "attrs": {},
                        "points": [
                            {"time": "0s", "value": "0s"},
                            {"time": "2s", "value": "4s"},
                        ],
                    }
                }
            },
        )
    )
    freeze_clip = make_external_clip("Freeze")
    freeze_clip.effects.append(
        otio.schema.FreezeFrame(
            name="FreezeFrame",
            metadata={
                META_NAMESPACE: {
                    "time_map": {
                        "attrs": {},
                        "points": [
                            {"time": "0s", "value": "0s"},
                            {"time": "2s", "value": "0s"},
                        ],
                    }
                }
            },
        )
    )
    timeline = make_video_timeline("TimeMapTest", linear_clip, freeze_clip)

    xml_string = write_fcpx(timeline)
    assert_v114_valid(xml_string)
    roundtrip = read_fcpx_string(xml_string)
    effect_types = [
        type(effect).__name__
        for clip in roundtrip.video_tracks()[0]
        if isinstance(clip, otio.schema.Clip)
        for effect in clip.effects
    ]
    assert effect_types == ["LinearTimeWarp", "FreezeFrame"]


def test_note_keywords_ratings_and_metadata_arrays_are_preserved(complex_library):
    clips_collection = read_fcpx_file(SAMPLE_CLIPS_XML)
    annotated_clip = clips_collection[1]
    assert annotated_clip.metadata[META_NAMESPACE]["note"] == "Truck in snow"
    assert [keyword["value"] for keyword in annotated_clip.metadata[META_NAMESPACE]["keywords"]] == [
        "snow",
        "truck",
    ]

    sample_timeline = read_fcpx_file(SAMPLE_PROJECT_XML)
    media_metadata = (
        first_non_gap(sample_timeline.video_tracks()[0])
        .media_reference.metadata[META_NAMESPACE]["asset"]["metadata"]
    )
    codecs_entry = next(
        entry for entry in media_metadata
        if entry["key"] == "com.apple.proapps.spotlight.kMDItemCodecs"
    )
    assert [item["text"] for item in codecs_entry["array"]] == ["AAC", "H.264"]

    rated_clip = next(
        clip
        for clip in complex_library.find_children(descended_from_type=otio.schema.Clip)
        if clip.metadata.get(META_NAMESPACE, {}).get("ratings")
    )
    assert rated_clip.metadata[META_NAMESPACE]["ratings"][0]["value"] == "favorite"


def test_format_without_frame_duration_falls_back_to_format_name_rate():
    xml_string = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE fcpxml>
        <fcpxml version="1.14">
            <resources>
                <format id="r1" name="FFVideoFormat720p25" width="1280" height="720"/>
                <asset id="r2" name="still" format="r1" start="0s" duration="1s" hasVideo="1" hasAudio="0">
                    <media-rep kind="original-media" src="file:///tmp/still.jpg"/>
                </asset>
            </resources>
            <project name="Still Frame">
                <sequence duration="1s" format="r1" tcStart="0s" tcFormat="NDF">
                    <spine>
                        <asset-clip name="still" ref="r2" offset="0s" start="0s" duration="1s"/>
                    </spine>
                </sequence>
            </project>
        </fcpxml>
        """
    )

    timeline = read_fcpx_string(xml_string)
    clip = timeline.video_tracks()[0][0]
    assert clip.source_range.duration.rate == 25
    assert clip.media_reference.available_range.duration.rate == 25


@pytest.mark.parametrize("tag_name", ["mc-clip", "audition"])
def test_top_level_unsupported_story_items_raise(tag_name):
    xml_string = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE fcpxml>
        <fcpxml version="1.14">
            <resources/>
            <event name="Unsupported">
                <{tag} name="Example" duration="1s"/>
            </event>
        </fcpxml>
        """.format(tag=tag_name)
    )

    with pytest.raises(NotImplementedError):
        read_fcpx_string(xml_string)


@pytest.mark.parametrize(
    "fixture_path, expected_type, min_timelines, min_clips",
    [
        (DRAGGED_EVENT_XML, otio.schema.SerializableCollection, 1, 1),
        (DRAGGED_LIBRARY_XML, otio.schema.SerializableCollection, 1, 1),
        (DRAGGED_PROJECT_XML, otio.schema.Timeline, 1, 0),
        (DRAGGED_CLIPS_XML, otio.schema.SerializableCollection, 0, 1),
        (DRAGGED_EVENTS_XML, otio.schema.SerializableCollection, 1, 1),
    ],
)
def test_smoke_read_dragged_samples(fixture_path, expected_type, min_timelines, min_clips):
    obj = read_fcpx_file(fixture_path)

    assert isinstance(obj, expected_type)
    if isinstance(obj, otio.schema.Timeline):
        assert len(obj.tracks) >= 1
    else:
        assert len(list(obj.find_children(descended_from_type=otio.schema.Timeline))) >= (
            min_timelines
        )
        assert len(list(obj.find_children(descended_from_type=otio.schema.Clip))) >= (
            min_clips
        )


def test_dragged_library_preserves_non_editorial_collection_metadata(dragged_library):
    events = list(dragged_library)
    assert len(events) == 5
    assert events[1].metadata[META_NAMESPACE]["event"]["raw_items"]

    xml_string = write_fcpx(dragged_library)
    assert_v114_valid(xml_string)


def test_complex_library_smoke_read_and_write_validate(complex_library):
    assert len(complex_library) == 40
    assert any(
        isinstance(clip.media_reference, otio.schema.GeneratorReference)
        and clip.media_reference.generator_kind == "fcpx.title"
        for clip in complex_library.find_children(descended_from_type=otio.schema.Clip)
    )
    assert any(
        stack.metadata.get(META_NAMESPACE, {}).get("container") == "sync-clip"
        for stack in complex_library.find_children(descended_from_type=otio.schema.Stack)
    )

    xml_string = write_fcpx(complex_library)
    assert_v114_valid(xml_string)
