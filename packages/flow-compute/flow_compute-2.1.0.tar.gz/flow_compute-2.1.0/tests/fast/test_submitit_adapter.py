"""Tests for Submitit frontend adapter."""

import base64

import cloudpickle
import pytest

from flow._internal.frontends.submitit.adapter import SubmititFrontendAdapter
from flow.api.models import TaskConfig


class TestSubmititFrontendAdapter:
    """Test Submitit frontend adapter functionality."""

    @pytest.fixture
    def adapter(self):
        """Create Submitit adapter instance."""
        return SubmititFrontendAdapter()

    @pytest.fixture
    def simple_function(self):
        """Simple test function."""
        def add_numbers(a, b):
            """Add two numbers."""
            return a + b
        return add_numbers

    @pytest.fixture
    def complex_function(self):
        """Complex test function with imports."""
        def train_model(data_path, epochs=10, batch_size=32):
            """Simulate model training."""
            import time

            import numpy as np

            print(f"Loading data from {data_path}")
            print(f"Training for {epochs} epochs with batch size {batch_size}")

            # Simulate training
            for epoch in range(epochs):
                loss = np.random.random()
                print(f"Epoch {epoch}: loss = {loss}")
                time.sleep(0.1)

            return {"final_loss": 0.05, "accuracy": 0.95}

        return train_model

    @pytest.mark.asyncio
    async def test_parse_simple_function(self, adapter, simple_function):
        """Test parsing simple function submission.
        
        GIVEN: Simple function with arguments
        WHEN: parse_and_convert() is called
        THEN: Valid TaskConfig is created with serialized function
        """
        # WHEN
        config = await adapter.parse_and_convert(
            simple_function,
            5, 3,  # args
            name="add_job"
        )

        # THEN
        assert isinstance(config, TaskConfig)
        assert config.name == "add_job"
        assert config.image == "python:3.9"  # Default
        assert config.num_instances == 1
        assert "cloudpickle" in config.command
        assert "SERIALIZED_DATA" in config.command

        # Verify function can be deserialized
        script_lines = config.command.split('\n')
        for i, line in enumerate(script_lines):
            if line.startswith('SERIALIZED_DATA = """'):
                serialized = script_lines[i].split('"""')[1]
                break

        pickled = base64.b64decode(serialized)
        data = cloudpickle.loads(pickled)
        assert data["func"].__name__ == "add_numbers"
        assert data["args"] == (5, 3)
        assert data["kwargs"] == {}

    @pytest.mark.asyncio
    async def test_parse_with_submitit_params(self, adapter, complex_function):
        """Test parsing with Submitit-style parameters.
        
        GIVEN: Function with Submitit parameters
        WHEN: parse_and_convert() is called with nodes, gpus, etc.
        THEN: Parameters are correctly mapped to TaskConfig
        """
        # WHEN
        config = await adapter.parse_and_convert(
            complex_function,
            "/data/train",  # positional arg
            epochs=100,  # function kwarg
            batch_size=64,  # function kwarg
            # Submitit params
            name="training_job",
            nodes=2,
            gpus_per_node=4,
            mem_gb=128,
            timeout_min=720,  # 12 hours
            slurm_partition="gpu_a100",
            container_image="pytorch/pytorch:latest"
        )

        # THEN
        assert config.name == "training_job"
        assert config.image == "pytorch/pytorch:latest"
        assert config.num_instances == 2
        assert config.instance_type == "a100.80gb.sxm4.4x"  # 4 GPUs per node
        assert config.max_price_per_hour == 100.0  # Set from timeout

        # Check environment variables
        assert config.env["SUBMITIT_EXECUTOR"] == "flow"
        assert config.env["SUBMITIT_JOB_ID"] == "$FLOW_TASK_ID"

        # Verify function arguments were preserved
        script_lines = config.command.split('\n')
        for i, line in enumerate(script_lines):
            if line.startswith('SERIALIZED_DATA = """'):
                serialized = script_lines[i].split('"""')[1]
                break

        pickled = base64.b64decode(serialized)
        data = cloudpickle.loads(pickled)
        assert data["args"] == ("/data/train",)
        assert data["kwargs"] == {"epochs": 100, "batch_size": 64}

    @pytest.mark.asyncio
    async def test_function_without_name(self, adapter):
        """Test handling lambda or unnamed functions.
        
        GIVEN: Lambda function without __name__
        WHEN: parse_and_convert() is called
        THEN: Default name is used
        """
        # GIVEN
        lambda_func = lambda x, y: x * y

        # WHEN
        config = await adapter.parse_and_convert(lambda_func, 10, 20)

        # THEN
        assert config.name == "lambda_function"  # Sanitized from <lambda>

    def test_extract_submitit_params(self, adapter):
        """Test extracting Submitit-specific parameters.
        
        GIVEN: Mixed options with Submitit params and function kwargs
        WHEN: _extract_submitit_params() is called
        THEN: Only Submitit params are extracted
        """
        # GIVEN
        options = {
            # Submitit params
            "nodes": 4,
            "gpus_per_node": 8,
            "mem_gb": 256,
            "timeout_min": 1440,
            "slurm_partition": "compute",
            "name": "my_job",
            # Function kwargs
            "learning_rate": 0.001,
            "optimizer": "adam",
            "dataset": "imagenet"
        }

        # WHEN
        submitit_params = adapter._extract_submitit_params(options)

        # THEN
        assert submitit_params == {
            "nodes": 4,
            "gpus_per_node": 8,
            "mem_gb": 256,
            "timeout_min": 1440,
            "slurm_partition": "compute",
            "name": "my_job"
        }
        # Function kwargs not included
        assert "learning_rate" not in submitit_params
        assert "optimizer" not in submitit_params

    def test_gpu_type_inference(self, adapter):
        """Test GPU type inference from partition names.
        
        GIVEN: Various partition names
        WHEN: _infer_gpu_type() is called
        THEN: Correct GPU types are inferred
        """
        assert adapter._infer_gpu_type("gpu_a100") == "a100"
        assert adapter._infer_gpu_type("A100_PARTITION") == "a100"
        assert adapter._infer_gpu_type("v100-cluster") == "v100"
        assert adapter._infer_gpu_type("h100_nodes") == "h100"
        assert adapter._infer_gpu_type("gpu_t4_small") == "t4"
        assert adapter._infer_gpu_type("gpu") == "a100"  # Default
        assert adapter._infer_gpu_type("cpu_only") is None

    @pytest.mark.asyncio
    async def test_runner_script_structure(self, adapter, simple_function):
        """Test generated runner script structure.
        
        GIVEN: Function to serialize
        WHEN: parse_and_convert() creates runner script
        THEN: Script has correct structure and error handling
        """
        # WHEN
        config = await adapter.parse_and_convert(simple_function, 1, 2)

        # THEN
        script = config.command

        # Check shebang
        assert script.startswith("#!/usr/bin/env python3")

        # Check imports
        assert "import base64" in script
        assert "import cloudpickle" in script
        assert "import traceback" in script

        # Check main function
        assert "def main():" in script
        assert 'if __name__ == "__main__":' in script

        # Check error handling
        assert "try:" in script
        assert "except Exception as e:" in script
        assert "traceback.print_exc" in script

        # Check result saving
        assert "result.pkl" in script

        # Check environment setup
        assert 'os.environ["SUBMITIT_EXECUTOR"] = "flow"' in script

    def test_format_job_id(self, adapter):
        """Test job ID formatting for Submitit compatibility.
        
        GIVEN: Flow job IDs
        WHEN: format_job_id() is called
        THEN: Numeric job IDs are returned
        """
        assert adapter.format_job_id("task-abc") == "1000"
        assert adapter.format_job_id("task-def") == "1001"
        assert adapter.format_job_id("task-xyz") == "1002"

    def test_format_status(self, adapter):
        """Test status formatting for Submitit.
        
        GIVEN: Flow status strings
        WHEN: format_status() is called
        THEN: Submitit status strings are returned
        """
        assert adapter.format_status("pending") == "PENDING"
        assert adapter.format_status("running") == "RUNNING"
        assert adapter.format_status("completed") == "DONE"
        assert adapter.format_status("failed") == "FAILED"
        assert adapter.format_status("cancelled") == "CANCELLED"
        assert adapter.format_status("timeout") == "TIMEOUT"
        assert adapter.format_status("preempted") == "INTERRUPTED"
        assert adapter.format_status("unknown") == "UNKNOWN"

    @pytest.mark.asyncio
    async def test_complex_object_serialization(self, adapter):
        """Test serialization of functions with complex objects.
        
        GIVEN: Function using numpy arrays and custom classes
        WHEN: parse_and_convert() is called
        THEN: Objects are properly serialized
        """
        # GIVEN
        import numpy as np

        class ModelConfig:
            def __init__(self, layers, activation):
                self.layers = layers
                self.activation = activation

        def train_with_config(config, data):
            """Train with config object."""
            print(f"Layers: {config.layers}")
            print(f"Activation: {config.activation}")
            print(f"Data shape: {data.shape}")
            return np.mean(data)

        config_obj = ModelConfig([64, 128, 10], "relu")
        data_array = np.random.randn(100, 10)

        # WHEN
        task_config = await adapter.parse_and_convert(
            train_with_config,
            config_obj,
            data_array,
            name="complex_job"
        )

        # THEN
        assert task_config.name == "complex_job"

        # Verify deserialization works
        script_lines = task_config.command.split('\n')
        for i, line in enumerate(script_lines):
            if line.startswith('SERIALIZED_DATA = """'):
                serialized = script_lines[i].split('"""')[1]
                break

        pickled = base64.b64decode(serialized)
        data = cloudpickle.loads(pickled)

        # Check objects were preserved
        assert data["args"][0].layers == [64, 128, 10]
        assert data["args"][0].activation == "relu"
        assert data["args"][1].shape == (100, 10)


