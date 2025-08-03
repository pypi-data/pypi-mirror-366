import os
import sys
import json
from datetime import datetime, timezone, timedelta
from collections import Counter

sys.path.insert(0, "/Users/jq/Downloads/flow-sdk/src")

try:
    from flow._internal.config import Config
    from flow._internal.io.http import HttpClientPool

    # Load config
    config = Config.from_env()
    api_url = config.provider_config.get("api_url", "https://api.mlfoundry.com")
    headers = {
        "Authorization": f"Bearer {config.auth_token}",
        "Content-Type": "application/json",
        "User-Agent": "flow-sdk/test",
    }

    http_client = HttpClientPool.get_client(base_url=api_url, headers=headers)
    project_id = "proj_0C7CSvEyFRpE8o8V"

    print("Analyzing all bids to find active instances...")
    print("=" * 60)

    # Get ALL bids
    all_bids = []
    next_cursor = None

    while True:
        params = {"project": project_id, "limit": "100"}
        if next_cursor:
            params["cursor"] = next_cursor

        response = http_client.request(method="GET", url="/v2/spot/bids", params=params)

        if isinstance(response, dict):
            bids = response.get("data", [])
            all_bids.extend(bids)
            next_cursor = response.get("next_cursor")
            if not next_cursor:
                break
        else:
            all_bids = response
            break

    print(f"Total bids found: {len(all_bids)}")

    # Analyze status distribution
    status_counts = Counter(bid.get("status", "Unknown") for bid in all_bids)
    print("\nStatus distribution:")
    for status, count in status_counts.most_common():
        print(f"  {status}: {count}")

    # Find non-terminated bids
    active_statuses = ["Running", "Pending", "Starting", "Provisioning"]
    active_bids = [bid for bid in all_bids if bid.get("status") in active_statuses]

    print(f"\nActive bids (non-terminated): {len(active_bids)}")

    # Show active bids
    if active_bids:
        print("\nActive instances:")
        for bid in active_bids[:10]:  # Show first 10
            print(f"\n  ID: {bid.get('fid', 'N/A')}")
            print(f"  Status: {bid.get('status')}")
            print(f"  Created: {bid.get('created_at')}")
            print(f"  Instance Type: {bid.get('instance_type')}")
            print(f"  Task Name: {bid.get('task_name', 'N/A')}")

    # Check recent bids (last 24 hours)
    now = datetime.now(timezone.utc)
    recent_bids = []

    for bid in all_bids:
        created_str = bid.get("created_at")
        if created_str:
            # Parse ISO format timestamp
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            if now - created < timedelta(hours=24):
                recent_bids.append(bid)

    print(f"\n\nBids created in last 24 hours: {len(recent_bids)}")

    # Check what flow status is doing
    print("\n\nChecking flow status filtering logic...")
    print("Flow status by default shows:")
    print("  - Tasks from last 24 hours")
    print("  - Plus any currently running/pending tasks")

    # Simulate flow status logic
    flow_status_bids = []
    for bid in all_bids:
        status = bid.get("status", "")
        created_str = bid.get("created_at")

        # Include if running/pending
        if status in ["Running", "Pending", "Starting", "Provisioning"]:
            flow_status_bids.append(bid)
            continue

        # Include if created in last 24 hours
        if created_str:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            if now - created < timedelta(hours=24):
                flow_status_bids.append(bid)

    print(f"\nBids that should show in 'flow status': {len(flow_status_bids)}")

    # Show a sample bid structure
    if all_bids:
        print("\n\nSample bid structure:")
        sample = all_bids[0]
        print(json.dumps(sample, indent=2, default=str)[:500] + "...")

except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
