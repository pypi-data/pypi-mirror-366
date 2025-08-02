# Robot Framework Tabular Report

[![Build Status](https://img.shields.io/github/workflow/status/p-zander/robotframework-tabular-report/CI)](https://github.com/p-zander/robotframework-tabular-report/actions)

## Overview

**Robot Framework Tabular Report** is an extension for Robot Framework that generates tabular test reports for easier overview and to make them more accessible. The report can be converted into various formats, currently CSV and Excel.

## Features

- Generates test results in a tabular format
- Supports multiple file formats: CSV, XLSX
- Easy integration with Robot Framework
- Customizable columns and report content
- Customizable formatting (only XLSX)

## Installation

```bash
pip install robotframework-tabular-report
```

## Usage

### Basic Example

The Writers provided by this library can easily be utilized using the `--prerebotmodifier` option (see [here](https://robotframework.org/robotframework//latest/RobotFrameworkUserGuide.html#programmatic-modification-of-results)) either directly during the test execution

```bash
robot --prerebotmodifier CsvWriter:myfile my_tests
```

or afterwards using existing test results:

```bash
rebot --prerebotmodifier XlsWriter:workbook output.xml
```

## Configuration

You can customize the columns and formatting in the command line. All writers support the following parameters:

- `output_filename`: Name for the output file without extension (mandatory argument)
- `format_specifier`: Select test result properties for the output (See [Format Specifiers](#format-specifiers)) 
- `docs_max_len`: When writing Test/Suite documentation to output, limit length (default: 100)

### CsvWriter

Additionally this Writer support the following arguments:

- `delim`: Delimeter (one character) to use in CSV file, use special value "TAB" to generate a Tab-separated file (default: `,`)

### XlsWriter

Additionally this Writer support the following arguments:

- `colored_status`: Use conditional formatting to color red/green in test status column (Truthy/Falsy, default: `True`)
- `colored_rows`: Color complete test case row read/green depending on test status (Truthy/Falsy, default: `False`)

### Details

Note: The formatting based on test status is only supported, when the `status` field is present in the output.

The arguments need to be provided in order, following the Modifier name and separated by `:`, all parameters other then the filename are optional. An argument setting can be skipped (empty assignment, i.e. `::`), when needing to set a latter parameter.

**Example:**
```
robot --prerebotmodifier CsvWriter:myfile:name,status,parent.metadata,tags::TAB my_tests
```
This would create a Tab-separated file ``myfile.csv``, with the provided fields and the default Doc length.

**Example 2:**
```
robot --prerebotmodifier XlsWriter:workbook::::Yes my_tests
```
This would create a Excel file ``workbook.xlsx``, with the default fields and formatting (red/green) applied to each test depending on the test status.

## Format Specifiers

The format specifiers are expected to be one of the properties of the [TestCase](https://robot-framework.readthedocs.io/en/latest/autodoc/robot.result.html#robot.result.model.TestCase) result model or the [TestSuite](https://robot-framework.readthedocs.io/en/latest/autodoc/robot.result.html#robot.result.model.TestSuite) result model, accessible via the `parent` field. This includes, but might not be limited to:

|Fields|Comments|
|  ---  |  ---  |
| `(parent.)doc`            |  Test Case/Suite Documentation                       |
| `(parent.)elapsedtime`    |  Time spent in Test Case/Suite as String             |
| `(parent.)endtime`        |  Timestamp of Test Case/Suite end                    |
| `(parent.)failed`         |  Representation of "FAIL" status as Bool             |
| `(parent.)full_name`      |  Normally "Suite Name.Test Name"                     |
| `(parent.)has_setup`      |  If Test Case/Suite has a setup defined              |
| `(parent.)has_teardown`   |  If Test Case/Suite has a teardown defined           |
| `(parent.)id`             |  Automatically set Id                                |
| `(parent.)message`        |  Test Message of Test Case/Suite if set              |
| `(parent.)name`           |  Name of the Test Case/Suite                         |
| `(parent.)not_run`        |  Representation of "NOT RUN" status as Bool          |
| `(parent.)passed`         |  Representation of "PASS" status as Bool             |
| `(parent.)setup`          |  Keyword name for Test Case/Suite setup if set       |
| `(parent.)skipped`        |  Representation of "SKIP" status as Bool             |
| `(parent.)source`         |  Path to source file of Test Case/Suite              |
| `(parent.)starttime`      |  Timestamp of Test Case/Suite start                  |
| `(parent.)status`         |  Test Case/Suite result                              |
| `(parent.)teardown`       |  Keyword name for Test Case/Suite teardown if set    |
| `body`                    |  Test Case content as parsed from source file        |
| `lineno`                  |  Line number to Test Case definition in source file  |
| `parent.all_tests`        |  List of all Test Cases in Suite                     |
| `parent.full_message`     |  Combination of message and stat_message             |
| `parent.has_tests`        |  If Test Suite is empty                              |
| `parent.metadata`         |  Free suite metadata if set (list of tuples)         |
| `parent.stat_message`     |  Test Suite statistics as String                     |
| `parent.test_count`       |  Number of all Test Cases in Suite                   |
| `tags`                    |  Test Case Tags                                      |
| `timeout`                 |  Test Case Timeout                                   |

The **Default format** would be equivalent to the following specifier:
```full_name,doc,tags,status,message,elapsedtime,starttime,endtime```

When using the special value `LONG` for the `format_specifier` argument, this library provides another pre-configured format, which is equivalent to:
```id,parent.name,name,parent.metadata,doc,tags,status,message,elapsedtime,starttime,endtime,timeout,source,lineno```

Limited testing was done on all the other fields seen here. Your kilometerage may vary.

Examples files can be found here ([myfile.csv](test/myfile.csv) and [myfile.xlsx](test/myfile.xlsx)) as well as my basis for testing.

## Contact

For questions or support, please open an issue.

---

*No AI was harmed in the making of this Readme.*

