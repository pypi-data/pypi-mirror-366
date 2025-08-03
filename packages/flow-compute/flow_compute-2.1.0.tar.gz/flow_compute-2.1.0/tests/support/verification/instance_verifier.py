"""
Instance Verification Agent - Runs on provisioned instances to verify configuration.

This agent is deployed to instances during testing to verify that the actual
hardware, storage, and environment match what was requested.
"""

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class GPUInfo:
    """Information about a single GPU"""
    index: int
    name: str
    memory_mb: int
    utilization_percent: int
    driver_version: str
    cuda_version: str


@dataclass
class StorageMount:
    """Information about a storage mount"""
    mount_path: str
    device: str
    filesystem: str
    size_gb: float
    used_gb: float
    available_gb: float
    mount_options: List[str]
    is_persistent: bool


@dataclass
class NetworkInterface:
    """Information about network configuration"""
    interface: str
    ip_address: str
    is_public: bool
    bandwidth_mbps: Optional[float] = None


@dataclass
class PortForwarding:
    """Information about port forwarding setup"""
    name: str
    internal_port: int
    external_port: int
    is_accessible: bool


@dataclass
class EnvironmentInfo:
    """Information about the runtime environment"""
    hostname: str
    kernel_version: str
    os_version: str
    docker_installed: bool
    docker_version: Optional[str] = None
    env_vars: Dict[str, str] = field(default_factory=dict)
    startup_script_executed: bool = False
    startup_script_exit_code: Optional[int] = None


@dataclass
class VerificationReport:
    """Complete verification report for an instance"""
    timestamp: str
    gpus: List[GPUInfo] = field(default_factory=list)
    storage: List[StorageMount] = field(default_factory=list)
    network: List[NetworkInterface] = field(default_factory=list)
    ports: List[PortForwarding] = field(default_factory=list)
    environment: Optional[EnvironmentInfo] = None
    errors: List[str] = field(default_factory=list)


