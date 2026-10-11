// Entropy-Guided Cluster Video Streamer - Client Telemetry Engine
document.addEventListener("DOMContentLoaded", () => {
    // --- State & DOM References ---
    let ws = null;
    let clusterState = null;
    let recentDispatches = [];
    let latencyHistory = { tree: [], lln: [] };
    let dispatchedChunkCount = 0;
    let activePathTimeout = null;
    let terminalCursorEl = null;

    let hasAnimatedTreeOnce = false;

    // ===== LIGHTWEIGHT AMBIENT PARTICLE CANVAS (60FPS OPTIMIZED) =====
    (function initParticles() {
        const canvas = document.getElementById("particleCanvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        let W, H, particles = [];

        function resize() {
            W = canvas.width  = window.innerWidth;
            H = canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener("resize", resize);

        const COUNT = 24;
        for (let i = 0; i < COUNT; i++) {
            particles.push({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                r: Math.random() * 2.0 + 0.8,
                vx: (Math.random() - 0.5) * 0.25,
                vy: (Math.random() - 0.5) * 0.25,
                alpha: Math.random() * 0.4 + 0.2,
                hue: Math.random() > 0.5 ? 190 : 265
            });
        }

        function drawFrame() {
            ctx.clearRect(0, 0, W, H);
            const isLight = document.documentElement.getAttribute("data-theme") === "light";
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0) p.x = W;
                if (p.x > W) p.x = 0;
                if (p.y < 0) p.y = H;
                if (p.y > H) p.y = 0;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = isLight
                    ? `hsla(${p.hue}, 80%, 45%, ${p.alpha * 0.35})`
                    : `hsla(${p.hue}, 90%, 65%, ${p.alpha})`;
                ctx.fill();
            }
            requestAnimationFrame(drawFrame);
        }
        drawFrame();
    })();

    // ===== BUTTON RIPPLE =====
    document.querySelectorAll(".btn").forEach(btn => {
        btn.addEventListener("click", function(e) {
            const r = document.createElement("span");
            r.className = "ripple-effect";
            const rect = this.getBoundingClientRect();
            r.style.left = (e.clientX - rect.left) + "px";
            r.style.top  = (e.clientY - rect.top)  + "px";
            this.appendChild(r);
            r.addEventListener("animationend", () => r.remove());
        });
    });


    // Elements
    const videoPlayer = document.getElementById("videoPlayer");
    const videoSelect = document.getElementById("videoSelect");
    const uploadDropzone = document.getElementById("uploadDropzone");
    const videoFileInput = document.getElementById("videoFileInput");
    const btnBrowseFiles = document.getElementById("btnBrowseFiles");
    const uploadProgressContainer = document.getElementById("uploadProgressContainer");
    const uploadFileName = document.getElementById("uploadFileName");
    const uploadProgressBar = document.getElementById("uploadProgressBar");
    const uploadPercent = document.getElementById("uploadPercent");

    const entropyValuePill = document.getElementById("entropyValuePill");
    const stabilityClassPill = document.getElementById("stabilityClassPill");
    const btnBurst = document.getElementById("btnBurst");
    const btnRebalance = document.getElementById("btnRebalance");
    const btnSimulateStream = document.getElementById("btnSimulateStream");

    const hudVideoName = document.getElementById("hudVideoName");
    const hudChunkId = document.getElementById("hudChunkId");
    const hudAssignedNode = document.getElementById("hudAssignedNode");
    const streamBufferFill = document.getElementById("streamBufferFill");
    const statDispatchedCount = document.getElementById("statDispatchedCount");
    const statAvgDecision = document.getElementById("statAvgDecision");

    // Live Streaming & Algorithm Simulation Controls
    const btnToggleLiveSim = document.getElementById("btnToggleLiveSim");
    const liveSimDot = document.getElementById("liveSimDot");
    const liveSimLabel = document.getElementById("liveSimLabel");
    const playbackStreamBadge = document.getElementById("playbackStreamBadge");
    const streamBadgeDot = document.getElementById("streamBadgeDot");
    const streamBadgeText = document.getElementById("streamBadgeText");

    const algoTagPill = document.getElementById("algoTagPill");
    const simStep1 = document.getElementById("simStep1");
    const simStep1Text = document.getElementById("simStep1Text");
    const simStep2 = document.getElementById("simStep2");
    const simStep2Text = document.getElementById("simStep2Text");
    const simStep3 = document.getElementById("simStep3");
    const simStep3Text = document.getElementById("simStep3Text");
    const contrastBaselineMetric = document.getElementById("contrastBaselineMetric");
    const contrastThesisMetric = document.getElementById("contrastThesisMetric");

    // Playback and Simulation State
    let livePlaybackInterval = null;
    let continuousTrafficInterval = null;
    let currentPlaybackChunkIndex = 0;
    let isContinuousSimActive = false;

    const treeSvg = document.getElementById("clusterTreeSvg");
    const dispatchRouteBanner = document.getElementById("dispatchRouteBanner");
    const crumbRack = document.getElementById("crumbRack");
    const crumbNode = document.getElementById("crumbNode");
    const routeDecisionTime = document.getElementById("routeDecisionTime");
    const routeSpeedup = document.getElementById("routeSpeedup");
    const dispatchTerminal = document.getElementById("dispatchTerminal");

    const speedupBadge = document.getElementById("speedupBadge");
    const avgTreeLatency = document.getElementById("avgTreeLatency");
    const avgLlnLatency = document.getElementById("avgLlnLatency");
    const latencyCanvas = document.getElementById("latencyCanvas");
    const racksContainer = document.getElementById("racksContainer");
    const toastContainer = document.getElementById("toastContainer");

    // --- Theme Management (Dark & Light Mode) ---
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const sunIcon = document.getElementById("sunIcon");
    const moonIcon = document.getElementById("moonIcon");
    const themeToggleLabel = document.getElementById("themeToggleLabel");

    function applyTheme(theme) {
        if (theme === "light") {
            document.documentElement.setAttribute("data-theme", "light");
            if (sunIcon) sunIcon.style.display = "none";
            if (moonIcon) moonIcon.style.display = "inline-block";
            if (themeToggleLabel) themeToggleLabel.textContent = "Dark";
        } else {
            document.documentElement.removeAttribute("data-theme");
            if (sunIcon) sunIcon.style.display = "inline-block";
            if (moonIcon) moonIcon.style.display = "none";
            if (themeToggleLabel) themeToggleLabel.textContent = "Light";
        }
        localStorage.setItem("entropy_theme", theme);
        if (clusterState) renderClusterTreeSvg(clusterState);
    }

    const savedTheme = localStorage.getItem("entropy_theme") || "dark";
    applyTheme(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
            const newTheme = currentTheme === "light" ? "dark" : "light";
            applyTheme(newTheme);
            showToast(`Switched to ${newTheme.toUpperCase()} mode`, "info");
        });
    }

    // --- Initial State Fetch & WebSocket Connection ---
    async function fetchInitialState() {
        try {
            const res = await fetch("/api/cluster/state");
            if (res.ok) {
                clusterState = await res.json();
                renderClusterTelemetry(clusterState);
            }
        } catch (e) {
            // Server may still be booting
        }
    }

    let wsRetryDelay = 300;
    function initWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            wsRetryDelay = 300;
            logTerminal("⚡ Connected to Cluster Telemetry WebSocket", "text-cyan");
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === "TELEMETRY") {
                    clusterState = msg.data;
                    renderClusterTelemetry(clusterState);
                } else if (msg.type === "CHUNK_DISPATCHED") {
                    handleChunkDispatched(msg.event);
                } else if (msg.type === "BURST_RESULT") {
                    showToast(`Burst injected on Rack ${msg.data.target_rack}! Entropy: ${msg.data.entropy_class}`, "warning");
                } else if (msg.type === "REBALANCE_RESULT") {
                    const txt = msg.data.was_rebuilt ? "Tree Reconstructed bottom-up (Algorithm 1)!" : "Tree refreshed in-place.";
                    showToast(`Algorithm 3: ${txt}`, "info");
                }
            } catch (err) {
                console.error("WS Parse error:", err);
            }
        };

        ws.onclose = () => {
            setTimeout(initWebSocket, wsRetryDelay);
            wsRetryDelay = Math.min(2000, Math.round(wsRetryDelay * 1.5));
        };
    }

    // --- Render Real-Time Cluster Telemetry ---
    function renderClusterTelemetry(state) {
        if (!state) return;

        // Entropy and Stability State
        const entropyVal = state.entropy.shannon.toFixed(3);
        const normVal = state.entropy.normalized.toFixed(3);
        animateNumberFlash(entropyValuePill, `${entropyVal} (norm: ${normVal})`);

        const classification = state.entropy.classification;
        stabilityClassPill.textContent = classification;
        stabilityClassPill.className = `pill-value status-badge badge-${classification.toLowerCase()}`;

        // Latency Comparison Cards
        const treeAvg = state.latency_comparison.hierarchical_tree_avg_us || 0.0;
        const llnAvg = state.latency_comparison.flat_scan_lln_avg_us || 0.0;
        animateNumberFlash(avgTreeLatency, treeAvg.toFixed(1));
        animateNumberFlash(avgLlnLatency, llnAvg.toFixed(1));

        statAvgDecision.textContent = `${treeAvg.toFixed(1)} µs`;

        if (treeAvg > 0 && llnAvg > 0) {
            const ratio = (llnAvg / treeAvg).toFixed(1);
            animateNumberFlash(speedupBadge, `${ratio}x Faster`);
        }

        // Render Latency Sparkline Chart
        latencyHistory.tree = state.latency_comparison.recent_tree_samples || [];
        latencyHistory.lln = state.latency_comparison.recent_lln_samples || [];
        drawSparkline(latencyHistory);

        // Render Racks & Nodes Grid
        renderRackMatrix(state.racks, state.nodes);

        // Render Interactive SVG Topology Tree
        renderClusterTreeSvg(state);
    }

    // --- Render Rack Matrix ---
    function renderRackMatrix(racks, nodes) {
        if (!racks || !nodes) return;

        // Ensure all 4 racks are displayed even if a single rack is returned
        const effectiveRacks = (racks && racks.length > 1) ? racks : [
            { rack_id: 0, avg_cpu: 0, avg_net: 1.0 },
            { rack_id: 1, avg_cpu: 0, avg_net: 1.0 },
            { rack_id: 2, avg_cpu: 0, avg_net: 1.0 },
            { rack_id: 3, avg_cpu: 0, avg_net: 1.0 },
        ];

        let html = "";
        effectiveRacks.forEach((rack) => {
            const rackNodes = nodes.filter(n => {
                if (racks && racks.length > 1 && n.rack_id !== undefined && n.rack_id !== null) {
                    return n.rack_id === rack.rack_id;
                }
                return Math.floor(n.node_id / 4) === rack.rack_id;
            });
            const rackAvgCpu = rack.avg_cpu || (rackNodes.length ? Math.round(rackNodes.reduce((a, b) => a + (b.cpu || 0), 0) / rackNodes.length) : 0);
            html += `
                <div class="rack-card" id="rackCard_${rack.rack_id}">
                    <div class="rack-header">
                        <span>Rack ${rack.rack_id} (Avg CPU: ${rackAvgCpu}%)</span>
                        <span class="font-mono text-muted">Net: ${rack.avg_net || 1.0} MB/s</span>
                    </div>
                    <div class="rack-nodes-grid">
            `;

            rackNodes.forEach((node) => {
                const loadPercent = Math.min(100, Math.round(node.cpu));
                const meterColor = loadPercent > 75 ? "var(--rose)" : loadPercent > 45 ? "var(--amber)" : "var(--emerald)";
                const tagClass = `tag-${node.entropy_class.toLowerCase()}`;

                html += `
                    <div class="node-mini-card" id="nodeCard_${node.node_id}">
                        <div class="node-top-row">
                            <span class="node-name font-mono">N${node.node_id}</span>
                            <span class="node-entropy-tag ${tagClass}">${node.entropy_class.substring(0, 3)}</span>
                        </div>
                        <div class="node-meter-bar">
                            <div class="node-meter-fill" style="width: ${loadPercent}%; background: ${meterColor};"></div>
                        </div>
                        <div class="node-load-text font-mono">
                            <span>${loadPercent}%</span>
                            <span>${node.active_jobs_count}j</span>
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        });

        racksContainer.innerHTML = html;
    }

    // --- Render SVG Hierarchical Tree (ClusterRoot -> 4 Racks -> 16 Nodes) ---
    function renderClusterTreeSvg(state) {
        const width = 900;
        const height = 400;

        // Tree Coordinates
        const rootPos = { x: 450, y: 40 };
        const rackPositions = [
            { id: 0, x: 130, y: 150 },
            { id: 1, x: 340, y: 150 },
            { id: 2, x: 560, y: 150 },
            { id: 3, x: 770, y: 150 }
        ];

        let linksHtml = "";
        let nodesHtml = "";

        // Links from Root to Racks
        rackPositions.forEach(rack => {
            linksHtml += `
                <line id="link_root_rack_${rack.id}" class="tree-link" 
                      x1="${rootPos.x}" y1="${rootPos.y + 15}" 
                      x2="${rack.x}" y2="${rack.y - 15}" />
            `;
        });

        // Compute Node positions (4 per rack)
        const nodePositions = [];
        rackPositions.forEach(rack => {
            const rackNodes = state.nodes.filter(n => {
                if (state.racks && state.racks.length > 1 && n.rack_id !== undefined && n.rack_id !== null) {
                    return n.rack_id === rack.id;
                }
                return Math.floor(n.node_id / 4) === rack.id;
            });
            const count = rackNodes.length || 4;
            const rackSpan = 180;
            const startX = rack.x - (rackSpan / 2) + 20;
            const stepX = count > 1 ? (rackSpan - 40) / (count - 1) : 0;

            rackNodes.forEach((node, idx) => {
                const nodeX = count > 1 ? startX + (idx * stepX) : rack.x;
                const nodeY = 320;
                nodePositions.push({ id: node.node_id, rackId: rack.id, x: nodeX, y: nodeY, data: node });

                linksHtml += `
                    <line id="link_rack_${rack.id}_node_${node.node_id}" class="tree-link" 
                          x1="${rack.x}" y1="${rack.y + 15}" 
                          x2="${nodeX}" y2="${nodeY - 14}" />
                `;
            });
        });

        // Theme-aware SVG styling
        const isLight = document.documentElement.getAttribute("data-theme") === "light";
        const nodeFill = isLight ? "#ffffff" : "#1e293b";
        const leafFill = isLight ? "#f8fafc" : "#0f172a";

        // Draw Root Node
        const rootCpu = state.root.avg_cpu || 0;
        nodesHtml += `
            <g id="svg_node_root" class="tree-node-group">
                <circle cx="${rootPos.x}" cy="${rootPos.y}" r="22" fill="${nodeFill}" stroke="var(--blue)" stroke-width="2.5" class="tree-node-circle" />
                <text x="${rootPos.x}" y="${rootPos.y + 4}" class="tree-node-text">ROOT</text>
                <text x="${rootPos.x}" y="${rootPos.y + 36}" class="tree-node-subtext">Avg ${rootCpu}%</text>
            </g>
        `;

        // Draw Rack Nodes
        rackPositions.forEach(rack => {
            const rData = (state.racks && state.racks.find(r => r.rack_id === rack.id)) || { avg_cpu: 0 };
            const strokeColor = rData.avg_cpu > 70 ? "var(--rose)" : rData.avg_cpu > 40 ? "var(--amber)" : "var(--violet)";
            nodesHtml += `
                <g id="svg_node_rack_${rack.id}" class="tree-node-group">
                    <circle cx="${rack.x}" cy="${rack.y}" r="17" fill="${nodeFill}" stroke="${strokeColor}" stroke-width="2" class="tree-node-circle" />
                    <text x="${rack.x}" y="${rack.y + 4}" class="tree-node-text">R${rack.id}</text>
                    <text x="${rack.x}" y="${rack.y + 28}" class="tree-node-subtext">${rData.avg_cpu}%</text>
                </g>
            `;
        });

        // Draw Compute Nodes (Leaves)
        nodePositions.forEach(node => {
            const cpu = node.data.cpu || 0;
            const fillColor = cpu > 75 ? "var(--rose)" : cpu > 45 ? "var(--amber)" : "var(--emerald)";
            nodesHtml += `
                <g id="svg_node_compute_${node.id}" class="tree-node-group">
                    <circle id="node_circle_${node.id}" cx="${node.x}" cy="${node.y}" r="12" fill="${leafFill}" stroke="${fillColor}" stroke-width="2" class="tree-node-circle" />
                    <text x="${node.x}" y="${node.y + 3}" class="tree-node-text" style="font-size: 8px;">N${node.id}</text>
                    <text x="${node.x}" y="${node.y + 22}" class="tree-node-subtext" style="font-size: 8px;">${Math.round(cpu)}%</text>
                </g>
            `;
        });

        treeSvg.innerHTML = `<g id="treeLinks">${linksHtml}</g><g id="treeNodes">${nodesHtml}</g>`;

        // Animate entrance ONLY once on initial mount to eliminate layout thrashing
        if (!hasAnimatedTreeOnce) {
            hasAnimatedTreeOnce = true;
            const nodeGroups = treeSvg.querySelectorAll(".tree-node-group");
            nodeGroups.forEach((g, i) => {
                g.style.opacity = "0";
                g.style.transition = `opacity 0.25s ${i * 0.02}s ease`;
                requestAnimationFrame(() => {
                    g.style.opacity = "1";
                });
            });
        }
    }

    // --- Handle Dispatched Chunk Event ---
    function handleChunkDispatched(event) {
        if (!event) return;

        dispatchedChunkCount++;
        statDispatchedCount.textContent = dispatchedChunkCount;

        // Update Video HUD
        hudVideoName.textContent = event.video_name;
        hudChunkId.textContent = `Chunk #${event.chunk_index} (${Math.round(event.byte_size / 1024)} KB)`;
        hudAssignedNode.textContent = `Node_${event.assigned_node_id} (Rack_${event.assigned_rack_id})`;

        // Dynamic buffer fill indicator based on dispatched chunks
        if (streamBufferFill) {
            const fillPct = Math.min(100, Math.max(20, ((dispatchedChunkCount * 8) % 85) + 15));
            streamBufferFill.style.width = `${fillPct}%`;
        }

        // Update Route Crumb Bar
        crumbRack.textContent = `Rack_${event.assigned_rack_id}`;
        crumbNode.textContent = `Node_${event.assigned_node_id}`;
        routeDecisionTime.textContent = `${event.tree_time_us} µs`;
        routeSpeedup.textContent = `${event.speedup_ratio}x vs O(N)`;

        // Update Live Algorithmic Simulation & Decision Breakdown
        const sim = event.simulation || {};
        if (simStep1Text) {
            simStep1Text.textContent = sim.step1_rack || `Rack_${event.assigned_rack_id} chosen (Lowest min composite load). 3 racks (12 nodes) pruned in O(1)!`;
        }
        if (simStep2Text) {
            simStep2Text.textContent = sim.step2_node || `Node_${event.assigned_node_id} selected (Stability: ${event.node_entropy_class}). Entropy-guided guard active.`;
        }
        if (simStep3Text) {
            simStep3Text.textContent = sim.step3_propagate || `Propagated load upward in ${event.tree_time_us} µs (${event.speedup_ratio}x faster than scanning all 16 nodes).`;
        }
        if (contrastBaselineMetric) {
            contrastBaselineMetric.textContent = sim.traditional_cost || `16 node checks • ${event.lln_time_us} µs • Blind to Volatility`;
        }
        if (contrastThesisMetric) {
            contrastThesisMetric.textContent = sim.thesis_cost || `8 tree checks • ${event.tree_time_us} µs • ${event.speedup_ratio}x Faster`;
        }
        if (algoTagPill) {
            algoTagPill.textContent = `Tree O(log N): ${event.speedup_ratio}x Speedup`;
        }

        // 3-Step Decision Flow Pulse Animation
        if (simStep1) simStep1.classList.add("step-active");
        setTimeout(() => {
            if (simStep2) simStep2.classList.add("step-active");
        }, 130);
        setTimeout(() => {
            if (simStep3) simStep3.classList.add("step-active");
        }, 260);
        setTimeout(() => {
            if (simStep1) simStep1.classList.remove("step-active");
            if (simStep2) simStep2.classList.remove("step-active");
            if (simStep3) simStep3.classList.remove("step-active");
        }, 850);

        // Highlight SVG Tree Path and Node Circles
        highlightTreePath(event.assigned_rack_id, event.assigned_node_id);

        // Highlight Matrix Card
        const nodeCard = document.getElementById(`nodeCard_${event.assigned_node_id}`);
        if (nodeCard) {
            nodeCard.classList.add("highlight-target");
            setTimeout(() => nodeCard.classList.remove("highlight-target"), 650);
        }

        // Add to Terminal
        const logLine = `[LIVE CHUNK #${event.chunk_index}] Route: Root ➔ Rack_${event.assigned_rack_id} ➔ Node_${event.assigned_node_id} | Tree: ${event.tree_time_us} µs (${event.speedup_ratio}x) | Flat: ${event.lln_time_us} µs | H(S): ${event.cluster_entropy}`;
        logTerminal(logLine, "text-cyan");
    }

    function highlightTreePath(rackId, nodeId) {
        // Clear previous path highlights
        document.querySelectorAll(".tree-link.active-path").forEach(el => el.classList.remove("active-path"));
        document.querySelectorAll(".tree-node-circle.active-target").forEach(el => el.classList.remove("active-target"));

        const linkRootRack = document.getElementById(`link_root_rack_${rackId}`);
        const linkRackNode = document.getElementById(`link_rack_${rackId}_node_${nodeId}`);
        const rackCircle = document.getElementById(`rack_circle_${rackId}`);
        const nodeCircle = document.getElementById(`node_circle_${nodeId}`);

        if (linkRootRack) linkRootRack.classList.add("active-path");
        if (linkRackNode) linkRackNode.classList.add("active-path");
        if (rackCircle) rackCircle.classList.add("active-target");
        if (nodeCircle) nodeCircle.classList.add("active-target");

        if (activePathTimeout) clearTimeout(activePathTimeout);
        activePathTimeout = setTimeout(() => {
            if (linkRootRack) linkRootRack.classList.remove("active-path");
            if (linkRackNode) linkRackNode.classList.remove("active-path");
            if (rackCircle) rackCircle.classList.remove("active-target");
            if (nodeCircle) nodeCircle.classList.remove("active-target");
        }, 950);
    }

    // --- Draw Latency Sparkline ---
    function drawSparkline(history) {
        const ctx = latencyCanvas.getContext("2d");
        const w = latencyCanvas.width;
        const h = latencyCanvas.height;
        ctx.clearRect(0, 0, w, h);

        const treeSamples = history.tree;
        const llnSamples = history.lln;
        const maxLen = Math.max(treeSamples.length, llnSamples.length);
        if (maxLen < 2) return;

        const maxVal = Math.max(...treeSamples, ...llnSamples, 20.0);

        function drawLine(data, color) {
            if (data.length < 2) return;
            ctx.beginPath();
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            const step = w / (data.length - 1);
            data.forEach((val, i) => {
                const x = i * step;
                const y = h - ((val / maxVal) * (h - 10)) - 5;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();
        }

        drawLine(llnSamples, "#f43f5e"); // Rose for Flat Scan O(N)
        drawLine(treeSamples, "#00f2fe"); // Cyan for Hierarchical O(log N)
    }

    // --- Terminal Logging (High-Performance Zero-Lag Append) ---
    function logTerminal(text, colorClass = "text-muted") {
        if (terminalCursorEl && terminalCursorEl.parentNode) {
            terminalCursorEl.parentNode.removeChild(terminalCursorEl);
        }

        const line = document.createElement("div");
        line.className = `terminal-line ${colorClass}`;
        const prefix = `[${new Date().toLocaleTimeString()}] `;
        line.textContent = prefix + text;

        terminalCursorEl = document.createElement("span");
        terminalCursorEl.className = "terminal-cursor";
        line.appendChild(terminalCursorEl);

        dispatchTerminal.appendChild(line);
        dispatchTerminal.scrollTop = dispatchTerminal.scrollHeight;

        if (dispatchTerminal.children.length > 80) {
            dispatchTerminal.removeChild(dispatchTerminal.firstChild);
        }
    }

    // --- Animated Number Flash ---
    function animateNumberFlash(el, newVal) {
        if (!el) return;
        if (el.textContent === String(newVal)) return;
        el.textContent = newVal;
        el.style.animation = "none";
        void el.offsetWidth; // reflow trigger
        el.style.animation = "numberFlash 0.7s ease-out";
    }

    // --- Toast Notifications ---
    function showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${type === "warning" ? "⚠️" : "ℹ️"}</span>
            <span>${message}</span>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 400);
        }, 3200);
    }

    // --- Video Player Buffer & Playback Listeners ---
    function setStreamBadge(isActive, text) {
        if (!playbackStreamBadge || !streamBadgeDot || !streamBadgeText) return;
        if (isActive) {
            playbackStreamBadge.classList.add("active-stream");
            streamBadgeDot.className = "badge-dot pulse-streaming";
        } else {
            playbackStreamBadge.classList.remove("active-stream");
            streamBadgeDot.className = "badge-dot pulse-idle";
        }
        streamBadgeText.textContent = text;
    }

    async function dispatchNextStreamChunk() {
        currentPlaybackChunkIndex++;
        const vid = videoSelect.value || "demo_stream.mp4";
        try {
            const res = await fetch("/api/stream/dispatch_chunk", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    video_name: vid,
                    chunk_index: currentPlaybackChunkIndex,
                    byte_size: 256 * 1024
                })
            });
            if (res.ok) {
                const data = await res.json();
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    handleChunkDispatched(data.event);
                }
            }
        } catch (e) {
            console.error("Chunk dispatch request error:", e);
        }
    }

    function startPlaybackStreaming() {
        if (livePlaybackInterval) return;
        setStreamBadge(true, "PLAYBACK STREAMING (ACTIVE)");
        dispatchNextStreamChunk();
        livePlaybackInterval = setInterval(() => {
            if (!videoPlayer.paused && !videoPlayer.ended) {
                dispatchNextStreamChunk();
            }
        }, 850);
    }

    function stopPlaybackStreaming() {
        if (livePlaybackInterval) {
            clearInterval(livePlaybackInterval);
            livePlaybackInterval = null;
        }
        if (!isContinuousSimActive) {
            setStreamBadge(false, "IDLE (PRESS PLAY TO STREAM)");
        }
    }

    videoPlayer.addEventListener("play", () => {
        startPlaybackStreaming();
    });

    videoPlayer.addEventListener("pause", () => {
        stopPlaybackStreaming();
    });

    videoPlayer.addEventListener("ended", () => {
        stopPlaybackStreaming();
        if (!isContinuousSimActive) {
            setStreamBadge(false, "PLAYBACK FINISHED");
        }
    });

    videoPlayer.addEventListener("timeupdate", () => {
        if (videoPlayer.duration > 0 && videoPlayer.buffered.length > 0) {
            const bufferedEnd = videoPlayer.buffered.end(videoPlayer.buffered.length - 1);
            const percent = Math.min(100, Math.round((bufferedEnd / videoPlayer.duration) * 100));
            if (streamBufferFill && streamBufferFill.style.width === "0%") {
                streamBufferFill.style.width = `${percent}%`;
            }
        }
    });

    // Toggle Continuous Live Simulation Button
    if (btnToggleLiveSim) {
        btnToggleLiveSim.addEventListener("click", () => {
            isContinuousSimActive = !isContinuousSimActive;
            if (isContinuousSimActive) {
                if (liveSimDot) liveSimDot.classList.add("active");
                if (liveSimLabel) liveSimLabel.textContent = "Stop Continuous Stream";
                setStreamBadge(true, "CONTINUOUS TRAFFIC SIMULATION ACTIVE");
                showToast("Simulating continuous live stream traffic...", "info");
                dispatchNextStreamChunk();
                continuousTrafficInterval = setInterval(() => {
                    dispatchNextStreamChunk();
                }, 850);
            } else {
                if (liveSimDot) liveSimDot.classList.remove("active");
                if (liveSimLabel) liveSimLabel.textContent = "Simulate Continuous Stream";
                if (continuousTrafficInterval) {
                    clearInterval(continuousTrafficInterval);
                    continuousTrafficInterval = null;
                }
                if (videoPlayer.paused) {
                    setStreamBadge(false, "IDLE (PRESS PLAY TO STREAM)");
                } else {
                    setStreamBadge(true, "PLAYBACK STREAMING (ACTIVE)");
                }
                showToast("Continuous simulation stopped", "info");
            }
        });
    }

    // --- Video Ingestion & Upload ---
    async function fetchVideosList() {
        try {
            const res = await fetch("/api/videos");
            const data = await res.json();
            videoSelect.innerHTML = "";
            data.videos.forEach(v => {
                const opt = document.createElement("option");
                opt.value = v.filename;
                opt.textContent = `${v.filename} (${v.size_mb} MB)`;
                videoSelect.appendChild(opt);
            });
        } catch (err) {
            console.error("Error fetching videos:", err);
        }
    }

    videoSelect.addEventListener("change", (e) => {
        const selected = e.target.value;
        videoPlayer.src = `/api/stream/${selected}`;
        videoPlayer.load();
        videoPlayer.play().catch(() => {});
        hudVideoName.textContent = selected;
        showToast(`Switched active stream to ${selected}`, "info");
    });

    btnBrowseFiles.addEventListener("click", () => videoFileInput.click());

    uploadDropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadDropzone.classList.add("dragover");
    });

    uploadDropzone.addEventListener("dragleave", () => {
        uploadDropzone.classList.remove("dragover");
    });

    uploadDropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadDropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    videoFileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    function handleFileUpload(file) {
        if (!file) return;
        const allowed = [".mp4", ".webm", ".mkv", ".mov"];
        const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
        if (!allowed.includes(ext)) {
            showToast("Invalid format! Please upload MP4, WEBM, or MKV video.", "warning");
            return;
        }

        uploadProgressContainer.style.display = "block";
        uploadFileName.textContent = file.name;
        uploadProgressBar.style.width = "0%";
        uploadPercent.textContent = "0%";

        const formData = new FormData();
        formData.append("file", file);

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/upload", true);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                uploadProgressBar.style.width = `${percent}%`;
                uploadPercent.textContent = `${percent}%`;
            }
        };

        xhr.onload = async () => {
            if (xhr.status === 200) {
                const res = JSON.parse(xhr.responseText);
                showToast(`Uploaded ${res.filename}! Ingested into cluster.`, "info");
                await fetchVideosList();
                videoSelect.value = res.filename;
                videoPlayer.src = `/api/stream/${res.filename}`;
                videoPlayer.load();
                videoPlayer.play().catch(() => {});
                hudVideoName.textContent = res.filename;
                setTimeout(() => {
                    uploadProgressContainer.style.display = "none";
                }, 2000);
            } else {
                showToast("Upload failed!", "warning");
            }
        };

        xhr.onerror = () => {
            showToast("Network error during upload!", "warning");
        };

        xhr.send(formData);
    }

    // --- Action Button Listeners ---
    btnBurst.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/action/burst", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ magnitude: 75.0 })
            });
            const data = await res.json();
            showToast(`Traffic Spike on Rack ${data.details.target_rack}! Cluster Entropy spiked to ${data.details.entropy_class}`, "warning");
        } catch (err) {
            console.error(err);
        }
    });

    btnRebalance.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/action/rebalance", { method: "POST" });
            const data = await res.json();
            const rebuilt = data.details.was_rebuilt;
            showToast(rebuilt ? "Reconstructed Hierarchical Tree (Alg 1)!" : "Aggregated In-Place Refresh complete.", "info");
        } catch (err) {
            console.error(err);
        }
    });

    btnSimulateStream.addEventListener("click", () => {
        showToast("Simulating 20 rapid stream chunk dispatches...", "info");
        let count = 0;
        const interval = setInterval(() => {
            dispatchNextStreamChunk();
            count++;
            if (count >= 20) clearInterval(interval);
        }, 120);
    });

    // --- Initialize ---
    fetchInitialState();
    initWebSocket();
    fetchVideosList();
});
