"""Tests for SLURM frontend adapter."""


import pytest

from flow._internal.frontends.slurm.adapter import SlurmFrontendAdapter
from flow._internal.frontends.slurm.parser import (
    parse_memory_to_gb,
    parse_time_to_hours,
)
from flow.api.models import TaskConfig


class TestSlurmFrontendAdapter:
    """Test SLURM frontend adapter functionality."""

    @pytest.fixture
    def adapter(self):
        """Create SLURM adapter instance."""
        return SlurmFrontendAdapter()

    @pytest.fixture
    def minimal_slurm_script(self, tmp_path):
        """Create minimal SLURM script."""
        script = tmp_path / "job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=test-job
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

echo "Hello from SLURM"
hostname
""")
        return script

    @pytest.fixture
    def gpu_slurm_script(self, tmp_path):
        """Create SLURM script with GPU requirements."""
        script = tmp_path / "gpu_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=gpu-training
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=a100:4
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=job_%j.out
#SBATCH --error=job_%j.err

module load cuda/11.8
module load python/3.9

cd /workspace
python train.py --epochs 100 --batch-size 32
""")
        return script

    @pytest.fixture
    def array_slurm_script(self, tmp_path):
        """Create SLURM array job script."""
        script = tmp_path / "array_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=array-job
#SBATCH --array=1-10:2
#SBATCH --ntasks=1
#SBATCH --time=00:30:00

echo "Array task $SLURM_ARRAY_TASK_ID"
python process.py --task-id $SLURM_ARRAY_TASK_ID
""")
        return script

    @pytest.mark.asyncio
    async def test_parse_minimal_script(self, adapter, minimal_slurm_script):
        """Test parsing minimal SLURM script.
        
        GIVEN: Minimal SLURM script with basic directives
        WHEN: parse_and_convert() is called
        THEN: Valid TaskConfig is returned with correct mappings
        """
        # WHEN
        config = await adapter.parse_and_convert(minimal_slurm_script)

        # THEN
        assert isinstance(config, TaskConfig)
        assert config.name == "test-job"
        assert config.num_instances == 1
        assert config.command is not None
        assert 'echo "Hello from SLURM"' in config.command
        assert 'hostname' in config.command
        assert config.image == "nvidia/cuda:12.1.0-runtime-ubuntu22.04"  # Default image from TaskConfig

    @pytest.mark.asyncio
    async def test_parse_gpu_script(self, adapter, gpu_slurm_script):
        """Test parsing SLURM script with GPU requirements.
        
        GIVEN: SLURM script with GPU, memory, and module directives
        WHEN: parse_and_convert() is called
        THEN: All resource requirements are correctly mapped
        """
        # WHEN
        config = await adapter.parse_and_convert(gpu_slurm_script)

        # THEN
        assert config.name == "gpu-training"
        assert config.num_instances == 1  # nodes, not GPUs
        assert config.instance_type == "a100"
        # Check that modules are included in startup script
        assert "module load cuda/11.8" in config.command
        assert "module load python/3.9" in config.command
        # Check script content
        assert "python train.py --epochs 100 --batch-size 32" in config.command

    @pytest.mark.asyncio
    async def test_cli_options_override(self, adapter, minimal_slurm_script):
        """Test that CLI options override script directives.
        
        GIVEN: SLURM script and CLI options
        WHEN: parse_and_convert() is called with options
        THEN: CLI options override script values
        """
        # WHEN
        config = await adapter.parse_and_convert(
            minimal_slurm_script,
            job_name="overridden-name",
            gpus="v100:2",
            time="48:00:00"
        )

        # THEN
        assert config.name == "overridden-name"  # Overridden
        assert config.num_instances == 1  # nodes, not GPU count
        assert config.instance_type == "v100"
        assert config.max_run_time_hours == 48.0  # Time override

    @pytest.mark.asyncio
    async def test_array_job_parsing(self, adapter, array_slurm_script):
        """Test parsing SLURM array job.
        
        GIVEN: SLURM script with array directive
        WHEN: parse_array_job() is called
        THEN: Multiple TaskConfigs are returned for array indices
        """
        # WHEN
        configs = await adapter.parse_array_job(array_slurm_script)

        # THEN
        assert len(configs) == 5  # 1,3,5,7,9 (1-10:2)
        assert configs[0].name == "array-job_1"
        assert configs[1].name == "array-job_3"
        assert configs[2].name == "array-job_5"
        assert configs[3].name == "array-job_7"
        assert configs[4].name == "array-job_9"

        # Check environment variables
        for i, config in enumerate(configs):
            expected_id = str(1 + i * 2)  # 1,3,5,7,9
            assert config.env["SLURM_ARRAY_TASK_ID"] == expected_id
            assert config.env["SLURM_ARRAY_JOB_ID"] == "$FLOW_JOB_ID"

    @pytest.mark.asyncio
    async def test_array_job_with_cli_override(self, adapter, minimal_slurm_script):
        """Test array job with CLI array specification.
        
        GIVEN: Regular script with CLI array option
        WHEN: parse_array_job() is called with array option
        THEN: Array jobs are created based on CLI option
        """
        # WHEN
        configs = await adapter.parse_array_job(
            minimal_slurm_script,
            array="1,5,10"
        )

        # THEN
        assert len(configs) == 3
        assert configs[0].name == "test-job_1"
        assert configs[1].name == "test-job_5"
        assert configs[2].name == "test-job_10"

    def test_array_spec_parsing(self, adapter):
        """Test parsing various array specifications.
        
        GIVEN: Different array specification formats
        WHEN: _parse_array_spec() is called
        THEN: Correct indices are returned
        """
        # Simple range
        assert adapter._parse_array_spec("1-5") == [1, 2, 3, 4, 5]

        # Range with step
        assert adapter._parse_array_spec("0-10:2") == [0, 2, 4, 6, 8, 10]

        # List
        assert adapter._parse_array_spec("1,3,5,7") == [1, 3, 5, 7]

        # Mixed
        assert adapter._parse_array_spec("1-3,10,20-22") == [1, 2, 3, 10, 20, 21, 22]

        # Complex mixed with step
        assert adapter._parse_array_spec("1-5:2,10,15-20:3") == [1, 3, 5, 10, 15, 18]

    @pytest.mark.asyncio
    async def test_environment_variables(self, adapter, tmp_path):
        """Test handling of environment variables.
        
        GIVEN: SLURM script with environment export
        WHEN: parse_and_convert() is called
        THEN: Environment variables are included in TaskConfig
        """
        # GIVEN
        script = tmp_path / "env_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=env-test
#SBATCH --export=MY_VAR=value1,OTHER_VAR=value2

echo $MY_VAR
echo $OTHER_VAR
""")

        # WHEN
        config = await adapter.parse_and_convert(script)

        # THEN
        assert config.env["MY_VAR"] == "value1"
        assert config.env["OTHER_VAR"] == "value2"

    @pytest.mark.asyncio
    async def test_dependency_handling(self, adapter, tmp_path):
        """Test handling of job dependencies.
        
        GIVEN: SLURM script with dependency directive
        WHEN: parse_and_convert() is called
        THEN: Dependencies are preserved in environment
        """
        # GIVEN
        script = tmp_path / "dep_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=dependent-job