class InstanceVerificationAgent:
    """Verifies instance configuration matches requirements"""

    def __init__(self, output_path: str = "/tmp/verification_report.json"):
        self.output_path = output_path
        self.report = VerificationReport(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        )

    def verify_all(self) -> VerificationReport:
        """Run all verification checks"""
        self.verify_gpus()
        self.verify_storage()
        self.verify_network()
        self.verify_environment()
        self.verify_ports()
        self.save_report()
        return self.report

    def verify_gpus(self) -> List[GPUInfo]:
        """Verify GPU configuration using nvidia-smi"""
        try:
            # Check if nvidia-smi is available
            result = subprocess.run(
                ["which", "nvidia-smi"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.report.errors.append("No GPU detected (nvidia-smi not found)")
                return []

            # Query GPU information
            cmd = [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,utilization.gpu,driver_version",
                "--format=csv,noheader,nounits"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = [p.strip() for p in line.split(',')]
                gpu = GPUInfo(
                    index=int(parts[0]),
                    name=parts[1],
                    memory_mb=int(parts[2]),
                    utilization_percent=int(parts[3]),
                    driver_version=parts[4],
                    cuda_version=self._get_cuda_version()
                )
                self.report.gpus.append(gpu)

        except subprocess.CalledProcessError as e:
            self.report.errors.append(f"GPU verification failed: {e}")
        except Exception as e:
            self.report.errors.append(f"Unexpected GPU error: {e}")

        return self.report.gpus

    def verify_storage(self) -> List[StorageMount]:
        """Verify storage mounts and sizes"""
        try:
            # Get all mounts
            df_result = subprocess.run(
                ["df", "-BG", "-T"],  # Gigabyte units, show filesystem type
                capture_output=True,
                text=True,
                check=True
            )

            # Get mount options
            mount_result = subprocess.run(
                ["mount"],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse df output
            for line in df_result.stdout.strip().split('\n')[1:]:  # Skip header
                parts = line.split()
                if len(parts) < 7:
                    continue

                device = parts[0]
                filesystem = parts[1]
                size_str = parts[2].rstrip('G')
                used_str = parts[3].rstrip('G')
                avail_str = parts[4].rstrip('G')
                mount_path = parts[6]

                # Skip system mounts
                if mount_path in ['/', '/boot', '/dev', '/proc', '/sys', '/run']:
                    continue

                # Get mount options for this device
                mount_options = self._get_mount_options(device, mount_result.stdout)

                # Check if volume is persistent (has UUID in fstab)
                is_persistent = self._check_persistence(device)

                mount = StorageMount(
                    mount_path=mount_path,
                    device=device,
                    filesystem=filesystem,
                    size_gb=float(size_str),
                    used_gb=float(used_str),
                    available_gb=float(avail_str),
                    mount_options=mount_options,
                    is_persistent=is_persistent
                )
                self.report.storage.append(mount)

        except subprocess.CalledProcessError as e:
            self.report.errors.append(f"Storage verification failed: {e}")
        except Exception as e:
            self.report.errors.append(f"Unexpected storage error: {e}")

        return self.report.storage

    def verify_network(self) -> List[NetworkInterface]:
        """Verify network configuration"""
        try:
            # Get network interfaces
            result = subprocess.run(
                ["ip", "-j", "addr", "show"],
                capture_output=True,
                text=True,
                check=True
            )

            interfaces = json.loads(result.stdout)

            for iface in interfaces:
                if iface['ifname'] == 'lo':  # Skip loopback
                    continue

                for addr_info in iface.get('addr_info', []):
                    if addr_info['family'] == 'inet':  # IPv4
                        network = NetworkInterface(
                            interface=iface['ifname'],
                            ip_address=addr_info['local'],
                            is_public=not self._is_private_ip(addr_info['local'])
                        )
                        self.report.network.append(network)

        except subprocess.CalledProcessError as e:
            self.report.errors.append(f"Network verification failed: {e}")
        except Exception as e:
            self.report.errors.append(f"Unexpected network error: {e}")

        return self.report.network

    def verify_environment(self) -> EnvironmentInfo:
        """Verify runtime environment"""
        try:
            # Basic system info
            hostname = subprocess.run(
                ["hostname"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            kernel = subprocess.run(
                ["uname", "-r"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            os_info = "Unknown"
            if Path("/etc/os-release").exists():
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            os_info = line.split('=')[1].strip().strip('"')
                            break

            # Check Docker
            docker_installed = False
            docker_version = None
            try:
                result = subprocess.run(
                    ["docker", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    docker_installed = True
                    docker_version = result.stdout.strip()
            except:
                pass

            # Get Flow environment variables
            env_vars = {
                k: v for k, v in os.environ.items()
                if k.startswith(('FLOW_', 'TEST_'))
            }

            # Check startup script execution
            startup_log = Path("/tmp/flow-startup.log")
            startup_executed = startup_log.exists()
            exit_code = None

            if startup_executed:
                # Look for completion marker
                completion_marker = Path("/tmp/flow-startup-complete")
                if completion_marker.exists():
                    with open(completion_marker) as f:
                        exit_code = int(f.read().strip())

            self.report.env = EnvironmentInfo(
                hostname=hostname,
                kernel_version=kernel,
                os_version=os_info,
                docker_installed=docker_installed,
                docker_version=docker_version,
                env_vars=env_vars,
                startup_script_executed=startup_executed,
                startup_script_exit_code=exit_code
            )

        except Exception as e:
            self.report.errors.append(f"Environment verification failed: {e}")

        return self.report.env

    def verify_ports(self) -> List[PortForwarding]:
        """Verify port forwarding configuration"""
        try:
            # Check common forwarded ports
            ports_to_check = [
                ("jupyter", 8888),
                ("tensorboard", 6006),
                ("ssh", 22)
            ]

            for name, port in ports_to_check:
                # Check if port is listening
                result = subprocess.run(
                    ["ss", "-tlna"],
                    capture_output=True,
                    text=True,
                    check=True
                )

                is_listening = f":{port}" in result.stdout

                if is_listening:
                    # Try to determine external port from nginx config
                    external_port = self._get_external_port(port)

                    port_info = PortForwarding(
                        name=name,
                        internal_port=port,
                        external_port=external_port or port,
                        is_accessible=True
                    )
                    self.report.ports.append(port_info)

        except Exception as e:
            self.report.errors.append(f"Port verification failed: {e}")

        return self.report.ports

    def save_report(self):
        """Save verification report to disk"""
        with open(self.output_path, 'w') as f:
            json.dump(self._report_to_dict(), f, indent=2)

    def _get_cuda_version(self) -> str:
        """Get CUDA version if available"""
        try:
            result = subprocess.run(
                ["nvcc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version from output
                for line in result.stdout.split('\n'):
                    if 'release' in line:
                        return line.split('release')[1].split(',')[0].strip()
        except:
            pass
        return "unknown"

    def _get_mount_options(self, device: str, mount_output: str) -> List[str]:
        """Extract mount options for a device"""
        for line in mount_output.split('\n'):
            if device in line:
                # Extract options from parentheses
                if '(' in line and ')' in line:
                    options_str = line.split('(')[1].split(')')[0]
                    return options_str.split(',')
        return []

    def _check_persistence(self, device: str) -> bool:
        """Check if device is in fstab for persistence"""
        try:
            with open('/etc/fstab') as f:
                return device in f.read()
        except:
            return False

    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is in private range"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False

        # Check common private ranges
        if parts[0] == '10':
            return True
        if parts[0] == '172' and 16 <= int(parts[1]) <= 31:
            return True
        if parts[0] == '192' and parts[1] == '168':
            return True

        return False

    def _get_external_port(self, internal_port: int) -> Optional[int]:
        """Try to determine external port from nginx config"""
        # This would check nginx config or Flow metadata
        # For now, return None
        return None

    def _report_to_dict(self) -> dict:
        """Convert report to dictionary for JSON serialization"""
        return {
            'timestamp': self.report.timestamp,
            'gpus': [
                {
                    'index': g.index,
                    'name': g.name,
                    'memory_mb': g.memory_mb,
                    'utilization_percent': g.utilization_percent,
                    'driver_version': g.driver_version,
                    'cuda_version': g.cuda_version
                }
                for g in self.report.gpus
            ],
            'storage': [
                {
                    'mount_path': s.mount_path,
                    'device': s.device,
                    'filesystem': s.filesystem,
                    'size_gb': s.size_gb,
                    'used_gb': s.used_gb,
                    'available_gb': s.available_gb,
                    'mount_options': s.mount_options,
                    'is_persistent': s.is_persistent
                }
                for s in self.report.storage
            ],
            'network': [
                {
                    'interface': n.interface,
                    'ip_address': n.ip_address,
                    'is_public': n.is_public,
                    'bandwidth_mbps': n.bandwidth_mbps
                }
                for n in self.report.network
            ],
            'ports': [
                {
                    'name': p.name,
                    'internal_port': p.internal_port,
                    'external_port': p.external_port,
                    'is_accessible': p.is_accessible
                }
                for p in self.report.ports
            ],
            'env': {
                'hostname': self.report.env.hostname,
                'kernel_version': self.report.env.kernel_version,
                'os_version': self.report.env.os_version,
                'docker_installed': self.report.env.docker_installed,
                'docker_version': self.report.env.docker_version,
                'env_vars': self.report.env.env_vars,
                'startup_script_executed': self.report.env.startup_script_executed,
                'startup_script_exit_code': self.report.env.startup_script_exit_code
            } if self.report.env else None,
            'errors': self.report.errors
        }


if __name__ == "__main__":
    # Run verification when script is executed directly
    agent = InstanceVerificationAgent()
    report = agent.verify_all()

    print(f"Verification complete. Report saved to: {agent.output_path}")
    print(f"Found {len(report.gpus)} GPUs")
    print(f"Found {len(report.storage)} storage mounts")
    print(f"Found {len(report.errors)} errors")

    if report.errors:
        print("\nErrors:")
        for error in report.errors:
            print(f"  - {error}")
