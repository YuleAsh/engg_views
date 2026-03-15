#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Hotwire Engineer Workbench", layout="wide")

# =========================================================
# DUMMY DATA
# =========================================================
np.random.seed(42)

properties = ["F1598", "F0688", "F1168", "F1107", "F0568", "FX8045"]
root_causes = {
    "F1598": "Mesh / Topology Overload",
    "F0688": "Streaming Degradation",
    "F1168": "RF Congestion",
    "F1107": "Device Failure",
    "F0568": "Platform Instability",
    "FX8045": "Mesh / Topology Overload",
}

base_time = pd.Timestamp("2026-03-14 00:00:00")
hours = pd.date_range(base_time, periods=24, freq="h")

rows = []
rf_detail_rows = []

for prop in properties:
    cause = root_causes[prop]

    for ts in hours:
        hr = ts.hour

        wifi_busy_24 = np.clip(np.random.normal(0.55, 0.12), 0.08, 0.98)
        wifi_busy_5 = np.clip(np.random.normal(0.42, 0.10), 0.05, 0.95)
        wifi_noise_24 = np.clip(np.random.normal(-83, 4), -98, -65)
        wifi_noise_5 = np.clip(np.random.normal(-90, 4), -102, -70)

        interference_24 = np.clip(np.random.normal(0.32, 0.12), 0.01, 0.95)
        interference_5 = np.clip(np.random.normal(0.18, 0.08), 0.00, 0.85)
        self_traffic_24 = np.clip(np.random.normal(0.30, 0.10), 0.01, 0.90)
        self_traffic_5 = np.clip(np.random.normal(0.34, 0.10), 0.01, 0.90)

        stall_ratio = np.clip(np.random.normal(0.012, 0.007), 0.000, 0.09)
        buffer_ratio = np.clip(np.random.normal(0.020, 0.010), 0.000, 0.12)
        tivo_sessions = int(np.clip(np.random.normal(140, 40), 10, 400))

        error_events = int(np.clip(np.random.normal(8, 6), 0, 90))
        error_devices = int(np.clip(np.random.normal(2, 2), 0, 20))
        l101_errors = int(max(0, error_events * np.random.uniform(0.25, 0.55)))
        v56_errors = int(max(0, error_events * np.random.uniform(0.05, 0.25)))
        l102_errors = int(max(0, error_events * np.random.uniform(0.03, 0.20)))
        ui_errors = int(max(0, error_events * np.random.uniform(0.02, 0.15)))

        alerts_total = int(np.clip(np.random.normal(2, 2), 0, 12))
        alerts_red = int(min(alerts_total, np.random.binomial(max(alerts_total, 1), 0.35)))
        alerts_yellow = max(0, alerts_total - alerts_red)
        top_alert_type = np.random.choice(
            ["ThermalThrottle", "WANSpeedLow", "SSIDConflict", "None"],
            p=[0.20, 0.25, 0.20, 0.35],
        )

        mesh_eeros = int(np.clip(np.random.normal(180, 60), 20, 450))
        gateway_nodes = int(np.clip(np.random.normal(95, 30), 10, 220))
        leaf_nodes = int(np.clip(np.random.normal(70, 35), 0, 260))
        avg_hops_to_gateway = np.clip(np.random.normal(1.7, 0.5), 1.0, 5.0)
        max_hops_to_gateway = int(np.clip(np.random.normal(3, 1), 1, 7))
        low_backhaul_links = int(np.clip(np.random.normal(6, 4), 0, 50))
        avg_next_hop_rssi = np.clip(np.random.normal(-63, 6), -85, -45)
        min_next_hop_rssi = np.clip(avg_next_hop_rssi - np.random.uniform(4, 12), -95, -50)

        if cause == "RF Congestion":
            wifi_busy_24 = np.clip(np.random.normal(0.89, 0.04), 0.78, 0.99)
            wifi_busy_5 = np.clip(np.random.normal(0.47, 0.05), 0.30, 0.70)
            interference_24 = np.clip(np.random.normal(0.62, 0.08), 0.35, 0.95)
            wifi_noise_24 = np.clip(np.random.normal(-77, 3), -88, -68)
            stall_ratio = np.clip(np.random.normal(0.026, 0.007), 0.008, 0.09)
            buffer_ratio = np.clip(np.random.normal(0.040, 0.010), 0.010, 0.12)

        elif cause == "Streaming Degradation":
            stall_ratio = np.clip(np.random.normal(0.035, 0.010), 0.012, 0.10)
            buffer_ratio = np.clip(np.random.normal(0.055, 0.015), 0.010, 0.14)
            l101_errors = int(np.clip(np.random.normal(18, 6), 4, 40))
            l102_errors = int(np.clip(np.random.normal(7, 3), 0, 20))
            error_events = max(error_events, l101_errors + l102_errors + np.random.randint(2, 12))

        elif cause == "Device Failure":
            error_devices = int(np.clip(np.random.normal(8, 3), 3, 18))
            error_events = int(np.clip(np.random.normal(30, 10), 8, 90))
            l101_errors = int(np.clip(np.random.normal(10, 4), 0, 25))
            v56_errors = int(np.clip(np.random.normal(8, 3), 0, 20))
            ui_errors = int(np.clip(np.random.normal(6, 3), 0, 15))
            stall_ratio = np.clip(np.random.normal(0.022, 0.008), 0.005, 0.09)

        elif cause == "Platform Instability":
            alerts_total = int(np.clip(np.random.normal(8, 3), 3, 18))
            alerts_red = int(np.clip(np.random.normal(4, 2), 1, alerts_total))
            alerts_yellow = max(0, alerts_total - alerts_red)
            ui_errors = int(np.clip(np.random.normal(5, 2), 0, 12))
            stall_ratio = np.clip(np.random.normal(0.018, 0.006), 0.004, 0.07)

        elif cause == "Mesh / Topology Overload":
            leaf_nodes = int(np.clip(np.random.normal(130, 40), 40, 320))
            gateway_nodes = int(np.clip(np.random.normal(80, 20), 15, 180))
            avg_hops_to_gateway = np.clip(np.random.normal(2.5, 0.6), 1.4, 5.0)
            max_hops_to_gateway = int(np.clip(np.random.normal(4.5, 1.0), 2, 7))
            low_backhaul_links = int(np.clip(np.random.normal(14, 5), 4, 45))
            avg_next_hop_rssi = np.clip(np.random.normal(-70, 5), -88, -55)
            min_next_hop_rssi = np.clip(avg_next_hop_rssi - np.random.uniform(5, 12), -95, -60)
            l102_errors = int(np.clip(np.random.normal(6, 2), 0, 18))
            stall_ratio = np.clip(np.random.normal(0.024, 0.010), 0.005, 0.09)

        leaf_to_gateway_ratio = leaf_nodes / gateway_nodes if gateway_nodes > 0 else np.nan
        observed_channels_24 = 3
        observed_channels_5 = int(np.random.choice([4, 5, 6, 8]))
        congested_channels_24 = int(max(0, round((wifi_busy_24 - 0.65) * 10)))
        congested_channels_5 = int(max(0, round((wifi_busy_5 - 0.70) * 10)))
        congested_eeros_24 = int(max(0, congested_channels_24 + np.random.randint(0, 3)))
        congested_eeros_5 = int(max(0, congested_channels_5 + np.random.randint(0, 3)))

        wifi_busy = np.nanmean([wifi_busy_24, wifi_busy_5])
        wifi_noise = np.nanmean([wifi_noise_24, wifi_noise_5])
        has_platform_alert = int(alerts_total > 0)
        device_failure_flag = int(error_devices >= 3)

        is_congested_24 = int((wifi_busy_24 > 0.80) and (congested_channels_24 >= 1))
        is_congested_5 = int((wifi_busy_5 > 0.80) and (congested_channels_5 >= 1))

        if is_congested_24 == 1 and wifi_busy_24 >= wifi_busy_5:
            dominant_congestion_band = "2.4GHz dominated"
        elif is_congested_5 == 1 and wifi_busy_5 > wifi_busy_24:
            dominant_congestion_band = "5GHz dominated"
        else:
            dominant_congestion_band = "Balanced / Not congested"

        max_busy_any_band = max(wifi_busy_24, wifi_busy_5)
        max_interference_any_band = max(interference_24, interference_5)
        max_noise_any_band = max(wifi_noise_24, wifi_noise_5)

        if (max_busy_any_band >= 0.85) and (max_interference_any_band >= 0.50):
            rf_issue_type = "Congestion + Interference"
        elif (max_busy_any_band >= 0.85) and (max_interference_any_band < 0.50):
            rf_issue_type = "Internal Load Saturation"
        elif (max_busy_any_band < 0.85) and (max_interference_any_band >= 0.50):
            rf_issue_type = "External RF Interference"
        else:
            rf_issue_type = "No Major RF Issue"

        rf_flag = int(is_congested_24 or is_congested_5 or (max_interference_any_band >= 0.50))
        streaming_flag = int((stall_ratio >= 0.025) or (buffer_ratio >= 0.045))
        topology_flag = int(
            (leaf_to_gateway_ratio >= 1.0)
            or (avg_hops_to_gateway >= 2.4)
            or (low_backhaul_links >= 12)
            or (min_next_hop_rssi <= -75)
        )

        evidence_confidence_score = (
            rf_flag
            + streaming_flag
            + device_failure_flag
            + int(alerts_red > 0)
            + topology_flag
        ) / 5.0

        degraded_flag = int(
            rf_flag
            or streaming_flag
            or device_failure_flag
            or alerts_red > 0
            or topology_flag
        )

        total_congested_channels = congested_channels_24 + congested_channels_5
        total_congested_eeros = congested_eeros_24 + congested_eeros_5
        band_imbalance_ratio_24_to_5 = wifi_busy_24 / wifi_busy_5 if wifi_busy_5 > 0 else np.nan

        rf_risk_score = (
            0.35 * np.clip(max_busy_any_band, 0, 1)
            + 0.20 * np.clip((max_noise_any_band + 100) / 40, 0, 1)
            + 0.20 * np.clip(max_interference_any_band, 0, 1)
            + 0.15 * np.clip(total_congested_channels / 6, 0, 1)
            + 0.10 * np.clip(total_congested_eeros / 10, 0, 1)
        )

        severity_score = round(
            25 * min(wifi_busy, 1.0)
            + 20 * min(stall_ratio / 0.05, 2.0)
            + 15 * min(error_devices / 8.0, 2.0)
            + 15 * min(alerts_red / 4.0, 2.0)
            + 15 * min(leaf_to_gateway_ratio / 1.2, 2.0)
            + 10 * min(low_backhaul_links / 15.0, 2.0),
            2
        )

        rows.append(
            {
                "mduid": prop,
                "timestamp": ts,
                "dt": ts.date(),
                "hr": hr,
                "primary_root_cause": cause,
                "wifi_busy": round(float(wifi_busy), 3),
                "wifi_noise": round(float(wifi_noise), 2),
                "wifi_samples": int(np.clip(np.random.normal(900, 180), 200, 1800)),
                "wifi_busy_24ghz": round(float(wifi_busy_24), 3),
                "wifi_busy_5ghz": round(float(wifi_busy_5), 3),
                "wifi_noise_24ghz": round(float(wifi_noise_24), 2),
                "wifi_noise_5ghz": round(float(wifi_noise_5), 2),
                "interference_ratio_24ghz": round(float(interference_24), 3),
                "interference_ratio_5ghz": round(float(interference_5), 3),
                "self_traffic_ratio_24ghz": round(float(self_traffic_24), 3),
                "self_traffic_ratio_5ghz": round(float(self_traffic_5), 3),
                "observed_channels_24ghz": observed_channels_24,
                "observed_channels_5ghz": observed_channels_5,
                "congested_channels_24ghz": congested_channels_24,
                "congested_channels_5ghz": congested_channels_5,
                "congested_eeros_24ghz": congested_eeros_24,
                "congested_eeros_5ghz": congested_eeros_5,
                "dominant_congestion_band": dominant_congestion_band,
                "rf_issue_type": rf_issue_type,
                "rf_risk_score": round(float(rf_risk_score), 3),
                "band_imbalance_ratio_24_to_5": round(float(band_imbalance_ratio_24_to_5), 3),
                "stall_ratio": round(float(stall_ratio), 4),
                "buffer_ratio": round(float(buffer_ratio), 4),
                "tivo_sessions": tivo_sessions,
                "error_events": error_events,
                "error_devices": error_devices,
                "l101_errors": l101_errors,
                "v56_errors": v56_errors,
                "l102_errors": l102_errors,
                "ui_errors": ui_errors,
                "device_failure_flag": device_failure_flag,
                "alerts_total": alerts_total,
                "alerts_red": alerts_red,
                "alerts_yellow": alerts_yellow,
                "top_alert_type": top_alert_type,
                "has_platform_alert": has_platform_alert,
                "mesh_eeros": mesh_eeros,
                "gateway_nodes": gateway_nodes,
                "leaf_nodes": leaf_nodes,
                "leaf_to_gateway_ratio": round(float(leaf_to_gateway_ratio), 2),
                "avg_hops_to_gateway": round(float(avg_hops_to_gateway), 2),
                "max_hops_to_gateway": max_hops_to_gateway,
                "low_backhaul_links": low_backhaul_links,
                "avg_next_hop_rssi": round(float(avg_next_hop_rssi), 1),
                "min_next_hop_rssi": round(float(min_next_hop_rssi), 1),
                "rf_flag": rf_flag,
                "streaming_flag": streaming_flag,
                "topology_flag": topology_flag,
                "degraded_flag": degraded_flag,
                "evidence_confidence_score": round(float(evidence_confidence_score), 2),
                "severity_score": severity_score,
                "total_congested_channels": total_congested_channels,
                "total_congested_eeros": total_congested_eeros,
            }
        )

        # RF detail rows kept without visible channel references in UI
        two_four_channels = [1, 6, 11]
        five_channels = [36, 40, 44, 48]

        for i, _ch in enumerate(two_four_channels):
            eero_id = f"{prop}_EERO_{i+1}"
            ch_busy = np.clip(wifi_busy_24 + np.random.normal(0, 0.05), 0.05, 0.99)
            ch_noise = np.clip(wifi_noise_24 + np.random.normal(0, 1.5), -100, -60)
            ch_interference = np.clip(interference_24 + np.random.normal(0, 0.04), 0.0, 0.99)
            ch_self = np.clip(self_traffic_24 + np.random.normal(0, 0.04), 0.0, 0.99)
            rf_detail_rows.append(
                {
                    "mduid": prop,
                    "timestamp": ts,
                    "dt": ts.date(),
                    "hr": hr,
                    "eero_id": eero_id,
                    "band": "2.4GHz",
                    "wifi_busy_ratio": round(float(ch_busy), 3),
                    "wifi_noise": round(float(ch_noise), 2),
                    "interference_ratio": round(float(ch_interference), 3),
                    "self_traffic_ratio": round(float(ch_self), 3),
                }
            )

        for i, _ch in enumerate(five_channels):
            eero_id = f"{prop}_EERO_{i+1}"
            ch_busy = np.clip(wifi_busy_5 + np.random.normal(0, 0.05), 0.05, 0.99)
            ch_noise = np.clip(wifi_noise_5 + np.random.normal(0, 1.5), -105, -65)
            ch_interference = np.clip(interference_5 + np.random.normal(0, 0.04), 0.0, 0.99)
            ch_self = np.clip(self_traffic_5 + np.random.normal(0, 0.04), 0.0, 0.99)
            rf_detail_rows.append(
                {
                    "mduid": prop,
                    "timestamp": ts,
                    "dt": ts.date(),
                    "hr": hr,
                    "eero_id": eero_id,
                    "band": "5GHz",
                    "wifi_busy_ratio": round(float(ch_busy), 3),
                    "wifi_noise": round(float(ch_noise), 2),
                    "interference_ratio": round(float(ch_interference), 3),
                    "self_traffic_ratio": round(float(ch_self), 3),
                }
            )

