# Sanctum Brain: Operations & Deployment (The Guard)

Scripts for managing the Sanctum VPS, monorepo deployment, and ecosystem validation.

## Deployment

- `deploy_all.sh`: Deploys the entire ecosystem (Backend, Web, and DB).
- `deploy_to_vps.sh`: Specific script for pushing updates to the Sanctum Guard VPS.
- `start_ecosystem.sh`: Local development launcher that starts all services in the correct sequence.

## Security & Maintenance

- `lockdown-vps.sh`: Hardens the VPS network configuration, ensuring only authorized client nodes (Tailscale/mDNS) can connect.
- `update_vps.sh`: Fetches updates, rebuilds Docker containers, and performs a hot-reload of the LangGraph config.
- `vps-connect.sh`: Helper for establishing a secure tunnel to the VPS console.

## Validation & Pulse

- `validate_comprehensive_v2.sh`: Runs the full system health check, covering gRPC latency, OpenSearch connectivity, and PARA state consistency.
- `autonomous_validate.sh`: Periodically runs validation and logs health pulses to `validation_pulse.log`.