class TestSubmititFrontendAdapterIntegration:
    """Integration tests for Submitit adapter."""

    @pytest.mark.asyncio
    async def test_real_world_ml_submission(self):
        """Test real-world ML training submission.
        
        GIVEN: Realistic ML training function
        WHEN: Submitted with typical parameters
        THEN: Correct TaskConfig is generated
        """
        # GIVEN
        def train_transformer(
            model_name="bert-base",
            dataset="squad",
            learning_rate=5e-5,
            warmup_steps=500,
            max_steps=10000,
            fp16=True,
            gradient_checkpointing=False
        ):
            """Train a transformer model."""

            print(f"Training {model_name} on {dataset}")
            print(f"Learning rate: {learning_rate}")
            print(f"Max steps: {max_steps}")
            print(f"FP16: {fp16}")

            # Training logic would go here
            metrics = {
                "final_loss": 0.234,
                "eval_accuracy": 0.891,
                "training_time": 3600
            }

            return metrics

        adapter = SubmititFrontendAdapter()

        # WHEN
        config = await adapter.parse_and_convert(
            train_transformer,
            model_name="roberta-large",
            dataset="mnli",
            learning_rate=2e-5,
            max_steps=50000,
            # Submitit params
            name="roberta-mnli-finetuning",
            nodes=1,
            gpus_per_node=8,
            mem_gb=512,
            timeout_min=2880,  # 48 hours
            slurm_partition="ml_h100",
            container_image="huggingface/transformers-pytorch-gpu:latest"
        )

        # THEN
        assert config.name == "roberta-mnli-finetuning"
        assert config.image == "huggingface/transformers-pytorch-gpu:latest"
        assert config.num_instances == 1
        assert config.instance_type == "h100.80gb.sxm5.8x"  # 8 GPUs per node, H100 from partition

        # Verify function arguments
        script_lines = config.command.split('\n')
        for i, line in enumerate(script_lines):
            if line.startswith('SERIALIZED_DATA = """'):
                serialized = script_lines[i].split('"""')[1]
                break

        pickled = base64.b64decode(serialized)
        data = cloudpickle.loads(pickled)

        assert data["kwargs"]["model_name"] == "roberta-large"
        assert data["kwargs"]["dataset"] == "mnli"
        assert data["kwargs"]["learning_rate"] == 2e-5
        assert data["kwargs"]["max_steps"] == 50000
