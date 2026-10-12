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
    const btnSimulateDropdownToggle = document.getElementById("btnSimulateDropdownToggle");
    const simulateDropdownMenu = document.getElementById("simulateDropdownMenu");
    const btnSimulateLabel = document.getElementById("btnSimulateLabel");
    const activeModeLabel = document.getElementById("activeModeLabel");
    const policyTableBody = document.getElementById("policyTableBody");
    let currentActivePolicy = "hierarchical";

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

    // Progressive Disclosure Tree Controls & Inspector Elements
    const viewModeTabs = document.getElementById("viewModeTabs");
    const inspectorLevelBadge = document.getElementById("inspectorLevelBadge");
    const inspectorNodeName = document.getElementById("inspectorNodeName");
    const inspectorParentRef = document.getElementById("inspectorParentRef");
    const inspectorChildrenRef = document.getElementById("inspectorChildrenRef");
    const inspectorMinLoad = document.getElementById("inspectorMinLoad");
    const inspectorMaxLoad = document.getElementById("inspectorMaxLoad");
    const inspectorBoundsRange = document.getElementById("inspectorBoundsRange");
    const inspectorHVar = document.getElementById("inspectorHVar");
    const inspectorHShannon = document.getElementById("inspectorHShannon");
    const inspectorEntropyBadge = document.getElementById("inspectorEntropyBadge");
    const inspectorCpuVal = document.getElementById("inspectorCpuVal");
    const inspectorCpuBar = document.getElementById("inspectorCpuBar");
    const inspectorMemVal = document.getElementById("inspectorMemVal");
    const inspectorMemBar = document.getElementById("inspectorMemBar");
    const inspectorNetVal = document.getElementById("inspectorNetVal");
    const inspectorNetBar = document.getElementById("inspectorNetBar");
    const inspectorDiskVal = document.getElementById("inspectorDiskVal");
    const inspectorDiskBar = document.getElementById("inspectorDiskBar");

    let currentTreeMode = "topology";
    let selectedNodeTarget = { type: "root", id: "root" };

    if (viewModeTabs) {
        viewModeTabs.querySelectorAll(".mode-tab").forEach(tab => {
            tab.addEventListener("click", () => {
                viewModeTabs.querySelectorAll(".mode-tab").forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                currentTreeMode = tab.dataset.mode || "topology";
                if (clusterState) renderClusterTreeSvg(clusterState);
            });
        });
    }

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
        updateInspectorHUD(selectedNodeTarget.type, selectedNodeTarget.id, state);

        // Render Real-Time Policy Comparison Table (All 6 Baselines)
        if (state.policy_comparison_table) {
            renderPolicyComparisonTable(state.policy_comparison_table, state.active_algorithm);
        }
        if (state.active_algorithm && state.active_algorithm !== currentActivePolicy) {
            syncActivePolicyUI(state.active_algorithm, state.active_policy_name);
        }
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

    // --- Progressive Disclosure Inspector & SVG Hierarchical Tree ---
    function updateInspectorHUD(type, id, state) {
        if (!state) return;

        if (type === "root" || id === "root") {
            if (inspectorLevelBadge) inspectorLevelBadge.textContent = "LEVEL 0 • CLUSTER ROOT";
            if (inspectorNodeName) inspectorNodeName.textContent = "ClusterRoot";
            if (inspectorParentRef) inspectorParentRef.innerHTML = 'Parent: <span class="text-muted">None (Partition Root)</span>';
            
            const childChips = [0, 1, 2, 3].map(rid => 
                `<span class="chip-child" onclick="window.__selectTreeNode('rack', ${rid})">R${rid}</span>`
            ).join(" ");
            if (inspectorChildrenRef) inspectorChildrenRef.innerHTML = `Children: ${childChips}`;

            const minL = state.root.min_load !== undefined ? state.root.min_load : (state.root.min_cpu || 0);
            const maxL = state.root.max_cpu !== undefined ? state.root.max_cpu : (state.root.avg_cpu || 0);
            if (inspectorMinLoad) inspectorMinLoad.textContent = `${minL}%`;
            if (inspectorMaxLoad) inspectorMaxLoad.textContent = `${maxL}%`;
            if (inspectorBoundsRange) {
                inspectorBoundsRange.style.left = `${Math.min(85, minL)}%`;
                inspectorBoundsRange.style.width = `${Math.max(8, Math.min(100 - minL, maxL - minL))}%`;
            }

            const avgVar = state.nodes ? (state.nodes.reduce((a, b) => a + (b.variance || 0), 0) / state.nodes.length).toFixed(2) : "0.0";
            if (inspectorHVar) inspectorHVar.textContent = avgVar;
            if (inspectorHShannon) inspectorHShannon.textContent = `${(state.entropy.shannon || 0).toFixed(3)} bits`;
            if (inspectorEntropyBadge) {
                const cls = state.entropy.classification || "LOW";
                inspectorEntropyBadge.textContent = `${cls} REGIME (ENTROPY)`;
                inspectorEntropyBadge.className = `entropy-status-pill status-badge ${cls === 'HIGH' ? 'badge-volatile' : cls === 'MEDIUM' ? 'badge-transitional' : 'badge-stable'}`;
            }

            setMetricBars(
                state.root.avg_cpu || 0,
                state.root.avg_mem || 0,
                state.root.avg_net || 2.4,
                state.root.avg_disk || 1.8
            );
        } else if (type === "rack") {
            const rackId = parseInt(id, 10);
            const rack = (state.racks && state.racks.find(r => r.rack_id === rackId)) || {
                rack_id: rackId, avg_cpu: 0, avg_mem: 0, avg_net: 1.0, avg_disk: 1.0, min_load: 0, max_cpu: 0
            };
            if (inspectorLevelBadge) inspectorLevelBadge.textContent = "LEVEL 1 • RACK AGGREGATOR";
            if (inspectorNodeName) inspectorNodeName.textContent = `Rack_${rackId}`;
            if (inspectorParentRef) inspectorParentRef.innerHTML = 'Parent: <span class="chip-child" onclick="window.__selectTreeNode(\'root\', \'root\')">ClusterRoot</span>';

            const rackNodes = (state.nodes || []).filter(n => (n.rack_id !== undefined ? n.rack_id === rackId : Math.floor(n.node_id / 4) === rackId));
            const childChips = rackNodes.map(n => 
                `<span class="chip-child" onclick="window.__selectTreeNode('node', ${n.node_id})">N${n.node_id}</span>`
            ).join(" ") || `<span class="chip-child" onclick="window.__selectTreeNode('node', ${rackId * 4})">N${rackId * 4}</span>`;
            if (inspectorChildrenRef) inspectorChildrenRef.innerHTML = `Children: ${childChips}`;

            const minL = rack.min_load !== undefined ? rack.min_load : (rack.min_cpu || 0);
            const maxL = rack.max_cpu !== undefined ? rack.max_cpu : (rack.avg_cpu || 0);
            if (inspectorMinLoad) inspectorMinLoad.textContent = `${minL}%`;
            if (inspectorMaxLoad) inspectorMaxLoad.textContent = `${maxL}%`;
            if (inspectorBoundsRange) {
                inspectorBoundsRange.style.left = `${Math.min(85, minL)}%`;
                inspectorBoundsRange.style.width = `${Math.max(8, Math.min(100 - minL, maxL - minL))}%`;
            }

            const rackVar = rackNodes.length ? (rackNodes.reduce((a, b) => a + (b.variance || 0), 0) / rackNodes.length).toFixed(2) : "0.0";
            if (inspectorHVar) inspectorHVar.textContent = rackVar;
            if (inspectorHShannon) inspectorHShannon.textContent = `${((state.entropy.shannon || 0) * 0.9).toFixed(3)} bits`;
            if (inspectorEntropyBadge) {
                const eCls = parseFloat(rackVar) > 50 ? "HIGH" : parseFloat(rackVar) > 15 ? "MEDIUM" : "LOW";
                inspectorEntropyBadge.textContent = `${eCls} REGIME (ENTROPY)`;
                inspectorEntropyBadge.className = `entropy-status-pill status-badge ${eCls === 'HIGH' ? 'badge-volatile' : eCls === 'MEDIUM' ? 'badge-transitional' : 'badge-stable'}`;
            }

            setMetricBars(
                rack.avg_cpu || 0,
                rack.avg_mem || 0,
                rack.avg_net || 1.0,
                rack.avg_disk || 1.0
            );
        } else if (type === "node") {
            const nodeId = parseInt(id, 10);
            const node = (state.nodes && state.nodes.find(n => n.node_id === nodeId)) || {
                node_id: nodeId, rack_id: Math.floor(nodeId / 4), cpu: 0, mem: 0, net: 0, disk: 0, variance: 0, entropy_class: "LOW", composite_load: 0
            };
            if (inspectorLevelBadge) inspectorLevelBadge.textContent = "LEVEL 2 • COMPUTE NODE (LEAF)";
            if (inspectorNodeName) inspectorNodeName.textContent = `ComputeNode_${nodeId}`;
            if (inspectorParentRef) inspectorParentRef.innerHTML = `Parent: <span class="chip-child" onclick="window.__selectTreeNode('rack', ${node.rack_id})">Rack_${node.rack_id}</span>`;
            if (inspectorChildrenRef) inspectorChildrenRef.innerHTML = 'Children: <span class="text-muted">None (Physical Leaf)</span>';

            const compL = node.composite_load !== undefined ? node.composite_load : node.cpu;
            if (inspectorMinLoad) inspectorMinLoad.textContent = `${compL}% (Score)`;
            if (inspectorMaxLoad) inspectorMaxLoad.textContent = `${node.cpu}% (CPU)`;
            if (inspectorBoundsRange) {
                inspectorBoundsRange.style.left = `${Math.min(85, compL)}%`;
                inspectorBoundsRange.style.width = `15%`;
            }

            if (inspectorHVar) inspectorHVar.textContent = node.variance;
            if (inspectorHShannon) inspectorHShannon.textContent = `${(node.shannon || 0.42).toFixed(3)} bits`;
            if (inspectorEntropyBadge) {
                inspectorEntropyBadge.textContent = `${node.entropy_class} STABILITY`;
                inspectorEntropyBadge.className = `entropy-status-pill status-badge ${node.entropy_class === 'HIGH' ? 'badge-volatile' : node.entropy_class === 'MEDIUM' ? 'badge-transitional' : 'badge-stable'}`;
            }

            setMetricBars(node.cpu || 0, node.mem || 0, node.net || 0, node.disk || 0);
        }
    }

    function setMetricBars(cpu, mem, net, disk) {
        if (inspectorCpuVal) inspectorCpuVal.textContent = `${Math.round(cpu)}%`;
        if (inspectorCpuBar) inspectorCpuBar.style.width = `${Math.min(100, Math.round(cpu))}%`;

        if (inspectorMemVal) inspectorMemVal.textContent = `${Math.round(mem)}%`;
        if (inspectorMemBar) inspectorMemBar.style.width = `${Math.min(100, Math.round(mem))}%`;

        if (inspectorNetVal) inspectorNetVal.textContent = `${(net || 0).toFixed(1)} MB/s`;
        if (inspectorNetBar) inspectorNetBar.style.width = `${Math.min(100, Math.round((net / 30) * 100))}%`;

        if (inspectorDiskVal) inspectorDiskVal.textContent = `${(disk || 0).toFixed(1)} MB/s`;
        if (inspectorDiskBar) inspectorDiskBar.style.width = `${Math.min(100, Math.round((disk / 20) * 100))}%`;
    }

    window.__selectTreeNode = function(type, id) {
        selectedNodeTarget = { type, id };
        if (clusterState) {
            renderClusterTreeSvg(clusterState);
            updateInspectorHUD(type, id, clusterState);
        }
    };

    // --- Render SVG Hierarchical Tree with Progressive Disclosure ---
    function renderClusterTreeSvg(state) {
        const rootPos = { x: 450, y: 45 };
        const rackPositions = [
            { id: 0, x: 130, y: 160 },
            { id: 1, x: 340, y: 160 },
            { id: 2, x: 560, y: 160 },
            { id: 3, x: 770, y: 160 }
        ];

        let linksHtml = "";
        let nodesHtml = "";

        // Links from Root to Racks (Pointers to Children Level 0 -> Level 1)
        rackPositions.forEach(rack => {
            linksHtml += `
                <line id="link_root_rack_${rack.id}" class="tree-link" 
                      x1="${rootPos.x}" y1="${rootPos.y + 18}" 
                      x2="${rack.x}" y2="${rack.y - 18}" />
            `;
        });

        // Compute Node positions (Pointers to Children Level 1 -> Level 2)
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
                const nodeY = 325;
                nodePositions.push({ id: node.node_id, rackId: rack.id, x: nodeX, y: nodeY, data: node });

                linksHtml += `
                    <line id="link_rack_${rack.id}_node_${node.node_id}" class="tree-link" 
                          x1="${rack.x}" y1="${rack.y + 18}" 
                          x2="${nodeX}" y2="${nodeY - 14}" />
                `;
            });
        });

        const isLight = document.documentElement.getAttribute("data-theme") === "light";
        const nodeFill = isLight ? "#ffffff" : "#1e293b";
        const leafFill = isLight ? "#f8fafc" : "#0f172a";

        // Draw Root Node (Level 0)
        const isRootSelected = selectedNodeTarget.type === "root" ? "node-selected" : "";
        const rootCpu = state.root.avg_cpu || 0;
        const rootMin = state.root.min_load !== undefined ? state.root.min_load : (state.root.min_cpu || 0);
        const rootMax = state.root.max_cpu !== undefined ? state.root.max_cpu : (state.root.avg_cpu || 0);

        let rootSubLabel = `Avg ${rootCpu}%`;
        if (currentTreeMode === "bounds") {
            rootSubLabel = `Min ${rootMin}% • Max ${rootMax}%`;
        } else if (currentTreeMode === "multires") {
            rootSubLabel = `C:${rootCpu}% M:${state.root.avg_mem || 0}%`;
        } else if (currentTreeMode === "entropy") {
            rootSubLabel = `${state.entropy.classification} REGIME`;
        }

        nodesHtml += `
            <g id="svg_node_root" class="tree-node-group ${isRootSelected}" onclick="window.__selectTreeNode('root', 'root')">
                <circle cx="${rootPos.x}" cy="${rootPos.y}" r="22" fill="${nodeFill}" stroke="var(--blue)" stroke-width="2.5" class="tree-node-circle" />
                <text x="${rootPos.x}" y="${rootPos.y + 4}" class="tree-node-text">ROOT</text>
                <text x="${rootPos.x}" y="${rootPos.y + 36}" class="tree-node-subtext" fill="${currentTreeMode === 'bounds' ? 'var(--cyan)' : 'var(--text-secondary)'}">${rootSubLabel}</text>
            </g>
        `;

        // Draw Rack Nodes (Level 1)
        rackPositions.forEach(rack => {
            const isRackSelected = (selectedNodeTarget.type === "rack" && selectedNodeTarget.id == rack.id) ? "node-selected" : "";
            const rData = (state.racks && state.racks.find(r => r.rack_id === rack.id)) || { avg_cpu: 0, min_load: 0, max_cpu: 0 };
            const rMin = rData.min_load !== undefined ? rData.min_load : 0;
            const rMax = rData.max_cpu !== undefined ? rData.max_cpu : rData.avg_cpu;

            let rackStroke = rData.avg_cpu > 70 ? "var(--rose)" : rData.avg_cpu > 40 ? "var(--amber)" : "var(--violet)";
            let rackSubLabel = `${rData.avg_cpu}%`;

            if (currentTreeMode === "bounds") {
                rackSubLabel = `[${rMin}% ➔ ${rMax}%]`;
            } else if (currentTreeMode === "multires") {
                rackSubLabel = `C:${rData.avg_cpu}% M:${rData.avg_mem || 0}%`;
            } else if (currentTreeMode === "entropy") {
                const rNodes = state.nodes.filter(n => n.rack_id === rack.id);
                const rAvgVar = rNodes.length ? rNodes.reduce((a,b)=>a+b.variance,0)/rNodes.length : 0;
                rackStroke = rAvgVar > 50 ? "var(--rose)" : rAvgVar > 15 ? "var(--amber)" : "var(--emerald)";
                rackSubLabel = rAvgVar > 50 ? "VOLATILE" : rAvgVar > 15 ? "TRANS" : "STABLE";
            }

            nodesHtml += `
                <g id="svg_node_rack_${rack.id}" class="tree-node-group ${isRackSelected}" onclick="window.__selectTreeNode('rack', ${rack.id})">
                    <circle cx="${rack.x}" cy="${rack.y}" r="17" fill="${nodeFill}" stroke="${rackStroke}" stroke-width="2" class="tree-node-circle" />
                    <text x="${rack.x}" y="${rack.y + 4}" class="tree-node-text">R${rack.id}</text>
                    <text x="${rack.x}" y="${rack.y + 28}" class="tree-node-subtext" fill="${currentTreeMode === 'bounds' ? 'var(--cyan)' : 'var(--text-secondary)'}">${rackSubLabel}</text>
                </g>
            `;
        });

        // Draw Compute Nodes (Level 2 - Leaves)
        nodePositions.forEach(node => {
            const isNodeSelected = (selectedNodeTarget.type === "node" && selectedNodeTarget.id == node.id) ? "node-selected" : "";
            const cpu = node.data.cpu || 0;
            let nodeStroke = cpu > 75 ? "var(--rose)" : cpu > 45 ? "var(--amber)" : "var(--emerald)";
            let nodeSubLabel = `${Math.round(cpu)}%`;

            if (currentTreeMode === "bounds") {
                nodeSubLabel = `L:${Math.round(node.data.composite_load || cpu)}%`;
            } else if (currentTreeMode === "multires") {
                nodeSubLabel = `${Math.round(cpu)}|${Math.round(node.data.mem || 0)}`;
            } else if (currentTreeMode === "entropy") {
                const eCls = node.data.entropy_class || "LOW";
                nodeStroke = eCls === "HIGH" ? "var(--rose)" : eCls === "MEDIUM" ? "var(--amber)" : "var(--emerald)";
                nodeSubLabel = eCls.substring(0, 3);
            }

            nodesHtml += `
                <g id="svg_node_compute_${node.id}" class="tree-node-group ${isNodeSelected}" onclick="window.__selectTreeNode('node', ${node.id})">
                    <circle id="node_circle_${node.id}" cx="${node.x}" cy="${node.y}" r="12" fill="${leafFill}" stroke="${nodeStroke}" stroke-width="2" class="tree-node-circle" />
                    <text x="${node.x}" y="${node.y + 3}" class="tree-node-text" style="font-size: 8px;">N${node.id}</text>
                    <text x="${node.x}" y="${node.y + 22}" class="tree-node-subtext" style="font-size: 7.5px;">${nodeSubLabel}</text>
                </g>
            `;
        });

        treeSvg.innerHTML = `<g id="treeLinks">${linksHtml}</g><g id="treeNodes">${nodesHtml}</g>`;

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
        const polIcon = event.policy_icon || "⚡";
        const polName = event.policy_name || "Proposed Tree";
        const latTime = event.dispatch_latency_us !== undefined ? event.dispatch_latency_us : event.tree_time_us;
        const logLine = `[${polIcon} ${polName}] Chunk #${event.chunk_index} ➔ Node_${event.assigned_node_id} (Rack_${event.assigned_rack_id}) | Latency: ${latTime} µs | Tree: ${event.tree_time_us} µs (${event.speedup_ratio}x) | Flat: ${event.lln_time_us} µs | H(S): ${event.cluster_entropy}`;
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

    async function dispatchNextStreamChunk(overridePolicy = null) {
        currentPlaybackChunkIndex++;
        const vid = videoSelect.value || "demo_stream.mp4";
        try {
            const payload = {
                video_name: vid,
                chunk_index: currentPlaybackChunkIndex,
                byte_size: 256 * 1024,
                policy: overridePolicy || currentActivePolicy
            };
            const res = await fetch("/api/stream/dispatch_chunk", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
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

    // =========================================================================
    // --- Pure Simulation Policies & Real-Time Comparison Table Logic ---
    // =========================================================================

    const policyLabels = {
        "hierarchical": "Simulate Traffic (P9 Tree)",
        "round_robin": "Simulate Traffic (Round-Robin)",
        "least_loaded": "Simulate Traffic (Least-Loaded)",
        "work_queue": "Simulate Traffic (Work Queue)",
        "random": "Simulate Traffic (Random)",
        "work_stealing": "Simulate Traffic (Work Stealing)"
    };

    const policyFullNames = {
        "hierarchical": "Proposed P9 Tree",
        "round_robin": "Round-Robin (RR)",
        "least_loaded": "Least-Loaded Node (LLN)",
        "work_queue": "Work Queue",
        "random": "Random",
        "work_stealing": "Work Stealing"
    };

    function syncActivePolicyUI(policyKey, customName = null) {
        currentActivePolicy = policyKey;
        if (btnSimulateLabel) {
            btnSimulateLabel.textContent = policyLabels[policyKey] || `Simulate Traffic (${policyKey})`;
        }
        if (activeModeLabel) {
            activeModeLabel.textContent = customName || policyFullNames[policyKey] || policyKey;
        }
        document.querySelectorAll(".dropdown-item").forEach(item => {
            item.classList.toggle("active", item.getAttribute("data-policy") === policyKey);
        });
    }

    function renderPolicyComparisonTable(tableData, activeAlg) {
        if (!tableData || !Array.isArray(tableData)) return;

        tableData.forEach(p => {
            const row = document.getElementById(`row-${p.key}`);
            if (!row) return;

            const isRowActive = p.key === activeAlg;
            row.classList.toggle("row-active", isRowActive);

            // Update active badge in title
            const titleWrap = row.querySelector(".policy-title-wrap");
            if (titleWrap) {
                let activeBadge = titleWrap.querySelector(".badge-active-live");
                if (isRowActive && !activeBadge) {
                    activeBadge = document.createElement("span");
                    activeBadge.className = "badge-active-live";
                    activeBadge.textContent = "ACTIVE";
                    titleWrap.appendChild(activeBadge);
                } else if (!isRowActive && activeBadge) {
                    activeBadge.remove();
                }
            }

            // Avg Decision Latency
            const latEl = document.getElementById(`lat-${p.key}`);
            if (latEl) {
                const formattedLat = Number(p.avg_latency_us).toFixed(1);
                if (latEl.textContent !== formattedLat) {
                    latEl.textContent = formattedLat;
                    latEl.parentElement.classList.add("cell-flash");
                    setTimeout(() => latEl.parentElement.classList.remove("cell-flash"), 600);
                }
            }

            // CPU Variance
            const varEl = document.getElementById(`var-${p.key}`);
            if (varEl) {
                const formattedVar = Number(p.variance).toFixed(1);
                if (varEl.textContent !== formattedVar) {
                    varEl.textContent = formattedVar;
                }
            }

            // Jain's Fairness & Mini Bar
            const jainEl = document.getElementById(`jain-${p.key}`);
            const barEl = document.getElementById(`bar-${p.key}`);
            if (jainEl) {
                const jainScore = Number(p.jain_fairness);
                jainEl.textContent = jainScore.toFixed(3);
                
                let colorClass = "fill-emerald";
                let textClass = "text-emerald";
                if (jainScore < 0.75) {
                    colorClass = "fill-rose";
                    textClass = "text-rose";
                } else if (jainScore < 0.82) {
                    colorClass = "fill-amber";
                    textClass = "text-amber";
                } else if (jainScore < 0.92) {
                    colorClass = "fill-cyan";
                    textClass = "text-cyan";
                }
                jainEl.className = `val-fairness ${textClass}`;

                if (barEl) {
                    barEl.style.width = `${Math.min(100, Math.max(5, jainScore * 100))}%`;
                    barEl.className = `mini-bar-fill ${colorClass}`;
                }
            }

            // Dispatches Counter
            const dispEl = document.getElementById(`disp-${p.key}`);
            if (dispEl) {
                dispEl.textContent = p.dispatches || 0;
            }

            // Run Pure button state
            const runBtn = row.querySelector(".btn-pure-run");
            if (runBtn) {
                if (isRowActive) {
                    runBtn.className = "btn btn-xs btn-pure-run btn-accent";
                    runBtn.textContent = "Active Mode";
                } else {
                    runBtn.className = "btn btn-xs btn-pure-run btn-outline";
                    runBtn.textContent = "Run Pure";
                }
            }
        });
    }

    async function setActivePolicy(policyKey, shouldSimulateBurst = true) {
        syncActivePolicyUI(policyKey);
        try {
            const res = await fetch("/api/action/set_policy", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ policy: policyKey })
            });
            if (res.ok) {
                const data = await res.json();
                if (shouldSimulateBurst) {
                    simulatePureTraffic(policyKey, 20);
                } else {
                    showToast(`Activated ${data.active_policy_name || policyKey} mode`, "info");
                }
            }
        } catch (e) {
            console.error("Failed to switch policy:", e);
            if (shouldSimulateBurst) {
                simulatePureTraffic(policyKey, 20);
            }
        }
    }

    async function simulatePureTraffic(policyKey, count = 20) {
        const policyName = policyFullNames[policyKey] || policyKey;
        showToast(`Simulating ${count} chunks in pure ${policyName} mode...`, "info");

        try {
            const vid = videoSelect.value || "demo_stream.mp4";
            const res = await fetch("/api/action/simulate_traffic", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ count, policy: policyKey, video_name: vid })
            });
            if (res.ok) {
                const data = await res.json();
                if (data.last_event && (!ws || ws.readyState !== WebSocket.OPEN)) {
                    handleChunkDispatched(data.last_event);
                }
            }
        } catch (e) {
            console.warn("REST simulation failed, falling back to client dispatch loop:", e);
            let c = 0;
            const interval = setInterval(() => {
                dispatchNextStreamChunk(policyKey);
                c++;
                if (c >= count) clearInterval(interval);
            }, 100);
        }
    }

    // Toggle Dropdown Menu
    if (btnSimulateDropdownToggle && simulateDropdownMenu) {
        btnSimulateDropdownToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            const isOpen = simulateDropdownMenu.classList.contains("show");
            simulateDropdownMenu.classList.toggle("show", !isOpen);
            btnSimulateDropdownToggle.setAttribute("aria-expanded", String(!isOpen));
        });

        // Close dropdown when clicking anywhere outside
        document.addEventListener("click", (e) => {
            if (!simulateDropdownMenu.contains(e.target) && e.target !== btnSimulateDropdownToggle) {
                simulateDropdownMenu.classList.remove("show");
                btnSimulateDropdownToggle.setAttribute("aria-expanded", "false");
            }
        });

        // Dropdown Items click listener
        document.querySelectorAll(".dropdown-item").forEach(item => {
            item.addEventListener("click", () => {
                const pol = item.getAttribute("data-policy");
                if (pol) {
                    simulateDropdownMenu.classList.remove("show");
                    btnSimulateDropdownToggle.setAttribute("aria-expanded", "false");
                    setActivePolicy(pol, true);
                }
            });
        });
    }

    // Main Dropdown Action Button (Simulate 20 chunks with current active policy)
    btnSimulateStream.addEventListener("click", () => {
        simulatePureTraffic(currentActivePolicy, 20);
    });

    // Delegate "Run Pure" buttons inside the Comparison Table
    if (policyTableBody) {
        policyTableBody.addEventListener("click", (e) => {
            const btn = e.target.closest(".btn-pure-run");
            if (btn) {
                const pol = btn.getAttribute("data-policy");
                if (pol) {
                    setActivePolicy(pol, true);
                }
            }
        });
    }

    // --- Initialize ---
    fetchInitialState();
    initWebSocket();
    fetchVideosList();
});
