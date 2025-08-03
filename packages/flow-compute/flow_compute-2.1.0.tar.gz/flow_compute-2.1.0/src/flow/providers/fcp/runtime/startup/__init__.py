"""FCP startup script generation.

This package builds startup scripts for FCP instances:
- Main builder orchestration
- Modular script sections
- Template engine abstraction
"""

from .builder import FCPStartupScriptBuilder, StartupScript
from .sections import (
    CodeUploadSection,
    DockerSection,
    HeaderSection,
    S3Section,
    ScriptContext,
    UserScriptSection,
    VolumeSection,
)
from .templates import create_template_engine, ITemplateEngine

__all__ = [
    # Builder
    "FCPStartupScriptBuilder",
    "StartupScript",
    # Sections
    "ScriptContext",
    "HeaderSection",
    "VolumeSection",
    "S3Section",
    "DockerSection",
    "CodeUploadSection",
    "UserScriptSection",
    # Templates
    "ITemplateEngine",
    "create_template_engine",
]
