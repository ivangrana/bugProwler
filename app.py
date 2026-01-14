import asyncio

import streamlit as st

from src.app.agent import agno_assist  # import your BugProwler agent
from src.app.markdown_idor import generate_markdown
from src.app.reconaissance_agent import recon_agent
from src.app.swagger_analysis import IDORAnalyzer

st.set_page_config(page_title="BugProwler Agent", layout="wide")

st.title("BugProwler 𖢥")

# ---------- sidebar navigation ----------
with st.sidebar:
    st.markdown("### Toolbox:")
    chat_btn = st.button("Chat", key="chat_btn")
    swagger_btn = st.button("Swagger Docs Analyzer", key="swagger_btn")
    recon_btn = st.button("Reconaissance agent", key="recon_btn")
    report_btn = st.button("Reports", key="report_btn")

    if "page" not in st.session_state:
        st.session_state.page = "Chat"

    if chat_btn:
        st.session_state.page = "Chat"
    if swagger_btn:
        st.session_state.page = "Swagger Docs Analyzer"
    if recon_btn:
        st.session_state.page = "Reconaissance agent"
    if report_btn:
        st.session_state.page = "Reports"

page = st.session_state.page

# ---------- session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "swagger_analysis" not in st.session_state:
    st.session_state.swagger_analysis = []

