# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os
import subprocess
import sys
import unittest
import unittest.mock
import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils
from otio_fcpx_xml_adapter.fcpx_xml import format_name


SAMPLE_LIBRARY_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_library.fcpxml"
)
SAMPLE_PROJECT_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_project.fcpxml"
)
SAMPLE_EVENT_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_event.fcpxml"
)
SAMPLE_CLIPS_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_clips.fcpxml"
)
SAMPLE_VERSION_1_14_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_version_1_14.fcpxml"
)
SAMPLE_MULTI_EVENT_LIBRARY_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_multi_event_library.fcpxml"
)
SAMPLE_TRANSITIONS_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_transitions.fcpxml"
)


class AdaptersFcpXXmlTest(unittest.TestCase, otio_test_utils.OTIOAssertions):
    """
    The test class for the FCP X XML adapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_library_roundtrip(self):
        container = otio.adapters.read_from_file(SAMPLE_LIBRARY_XML)
        timeline = container.find_children(
            descended_from_type=otio.schema.Timeline)[0]

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        self.assertEqual(len(timeline.video_tracks()), 3)
        self.assertEqual(len(timeline.audio_tracks()), 1)

        video_clip_names = (
            (
                'IMG_0715',
                "",
                'compound_clip_1',
                'IMG_0233',
                'IMG_0687',
                'IMG_0268',
                'compound_clip_1'
            ),
            ("", 'IMG_0513', "", 'IMG_0268', 'IMG_0740'),
            ("", 'IMG_0857')
        )

        for n, track in enumerate(timeline.video_tracks()):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(container, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(container, new_timeline)

    def test_event_roundtrip(self):
        container = otio.adapters.read_from_file(SAMPLE_EVENT_XML)
        timeline = container.find_children(
            descended_from_type=otio.schema.Timeline)[0]

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        self.assertEqual(len(timeline.video_tracks()), 3)
        self.assertEqual(len(timeline.audio_tracks()), 1)

        video_clip_names = (
            (
                'IMG_0715',
                "",
                'compound_clip_1',
                'IMG_0233',
                'IMG_0687',
                'IMG_0268',
                'compound_clip_1'
            ),
            ("", 'IMG_0513', "", 'IMG_0268', 'IMG_0740'),
            ("", 'IMG_0857')
        )

        for n, track in enumerate(timeline.video_tracks()):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(container, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(container, new_timeline)

    def test_project_roundtrip(self):
        timeline = otio.adapters.read_from_file(SAMPLE_PROJECT_XML)

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        self.assertEqual(len(timeline.video_tracks()), 3)
        self.assertEqual(len(timeline.audio_tracks()), 1)

        video_clip_names = (
            (
                'IMG_0715',
                "",
                'compound_clip_1',
                'IMG_0233',
                'IMG_0687',
                'IMG_0268',
                'compound_clip_1'
            ),
            ("", 'IMG_0513', "", 'IMG_0268', 'IMG_0740'),
            ("", 'IMG_0857')
        )

        for n, track in enumerate(timeline.video_tracks()):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(timeline, new_timeline)

    def test_clips_roundtrip(self):
        container = otio.adapters.read_from_file(SAMPLE_CLIPS_XML)
        fcpx_xml = otio.adapters.write_to_string(container, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(container, new_timeline)

    # --------------------
    # Phase 1: Foundation tests
    # --------------------

    def test_version_read(self):
        """Verify we can read a v1.14 FCPXML without errors."""
        timeline = otio.adapters.read_from_file(SAMPLE_VERSION_1_14_XML)
        self.assertIsNotNone(timeline)
        self.assertEqual(timeline.name, "Version_Test_Project")

    def test_version_write_default(self):
        """Verify default write version is 1.14."""
        timeline = otio.adapters.read_from_file(SAMPLE_VERSION_1_14_XML)
        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        self.assertIn('version="1.14"', fcpx_xml)

    def test_version_write_custom(self):
        """Verify writing with a custom version."""
        timeline = otio.adapters.read_from_file(SAMPLE_VERSION_1_14_XML)
        fcpx_xml = otio.adapters.write_to_string(
            timeline, "fcpx_xml", fcpxml_version="1.11"
        )
        self.assertIn('version="1.11"', fcpx_xml)

    def test_enabled_attribute_read(self):
        """Verify disabled clips are read with enabled=False."""
        timeline = otio.adapters.read_from_file(SAMPLE_VERSION_1_14_XML)
        tracks = timeline.video_tracks()
        self.assertTrue(len(tracks) >= 1)
        track = tracks[0]
        # First clip should be enabled (default)
        self.assertTrue(track[0].enabled)
        # Second clip has enabled="0"
        self.assertFalse(track[1].enabled)

    def test_enabled_attribute_write(self):
        """Verify disabled clips are written with enabled='0'."""
        timeline = otio.adapters.read_from_file(SAMPLE_VERSION_1_14_XML)
        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        self.assertIn('enabled="0"', fcpx_xml)

    def test_enabled_roundtrip(self):
        """Verify enabled attribute survives roundtrip."""
        timeline = otio.adapters.read_from_file(SAMPLE_VERSION_1_14_XML)
        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        new_tracks = new_timeline.video_tracks()
        self.assertFalse(new_tracks[0][1].enabled)

    def test_multi_event_library(self):
        """Verify all events are read from a multi-event library."""
        container = otio.adapters.read_from_file(
            SAMPLE_MULTI_EVENT_LIBRARY_XML
        )
        self.assertIsNotNone(container)
        # Should be a collection of event collections
        events = list(container)
        self.assertEqual(len(events), 2)
        # First event
        event1 = events[0]
        self.assertEqual(event1.name, "Event_One")
        timelines1 = list(event1.find_children(
            descended_from_type=otio.schema.Timeline
        ))
        self.assertEqual(len(timelines1), 1)
        self.assertEqual(timelines1[0].name, "Project_In_Event1")
        # Second event
        event2 = events[1]
        self.assertEqual(event2.name, "Event_Two")
        timelines2 = list(event2.find_children(
            descended_from_type=otio.schema.Timeline
        ))
        self.assertEqual(len(timelines2), 1)
        self.assertEqual(timelines2[0].name, "Project_In_Event2")

    def test_media_rep_read(self):
        """Verify assets with media-rep elements are read correctly."""
        timeline = otio.adapters.read_from_file(SAMPLE_VERSION_1_14_XML)
        tracks = timeline.video_tracks()
        clip = tracks[0][0]
        self.assertIsNotNone(clip.media_reference)
        self.assertFalse(clip.media_reference.is_missing_reference)
        self.assertIn("TestClip_A.mov", clip.media_reference.target_url)

    # --------------------
    # Phase 2: Transitions tests
    # --------------------

    def test_transition_read_count(self):
        """Verify transitions are read from FCPXML."""
        timeline = otio.adapters.read_from_file(SAMPLE_TRANSITIONS_XML)
        track = timeline.video_tracks()[0]
        transitions = [
            item for item in track
            if isinstance(item, otio.schema.Transition)
        ]
        self.assertEqual(len(transitions), 2)

    def test_transition_read_type(self):
        """Verify transition type is mapped correctly."""
        timeline = otio.adapters.read_from_file(SAMPLE_TRANSITIONS_XML)
        track = timeline.video_tracks()[0]
        transitions = [
            item for item in track
            if isinstance(item, otio.schema.Transition)
        ]
        self.assertEqual(transitions[0].name, "Cross Dissolve")
        self.assertEqual(
            transitions[0].transition_type,
            otio.schema.TransitionTypes.SMPTE_Dissolve
        )

    def test_transition_read_duration(self):
        """Verify transition in/out offsets are computed correctly."""
        timeline = otio.adapters.read_from_file(SAMPLE_TRANSITIONS_XML)
        track = timeline.video_tracks()[0]
        transitions = [
            item for item in track
            if isinstance(item, otio.schema.Transition)
        ]
        trans = transitions[0]
        # 1s transition at 30fps -> 15 frames each side
        self.assertEqual(trans.in_offset.value, 15)
        self.assertEqual(trans.out_offset.value, 15)

    def test_transition_read_metadata(self):
        """Verify filter params are preserved in metadata."""
        timeline = otio.adapters.read_from_file(SAMPLE_TRANSITIONS_XML)
        track = timeline.video_tracks()[0]
        transitions = [
            item for item in track
            if isinstance(item, otio.schema.Transition)
        ]
        fcpx_meta = transitions[0].metadata.get("fcpx", {})
        self.assertIn("filter_video", fcpx_meta)
        self.assertEqual(
            fcpx_meta["filter_video"]["name"],
            "Cross Dissolve"
        )
        self.assertIn("filter_audio", fcpx_meta)

    def test_transition_read_track_order(self):
        """Verify track contains clips and transitions in correct order."""
        timeline = otio.adapters.read_from_file(SAMPLE_TRANSITIONS_XML)
        track = timeline.video_tracks()[0]
        # Expected: Clip_A, Transition, Clip_B, Transition, Clip_C
        self.assertEqual(len(track), 5)
        self.assertEqual(track[0].name, "Clip_A")
        self.assertIsInstance(track[1], otio.schema.Transition)
        self.assertEqual(track[2].name, "Clip_B")
        self.assertIsInstance(track[3], otio.schema.Transition)
        self.assertEqual(track[4].name, "Clip_C")

    def test_transition_write(self):
        """Verify transitions are written to FCPXML."""
        timeline = otio.adapters.read_from_file(SAMPLE_TRANSITIONS_XML)
        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        self.assertIn("<transition", fcpx_xml)
        self.assertIn("Cross Dissolve", fcpx_xml)
        self.assertIn("<filter-video", fcpx_xml)
        self.assertIn("<filter-audio", fcpx_xml)

    def test_transition_roundtrip(self):
        """Verify transitions survive a roundtrip."""
        timeline = otio.adapters.read_from_file(SAMPLE_TRANSITIONS_XML)
        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        track = new_timeline.video_tracks()[0]
        transitions = [
            item for item in track
            if isinstance(item, otio.schema.Transition)
        ]
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0].name, "Cross Dissolve")

    def test_format_name(self):
        rvalue = subprocess.check_output(
            [sys.executable, '-c', 'print("640x360")']
        )
        mock_patch = unittest.mock.patch.object
        with mock_patch(subprocess, 'check_output', return_value=rvalue):
            with mock_patch(os.path, 'exists', return_value=True):
                self.assertEqual(
                    format_name(25, "file:///dummy.me"),
                    'FFVideoFormat640x360p25'
                )


if __name__ == '__main__':
    unittest.main()
