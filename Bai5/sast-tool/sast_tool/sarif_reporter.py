import jsonpickle
from sarif_om import (
    SarifLog,
    Run,
    Tool,
    ToolComponent,
    Result,
    Message,
    ArtifactLocation,
    Location,
    PhysicalLocation,
    Region,
)


class SarifReporter:
    """Xuất danh sách issue sang định dạng chuẩn SARIF 2.1.0."""

    SCHEMA_URI = "https://json.schemastore.org/sarif-2.1.0.json"

    def generate_report(self, issues, output_file="report.sarif",
                        analyzed_file="input.py"):
        results = []

        for item in issues:
            location = Location(
                physical_location=PhysicalLocation(
                    artifact_location=ArtifactLocation(uri=analyzed_file),
                    region=Region(
                        start_line=item["lineno"],
                        start_column=item["col_offset"] + 1,
                    ),
                )
            )
            results.append(Result(
                message=Message(text=item["message"]),
                locations=[location],
            ))

        run = Run(
            tool=Tool(driver=ToolComponent(name="PySAST", version="1.0.0")),
            results=results,
        )
        log = SarifLog(
            schema_uri=self.SCHEMA_URI,
            version="2.1.0",
            runs=[run],
        )

        with open(output_file, "w") as f:
            f.write(jsonpickle.encode(log, unpicklable=False, indent=2))
