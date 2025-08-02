from typing import Optional, Dict, Any
import pulumi
from airspot_dev.pulumi_ import BaseResourceConfig
from airspot_dev.pulumi_ import k8s as k8s_
from .identity import get_workload_identity, WorkloadIdentityConfig, create_sa_patch_transform
from .networking import get_static_ip, get_dns_record, StaticIPConfig, DNSConfig
from .ingress import get_gce_ingress, GCEIngressConfig


class GKEWebAppConfig(BaseResourceConfig):
    """Complete GKE Web Application with external exposure"""
    
    # Kubernetes application (gestito da k8s module)
    k8s_application: k8s_.ApplicationConfig
    
    # Identity (tutti i parametri espliciti)
    workload_identity: WorkloadIdentityConfig
    
    # Networking
    static_ip: StaticIPConfig
    dns: Optional[DNSConfig] = None  # Opzionale
    
    # Ingress
    ingress: GCEIngressConfig
    
    model_config = {"arbitrary_types_allowed": True}


def get_gke_web_app(config: GKEWebAppConfig, depends_on=None) -> Dict[str, Any]:
    """Crea applicazione web completa su GKE"""
    
    resources = {}
    
    # 1. Create identity
    identity = get_workload_identity(config.workload_identity)
    resources["identity"] = identity
    
    # 2. Create static IP
    static_ip = get_static_ip(config.static_ip)
    resources["static_ip"] = static_ip
    
    # 3. Create DNS record (se configurato)
    if config.dns:
        # Pass the static IP directly to the function
        dns_record = get_dns_record(
            config.dns, 
            ip_address=static_ip.address  # Pass IP as parameter
        )
        resources["dns_record"] = dns_record
    
    # 4. Create K8s application con SA patch
    k8s_transforms = config.k8s_application.get_transforms()
    k8s_transforms.append(create_sa_patch_transform(identity["ksa_name"]))
    
    # Update the k8s application config with transforms
    k8s_config = config.k8s_application
    k8s_config.transforms = k8s_transforms
    
    # Dependencies for k8s app
    k8s_depends_on = []
    if depends_on:
        if isinstance(depends_on, list):
            k8s_depends_on.extend(depends_on)
        else:
            k8s_depends_on.append(depends_on)
    if not identity["existing"] and "k8s_service_account" in identity:
        k8s_depends_on.append(identity["k8s_service_account"])
    
    k8s_app = k8s_.get_application(
        k8s_config,
        depends_on=k8s_depends_on if k8s_depends_on else None
    )
    resources["application"] = k8s_app
    
    # 5. Create ingress
    # Calculate service port name using the same logic as in application.py
    service_port_name = config.k8s_application.port_name or f"port-{config.k8s_application.container_port or config.k8s_application.service_port}"
    
    # Pass static IP name, service name, and port name as parameters
    ingress_resources = get_gce_ingress(
        config.ingress,
        static_ip_name=static_ip.name,
        service_name=config.k8s_application.name,
        service_port_name=service_port_name
    )
    
    # Dependencies for ingress
    ingress_depends_on = [static_ip]
    if config.dns and "dns_record" in resources:
        ingress_depends_on.append(resources["dns_record"])
    if k8s_app.get("service"):
        ingress_depends_on.append(k8s_app["service"])
    # Add BackendConfig dependency if it exists
    if k8s_app.get("backend_config"):
        ingress_depends_on.append(k8s_app["backend_config"])
    
    # Update ingress resources with additional dependencies
    for resource_name, resource in ingress_resources.items():
        if hasattr(resource, 'opts') and resource.opts:
            current_depends_on = resource.opts.depends_on or []
            if isinstance(current_depends_on, list):
                current_depends_on.extend(ingress_depends_on)
            else:
                current_depends_on = [current_depends_on] + ingress_depends_on
            resource.opts.depends_on = current_depends_on
        else:
            resource.opts = pulumi.ResourceOptions(depends_on=ingress_depends_on)
    
    resources["ingress"] = ingress_resources
    
    return resources