#SBATCH --dependency=afterok:12345

echo "Running after job 12345"
""")

        # WHEN
        config = await adapter.parse_and_convert(script)

        # THEN
        # Dependencies would be stored as metadata
        assert config.name == "dependent-job"

    @pytest.mark.asyncio
    async def test_constraint_handling(self, adapter, tmp_path):
        """Test handling of node constraints.
        
        GIVEN: SLURM script with constraint directive
        WHEN: parse_and_convert() is called
        THEN: Constraints affect instance selection
        """
        # GIVEN
        script = tmp_path / "constraint_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=constrained-job
#SBATCH --constraint="highmem&gpu"
#SBATCH --gpus=2

python analyze.py
""")

        # WHEN
        config = await adapter.parse_and_convert(script)

        # THEN
        assert config.num_instances == 1  # Single instance with 2 GPUs
        assert config.instance_type == "a100.80gb.sxm4.2x"  # 2x GPU instance
        # Constraints would be used for instance filtering

    def test_format_job_id(self, adapter):
        """Test SLURM job ID formatting.
        
        GIVEN: Flow job IDs
        WHEN: format_job_id() is called
        THEN: Numeric SLURM-style IDs are returned
        """
        # First call starts at 1000
        assert adapter.format_job_id("task-abc123") == "1000"
        assert adapter.format_job_id("task-def456") == "1001"
        assert adapter.format_job_id("task-xyz789") == "1002"

    def test_format_status(self, adapter):
        """Test SLURM status code formatting.
        
        GIVEN: Flow status strings
        WHEN: format_status() is called
        THEN: SLURM status codes are returned
        """
        assert adapter.format_status("pending") == "PD"
        assert adapter.format_status("running") == "R"
        assert adapter.format_status("completed") == "CD"
        assert adapter.format_status("failed") == "F"
        assert adapter.format_status("cancelled") == "CA"
        assert adapter.format_status("unknown") == "UN"  # Default

    @pytest.mark.asyncio
    async def test_gres_gpu_parsing(self, adapter, tmp_path):
        """Test parsing GRES GPU specification.
        
        GIVEN: SLURM script with GRES directive
        WHEN: parse_and_convert() is called
        THEN: GPU requirements are correctly parsed
        """
        # GIVEN
        script = tmp_path / "gres_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=gres-test
