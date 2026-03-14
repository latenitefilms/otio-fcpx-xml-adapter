# OpenTimelineIO FCPXML Adapter
[![Build Status](https://github.com/OpenTimelineIO/otio-fcpx-xml-adapter/actions/workflows/ci.yaml/badge.svg)](https://github.com/OpenTimelineIO/otio-fcpx-xml-adapter/actions/workflows/ci.yaml)
![Dynamic YAML Badge](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOpenTimelineIO%2Fotio-fcpx-xml-adapter%2Fmain%2F.github%2Fworkflows%2Fci.yaml&query=%24.jobs%5B%22test-plugin%22%5D.strategy.matrix%5B%22otio-version%22%5D&label=OpenTimelineIO)
![Dynamic YAML Badge](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOpenTimelineIO%2Fotio-fcpx-xml-adapter%2Fmain%2F.github%2Fworkflows%2Fci.yaml&query=%24.jobs%5B%22test-plugin%22%5D.strategy.matrix%5B%22python-version%22%5D&label=Python)

The `FCPXML` adapter is part of OpenTimelineIO's contrib adapter plugins.

It provides reading and writing of Final Cut Pro formatted XML files.

Supported inputs and outputs:

- `.fcpxml` files
- `.fcpxmld` packages, using `Info.fcpxml` as the document entrypoint

For more information on the FCPXML format please check the links in the [reference](#fcpx-xml-references) section.

---

# Maintainer

The OpenTimelineIO FCPXML Adapter is now maintained by [Chris Hocking](https://github.com/latenitefilms) at [LateNite](https://fcp.cafe/latenite/).

Chris runs [FCP Cafe](https://fcp.cafe) - the ultimate nerd community for Final Cut Pro editors and developers.

---

# Technical Support

You can get technical support for this adapter on the [FCP Cafe Discord](https://ltnt.tv/discord).

---

# Adapter Feature Matrix

The following features of OTIO are supported by the `FCPXML` adapter:

| Feature                      | Support | Notes |
|------------------------------|:-------:|-------|
| Single Track of Clips        | ✔       |       |
| Multiple Video Tracks        | ✔       | Includes secondary lanes and anchored storylines. |
| Audio Tracks & Clips         | ✔       | |
| Gap/Filler                   | ✔       | |
| Markers                      | ✔       | |
| Nesting                      | ✔       | `ref-clip` and `sync-clip` are supported. |
| Transitions                  | ✔       | Version-aware read/write across legacy and modern FCPXML variants. |
| Titles / Generators          | ✔       | Title text blocks and style defs are preserved on roundtrip. |
| Audio/Video Effects          | ◐       | Common `filter-*` and `adjust-*` elements roundtrip; unsupported mappings are preserved as metadata when possible. |
| Linear Speed Effects         | ✔       | Linear time maps and freeze frames are supported. |
| Fancy Speed Effects          | ✖       | Complex retime curves without a direct OTIO equivalent are not fully modeled. |
| Multicam (`mc-clip`)         | ◐       | Roundtrips through OTIO metadata because OTIO does not have a native multicam schema. |
| Auditions                    | ◐       | Roundtrips through OTIO metadata because OTIO does not have a native audition schema. |
| Color Decision List          | ✖       | |
| Image Sequence Reference     | ✖       | |

---

# Supported FCPXML Versions

The adapter currently supports reading and writing FCPXML `v1.0` through `v1.14`.

It supports both standard `.fcpxml` documents and `.fcpxmld` packages. When
reading a package, the adapter loads `Info.fcpxml`. When writing to a
`.fcpxmld` path, the adapter creates the package directory and writes the XML to
`Info.fcpxml`.

The writer is version-aware and adjusts output for differences such as:

- Root/library/project structure
- Project-scoped versus document-scoped resources
- Legacy `asset` source serialization versus `media-rep`
- Legacy filter and transition resource handling

---

# Testing

Run the test suite with:

```bash
python3 -m pytest -q
```

The suite includes:

- version-specific fixture coverage across supported FCPXML releases
- DTD validation with `xmllint` when it is available
- a real-world sample corpus roundtrip over `llm-resources/SampleFCPXMLs`
- `.fcpxmld` package read/write coverage using `Info.fcpxml`

The sample corpus test reads each sample, writes it back using the original
FCPXML version, re-reads the result, and asserts that the roundtrip does not
introduce new DTD validation errors relative to the source file.

---

# FCPX XML References

- [FCP Cafe](https://fcp.cafe/developers/fcpxml/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/professional-video-applications/fcpxml-reference)

---

# License

OpenTimelineIO and the FCPXML adapter are open source software.

Please see the [LICENSE](LICENSE) for details.

Nothing in the license file or this project grants any right to use Pixar or any other contributor’s trade names, trademarks, service marks, or product names.

---

# Contributions

If you want to contribute to the project, please see: https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html

Please also read up on [testing your code](https://github.com/OpenTimelineIO/otio-plugin-template#testing-your-plugin-during-development) in the "getting started" section of the OpenTimelineIO plugin template repository.

---

# Contact

For more information, please visit http://opentimeline.io/
or https://github.com/AcademySoftwareFoundation/OpenTimelineIO
or join our discussion forum: https://lists.aswf.io/g/otio-discussion