df = pd.DataFrame(rows)
df_rf_detail = pd.DataFrame(rf_detail_rows)

# =========================================================
# ADD ROLLING ENGINEER METRICS
# =========================================================
def add_recent_metrics(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values("timestamp").copy()
    group["degraded_last_8"] = group["degraded_flag"].rolling(8, min_periods=1).sum()
    group["issue_persistence_score"] = (group["degraded_last_8"] / 8).round(2)

    group["remote_fix_candidate"] = (
        (
            (group["rf_flag"] == 1)
            | (group["alerts_red"] > 0)
            | (group["has_platform_alert"] == 1)
        )
        & (group["low_backhaul_links"] < 12)
        & (group["max_hops_to_gateway"] < 5)
    ).astype(int)

    group["site_visit_likely"] = (
        (
            (group["low_backhaul_links"] >= 12)
            | (group["max_hops_to_gateway"] >= 5)
            | (group["min_next_hop_rssi"] <= -78)
        )
        & (group["issue_persistence_score"] >= 0.50)
    ).astype(int)

    group["suggested_next_step"] = np.select(
        [
            group["site_visit_likely"] == 1,
            group["remote_fix_candidate"] == 1,
            group["primary_root_cause"].eq("Device Failure"),
            group["primary_root_cause"].eq("RF Congestion"),
        ],
        [
            "Likely site visit / on-site validation",
            "Remote remediation first",
            "Inspect device fault evidence",
            "Review RF load by band",
        ],
        default="Monitor and investigate",
    )

    group["rf_summary_text"] = np.select(
        [
            group["rf_issue_type"].eq("Congestion + Interference") & group["dominant_congestion_band"].eq("2.4GHz dominated"),
            group["rf_issue_type"].eq("Congestion + Interference") & group["dominant_congestion_band"].eq("5GHz dominated"),
            group["rf_issue_type"].eq("Internal Load Saturation"),
            group["rf_issue_type"].eq("External RF Interference"),
        ],
        [
            "2.4GHz-dominated congestion with elevated interference; likely neighboring WiFi pressure.",
            "5GHz-dominated congestion with elevated interference; likely high-density high-throughput contention.",
            "High airtime utilization with lower interference; likely internal client load saturation.",
            "Elevated interference without major airtime saturation; likely external RF pressure.",
        ],
        default="No major RF stress; degradation may be driven by non-RF layers.",
    )
    return group

df = df.groupby("mduid", group_keys=False).apply(add_recent_metrics)

# =========================================================
# HELPER: TOP 3 ERRORS
# =========================================================
def get_top_3_errors(row):
    error_pairs = []

    error_map = {
        "L101": row.get("l101_errors", 0),
        "V56": row.get("v56_errors", 0),
        "L102": row.get("l102_errors", 0),
        "UI": row.get("ui_errors", 0),
    }

    for code, count in error_map.items():
        if count and count > 0:
            error_pairs.append((code, int(count)))

    error_pairs = sorted(error_pairs, key=lambda x: x[1], reverse=True)

    top1 = f"{error_pairs[0][0]} ({error_pairs[0][1]})" if len(error_pairs) > 0 else "-"
    top2 = f"{error_pairs[1][0]} ({error_pairs[1][1]})" if len(error_pairs) > 1 else "-"
    top3 = f"{error_pairs[2][0]} ({error_pairs[2][1]})" if len(error_pairs) > 2 else "-"

    return pd.Series([top1, top2, top3], index=["top_error_1", "top_error_2", "top_error_3"])

# =========================================================
# ACTION QUEUE
# =========================================================
latest_ts = df["timestamp"].max()
queue = df[df["timestamp"] == latest_ts].copy()

queue["severity_band"] = pd.cut(
    queue["severity_score"],
    bins=[-0.01, 35, 60, 1000],
    labels=["Medium", "High", "Critical"],
)

queue["priority_score"] = (
    0.40 * queue["severity_score"]
    + 0.25 * (queue["issue_persistence_score"] * 100)
    + 0.20 * (queue["alerts_red"] * 10)
    + 0.15 * (queue["error_devices"] * 5)
).round(1)

queue["persistence_display"] = (
    (queue["issue_persistence_score"] * 8)
    .round()
    .astype(int)
    .astype(str) + "/8"
)

queue[["top_error_1", "top_error_2", "top_error_3"]] = queue.apply(get_top_3_errors, axis=1)

queue = queue.sort_values(["priority_score", "severity_score"], ascending=False).reset_index(drop=True)
queue["priority_rank"] = np.arange(1, len(queue) + 1)

# =========================================================
# UI
# =========================================================
st.title("Hotwire Engineer Workbench")
st.caption("Engineer-first single-page dashboard focused on technical action and evidence.")

selected_property = st.sidebar.selectbox(
    "Select property",
    queue["mduid"].tolist(),
    index=0,
)

rf_metric_mode = st.sidebar.radio(
    "WiFi chart mode",
    ["Busy Ratio", "Noise", "Interference"],
    index=0,
)

selected_df = df[df["mduid"] == selected_property].sort_values("timestamp").copy()
current = selected_df.iloc[-1]

# =========================================================
# TOP ACTION QUEUE
# =========================================================
st.subheader("Assigned Technical Action Queue")

queue_display = queue[
    [
        "priority_rank",
        "mduid",
        "primary_root_cause",
        "severity_band",
        "severity_score",
        "persistence_display",
        "top_error_1",
        "top_error_2",
        "top_error_3",
        "remote_fix_candidate",
        "suggested_next_step",
    ]
].rename(
    columns={
        "priority_rank": "Priority",
        "mduid": "Property",
        "primary_root_cause": "Issue Type",
        "severity_band": "Severity",
        "severity_score": "Severity Score",
        "persistence_display": "Persistence",
        "top_error_1": "Top Error 1",
        "top_error_2": "Top Error 2",
        "top_error_3": "Top Error 3",
        "remote_fix_candidate": "Remote Fix?",
        "suggested_next_step": "Suggested Next Step",
    }
)
st.dataframe(queue_display, use_container_width=True, hide_index=True)

# =========================================================
# MAIN BODY
# =========================================================
left, right = st.columns([2.0, 1.1])

with left:
    st.subheader("Technical Evidence")

    tab1, tab2, tab3 = st.tabs(["WiFi / RF", "Streaming", "Device / Platform Faults"])

    with tab1:
        st.markdown("#### Band Comparison Snapshot")
        band_table = pd.DataFrame(
            {
                "Metric": [
                    "Busy Ratio",
                    "Noise",
                    "Congested Eeros",
                    "Interference Ratio",
                    "Self Traffic Ratio",
                ],
                "2.4GHz": [
                    current["wifi_busy_24ghz"],
                    current["wifi_noise_24ghz"],
                    int(current["congested_eeros_24ghz"]),
                    current["interference_ratio_24ghz"],
                    current["self_traffic_ratio_24ghz"],
                ],
                "5GHz": [
                    current["wifi_busy_5ghz"],
                    current["wifi_noise_5ghz"],
                    int(current["congested_eeros_5ghz"]),
                    current["interference_ratio_5ghz"],
                    current["self_traffic_ratio_5ghz"],
                ],
            }
        )
        st.dataframe(band_table, use_container_width=True, hide_index=True)

        st.markdown("#### Band-Aware WiFi Trend")

        if rf_metric_mode == "Busy Ratio":
            chart_df = selected_df[["timestamp", "wifi_busy_24ghz", "wifi_busy_5ghz"]].rename(
                columns={"wifi_busy_24ghz": "2.4GHz", "wifi_busy_5ghz": "5GHz"}
            )
            y_title = "Busy Ratio"
            threshold_value = 0.80
            add_threshold = True

        elif rf_metric_mode == "Noise":
            chart_df = selected_df[["timestamp", "wifi_noise_24ghz", "wifi_noise_5ghz"]].rename(
                columns={"wifi_noise_24ghz": "2.4GHz", "wifi_noise_5ghz": "5GHz"}
            )
            y_title = "Noise"
            threshold_value = None
            add_threshold = False

        else:
            chart_df = selected_df[["timestamp", "interference_ratio_24ghz", "interference_ratio_5ghz"]].rename(
                columns={"interference_ratio_24ghz": "2.4GHz", "interference_ratio_5ghz": "5GHz"}
            )
            y_title = "Interference Ratio"
            threshold_value = None
            add_threshold = False

        chart_long = chart_df.melt(
            id_vars=["timestamp"],
            var_name="Band",
            value_name="Value",
        )

        base_chart = alt.Chart(chart_long).mark_line(point=True).encode(
            x=alt.X("timestamp:T", title="Hour"),
            y=alt.Y("Value:Q", title=y_title),
            color=alt.Color("Band:N", title="Band"),
            tooltip=["timestamp:T", "Band:N", "Value:Q"],
        ).properties(height=300)

        if add_threshold:
            threshold_df = pd.DataFrame({"y": [threshold_value]})
            threshold_line = alt.Chart(threshold_df).mark_rule(strokeDash=[6, 4]).encode(y="y:Q")
            st.altair_chart(base_chart + threshold_line, use_container_width=True)
        else:
            st.altair_chart(base_chart, use_container_width=True)

        st.caption(current["rf_summary_text"])

        st.markdown("#### RF Hotspot Table")
        latest_rf_detail = (
            df_rf_detail[
                (df_rf_detail["mduid"] == selected_property)
                & (df_rf_detail["timestamp"] == selected_df["timestamp"].max())
            ]
            .sort_values(["wifi_busy_ratio", "interference_ratio"], ascending=False)
            .copy()
        )
        st.dataframe(
            latest_rf_detail.rename(
                columns={
                    "eero_id": "Eero",
                    "band": "Band",
                    "wifi_busy_ratio": "Busy Ratio",
                    "wifi_noise": "Noise",
                    "interference_ratio": "Interference",
                    "self_traffic_ratio": "Self Traffic",
                }
            )[["Eero", "Band", "Busy Ratio", "Noise", "Interference", "Self Traffic"]],
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        stream_melt = selected_df.melt(
            id_vars=["timestamp"],
            value_vars=["stall_ratio", "buffer_ratio"],
            var_name="Metric",
            value_name="Value",
        )
        stream_chart = (
            alt.Chart(stream_melt)
            .mark_line(point=True)
            .encode(
                x=alt.X("timestamp:T", title="Hour"),
                y=alt.Y("Value:Q", title="Ratio"),
                color=alt.Color("Metric:N"),
                tooltip=["timestamp:T", "Metric:N", "Value:Q"],
            )
            .properties(height=300)
        )
        st.altair_chart(stream_chart, use_container_width=True)

        st.dataframe(
            selected_df[["timestamp", "stall_ratio", "buffer_ratio", "tivo_sessions"]]
            .tail(8)
            .rename(
                columns={
                    "timestamp": "Hour",
                    "stall_ratio": "Stall Ratio",
                    "buffer_ratio": "Buffer Ratio",
                    "tivo_sessions": "TiVo Sessions",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with tab3:
        fault_melt = selected_df.melt(
            id_vars=["timestamp"],
            value_vars=["error_events", "error_devices", "alerts_total", "alerts_red"],
            var_name="Metric",
            value_name="Value",
        )
        fault_chart = (
            alt.Chart(fault_melt)
            .mark_line(point=True)
            .encode(
                x=alt.X("timestamp:T", title="Hour"),
                y=alt.Y("Value:Q", title="Count"),
                color=alt.Color("Metric:N"),
                tooltip=["timestamp:T", "Metric:N", "Value:Q"],
            )
            .properties(height=300)
        )
        st.altair_chart(fault_chart, use_container_width=True)

        fault_table = (
            selected_df[
                ["timestamp", "error_events", "error_devices", "alerts_total", "alerts_red", "top_alert_type"]
            ]
            .tail(8)
            .rename(
                columns={
                    "timestamp": "Hour",
                    "error_events": "Error Events",
                    "error_devices": "Error Devices",
                    "alerts_total": "Alerts Total",
                    "alerts_red": "Red Alerts",
                    "top_alert_type": "Top Alert Type",
                }
            )
        )
        st.dataframe(fault_table, use_container_width=True, hide_index=True)

with right:
    st.subheader("Topology Health")

    topo_snapshot = pd.DataFrame(
        {
            "Metric": [
                "Mesh Nodes",
                "Gateway Nodes",
                "Leaf Nodes",
                "Leaf/Gateway Ratio",
                "Avg Hops",
                "Max Hops",
                "Low Backhaul Links",
                "Avg Next-hop RSSI",
                "Min Next-hop RSSI",
            ],
            "Value": [
                int(current["mesh_eeros"]),
                int(current["gateway_nodes"]),
                int(current["leaf_nodes"]),
                float(current["leaf_to_gateway_ratio"]),
                float(current["avg_hops_to_gateway"]),
                int(current["max_hops_to_gateway"]),
                int(current["low_backhaul_links"]),
                float(current["avg_next_hop_rssi"]),
                float(current["min_next_hop_rssi"]),
            ],
        }
    )
    st.dataframe(topo_snapshot, use_container_width=True, hide_index=True)

with st.expander("Show current property-hour row"):
    st.dataframe(pd.DataFrame([current]), use_container_width=True)