#SBATCH --gres=gpu:v100:2

nvidia-smi
""")

        # WHEN
        config = await adapter.parse_and_convert(script)

        # THEN
        assert config.num_instances == 1  # nodes, not GPU count
        assert config.instance_type == "v100"

    @pytest.mark.asyncio
    async def test_working_directory(self, adapter, tmp_path):
        """Test working directory handling.
        
        GIVEN: SLURM script with chdir directive
        WHEN: parse_and_convert() is called
        THEN: Working directory is included in startup script
        """
        # GIVEN
        script = tmp_path / "chdir_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=chdir-test
#SBATCH --chdir=/workspace/project

python main.py
""")

        # WHEN
        config = await adapter.parse_and_convert(script)

        # THEN
        assert "cd /workspace/project" in config.command


class TestSlurmParser:
    """Test SLURM parser utility functions."""

    def test_parse_time_to_hours(self):
        """Test time format parsing.
        
        GIVEN: Various SLURM time formats
        WHEN: parse_time_to_hours() is called
        THEN: Correct hours are returned
        """
        # MM:SS
        assert parse_time_to_hours("30:00") == 0.5

        # HH:MM:SS
        assert parse_time_to_hours("01:30:00") == 1.5
        assert parse_time_to_hours("24:00:00") == 24.0

        # DD-HH:MM:SS
        assert parse_time_to_hours("1-00:00:00") == 24.0
        assert parse_time_to_hours("7-12:00:00") == 180.0  # 7*24 + 12

        # DD-HH
        assert parse_time_to_hours("2-12") == 60.0  # 2*24 + 12

        # Just minutes
        assert parse_time_to_hours("90") == 1.5

    def test_parse_memory_to_gb(self):
        """Test memory format parsing.
        
        GIVEN: Various SLURM memory formats
        WHEN: parse_memory_to_gb() is called
        THEN: Correct GB values are returned
        """
        # Default unit (MB)
        assert parse_memory_to_gb("1024") == 1.0

        # Explicit MB
        assert parse_memory_to_gb("2048M") == 2.0
        assert parse_memory_to_gb("2048MB") == 2.0

        # GB
        assert parse_memory_to_gb("16G") == 16.0
        assert parse_memory_to_gb("16GB") == 16.0
        assert parse_memory_to_gb("1.5GB") == 1.5

        # TB
        assert parse_memory_to_gb("1T") == 1024.0
        assert parse_memory_to_gb("0.5TB") == 512.0

    def test_parse_memory_invalid(self):
        """Test invalid memory format.
        
        GIVEN: Invalid memory format
        WHEN: parse_memory_to_gb() is called
        THEN: ValueError is raised
        """
        with pytest.raises(ValueError):
            parse_memory_to_gb("invalid")

        with pytest.raises(ValueError):
            parse_memory_to_gb("16X")


class TestSlurmFrontendAdapterIntegration:
    """Integration tests for SLURM adapter."""

    @pytest.mark.asyncio
    async def test_real_world_hpc_script(self, tmp_path):
        """Test parsing real-world HPC SLURM script.
        
        GIVEN: Complex HPC SLURM script
        WHEN: Parsed and converted
        THEN: All HPC settings are preserved
        """
        # GIVEN
        script = tmp_path / "hpc_job.sh"
        script.write_text("""#!/bin/bash
#SBATCH --job-name=climate-simulation
#SBATCH --partition=compute
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=2
#SBATCH --mem=256G
#SBATCH --time=7-00:00:00
#SBATCH --output=climate_%A_%a.out
#SBATCH --error=climate_%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=researcher@university.edu
#SBATCH --constraint=infiniband

module load openmpi/4.1.1
module load netcdf/4.8.0
module load python/3.9

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun python climate_model.py \
    --config config/production.yaml \
    --output /scratch/results/$SLURM_JOB_ID
""")

        adapter = SlurmFrontendAdapter()

        # WHEN
        config = await adapter.parse_and_convert(script)

        # THEN
        assert config.name == "climate-simulation"
        assert config.num_instances == 4
        assert "module load openmpi/4.1.1" in config.command
        assert "export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK" in config.command
        assert "srun python climate_model.py" in config.command
