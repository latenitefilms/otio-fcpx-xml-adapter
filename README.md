# OpenTimelineIO FCPXML Adapter
[![Build Status](https://github.com/OpenTimelineIO/otio-fcpx-xml-adapter/actions/workflows/ci.yaml/badge.svg)](https://github.com/OpenTimelineIO/otio-fcpx-xml-adapter/actions/workflows/ci.yaml)
![Dynamic YAML Badge](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOpenTimelineIO%2Fotio-fcpx-xml-adapter%2Fmain%2F.github%2Fworkflows%2Fci.yaml&query=%24.jobs%5B%22test-plugin%22%5D.strategy.matrix%5B%22otio-version%22%5D&label=OpenTimelineIO)
![Dynamic YAML Badge](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOpenTimelineIO%2Fotio-fcpx-xml-adapter%2Fmain%2F.github%2Fworkflows%2Fci.yaml&query=%24.jobs%5B%22test-plugin%22%5D.strategy.matrix%5B%22python-version%22%5D&label=Python)

The `FCPXML` adapter is part of OpenTimelineIO's contributor adapter plugins.

It provides reading and writing of Final Cut Pro formatted XML files.

Supported inputs and outputs:

- `.fcpxml` files
- `.fcpxmld` packages (using `Info.fcpxml` as the document entry point)

For more information on the FCPXML format please check the links in the [reference](#fcpx-xml-references) section.

---

## Maintainer

The OpenTimelineIO FCPXML Adapter is now maintained by [Chris Hocking](https://github.com/latenitefilms) at [LateNite](https://fcp.cafe/latenite/).

Chris runs [FCP Cafe](https://fcp.cafe) - the ultimate nerd community for Final Cut Pro editors and developers.

---

## Technical Support

You can get technical support for this adapter on the [FCP Cafe Discord](https://ltnt.tv/discord).

---

## Adapter Feature Matrix

The following features of OTIO are supported by the `FCPXML` adapter:

| Feature                      | Support | Notes                                                                                                              |
|------------------------------|:-------:|--------------------------------------------------------------------------------------------------------------------|
| Single Track of Clips        | ✔       |                                                                                                                    |
| Multiple Video Tracks        | ✔       | Includes secondary lanes and anchored storylines.                                                                  |
| Audio Tracks & Clips         | ✔       |                                                                                                                    |
| Gap/Filler                   | ✔       |                                                                                                                    |
| Markers                      | ✔       |                                                                                                                    |
| Nesting                      | ✔       | `ref-clip` and `sync-clip` are supported.                                                                          |
| Transitions                  | ✔       | Version-aware read/write across legacy and modern FCPXML variants.                                                 |
| Titles / Generators          | ✔       | Title text blocks and style defs are preserved on roundtrip.                                                       |
| Audio/Video Effects          | ◐       | Common `filter-*` and `adjust-*` elements roundtrip; unsupported mappings are preserved as metadata when possible. |
| Linear Speed Effects         | ✔       | Linear time maps and freeze frames are supported.                                                                  |
| Fancy Speed Effects          | ✖       | Complex retime curves without a direct OTIO equivalent are not fully modeled.                                      |
| Multicam (`mc-clip`)         | ◐       | Roundtrips through OTIO metadata because OTIO does not have a native multicam schema.                              |
| Auditions                    | ◐       | Roundtrips through OTIO metadata because OTIO does not have a native audition schema.                              |
| Color Decision List          | ✖       |                                                                                                                    |
| Image Sequence Reference     | ✖       |                                                                                                                    |

---

## Supported FCPXML Versions

The adapter currently supports reading and writing FCPXML `v1.0` through `v1.14`.

It supports both standard `.fcpxml` documents and `.fcpxmld` packages.

When reading a package, the adapter loads `Info.fcpxml`.

When writing to a `.fcpxmld` path, the adapter creates the package directory and writes the FCPXML to `Info.fcpxml`.

The writer is version-aware and adjusts output for differences such as:

- Root/library/project structure
- Project-scoped versus document-scoped resources
- Legacy `asset` source serialization versus `media-rep`
- Legacy filter and transition resource handling

---

## Frequently Asked Questions

### Why does FCPXML use Rational Numbers?

Final Cut Pro expresses time values as a rational number of seconds with a 64-bit numerator and a 32-bit denominator.

Frame rates for NTSC-compatible media, for example, use a frame duration of `1001/30000s` (`29.97fps`) or `1001/60000s` (`59.94fps`).

If a time value is equal to a whole number of seconds, Final Cut Pro may reduce the fraction into whole seconds (for example, `5s`).

So... Why?

Because one of Apple's core frameworks/technologies, [Core Media](https://developer.apple.com/documentation/coremedia) also represents time as a rational value, with a time value as the numerator and timescale as the denominator.

The structure can represent a specific numeric time in the media timeline, and can also represent nonnumeric values like invalid and indefinite times or positive and negative infinity.

---

### Learning FCPXML

You can read [Demystifying Final Cut Pro XMLs by Philip Hodgetts and Gregory Clarke](https://fcp.cafe/developer-case-studies/fcpxml/) on FCP Cafe, which gives a fantastic introduction to FCPXML.

---

### swift-daw-file-tools

[Steffan Andrews](https://github.com/orchetect) has created an amazing Swift Framework called [swift-daw-file-tools](https://github.com/orchetect/swift-daw-file-tools), which can read and process FCPXML.

---

### SwiftSecuencia

SwiftSecuencia provides a type-safe, Swift-native API for creating and exporting media timelines. Build timelines programmatically and export to professional formats for Final Cut Pro, audio production, and more.

You can learn more about [SwiftSecuencia](https://github.com/intrusive-memory/SwiftSecuencia).

---

### Pipeline Neo (CLI & Library)

**Pipeline Neo** is modern Swift 6 framework for working with Final Cut Pro's FCPXML with full concurrency support and SwiftTimecode integration. Pipeline Neo is a spiritual successor to the original [Pipeline](https://github.com/reuelk/pipeline), modernised for Swift 6.0 and contemporary development practices.

Pipeline Neo provides a comprehensive API for parsing, creating, and manipulating FCPXML files with advanced timecode operations, async/await patterns, and robust error handling. Built with Swift 6.0 and targeting macOS 12+, it offers type-safe operations, comprehensive test coverage, and seamless integration with SwiftTimecode for professional video editing workflows.

Pipeline Neo's codebase is derived from [swift-daw-file-tools](https://github.com/orchetect/swift-daw-file-tools) and [SwiftSecuencia](https://github.com/intrusive-memory/SwiftSecuencia). The project now includes an experimental CLI tool for testing and expanding Pipeline Neo's functionality.

This codebase is developed using AI agents.

You can learn more about [Pipeline Neo](https://github.com/TheAcharya/pipeline-neo).

---

### Preferred XML Editor

I'm a massive fan of [BBEdit 14](https://www.barebones.com/products/bbedit/).

It has a 30 day free trial, and is also available on the Mac App Store.

---

### DTD Validation

macOS has a built in XML lint tool - allowing you to validate a `FCPXML` document against it's `DTD` file.

!!!primary What's a DTD?
A DTD (Document Type Definition) file is used in XML to define the structure and the legal elements and attributes of an XML document. It's a set of markup declarations that provide a rulebook for a specific type of XML document, describing what the document contains and how those elements and attributes are organised.
!!!

You can download all the [`FCPXML` `DTD` files](https://github.com/CommandPost/CommandPost/tree/develop/src/extensions/cp/apple/fcpxml/dtd).

You can then use this Terminal Command to validate things:

```
xmllint --dtdvalid "/path/to/FCPXMLv1_9.dtd" "/path/to/your/file.fcpxml"
```

!!!primary Tip!
You can just drag in a file from Finder into Terminal, and Terminal will write out the file's path.<br />
Simply type `xmllint --dtdvalid`, then drag in the `DTD` file from Finder, and then your `FCPXML` file.
!!!

---

## Testing

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

## FCPXML Documentation

- [FCPXML on FCP Cafe](https://fcp.cafe/developers/fcpxml/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/professional-video-applications/fcpxml-reference)

---

## License

OpenTimelineIO and the FCPXML adapter are open source software.

Please see the [LICENSE](LICENSE.md) for details.

Nothing in the license file or this project grants any right to use Pixar or any other contributor’s trade names, trademarks, service marks, or product names.

---

## Contributions

If you want to contribute to the project, please read the [Contributing website](https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html).

Please also read up on [testing your code](https://github.com/OpenTimelineIO/otio-plugin-template#testing-your-plugin-during-development) in the **Getting Started** section of the OpenTimelineIO plugin template repository.

---

## Contact

For more information, please visit the [OpenTimelineIO website](https://opentimeline.io) or join our [Discussion Forum](https://lists.aswf.io/g/otio-discussion).