"""Unit tests for WorkloadResumeSection."""

import pytest
from flow.providers.fcp.runtime.startup.sections import WorkloadResumeSection, ScriptContext


class TestWorkloadResumeSection:
    """Test WorkloadResumeSection functionality."""
    
    def test_section_properties(self):
        """Test basic section properties."""
        section = WorkloadResumeSection()
        assert section.name == "workload_resume"
        assert section.priority == 85  # After Docker, before UserScript
    
    def test_should_include_with_docker(self):
        """Test section is included when Docker image is present."""
        section = WorkloadResumeSection()
        
        # Should include with Docker
        context = ScriptContext(
            docker_image="ubuntu:22.04",
            enable_workload_resume=True
        )
        assert section.should_include(context) is True
        
        # Should not include if disabled
        context.enable_workload_resume = False
        assert section.should_include(context) is False
    
    def test_should_include_with_user_script(self):
        """Test section is included when user script is present."""
        section = WorkloadResumeSection()
        
        # Should include with user script
        context = ScriptContext(
            user_script="#!/bin/bash\necho 'Hello'",
            enable_workload_resume=True
        )
        assert section.should_include(context) is True
        
        # Should not include with empty user script
        context.user_script = "  "
        assert section.should_include(context) is False
    
    def test_generate_creates_systemd_service(self):
        """Test that generate creates proper systemd service."""
        section = WorkloadResumeSection()
        context = ScriptContext(
            docker_image="ubuntu:22.04",
            enable_workload_resume=True,
            task_id="test-task-123"
        )
        
        output = section.generate(context)
        
        # Check key components
        assert "flow-workload-resume.service" in output
        assert "systemctl enable flow-workload-resume.service" in output
        assert "/usr/local/sbin/flow-workload-resume.sh" in output
        assert "TASK_ID=\"test-task-123\"" in output
        assert "After=network-online.target docker.service" in output
        assert "ConditionPathExists=!/var/run/fcp-startup-complete" in output
    
    def test_docker_resume_logic(self):
        """Test Docker-specific resume logic generation."""
        section = WorkloadResumeSection()
        context = ScriptContext(
            docker_image="nginx:latest",
            docker_command=["nginx", "-g", "daemon off;"],
            ports=[80, 443],
            enable_workload_resume=True
        )
        
        output = section.generate(context)
        
        # Check Docker resume logic
        assert "docker ps -a --format '{{.Names}}'" in output
        assert "docker inspect -f '{{.State.Status}}' main" in output
        assert "docker start main" in output
        assert "docker run" in output
        assert "-p 80:80" in output
        assert "-p 443:443" in output
        assert "nginx:latest" in output
    
    def test_user_script_resume_logic(self):
        """Test user script resume logic generation."""
        section = WorkloadResumeSection()
        user_script = """#!/bin/bash
# FLOW_RESUME_SAFE
echo "This script can be resumed"
"""
        context = ScriptContext(
            user_script=user_script,
            enable_workload_resume=True
        )
        
        output = section.generate(context)
        
        # Check user script resume logic
        assert "/tmp/user_startup.sh" in output
        assert "FLOW_RESUME_SAFE" in output
        assert "User script marked as resume-safe, re-running" in output
    
    def test_gpu_support_in_docker_resume(self):
        """Test GPU support is included in Docker resume command."""
        section = WorkloadResumeSection()
        context = ScriptContext(
            docker_image="nvidia/cuda:11.0-base",
            instance_type="a100-80gb.sxm.1x",
            enable_workload_resume=True
        )
        
        output = section.generate(context)
        
        # Check GPU support
        assert "--gpus all" in output
    
    def test_volume_mounts_in_docker_resume(self):
        """Test volume mounts are included in Docker resume command."""
        section = WorkloadResumeSection()
        context = ScriptContext(
            docker_image="ubuntu:22.04",
            volumes=[
                {"mount_path": "/data", "volume_id": "vol_123"},
                {"mount_path": "/models", "volume_id": "vol_456"}
            ],
            enable_workload_resume=True
        )
        
        output = section.generate(context)
        
        # Check volume mounts
        assert "-v /data:/data" in output
        assert "-v /models:/models" in output
    
    def test_task_state_detection(self):
        """Test task state file detection logic."""
        section = WorkloadResumeSection()
        context = ScriptContext(
            docker_image="ubuntu:22.04",
            enable_workload_resume=True
        )
        
        output = section.generate(context)
        
        # Check state detection logic
        assert "STATE_FILE=\"/var/lib/flow/task-state\"" in output
        assert "if [ ! -f \"$STATE_FILE\" ]; then" in output
        assert "source \"$STATE_FILE\"" in output
    
    def test_logging_functionality(self):
        """Test logging is properly configured."""
        section = WorkloadResumeSection()
        context = ScriptContext(
            docker_image="ubuntu:22.04",
            enable_workload_resume=True
        )
        
        output = section.generate(context)
        
        # Check logging setup
        assert "LOG_FILE=\"/var/log/flow/workload-resume.log\"" in output
        assert "mkdir -p /var/log/flow" in output
        assert "log()" in output
        assert "tee -a \"$LOG_FILE\"" in output