if page == "Chat":
    # ---------- display history ----------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ---------- file uploader ----------
    uploaded_file = st.file_uploader(
        "Upload a file...", type=["txt", "md", "csv", "json", "png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        st.write("File uploaded successfully!")
        # Optional: display the file contents if it's text
        if uploaded_file.type.startswith("text") or uploaded_file.type in [
            "application/json"
        ]:
            try:
                content_str = file_bytes.decode("utf-8")
                st.code(content_str)
            except Exception as e:
                st.write(f"Unable to display file contents: {e}")

    # ---------- input ----------
    if prompt := st.chat_input("Ask me anything…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ---------- run agent ----------
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""
            for chunk in agno_assist.run(
                prompt, stream=True, debug_mode=True
            ):  # 2️⃣ streaming straight into UI
                if chunk.content:
                    full += chunk.content
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})

elif page == "Swagger Docs Analyzer":
    st.header("Swagger/OpenAPI Docs Analyzer")
    swagger_file = st.file_uploader(
        "Upload a Swagger/OpenAPI JSON or YAML file", type=["json", "yaml", "yml"]
    )
    if swagger_file is not None:
        try:
            file_bytes = swagger_file.read()
            # Try to decode as UTF-8 text
            content_str = file_bytes.decode("utf-8")

            analyze_prompt = f"Analyze the following Swagger/OpenAPI specification and summarize its endpoints, authentication, and notable features:\n\n{content_str}"
            with st.spinner("Analyzing Swagger/OpenAPI docs..."):
                analyzer = IDORAnalyzer()
                spec = analyzer.analyze_file_bytes(file_bytes)
                st.success("Analysis completed")
                st.markdown(generate_markdown(spec))
        except Exception as e:
            st.error(f"Error reading or analyzing Swagger/OpenAPI file: {e}")

elif page == "Reports":
    st.header("Bug Bounty Dashboards")

    # cards
    st.html("""
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
            <div class="card" style="width: 18rem; border: 1px solid #ddd; border-radius: 8px; box-shadow: 2px 2px 12px #eee; margin: 1rem;">
                <div class="card-body" style="padding: 1rem;">
                    <h5 class="card-title" style="font-weight: bold; font-size: 1.25rem; margin-bottom: 0.5rem;">Total Reports Submitted</h5>
                    <p class="card-text" style="font-size: 2rem; color: white; margin: 0;">42</p>
                </div>
            </div>
            <div class="card" style="width: 18rem; border: 1px solid #ddd; border-radius: 8px; box-shadow: 2px 2px 12px #eee; margin: 1rem;">
                <div class="card-body" style="padding: 1rem;">
                    <h5 class="card-title" style="font-weight: bold; font-size: 1.25rem; margin-bottom: 0.5rem;">Valid Bugs Found</h5>
                    <p class="card-text" style="font-size: 2rem; color: white; margin: 0;">15</p>
                </div>
            </div>
            <div class="card" style="width: 18rem; border: 1px solid #ddd; border-radius: 8px; box-shadow: 2px 2px 12px #eee; margin: 1rem;">
                <div class="card-body" style="padding: 1rem;">
                    <h5 class="card-title" style="font-weight: bold; font-size: 1.25rem; margin-bottom: 0.5rem;">Total Rewards Earned</h5>
                    <p class="card-text" style="font-size: 2rem; color: white; margin: 0;">$3500</p>
                </div>
            </div>
        </div>
    """)

    # Placeholder for recent report details - in a real app this would load/report data dynamically
    recent_reports = [
        {
            "id": "BR-101",
            "title": "IDOR in user profile API",
            "status": "Acknowledged",
            "reward": "$500",
        },
        {
            "id": "BR-102",
            "title": "XSS in comment section",
            "status": "Under Review",
            "reward": "$0",
        },
        {
            "id": "BR-103",
            "title": "Auth bypass in admin panel",
            "status": "Resolved",
            "reward": "$1500",
        },
    ]

    st.subheader("Recent Bug Reports")
    for report in recent_reports:
        with st.expander(f"{report['id']}: {report['title']}"):
            st.write(f"Status: **{report['status']}**")
            st.write(f"Reward: {report['reward']}")
            st.write("Detailed description and notes go here...")

    # Optionally add charts or graphs here for visualizing trends or bug categories
    st.subheader("Bug Reports Over Time")
    import numpy as np
    import pandas as pd

    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    reports_per_day = np.random.poisson(lam=1.5, size=30)
    df = pd.DataFrame({"Date": dates, "Reports": reports_per_day})

    st.bar_chart(
        df.rename(columns={"Date": "index"}).set_index("index"), color="#ffaa00"
    )

    st.markdown("## Reports Donuts")
    st.html("""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Donut Chart</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: #f5f7fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            .chart-container {
                position: relative;
                width: 300px;
                height: 300px;
            }

            .donut-chart {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: conic-gradient(
                    #4f46e5 0% 30%,
                    #10b981 30% 65%,
                    #f59e0b 65% 85%,
                    #ef4444 85% 100%
                );
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: pointer;
                transition: transform 0.3s ease;
            }

            .donut-chart:hover {
                transform: scale(1.05);
            }

            .donut-hole {
                width: 60%;
                height: 60%;
                background: #f5f7fa;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }

            .total-value {
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
                margin-bottom: 4px;
            }

            .total-label {
                font-size: 14px;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .tooltip {
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
                z-index: 10;
            }

            .legend {
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-top: 24px;
                padding: 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .legend-item {
                display: flex;
                align-items: center;
                gap: 12px;
                cursor: pointer;
                transition: transform 0.2s ease;
            }

            .legend-item:hover {
                transform: translateX(5px);
            }

            .legend-color {
                width: 20px;
                height: 20px;
                border-radius: 4px;
            }

            .legend-text {
                font-size: 14px;
                color: #374151;
                font-weight: 500;
            }

            .legend-value {
                margin-left: auto;
                font-weight: 600;
                color: #1f2937;
            }

            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
            }

            .highlight {
                filter: brightness(1.2) contrast(1.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="chart-container">
                <div class="donut-chart" id="donutChart">
                    <div class="donut-hole">
                        <div class="total-value">100%</div>
                        <div class="total-label">Total</div>
                    </div>
                    <div class="tooltip" id="tooltip"></div>
                </div>
            </div>

            <div class="legend">
                <div class="legend-item" data-sector="0">
                    <div class="legend-color" style="background-color: #4f46e5;"></div>
                    <div class="legend-text">Product A</div>
                    <div class="legend-value">30%</div>
                </div>
                <div class="legend-item" data-sector="1">
                    <div class="legend-color" style="background-color: #10b981;"></div>
                    <div class="legend-text">Product B</div>
                    <div class="legend-value">35%</div>
                </div>
                <div class="legend-item" data-sector="2">
                    <div class="legend-color" style="background-color: #f59e0b;"></div>
                    <div class="legend-text">Product C</div>
                    <div class="legend-value">20%</div>
                </div>
                <div class="legend-item" data-sector="3">
                    <div class="legend-color" style="background-color: #ef4444;"></div>
                    <div class="legend-text">Product D</div>
                    <div class="legend-value">15%</div>
                </div>
            </div>
        </div>

        <script>
            const donutChart = document.getElementById('donutChart');
            const tooltip = document.getElementById('tooltip');
            const legendItems = document.querySelectorAll('.legend-item');
            const sectors = [
                { start: 0, end: 30, color: '#4f46e5', label: 'Product A', value: '30%' },
                { start: 30, end: 65, color: '#10b981', label: 'Product B', value: '35%' },
                { start: 65, end: 85, color: '#f59e0b', label: 'Product C', value: '20%' },
                { start: 85, end: 100, color: '#ef4444', label: 'Product D', value: '15%' }
            ];

            // Add mouse move event to chart
            donutChart.addEventListener('mousemove', (e) => {
                const rect = donutChart.getBoundingClientRect();
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const dx = mouseX - centerX;
                const dy = mouseY - centerY;
                const angle = Math.atan2(dy, dx) * 180 / Math.PI;
                const normalizedAngle = (angle + 360) % 360;

                let sectorIndex = -1;
                for (let i = 0; i < sectors.length; i++) {
                    if (normalizedAngle >= sectors[i].start && normalizedAngle < sectors[i].end) {
                        sectorIndex = i;
                        break;
                    }
                }

                if (sectorIndex !== -1) {
                    const sector = sectors[sectorIndex];
                    tooltip.textContent = `${sector.label}: ${sector.value}`;
                    tooltip.style.opacity = 1;

                    // Position tooltip near cursor
                    tooltip.style.left = (e.clientX - rect.left + 15) + 'px';
                    tooltip.style.top = (e.clientY - rect.top - 15) + 'px';

                    // Highlight sector
                    donutChart.style.background = `conic-gradient(
                        ${sector.color} 0% ${sector.start}%,
                        ${sector.color} ${sector.start}% ${sector.end}%,
                        #e5e7eb ${sector.end}% 100%
                    )`;
                } else {
                    tooltip.style.opacity = 0;
                    donutChart.style.background = `conic-gradient(
                        #4f46e5 0% 30%,
                        #10b981 30% 65%,
                        #f59e0b 65% 85%,
                        #ef4444 85% 100%
                    )`;
                }
            });

            // Reset when mouse leaves chart
            donutChart.addEventListener('mouseleave', () => {
                tooltip.style.opacity = 0;
                donutChart.style.background = `conic-gradient(
                    #4f46e5 0% 30%,
                    #10b981 30% 65%,
                    #f59e0b 65% 85%,
                    #ef4444 85% 100%
                )`;
            });

            // Legend item interactions
            legendItems.forEach(item => {
                item.addEventListener('mouseenter', () => {
                    const sectorIndex = parseInt(item.getAttribute('data-sector'));
                    const sector = sectors[sectorIndex];

                    // Highlight sector
                    donutChart.style.background = `conic-gradient(
                        ${sector.color} 0% ${sector.start}%,
                        ${sector.color} ${sector.start}% ${sector.end}%,
                        #e5e7eb ${sector.end}% 100%
                    )`;

                    // Show tooltip
                    tooltip.textContent = `${sector.label}: ${sector.value}`;
                    tooltip.style.opacity = 1;
                    tooltip.style.left = (item.offsetLeft + item.offsetWidth + 20) + 'px';
                    tooltip.style.top = (item.offsetTop + item.offsetHeight / 2 - 10) + 'px';
                });

                item.addEventListener('mouseleave', () => {
                    donutChart.style.background = `conic-gradient(
                        #4f46e5 0% 30%,
                        #10b981 30% 65%,
                        #f59e0b 65% 85%,
                        #ef4444 85% 100%
                    )`;
                    tooltip.style.opacity = 0;
                });
            });
        </script>
    </body>
    </html>

""")


elif page == "Reconaissance agent":
    st.header("Reconaissance Agent")
    # ---------- display history ----------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    # ---------- input ----------
    if prompt := st.chat_input("Ask me anything…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ---------- run agent ----------
        async def async_run_agent(prompt):
            full = ""
            placeholder = st.empty()
            async for chunk in recon_agent.arun(prompt, stream=True, debug_mode=True):
                if chunk.content:
                    full += chunk.content
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)
            return full

        with st.chat_message("assistant"):
            full = asyncio.run(async_run_agent(prompt))
        st.session_state.messages.append({"role": "assistant", "content": full})
