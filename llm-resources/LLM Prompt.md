# OpenTimelineIO FCPXML Adapter

## Overview

You are an LLM acting as a senior staff engineer and tech lead.

You are building a FCPXML adapter for OpenTimelineIO.

> OpenTimelineIO (OTIO) is an API and interchange format for editorial cut information. You can think of it as a modern Edit Decision List (EDL) that also includes an API for reading, writing, and manipulating editorial data. It also includes a plugin system for translating to/from existing editorial formats as well as a plugin system for linking to proprietary media storage schemas.
>
> OTIO supports clips, timing, tracks, transitions, markers, metadata, etc. but not embedded video or audio. Video and audio media are referenced externally. We encourage 3rd party vendors, animation studios and visual effects studios to work together as a community to provide adaptors for each video editing tool and pipeline.

You can find the OpenTimelineIO documentation here:

https://opentimelineio.readthedocs.io/en/stable/

The GitHub repo is here:

https://github.com/AcademySoftwareFoundation/OpenTimelineIO

However you can find the latest OpenTimelineIO Repo locally in:

    - `llm-resources/OpenTimelineIO`

---

## Resources

- You can find all the current `FCPXML` DTDs here:
    - `llm-resources/DTDs/FCPXMLv1_0.dtd`
    - `llm-resources/DTDs/FCPXMLv1_1.dtd`
    - `llm-resources/DTDs/FCPXMLv1_2.dtd`
    - `llm-resources/DTDs/FCPXMLv1_3.dtd`
    - `llm-resources/DTDs/FCPXMLv1_4.dtd`
    - `llm-resources/DTDs/FCPXMLv1_5.dtd`
    - `llm-resources/DTDs/FCPXMLv1_6.dtd`
    - `llm-resources/DTDs/FCPXMLv1_7.dtd`
    - `llm-resources/DTDs/FCPXMLv1_8.dtd`
    - `llm-resources/DTDs/FCPXMLv1_9.dtd`
    - `llm-resources/DTDs/FCPXMLv1_10.dtd`
    - `llm-resources/DTDs/FCPXMLv1_11.dtd`
    - `llm-resources/DTDs/FCPXMLv1_12.dtd`
    - `llm-resources/DTDs/FCPXMLv1_13.dtd`
    - `llm-resources/DTDs/FCPXMLv1_14.dtd`

- You can find some sample FCPXMLs as they appear when dragged from Final Cut Pro's Browser here:
    - `llm-resources/Dragged FCP Event.fcpxml`
    - `llm-resources/Dragged FCP Library.fcpxml`
    - `llm-resources/Dragged FCP Project.fcpxml`
    - `llm-resources/Dragged FCPXML Clips.fcpxml`
    - `llm-resources/Dragged FCPXML Events.fcpxml`

- You can find an example of a complex Final Cut Pro Library FCPXML here: `LLM Resources/Example of Complex Library FCPXML.fcpxml`.

- You can use `https://sosumi.ai/mcp` to read official Apple documentation - for example: `https://sosumi.ai/documentation/professional-video-applications/import-options`

---

## Your Task

I want you to come up with a sensible plan to make the OpenTimelineIO FCPXML Adapter feature complete for FCPXML v1.14 (with the eventual plan to support FCPXML v1.5 onwards).

We should do test-based development.

Once we have a solid plan, I would like you to implement that plan.