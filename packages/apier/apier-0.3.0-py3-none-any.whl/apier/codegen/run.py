"""
This module provides the main entry point for running the code generation process.
"""

from collections import defaultdict
from pathlib import Path
from datamodel_code_generator import InputFileType, generate, __main__

if __name__ == "__main__":
    generate(
        input_=Path("tests/definitions/file_upload_api.yaml"),
        input_file_type=InputFileType.OpenAPI,
        output=Path("apier/codegen/models.py"),
        base_class="_build.models.basemodel.IterBaseModel",
        custom_formatters=["apier.codegen.custom_formatter"],
        # custom_template_dir=Path("apier/codegen/templates"),
        # extra_template_data=defaultdict(dict, {"#all#": {"config": {"use_enum_values": True}}})
        # extra_template_data="apier/codegen/config.json",
    )

    # __main__.main([
    #         "--input",
    #         "tests/definitions/file_upload_api.yaml",
    #         "--output",
    #         "apier/codegen/models.py",
    #         "--input-file-type",
    #         "openapi",
    #         "--extra-template-data",
    #         "apier/codegen/config.json",
    #     ])
