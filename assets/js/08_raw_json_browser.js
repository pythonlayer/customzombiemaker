        const RAW_JSON_FILE_OPTIONS = [
            'ZOMBIETYPES_UPDATED.json',
            'ZOMBIEPROPERTIES_UPDATED.json',
            'ZombieActions.json',
            'ARMORTYPES.json',
            'PROJECTILES.json',
            'PT.json'
        ];

        let rawBrowserInitialized = false;
        let rawCurrentFile = '';
        let rawLastSearchHit = -1;

        function setRawJsonStatus(message, isError) {
            const status = document.getElementById('rawJsonStatus');
            if (!status) return;
            status.textContent = message || '';
            status.style.color = isError ? '#ff9a9a' : '#999';
        }

        function setRawSearchInfo(message, isError) {
            const info = document.getElementById('rawJsonSearchInfo');
            if (!info) return;
            info.textContent = message || '';
            info.style.color = isError ? '#ff9a9a' : '#999';
        }

        function getRawSearchContext() {
            const viewer = document.getElementById('rawJsonViewer');
            const searchInput = document.getElementById('rawJsonSearchInput');
            const caseCheckbox = document.getElementById('rawJsonSearchCase');
            if (!viewer || !searchInput) return null;

            const query = searchInput.value || '';
            const source = viewer.value || '';
            const matchCase = !!caseCheckbox?.checked;
            const haystack = matchCase ? source : source.toLowerCase();
            const needle = matchCase ? query : query.toLowerCase();

            return { viewer, query, source, haystack, needle };
        }

        function countMatches(haystack, needle) {
            if (!needle) return 0;
            let count = 0;
            let start = 0;
            while (start <= haystack.length) {
                const idx = haystack.indexOf(needle, start);
                if (idx === -1) break;
                count++;
                start = idx + Math.max(needle.length, 1);
            }
            return count;
        }

        function countMatchesUntil(haystack, needle, endIndex) {
            if (!needle) return 0;
            let count = 0;
            let start = 0;
            while (start <= haystack.length) {
                const idx = haystack.indexOf(needle, start);
                if (idx === -1 || idx > endIndex) break;
                count++;
                start = idx + Math.max(needle.length, 1);
            }
            return count;
        }

        function scrollRawViewerToHit(viewer, hitIndex) {
            if (!viewer || hitIndex < 0) return;

            const before = viewer.value.slice(0, hitIndex);
            const line = before.split('\n').length - 1;
            let lineHeight = parseFloat(window.getComputedStyle(viewer).lineHeight);
            if (!lineHeight || Number.isNaN(lineHeight)) {
                lineHeight = 16;
            }

            const targetTop = Math.max((line * lineHeight) - (viewer.clientHeight / 2), 0);
            viewer.scrollTop = targetTop;
        }

        function lineNumberForIndex(text, hitIndex) {
            if (hitIndex < 0) return 0;
            return text.slice(0, hitIndex).split('\n').length;
        }

        function applyRawSearchHit(ctx, hit, total, focusViewer) {
            rawLastSearchHit = hit;
            ctx.viewer.setSelectionRange(hit, hit + ctx.query.length);
            scrollRawViewerToHit(ctx.viewer, hit);
            const current = countMatchesUntil(ctx.haystack, ctx.needle, hit);
            const line = lineNumberForIndex(ctx.source, hit);
            setRawSearchInfo(`${current}/${total} (line ${line})`, false);

            if (focusViewer) {
                ctx.viewer.focus();
            }
        }

        function updateRawSearchSummary() {
            const ctx = getRawSearchContext();
            if (!ctx) return;
            if (!ctx.query) {
                setRawSearchInfo('', false);
                rawLastSearchHit = -1;
                ctx.viewer.setSelectionRange(0, 0);
                return;
            }
            const total = countMatches(ctx.haystack, ctx.needle);
            if (total === 0) {
                setRawSearchInfo('No matches', true);
                rawLastSearchHit = -1;
                ctx.viewer.setSelectionRange(0, 0);
                return;
            }
            const firstHit = ctx.haystack.indexOf(ctx.needle);
            if (firstHit !== -1) {
                // Live auto-select while typing so users can instantly see where the hit is.
                applyRawSearchHit(ctx, firstHit, total, false);
                return;
            }
            setRawSearchInfo(`${total} match${total === 1 ? '' : 'es'}`, false);
        }

        function initRawJsonBrowser() {
            const select = document.getElementById('rawJsonFileSelect');
            if (!select || rawBrowserInitialized) return;

            select.innerHTML = '';
            RAW_JSON_FILE_OPTIONS.forEach(fileName => {
                const option = document.createElement('option');
                option.value = fileName;
                option.textContent = fileName;
                select.appendChild(option);
            });

            select.addEventListener('change', () => {
                loadRawJsonFile();
            });

            const searchInput = document.getElementById('rawJsonSearchInput');
            if (searchInput) {
                searchInput.addEventListener('input', () => {
                    rawLastSearchHit = -1;
                    updateRawSearchSummary();
                });
                searchInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        findInRawJson(e.shiftKey ? -1 : 1);
                    }
                });
            }

            const caseCheckbox = document.getElementById('rawJsonSearchCase');
            if (caseCheckbox) {
                caseCheckbox.addEventListener('change', () => {
                    rawLastSearchHit = -1;
                    updateRawSearchSummary();
                });
            }

            const viewer = document.getElementById('rawJsonViewer');
            if (viewer) {
                viewer.addEventListener('input', () => {
                    rawLastSearchHit = -1;
                    updateRawSearchSummary();
                });
                viewer.addEventListener('keydown', (e) => {
                    if (e.key.toLowerCase() === 'f' && (e.ctrlKey || e.metaKey)) {
                        const rawSearchInput = document.getElementById('rawJsonSearchInput');
                        if (rawSearchInput) {
                            e.preventDefault();
                            rawSearchInput.focus();
                            rawSearchInput.select();
                        }
                    }
                });
            }

            rawBrowserInitialized = true;
            setRawJsonStatus('Pick a file and click Load.', false);
        }

        async function loadRawJsonFile() {
            const select = document.getElementById('rawJsonFileSelect');
            const viewer = document.getElementById('rawJsonViewer');
            if (!select || !viewer) return;

            const fileName = select.value;
            if (!fileName) return;

            setRawJsonStatus(`Loading ${fileName}...`, false);

            try {
                const response = await fetch(fileName, { cache: 'no-store' });
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const rawText = await response.text();
                viewer.value = rawText;
                rawCurrentFile = fileName;
                rawLastSearchHit = -1;
                updateRawSearchSummary();
                setRawJsonStatus(`Loaded ${fileName} (${rawText.length.toLocaleString()} chars).`, false);
            } catch (error) {
                setRawJsonStatus(`Failed to load ${fileName}: ${error.message}`, true);
            }
        }

        function findInRawJson(direction) {
            const step = direction === -1 ? -1 : 1;
            const ctx = getRawSearchContext();
            if (!ctx) return;
            if (!ctx.query) {
                setRawSearchInfo('Type something to search', true);
                return;
            }

            const total = countMatches(ctx.haystack, ctx.needle);
            if (total === 0) {
                setRawSearchInfo('No matches', true);
                rawLastSearchHit = -1;
                return;
            }

            const from = step > 0
                ? Math.max(ctx.viewer.selectionEnd, 0)
                : Math.max(ctx.viewer.selectionStart - 1, 0);

            let hit = step > 0
                ? ctx.haystack.indexOf(ctx.needle, from)
                : ctx.haystack.lastIndexOf(ctx.needle, from);

            if (hit === -1) {
                hit = step > 0
                    ? ctx.haystack.indexOf(ctx.needle, 0)
                    : ctx.haystack.lastIndexOf(ctx.needle);
            }

            if (hit === -1) {
                setRawSearchInfo('No matches', true);
                rawLastSearchHit = -1;
                return;
            }

            applyRawSearchHit(ctx, hit, total, true);
        }

        function copyRawJsonViewer() {
            const viewer = document.getElementById('rawJsonViewer');
            if (!viewer || !viewer.value) {
                setRawJsonStatus('Nothing to copy.', true);
                return;
            }
            viewer.select();
            document.execCommand('copy');
            setRawJsonStatus('Copied raw JSON.', false);
        }

        function downloadRawJsonViewer() {
            const viewer = document.getElementById('rawJsonViewer');
            if (!viewer || !viewer.value) {
                setRawJsonStatus('Nothing to download.', true);
                return;
            }

            const fileName = rawCurrentFile || 'raw-json.json';
            const blob = new Blob([viewer.value], { type: 'application/json;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement('a');
            anchor.href = url;
            anchor.download = fileName;
            document.body.appendChild(anchor);
            anchor.click();
            document.body.removeChild(anchor);
            URL.revokeObjectURL(url);
            setRawJsonStatus(`Downloaded ${fileName}.`, false);
        }

        function onRawTabOpened() {
            initRawJsonBrowser();
            const viewer = document.getElementById('rawJsonViewer');
            if (viewer && !viewer.value.trim()) {
                loadRawJsonFile();
                return;
            }
            updateRawSearchSummary();
        }
