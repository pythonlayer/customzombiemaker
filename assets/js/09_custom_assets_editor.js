        let customArmorEntries = [];
        let customProjectileEntries = [];
        let selectedCustomArmorIndex = -1;
        let selectedCustomProjectileIndex = -1;

        function deepCloneAsset(value) {
            return JSON.parse(JSON.stringify(value));
        }

        function sanitizeEntryAlias(raw, fallback) {
            const base = String(raw || '').trim().replace(/\s+/g, '_');
            if (base) return base;
            return fallback || 'NewEntry';
        }

        function getEntryAlias(entry, fallback) {
            if (!entry || !Array.isArray(entry.aliases) || !entry.aliases[0]) return fallback || 'Entry';
            return String(entry.aliases[0]);
        }

        const projectileGuidanceComments = Object.freeze({
            '#comment CollisionFlags': 'none, ground_zombies, off_ground_zombies, dying_zombies, griditems, plants, ground, all_zombies, everything',
            '#comment DamageFlags': 'none, bypass_shield, hits_shield_and_body, hits_only_shield, lightning, no_flash, doesnt_leave_body, fire, rolling, lobbed, shooter',
            '#comment DamageFlags Rules': " 'shooter' and 'catapult' should be mutually exclusive. 'lobbed' and 'shooter' can coexist, or not. 'catapult' should be a strict subset of 'lobbed'.",
            '#comment DamageFlags Examples': 'See bloomerang (lobbed, shooter), banana (lobbed only), cabbagepult (lobbed, catapult), and peashooter (shooter only) for examples.',
            '#comment ImpactOffset': 'This ImpactOffset affects both the particle and the PAM'
        });

        function ensureProjectileGuidanceComments(objdata) {
            if (!objdata || typeof objdata !== 'object' || Array.isArray(objdata)) return;
            Object.entries(projectileGuidanceComments).forEach(([key, value]) => {
                if (objdata[key] === undefined || objdata[key] === null || objdata[key] === '') {
                    objdata[key] = value;
                }
            });
        }

        function reorderProjectileGuidanceComments(objdata) {
            if (!objdata || typeof objdata !== 'object' || Array.isArray(objdata)) return;
            const orderedKeys = [
                'BaseDamage',
                'HealAmount',
                'SplashDamage',
                'SplashRadius',
                'ShakeBoardOnSplash',
                'CollisionFlags',
                '#comment CollisionFlags',
                'DamageFlags',
                '#comment DamageFlags',
                '#comment DamageFlags Rules',
                '#comment DamageFlags Examples',
                'DiesOnImpact',
                'InitialVelocity',
                'InitialAcceleration',
                'InitialVelocityScale',
                'InitialHeight',
                'InitialRotation',
                'InitialAngularVelocity',
                'InitialScale',
                'AttachedPAM',
                'AttachedPAMAnimRigClass',
                'AttachedPAMOffset',
                'AttachedPAMAnimationToPlay',
                'RenderImage',
                'CollisionRect',
                'ImpactSoundEvent',
                'ImpactSoundThrottleTimer',
                'ImpactPAM',
                'ImpactPAMAnimationToPlay',
                'ImpactOffset',
                '#comment ImpactOffset'
            ];

            const reordered = {};
            orderedKeys.forEach(key => {
                if (Object.prototype.hasOwnProperty.call(objdata, key)) {
                    reordered[key] = objdata[key];
                }
            });

            Object.keys(objdata).forEach(key => {
                if (!Object.prototype.hasOwnProperty.call(reordered, key)) {
                    reordered[key] = objdata[key];
                }
            });

            Object.keys(objdata).forEach(key => delete objdata[key]);
            Object.assign(objdata, reordered);
        }

        function resolveReferenceAlias(rawValue, refs) {
            const raw = String(rawValue || '').trim();
            if (!raw) return '__template__';
            const lower = raw.toLowerCase();
            if (lower === '__template__' || lower === 'template' || lower === 'template (recommended)') {
                return '__template__';
            }

            const entries = Array.isArray(refs) ? refs : [];
            const exact = entries.find(r => String(r.alias || '').toLowerCase() === lower);
            if (exact) return exact.alias;
            const startsWith = entries.find(r => String(r.alias || '').toLowerCase().startsWith(lower));
            if (startsWith) return startsWith.alias;
            const includes = entries.find(r => String(r.alias || '').toLowerCase().includes(lower));
            if (includes) return includes.alias;
            return '__template__';
        }

        function collectProjectileStringFieldOptions(fieldNames, maxItems) {
            const refs = getProjectileReferenceEntries();
            const fields = Array.isArray(fieldNames) ? fieldNames : [];
            const sets = {};
            fields.forEach(field => {
                sets[field] = new Set();
            });

            refs.forEach(ref => {
                const data = ref?.obj?.objdata || {};
                fields.forEach(field => {
                    const value = data[field];
                    if (typeof value === 'string' && value.trim()) {
                        sets[field].add(value.trim());
                    }
                });
            });

            const limit = Number.isFinite(Number(maxItems)) ? Number(maxItems) : 400;
            const output = {};
            fields.forEach(field => {
                output[field] = Array.from(sets[field]).sort((a, b) => a.localeCompare(b)).slice(0, limit);
            });
            return output;
        }

        function initCustomAssetEditors() {
            if (!armorTemplateObject) {
                armorTemplateObject = getDefaultArmorTemplateObject();
            }
            if (!projectileTemplateObject) {
                projectileTemplateObject = getDefaultProjectileTemplateObject();
            }

            if (!Array.isArray(armorTypeOptions) || armorTypeOptions.length === 0) {
                extractArmorReferenceData();
            }
            if (!Array.isArray(projectileCollisionFlags) || projectileCollisionFlags.length === 0) {
                extractProjectileReferenceData();
            }

            const editor = document.getElementById('editorContainer');
            if (editor) {
                editor.classList.remove('hidden');
            }

            buildCustomArmorTab();
            buildCustomProjectileTab();
            if (!selectedZombie && typeof switchTab === 'function') {
                switchTab('armor');
            }
        }

        function getArmorReferenceEntries() {
            const refs = (allArmorSheets || []).filter(obj => {
                const cls = String(obj?.objclass || '').toLowerCase();
                return cls.includes('armorpropertysheet') && !cls.includes('utils');
            });

            const map = new Map();
            refs.forEach(obj => {
                const alias = getEntryAlias(obj, '');
                if (!alias) return;
                if (!map.has(alias)) {
                    map.set(alias, obj);
                }
            });
            return Array.from(map.entries()).map(([alias, obj]) => ({ alias, obj }));
        }

        function getProjectileReferenceEntries() {
            const refs = (allProjectileSheets || []).filter(obj => {
                const cls = String(obj?.objclass || '').toLowerCase();
                return cls.includes('projectilepropertysheet');
            });

            const map = new Map();
            refs.forEach(obj => {
                const alias = getEntryAlias(obj, '');
                if (!alias) return;
                if (!map.has(alias)) {
                    map.set(alias, obj);
                }
            });
            return Array.from(map.entries()).map(([alias, obj]) => ({ alias, obj }));
        }

        function makeUniqueArmorAlias(baseAlias) {
            const existing = new Set(customArmorEntries.map(e => getEntryAlias(e, '')));
            if (!existing.has(baseAlias)) return baseAlias;
            let i = 2;
            let candidate = `${baseAlias}_${i}`;
            while (existing.has(candidate)) {
                i++;
                candidate = `${baseAlias}_${i}`;
            }
            return candidate;
        }

        function makeUniqueProjectileAlias(baseAlias) {
            const existing = new Set(customProjectileEntries.map(e => getEntryAlias(e, '')));
            if (!existing.has(baseAlias)) return baseAlias;
            let i = 2;
            let candidate = `${baseAlias}_${i}`;
            while (existing.has(candidate)) {
                i++;
                candidate = `${baseAlias}_${i}`;
            }
            return candidate;
        }

        function normalizeArmorEntry(entry) {
            if (!entry || typeof entry !== 'object') return;
            if (!Array.isArray(entry.aliases) || entry.aliases.length === 0) {
                entry.aliases = ['CustomArmor'];
            }
            if (!entry.objclass) {
                entry.objclass = 'ArmorPropertySheet';
            }
            if (!entry.objdata || typeof entry.objdata !== 'object') {
                entry.objdata = {};
            }

            const objdata = entry.objdata;
            if (typeof objdata.ArmorType !== 'string') objdata.ArmorType = 'Unknown';
            if (objdata.BaseHealth === undefined || objdata.BaseHealth === null || objdata.BaseHealth === '') objdata.BaseHealth = 0.0;
            if (!Array.isArray(objdata.ArmorFlags)) objdata.ArmorFlags = [];
            if (!Array.isArray(objdata.ArmorLayers)) objdata.ArmorLayers = [];
            if (!Array.isArray(objdata.ArmorLayerHealth)) objdata.ArmorLayerHealth = [];
            if (!Array.isArray(objdata.ParticleLayerOverride)) objdata.ParticleLayerOverride = [];

            const targetLen = objdata.ArmorLayers.length;
            while (objdata.ArmorLayerHealth.length < targetLen) {
                objdata.ArmorLayerHealth.push(1.0);
            }
            if (objdata.ArmorLayerHealth.length > targetLen) {
                objdata.ArmorLayerHealth = objdata.ArmorLayerHealth.slice(0, targetLen);
            }
        }

        function normalizeMinMax(value, fallbackMin, fallbackMax) {
            if (typeof value !== 'object' || value === null || Array.isArray(value)) {
                return { Min: fallbackMin, Max: fallbackMax };
            }
            const min = value.Min !== undefined ? Number(value.Min) : fallbackMin;
            const max = value.Max !== undefined ? Number(value.Max) : fallbackMax;
            return {
                Min: Number.isFinite(min) ? min : fallbackMin,
                Max: Number.isFinite(max) ? max : fallbackMax
            };
        }

        function normalizeProjectileEntry(entry) {
            if (!entry || typeof entry !== 'object') return;
            if (!Array.isArray(entry.aliases) || entry.aliases.length === 0) {
                entry.aliases = ['CustomProjectile'];
            }
            if (!entry.objclass) {
                entry.objclass = 'ProjectilePropertySheet';
            }
            if (!entry.objdata || typeof entry.objdata !== 'object') {
                entry.objdata = {};
            }

            const o = entry.objdata;
            ensureProjectileGuidanceComments(o);
            const numFields = ['BaseDamage', 'HealAmount', 'SplashDamage', 'SplashRadius', 'ImpactSoundThrottleTimer'];
            numFields.forEach(field => {
                if (o[field] === undefined || o[field] === null || o[field] === '') {
                    o[field] = 0.0;
                }
            });

            if (o.ShakeBoardOnSplash === undefined) o.ShakeBoardOnSplash = false;
            if (o.DiesOnImpact === undefined) o.DiesOnImpact = true;
            if (!Array.isArray(o.CollisionFlags)) o.CollisionFlags = ['none'];
            if (!Array.isArray(o.DamageFlags)) o.DamageFlags = ['none'];
            if (typeof o.RenderImage !== 'string') o.RenderImage = '';
            if (typeof o.AttachedPAM !== 'string') o.AttachedPAM = '';
            if (typeof o.AttachedPAMAnimRigClass !== 'string') o.AttachedPAMAnimRigClass = '';
            if (typeof o.ImpactPAM !== 'string') o.ImpactPAM = '';
            if (typeof o.AttachedPAMOffset !== 'object' || o.AttachedPAMOffset === null || Array.isArray(o.AttachedPAMOffset)) {
                o.AttachedPAMOffset = { x: 0.0, y: 0.0 };
            }
            const pamOffset = o.AttachedPAMOffset;
            const hasZOffset = Object.prototype.hasOwnProperty.call(pamOffset, 'z');
            o.AttachedPAMOffset = {
                x: Number.isFinite(Number(pamOffset.x)) ? Number(pamOffset.x) : 0.0,
                y: Number.isFinite(Number(pamOffset.y)) ? Number(pamOffset.y) : 0.0
            };
            if (hasZOffset) {
                o.AttachedPAMOffset.z = Number.isFinite(Number(pamOffset.z)) ? Number(pamOffset.z) : 0.0;
            }

            if (!Array.isArray(o.InitialVelocity)) o.InitialVelocity = [];
            while (o.InitialVelocity.length < 3) {
                o.InitialVelocity.push({ Min: 0.0, Max: 0.0 });
            }
            o.InitialVelocity = o.InitialVelocity.slice(0, 3).map(v => normalizeMinMax(v, 0.0, 0.0));

            if (!Array.isArray(o.InitialAcceleration)) o.InitialAcceleration = [];
            while (o.InitialAcceleration.length < 3) {
                o.InitialAcceleration.push({ Min: 0.0, Max: 0.0 });
            }
            o.InitialAcceleration = o.InitialAcceleration.slice(0, 3).map(v => normalizeMinMax(v, 0.0, 0.0));

            if (!Array.isArray(o.InitialVelocityScale)) o.InitialVelocityScale = [];
            while (o.InitialVelocityScale.length < 3) {
                o.InitialVelocityScale.push({ Min: 1.0, Max: 1.0 });
            }
            o.InitialVelocityScale = o.InitialVelocityScale.slice(0, 3).map(v => normalizeMinMax(v, 1.0, 1.0));

            o.InitialScale = normalizeMinMax(o.InitialScale, 1.0, 1.0);
            o.InitialHeight = normalizeMinMax(o.InitialHeight, 0.0, 0.0);
            o.InitialRotation = normalizeMinMax(o.InitialRotation, 0.0, 0.0);
            o.InitialAngularVelocity = normalizeMinMax(o.InitialAngularVelocity, 0.0, 0.0);

            if (!Array.isArray(o.ImpactOffset)) {
                o.ImpactOffset = [{ Min: 0.0, Max: 0.0 }, { Min: 0.0, Max: 0.0 }];
            }
            while (o.ImpactOffset.length < 2) {
                o.ImpactOffset.push({ Min: 0.0, Max: 0.0 });
            }
            o.ImpactOffset = o.ImpactOffset.slice(0, 2).map(v => normalizeMinMax(v, 0.0, 0.0));

            if (typeof o.CollisionRect !== 'object' || o.CollisionRect === null || Array.isArray(o.CollisionRect)) {
                o.CollisionRect = { mX: 0.0, mY: 0.0, mWidth: 0.0, mHeight: 0.0 };
            }
            const rect = o.CollisionRect;
            o.CollisionRect = {
                mX: Number.isFinite(Number(rect.mX)) ? Number(rect.mX) : 0.0,
                mY: Number.isFinite(Number(rect.mY)) ? Number(rect.mY) : 0.0,
                mWidth: Number.isFinite(Number(rect.mWidth)) ? Number(rect.mWidth) : 0.0,
                mHeight: Number.isFinite(Number(rect.mHeight)) ? Number(rect.mHeight) : 0.0
            };
            reorderProjectileGuidanceComments(o);
        }

        function isSimpleMinMaxObject(value) {
            return !!value && typeof value === 'object' && !Array.isArray(value) &&
                Object.prototype.hasOwnProperty.call(value, 'Min') &&
                Object.prototype.hasOwnProperty.call(value, 'Max');
        }

        function isSimpleCoordObject(value) {
            if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
            const keys = Object.keys(value);
            return keys.length > 0 && keys.every(k => ['x', 'y', 'z'].includes(k));
        }

        function renderAdvancedAssetFields(objdata, keys, changeFnName) {
            return keys.map(key => {
                const value = objdata[key];
                const safeKey = escapeHtml(key);
                if (isCommentKey(key)) {
                    return makeCommentFieldHTML(key, value);
                }
                if (typeof value === 'boolean') {
                    return `<div class="form-group bool-row"><label>${safeKey}</label><input type="checkbox" ${value ? 'checked' : ''} onchange="${changeFnName}('${escapeHtml(key)}', this.checked, 'bool')"></div>`;
                }
                if (typeof value === 'number') {
                    return `<div class="form-group"><label>${safeKey}</label><input type="number" step="0.01" value="${value}" onchange="${changeFnName}('${escapeHtml(key)}', this.value, 'number')"></div>`;
                }
                if (typeof value === 'string') {
                    return `<div class="form-group"><label>${safeKey}</label><input type="text" value="${escapeHtml(value)}" onchange="${changeFnName}('${escapeHtml(key)}', this.value, 'string')"></div>`;
                }
                if (Array.isArray(value) && value.every(v => typeof v === 'string')) {
                    return `<div class="form-group"><label>${safeKey}</label><input type="text" value="${escapeHtml(value.join(', '))}" placeholder="comma separated" onchange="${changeFnName}('${escapeHtml(key)}', this.value, 'string_array')"></div>`;
                }
                if (isSimpleMinMaxObject(value)) {
                    const min = Number(value.Min ?? 0);
                    const max = Number(value.Max ?? 0);
                    return `<div class="form-group"><label>${safeKey} (Min/Max)</label><div class="asset-inline-add"><input type="number" step="0.01" value="${min}" onchange="${changeFnName}('${escapeHtml(key)}', this.value, 'minmax_min')"><input type="number" step="0.01" value="${max}" onchange="${changeFnName}('${escapeHtml(key)}', this.value, 'minmax_max')"></div></div>`;
                }
                if (isSimpleCoordObject(value)) {
                    const parts = ['x', 'y', 'z'].filter(k => Object.prototype.hasOwnProperty.call(value, k)).map(coord => {
                        const coordValue = Number(value[coord] ?? 0);
                        return `<input type="number" step="0.01" value="${coordValue}" onchange="${changeFnName}('${escapeHtml(key)}', this.value, 'coord_${coord}')">`;
                    }).join('');
                    return `<div class="form-group"><label>${safeKey} (coord)</label><div class="asset-inline-add">${parts}</div></div>`;
                }
                return `<div class="form-group"><label>${safeKey} (JSON)</label><textarea class="output-textarea" style="height:90px;" onchange="${changeFnName}('${escapeHtml(key)}', this.value, 'json')">${escapeHtml(JSON.stringify(value, null, 2))}</textarea></div>`;
            }).join('');
        }

        function renderRectObjectFields(fieldName, rectObj, updateFnName) {
            const rect = rectObj || { mX: 0, mY: 0, mWidth: 0, mHeight: 0 };
            const keys = ['mX', 'mY', 'mWidth', 'mHeight'];
            const fields = keys.map(subKey => `
                <div class="rect-field">
                    <label>${escapeHtml(subKey)}</label>
                    <input type="number" step="0.01" value="${Number(rect[subKey] ?? 0)}" onchange="${updateFnName}('${escapeHtml(fieldName)}', '${escapeHtml(subKey)}', this.value)">
                </div>
            `).join('');
            return `<div class="rect-fields">${fields}</div>`;
        }

        function renderMinMaxArrayFields(fieldName, values, labels, updateFnName) {
            const list = Array.isArray(values) ? values : [];
            return labels.map((label, index) => {
                const range = normalizeMinMax(list[index], 0, 0);
                return `
                    <div class="form-group">
                        <label>${escapeHtml(fieldName)} ${escapeHtml(label)}</label>
                        <div class="rect-fields">
                            <div class="rect-field">
                                <label>Min</label>
                                <input type="number" step="0.01" value="${Number(range.Min)}" onchange="${updateFnName}('${escapeHtml(fieldName)}', ${index}, 'Min', this.value)">
                            </div>
                            <div class="rect-field">
                                <label>Max</label>
                                <input type="number" step="0.01" value="${Number(range.Max)}" onchange="${updateFnName}('${escapeHtml(fieldName)}', ${index}, 'Max', this.value)">
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function renderMinMaxObjectFields(fieldName, value, updateFnName) {
            const range = normalizeMinMax(value, 0, 0);
            return `
                <div class="rect-fields">
                    <div class="rect-field">
                        <label>Min</label>
                        <input type="number" step="0.01" value="${Number(range.Min)}" onchange="${updateFnName}('${escapeHtml(fieldName)}', 'Min', this.value)">
                    </div>
                    <div class="rect-field">
                        <label>Max</label>
                        <input type="number" step="0.01" value="${Number(range.Max)}" onchange="${updateFnName}('${escapeHtml(fieldName)}', 'Max', this.value)">
                    </div>
                </div>
            `;
        }

        function renderCoordObjectFields(fieldName, value, updateFnName, axes) {
            const source = (value && typeof value === 'object' && !Array.isArray(value)) ? value : {};
            let keys = Array.isArray(axes) && axes.length ? axes : Object.keys(source).filter(k => ['x', 'y', 'z'].includes(k));
            if (keys.length === 0) keys = ['x', 'y'];
            const fields = keys.map(coord => `
                <div class="rect-field">
                    <label>${escapeHtml(coord)}</label>
                    <input type="number" step="0.01" value="${Number(source[coord] ?? 0)}" onchange="${updateFnName}('${escapeHtml(fieldName)}', '${escapeHtml(coord)}', this.value)">
                </div>
            `).join('');
            return `<div class="rect-fields">${fields}</div>`;
        }

        function buildCustomArmorTab() {
            const container = document.getElementById('armorProperties');
            if (!container) return;

            container.innerHTML = `
                <div class="asset-toolbar">
                    <div class="asset-add-row">
                        <input type="text" id="newArmorSourceInput" class="search-input" list="newArmorSourceOptions" placeholder="Type armor alias or Template">
                        <button onclick="addCustomArmorEntry()">Add Armor</button>
                    </div>
                    <datalist id="newArmorSourceOptions"></datalist>
                    <div class="asset-help">Create one or more custom armor property sheets. They are included in the main Generated JSON tab.</div>
                </div>
                <div class="asset-layout">
                    <div class="asset-list-panel">
                        <h3>Custom Armors</h3>
                        <div id="customArmorList" class="asset-list"></div>
                    </div>
                    <div class="asset-editor-panel">
                        <div id="customArmorEditor"></div>
                    </div>
                </div>
            `;

            renderCustomArmorSourceOptions();
            renderCustomArmorList();
            renderCustomArmorEditor();
        }

        function renderCustomArmorSourceOptions() {
            const list = document.getElementById('newArmorSourceOptions');
            const input = document.getElementById('newArmorSourceInput');
            if (!list) return;
            const refs = getArmorReferenceEntries();
            let html = `<option value="Template"></option>`;
            refs.forEach(ref => {
                html += `<option value="${escapeHtml(ref.alias)}"></option>`;
            });
            list.innerHTML = html;
            if (input && !input.value) {
                input.value = 'Template';
            }
        }

        function addCustomArmorEntry() {
            const sourceInput = document.getElementById('newArmorSourceInput');
            if (!sourceInput) return;

            const refs = getArmorReferenceEntries();
            const sourceAlias = resolveReferenceAlias(sourceInput.value, refs);
            const baseAlias = sourceAlias && sourceAlias !== '__template__' ? sourceAlias : 'CustomArmor';
            const alias = makeUniqueArmorAlias(sanitizeEntryAlias(baseAlias, 'CustomArmor'));

            const sourceObj = sourceAlias === '__template__'
                ? (armorTemplateObject || getDefaultArmorTemplateObject())
                : ((refs.find(r => r.alias === sourceAlias)?.obj) || armorTemplateObject || getDefaultArmorTemplateObject());

            const cloned = deepCloneAsset(sourceObj);
            cloned.aliases = [alias];
            normalizeArmorEntry(cloned);

            customArmorEntries.push(cloned);
            selectedCustomArmorIndex = customArmorEntries.length - 1;
            sourceInput.value = sourceAlias === '__template__' ? 'Template' : sourceAlias;

            renderCustomArmorList();
            renderCustomArmorEditor();
        }

        function renderCustomArmorList() {
            const list = document.getElementById('customArmorList');
            if (!list) return;

            list.innerHTML = '';
            if (customArmorEntries.length === 0) {
                list.innerHTML = '<div class="asset-empty">No custom armors yet.</div>';
                return;
            }

            customArmorEntries.forEach((entry, idx) => {
                const row = document.createElement('div');
                row.className = `asset-list-item ${idx === selectedCustomArmorIndex ? 'active' : ''}`;

                const nameBtn = document.createElement('button');
                nameBtn.className = 'asset-item-main';
                nameBtn.textContent = getEntryAlias(entry, `Armor_${idx + 1}`);
                nameBtn.onclick = () => selectCustomArmorEntry(idx);

                const removeBtn = document.createElement('button');
                removeBtn.className = 'asset-item-remove';
                removeBtn.textContent = 'Remove';
                removeBtn.onclick = () => removeCustomArmorEntry(idx);

                row.appendChild(nameBtn);
                row.appendChild(removeBtn);
                list.appendChild(row);
            });
        }

        function selectCustomArmorEntry(index) {
            selectedCustomArmorIndex = index;
            renderCustomArmorList();
            renderCustomArmorEditor();
        }

        function removeCustomArmorEntry(index) {
            if (index < 0 || index >= customArmorEntries.length) return;
            customArmorEntries.splice(index, 1);
            if (selectedCustomArmorIndex >= customArmorEntries.length) {
                selectedCustomArmorIndex = customArmorEntries.length - 1;
            }
            renderCustomArmorList();
            renderCustomArmorEditor();
        }

        function getSelectedCustomArmor() {
            if (selectedCustomArmorIndex < 0 || selectedCustomArmorIndex >= customArmorEntries.length) return null;
            const entry = customArmorEntries[selectedCustomArmorIndex];
            normalizeArmorEntry(entry);
            return entry;
        }

        function renderCustomArmorEditor() {
            const editor = document.getElementById('customArmorEditor');
            if (!editor) return;
            const entry = getSelectedCustomArmor();

            if (!entry) {
                editor.innerHTML = '<div class="asset-empty">Select or add an armor entry to edit.</div>';
                return;
            }

            const obj = entry.objdata;
            const flagsHtml = obj.ArmorFlags.map((flag, i) => `
                <div class="asset-chip">
                    <span>${escapeHtml(flag)}</span>
                    <button onclick="removeCustomArmorFlag(${i})">x</button>
                </div>
            `).join('');

            const layerRows = obj.ArmorLayers.map((layer, i) => `
                <div class="asset-layer-row">
                    <input type="text" value="${escapeHtml(layer)}" onchange="updateCustomArmorLayerName(${i}, this.value)">
                    <input type="number" step="0.01" value="${obj.ArmorLayerHealth[i] ?? 1}" onchange="updateCustomArmorLayerHealth(${i}, this.value)">
                    <button onclick="removeCustomArmorLayer(${i})">Remove</button>
                </div>
            `).join('');

            const overrideRows = obj.ParticleLayerOverride.map((layer, i) => `
                <div class="asset-layer-row">
                    <input type="text" value="${escapeHtml(layer)}" onchange="updateCustomArmorParticleLayer(${i}, this.value)">
                    <button onclick="removeCustomArmorParticleLayer(${i})">Remove</button>
                </div>
            `).join('');

            const armorTypeOptionsHtml = (armorTypeOptions || []).slice(0, 500)
                .map(v => `<option value="${escapeHtml(v)}"></option>`)
                .join('');
            const armorFlagOptionsHtml = (armorFlagOptions || []).slice(0, 500)
                .map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`)
                .join('');
            const baseArmorKeys = new Set(['ArmorType', 'BaseHealth', 'ArmorFlags', 'ArmorLayers', 'ArmorLayerHealth', 'ParticleLayerOverride']);
            const advancedArmorKeys = Object.keys(obj).filter(k => !baseArmorKeys.has(k));
            const advancedArmorFields = renderAdvancedAssetFields(obj, advancedArmorKeys, 'updateCustomArmorAdvancedField');

            editor.innerHTML = `
                <div class="asset-form-grid">
                    <div class="form-group">
                        <label>Alias</label>
                        <input type="text" value="${escapeHtml(getEntryAlias(entry, 'CustomArmor'))}" onchange="updateCustomArmorAlias(this.value)">
                    </div>
                    <div class="form-group">
                        <label>ObjClass</label>
                        <input type="text" value="${escapeHtml(entry.objclass || 'ArmorPropertySheet')}" onchange="updateCustomArmorObjClass(this.value)">
                    </div>
                    <div class="form-group">
                        <label>ArmorType</label>
                        <input type="text" id="customArmorTypeInput" list="customArmorTypeOptions" value="${escapeHtml(obj.ArmorType || '')}" onchange="updateCustomArmorType(this.value)">
                        <datalist id="customArmorTypeOptions">${armorTypeOptionsHtml}</datalist>
                    </div>
                    <div class="form-group">
                        <label>BaseHealth</label>
                        <input type="number" step="0.01" value="${obj.BaseHealth ?? 0}" onchange="updateCustomArmorBaseHealth(this.value)">
                    </div>
                </div>

                <div class="asset-section">
                    <h4>ArmorFlags</h4>
                    <div class="asset-chip-list">${flagsHtml || '<span class="asset-muted">No flags</span>'}</div>
                    <div class="asset-inline-add">
                        <select id="newCustomArmorFlagSelect">${armorFlagOptionsHtml || '<option value="">none</option>'}</select>
                        <button onclick="addCustomArmorFlag()">Add Flag</button>
                    </div>
                </div>

                <div class="asset-section">
                    <h4>Armor Layers + Health</h4>
                    <div>${layerRows || '<span class="asset-muted">No layers</span>'}</div>
                    <button onclick="addCustomArmorLayer()">Add Layer</button>
                </div>

                <div class="asset-section">
                    <h4>ParticleLayerOverride</h4>
                    <div>${overrideRows || '<span class="asset-muted">No overrides</span>'}</div>
                    <div class="asset-inline-add">
                        <input id="newCustomArmorParticleLayerInput" type="text" placeholder="Add particle layer">
                        <button onclick="addCustomArmorParticleLayer()">Add Layer</button>
                    </div>
                </div>

                <div class="asset-section">
                    <h4>Other Properties</h4>
                    ${advancedArmorFields || '<div class="asset-muted">No additional properties.</div>'}
                </div>
            `;
        }

        function updateCustomArmorAlias(value) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            const alias = sanitizeEntryAlias(value, getEntryAlias(entry, 'CustomArmor'));
            entry.aliases[0] = alias;
            renderCustomArmorList();
        }

        function updateCustomArmorObjClass(value) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objclass = String(value || 'ArmorPropertySheet').trim() || 'ArmorPropertySheet';
        }

        function updateCustomArmorType(value) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objdata.ArmorType = String(value || '').trim();
        }

        function updateCustomArmorBaseHealth(value) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            const num = parseFloat(value);
            entry.objdata.BaseHealth = Number.isFinite(num) ? num : 0.0;
        }

        function addCustomArmorFlag() {
            const entry = getSelectedCustomArmor();
            const select = document.getElementById('newCustomArmorFlagSelect');
            const customInput = document.getElementById('newCustomArmorFlagCustomInput');
            if (!entry) return;
            const customValue = String(customInput?.value || '').trim();
            const selectedValue = String(select?.value || '').trim();
            const value = customValue || selectedValue;
            if (!value) return;
            if (!entry.objdata.ArmorFlags.includes(value)) {
                entry.objdata.ArmorFlags.push(value);
            }
            if (customInput) customInput.value = '';
            renderCustomArmorEditor();
        }

        function removeCustomArmorFlag(index) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objdata.ArmorFlags.splice(index, 1);
            renderCustomArmorEditor();
        }

        function addCustomArmorLayer() {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objdata.ArmorLayers.push('new_layer');
            entry.objdata.ArmorLayerHealth.push(1.0);
            renderCustomArmorEditor();
        }

        function removeCustomArmorLayer(index) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objdata.ArmorLayers.splice(index, 1);
            entry.objdata.ArmorLayerHealth.splice(index, 1);
            normalizeArmorEntry(entry);
            renderCustomArmorEditor();
        }

        function updateCustomArmorLayerName(index, value) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objdata.ArmorLayers[index] = String(value || '');
        }

        function updateCustomArmorLayerHealth(index, value) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            const num = parseFloat(value);
            entry.objdata.ArmorLayerHealth[index] = Number.isFinite(num) ? num : 1.0;
        }

        function addCustomArmorParticleLayer() {
            const entry = getSelectedCustomArmor();
            const input = document.getElementById('newCustomArmorParticleLayerInput');
            if (!entry || !input) return;
            const value = String(input.value || '').trim();
            if (!value) return;
            entry.objdata.ParticleLayerOverride.push(value);
            input.value = '';
            renderCustomArmorEditor();
        }

        function removeCustomArmorParticleLayer(index) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objdata.ParticleLayerOverride.splice(index, 1);
            renderCustomArmorEditor();
        }

        function updateCustomArmorParticleLayer(index, value) {
            const entry = getSelectedCustomArmor();
            if (!entry) return;
            entry.objdata.ParticleLayerOverride[index] = String(value || '');
        }

        function updateCustomArmorAdvancedField(key, value, mode) {
            const entry = getSelectedCustomArmor();
            if (!entry || !entry.objdata) return;
            if (!key) return;
            const obj = entry.objdata;

            if (mode === 'bool') obj[key] = !!value;
            else if (mode === 'number') obj[key] = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            else if (mode === 'string') obj[key] = String(value || '');
            else if (mode === 'string_array') obj[key] = String(value || '').split(',').map(v => v.trim()).filter(Boolean);
            else if (mode === 'minmax_min') {
                if (!isSimpleMinMaxObject(obj[key])) obj[key] = { Min: 0, Max: 0 };
                obj[key].Min = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            } else if (mode === 'minmax_max') {
                if (!isSimpleMinMaxObject(obj[key])) obj[key] = { Min: 0, Max: 0 };
                obj[key].Max = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            } else if (mode.startsWith('coord_')) {
                const axis = mode.replace('coord_', '');
                if (!isSimpleCoordObject(obj[key])) obj[key] = {};
                obj[key][axis] = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            } else if (mode === 'json') {
                try { obj[key] = JSON.parse(value); } catch (e) { return; }
            }
        }

        function buildCustomProjectileTab() {
            const container = document.getElementById('projectileProperties');
            if (!container) return;

            container.innerHTML = `
                <div class="asset-toolbar">
                    <div class="asset-add-row">
                        <input type="text" id="newProjectileSourceInput" class="search-input" list="newProjectileSourceOptions" placeholder="Type projectile alias or Template">
                        <button onclick="addCustomProjectileEntry()">Add Projectile</button>
                    </div>
                    <datalist id="newProjectileSourceOptions"></datalist>
                    <div class="asset-help">Create one or more custom projectile property sheets. They are included in the main Generated JSON tab.</div>
                </div>
                <div class="asset-layout">
                    <div class="asset-list-panel">
                        <h3>Custom Projectiles</h3>
                        <div id="customProjectileList" class="asset-list"></div>
                    </div>
                    <div class="asset-editor-panel">
                        <div id="customProjectileEditor"></div>
                    </div>
                </div>
            `;

            renderCustomProjectileSourceOptions();
            renderCustomProjectileList();
            renderCustomProjectileEditor();
        }

        function renderCustomProjectileSourceOptions() {
            const list = document.getElementById('newProjectileSourceOptions');
            const input = document.getElementById('newProjectileSourceInput');
            if (!list) return;
            const refs = getProjectileReferenceEntries();
            let html = `<option value="Template"></option>`;
            refs.forEach(ref => {
                html += `<option value="${escapeHtml(ref.alias)}"></option>`;
            });
            list.innerHTML = html;
            if (input && !input.value) {
                input.value = 'Template';
            }
        }

        function addCustomProjectileEntry() {
            const sourceInput = document.getElementById('newProjectileSourceInput');
            if (!sourceInput) return;

            const refs = getProjectileReferenceEntries();
            const sourceAlias = resolveReferenceAlias(sourceInput.value, refs);
            const baseAlias = sourceAlias && sourceAlias !== '__template__' ? sourceAlias : 'CustomProjectile';
            const alias = makeUniqueProjectileAlias(sanitizeEntryAlias(baseAlias, 'CustomProjectile'));

            const sourceObj = sourceAlias === '__template__'
                ? (projectileTemplateObject || getDefaultProjectileTemplateObject())
                : ((refs.find(r => r.alias === sourceAlias)?.obj) || projectileTemplateObject || getDefaultProjectileTemplateObject());

            const cloned = deepCloneAsset(sourceObj);
            cloned.aliases = [alias];
            normalizeProjectileEntry(cloned);

            customProjectileEntries.push(cloned);
            selectedCustomProjectileIndex = customProjectileEntries.length - 1;
            sourceInput.value = sourceAlias === '__template__' ? 'Template' : sourceAlias;

            renderCustomProjectileList();
            renderCustomProjectileEditor();
        }

        function renderCustomProjectileList() {
            const list = document.getElementById('customProjectileList');
            if (!list) return;

            list.innerHTML = '';
            if (customProjectileEntries.length === 0) {
                list.innerHTML = '<div class="asset-empty">No custom projectiles yet.</div>';
                return;
            }

            customProjectileEntries.forEach((entry, idx) => {
                const row = document.createElement('div');
                row.className = `asset-list-item ${idx === selectedCustomProjectileIndex ? 'active' : ''}`;

                const nameBtn = document.createElement('button');
                nameBtn.className = 'asset-item-main';
                nameBtn.textContent = getEntryAlias(entry, `Projectile_${idx + 1}`);
                nameBtn.onclick = () => selectCustomProjectileEntry(idx);

                const removeBtn = document.createElement('button');
                removeBtn.className = 'asset-item-remove';
                removeBtn.textContent = 'Remove';
                removeBtn.onclick = () => removeCustomProjectileEntry(idx);

                row.appendChild(nameBtn);
                row.appendChild(removeBtn);
                list.appendChild(row);
            });
        }

        function selectCustomProjectileEntry(index) {
            selectedCustomProjectileIndex = index;
            renderCustomProjectileList();
            renderCustomProjectileEditor();
        }

        function removeCustomProjectileEntry(index) {
            if (index < 0 || index >= customProjectileEntries.length) return;
            customProjectileEntries.splice(index, 1);
            if (selectedCustomProjectileIndex >= customProjectileEntries.length) {
                selectedCustomProjectileIndex = customProjectileEntries.length - 1;
            }
            renderCustomProjectileList();
            renderCustomProjectileEditor();
        }

        function getSelectedCustomProjectile() {
            if (selectedCustomProjectileIndex < 0 || selectedCustomProjectileIndex >= customProjectileEntries.length) return null;
            const entry = customProjectileEntries[selectedCustomProjectileIndex];
            normalizeProjectileEntry(entry);
            return entry;
        }

        function renderCustomProjectileEditor() {
            const editor = document.getElementById('customProjectileEditor');
            if (!editor) return;
            const entry = getSelectedCustomProjectile();

            if (!entry) {
                editor.innerHTML = '<div class="asset-empty">Select or add a projectile entry to edit.</div>';
                return;
            }

            const obj = entry.objdata;

            const collisionOptionsHtml = (projectileCollisionFlags || []).slice(0, 600)
                .map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`)
                .join('');
            const damageOptionsHtml = (projectileDamageFlags || []).slice(0, 600)
                .map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`)
                .join('');
            const projectileStringOptions = collectProjectileStringFieldOptions([
                'RenderImage',
                'AttachedPAM',
                'AttachedPAMAnimRigClass',
                'ImpactPAM',
                'ImpactSoundEvent'
            ], 400);
            const renderImageOptionsHtml = (projectileStringOptions.RenderImage || []).map(v => `<option value="${escapeHtml(v)}"></option>`).join('');
            const attachedPamOptionsHtml = (projectileStringOptions.AttachedPAM || []).map(v => `<option value="${escapeHtml(v)}"></option>`).join('');
            const attachedPamAnimRigOptionsHtml = (projectileStringOptions.AttachedPAMAnimRigClass || []).map(v => `<option value="${escapeHtml(v)}"></option>`).join('');
            const impactPamOptionsHtml = (projectileStringOptions.ImpactPAM || []).map(v => `<option value="${escapeHtml(v)}"></option>`).join('');
            const impactSoundOptionsHtml = (projectileStringOptions.ImpactSoundEvent || []).map(v => `<option value="${escapeHtml(v)}"></option>`).join('');

            const collisionFlagsHtml = obj.CollisionFlags.map((flag, i) => `
                <div class="asset-chip">
                    <span>${escapeHtml(flag)}</span>
                    <button onclick="removeCustomProjectileCollisionFlag(${i})">x</button>
                </div>
            `).join('');

            const damageFlagsHtml = obj.DamageFlags.map((flag, i) => `
                <div class="asset-chip">
                    <span>${escapeHtml(flag)}</span>
                    <button onclick="removeCustomProjectileDamageFlag(${i})">x</button>
                </div>
            `).join('');
            const collisionCommentHtml = makeCommentFieldHTML('#comment CollisionFlags', obj['#comment CollisionFlags']);
            const damageCommentHtml = [
                makeCommentFieldHTML('#comment DamageFlags', obj['#comment DamageFlags']),
                makeCommentFieldHTML('#comment DamageFlags Rules', obj['#comment DamageFlags Rules']),
                makeCommentFieldHTML('#comment DamageFlags Examples', obj['#comment DamageFlags Examples'])
            ].join('');
            const impactOffsetCommentHtml = makeCommentFieldHTML('#comment ImpactOffset', obj['#comment ImpactOffset']);
            const baseProjectileKeys = new Set([
                'BaseDamage', 'HealAmount', 'SplashDamage', 'SplashRadius',
                'ShakeBoardOnSplash', 'DiesOnImpact',
                'RenderImage', 'AttachedPAM', 'AttachedPAMAnimRigClass', 'ImpactPAM', 'ImpactSoundEvent',
                'CollisionFlags', 'DamageFlags',
                'InitialVelocity', 'InitialAcceleration', 'InitialVelocityScale',
                'InitialScale', 'InitialHeight', 'InitialRotation', 'InitialAngularVelocity',
                'AttachedPAMOffset', 'ImpactOffset', 'CollisionRect',
                '#comment CollisionFlags', '#comment DamageFlags', '#comment DamageFlags Rules', '#comment DamageFlags Examples', '#comment ImpactOffset'
            ]);
            const advancedProjectileKeys = Object.keys(obj).filter(k => !baseProjectileKeys.has(k));
            const advancedProjectileFields = renderAdvancedAssetFields(obj, advancedProjectileKeys, 'updateCustomProjectileAdvancedField');
            const initialVelocityFields = renderMinMaxArrayFields('InitialVelocity', obj.InitialVelocity, ['X', 'Y', 'Z'], 'updateCustomProjectileMinMaxArrayField');
            const initialAccelerationFields = renderMinMaxArrayFields('InitialAcceleration', obj.InitialAcceleration, ['X', 'Y', 'Z'], 'updateCustomProjectileMinMaxArrayField');
            const initialVelocityScaleFields = renderMinMaxArrayFields('InitialVelocityScale', obj.InitialVelocityScale, ['X', 'Y', 'Z'], 'updateCustomProjectileMinMaxArrayField');
            const initialScaleFields = renderMinMaxObjectFields('InitialScale', obj.InitialScale, 'updateCustomProjectileMinMaxField');
            const initialHeightFields = renderMinMaxObjectFields('InitialHeight', obj.InitialHeight, 'updateCustomProjectileMinMaxField');
            const initialRotationFields = renderMinMaxObjectFields('InitialRotation', obj.InitialRotation, 'updateCustomProjectileMinMaxField');
            const initialAngularVelocityFields = renderMinMaxObjectFields('InitialAngularVelocity', obj.InitialAngularVelocity, 'updateCustomProjectileMinMaxField');
            const attachedPAMOffsetFields = renderCoordObjectFields('AttachedPAMOffset', obj.AttachedPAMOffset, 'updateCustomProjectileCoordField');
            const impactOffsetFields = renderMinMaxArrayFields('ImpactOffset', obj.ImpactOffset, ['X', 'Y'], 'updateCustomProjectileMinMaxArrayField');
            const collisionRectFields = renderRectObjectFields('CollisionRect', obj.CollisionRect, 'updateCustomProjectileRectField');

            editor.innerHTML = `
                <div class="asset-form-grid">
                    <div class="form-group">
                        <label>Alias</label>
                        <input type="text" value="${escapeHtml(getEntryAlias(entry, 'CustomProjectile'))}" onchange="updateCustomProjectileAlias(this.value)">
                    </div>
                    <div class="form-group">
                        <label>ObjClass</label>
                        <input type="text" value="${escapeHtml(entry.objclass || 'ProjectilePropertySheet')}" onchange="updateCustomProjectileObjClass(this.value)">
                    </div>
                    <div class="form-group">
                        <label>BaseDamage</label>
                        <input type="number" step="0.01" value="${obj.BaseDamage ?? 0}" onchange="updateCustomProjectileNumberField('BaseDamage', this.value)">
                    </div>
                    <div class="form-group">
                        <label>HealAmount</label>
                        <input type="number" step="0.01" value="${obj.HealAmount ?? 0}" onchange="updateCustomProjectileNumberField('HealAmount', this.value)">
                    </div>
                    <div class="form-group">
                        <label>SplashDamage</label>
                        <input type="number" step="0.01" value="${obj.SplashDamage ?? 0}" onchange="updateCustomProjectileNumberField('SplashDamage', this.value)">
                    </div>
                    <div class="form-group">
                        <label>SplashRadius</label>
                        <input type="number" step="0.01" value="${obj.SplashRadius ?? 0}" onchange="updateCustomProjectileNumberField('SplashRadius', this.value)">
                    </div>
                </div>

                <div class="asset-form-grid">
                    <div class="form-group bool-row">
                        <label>ShakeBoardOnSplash</label>
                        <input type="checkbox" ${obj.ShakeBoardOnSplash ? 'checked' : ''} onchange="updateCustomProjectileBoolField('ShakeBoardOnSplash', this.checked)">
                    </div>
                    <div class="form-group bool-row">
                        <label>DiesOnImpact</label>
                        <input type="checkbox" ${obj.DiesOnImpact ? 'checked' : ''} onchange="updateCustomProjectileBoolField('DiesOnImpact', this.checked)">
                    </div>
                </div>

                <div class="asset-form-grid">
                    <div class="form-group">
                        <label>RenderImage</label>
                        <input type="text" list="customProjectileRenderImageOptions" value="${escapeHtml(obj.RenderImage || '')}" onchange="updateCustomProjectileStringField('RenderImage', this.value)">
                        <datalist id="customProjectileRenderImageOptions">${renderImageOptionsHtml}</datalist>
                    </div>
                    <div class="form-group">
                        <label>AttachedPAM</label>
                        <input type="text" list="customProjectileAttachedPAMOptions" value="${escapeHtml(obj.AttachedPAM || '')}" onchange="updateCustomProjectileStringField('AttachedPAM', this.value)">
                        <datalist id="customProjectileAttachedPAMOptions">${attachedPamOptionsHtml}</datalist>
                    </div>
                    <div class="form-group">
                        <label>AttachedPAMAnimRigClass</label>
                        <input type="text" list="customProjectileAttachedPAMAnimRigOptions" value="${escapeHtml(obj.AttachedPAMAnimRigClass || '')}" onchange="updateCustomProjectileStringField('AttachedPAMAnimRigClass', this.value)">
                        <datalist id="customProjectileAttachedPAMAnimRigOptions">${attachedPamAnimRigOptionsHtml}</datalist>
                    </div>
                    <div class="form-group">
                        <label>ImpactPAM</label>
                        <input type="text" list="customProjectileImpactPAMOptions" value="${escapeHtml(obj.ImpactPAM || '')}" onchange="updateCustomProjectileStringField('ImpactPAM', this.value)">
                        <datalist id="customProjectileImpactPAMOptions">${impactPamOptionsHtml}</datalist>
                    </div>
                    <div class="form-group">
                        <label>ImpactSoundEvent</label>
                        <input type="text" list="customProjectileImpactSoundOptions" value="${escapeHtml(obj.ImpactSoundEvent || '')}" onchange="updateCustomProjectileStringField('ImpactSoundEvent', this.value)">
                        <datalist id="customProjectileImpactSoundOptions">${impactSoundOptionsHtml}</datalist>
                    </div>
                </div>

                <div class="asset-section">
                    <h4>CollisionFlags</h4>
                    ${collisionCommentHtml}
                    <div class="asset-chip-list">${collisionFlagsHtml || '<span class="asset-muted">No flags</span>'}</div>
                    <div class="asset-inline-add">
                        <select id="newCustomProjectileCollisionFlagSelect">${collisionOptionsHtml || '<option value="">none</option>'}</select>
                        <input id="newCustomProjectileCollisionFlagCustomInput" type="text" placeholder="Or type custom flag">
                        <button onclick="addCustomProjectileCollisionFlag()">Add Flag</button>
                    </div>
                </div>

                <div class="asset-section">
                    <h4>DamageFlags</h4>
                    ${damageCommentHtml}
                    <div class="asset-chip-list">${damageFlagsHtml || '<span class="asset-muted">No flags</span>'}</div>
                    <div class="asset-inline-add">
                        <select id="newCustomProjectileDamageFlagSelect">${damageOptionsHtml || '<option value="">none</option>'}</select>
                        <input id="newCustomProjectileDamageFlagCustomInput" type="text" placeholder="Or type custom flag">
                        <button onclick="addCustomProjectileDamageFlag()">Add Flag</button>
                    </div>
                </div>

                <div class="asset-section">
                    <h4>InitialVelocity</h4>
                    <div class="asset-form-grid">
                        ${initialVelocityFields}
                    </div>
                </div>

                <div class="asset-section">
                    <h4>InitialAcceleration</h4>
                    <div class="asset-form-grid">
                        ${initialAccelerationFields}
                    </div>
                </div>

                <div class="asset-section">
                    <h4>InitialVelocityScale</h4>
                    <div class="asset-form-grid">
                        ${initialVelocityScaleFields}
                    </div>
                </div>

                <div class="asset-section">
                    <h4>InitialScale</h4>
                    ${initialScaleFields}
                </div>

                <div class="asset-section">
                    <h4>InitialHeight</h4>
                    ${initialHeightFields}
                </div>

                <div class="asset-section">
                    <h4>InitialRotation</h4>
                    ${initialRotationFields}
                </div>

                <div class="asset-section">
                    <h4>InitialAngularVelocity</h4>
                    ${initialAngularVelocityFields}
                </div>

                <div class="asset-section">
                    <h4>AttachedPAMOffset</h4>
                    ${attachedPAMOffsetFields}
                </div>

                <div class="asset-section">
                    <h4>ImpactOffset</h4>
                    ${impactOffsetCommentHtml}
                    <div class="asset-form-grid">
                        ${impactOffsetFields}
                    </div>
                </div>

                <div class="asset-section">
                    <h4>CollisionRect</h4>
                    ${collisionRectFields}
                </div>

                <div class="asset-section">
                    <h4>Other Properties</h4>
                    ${advancedProjectileFields || '<div class="asset-muted">No additional properties.</div>'}
                </div>
            `;
        }

        function updateCustomProjectileAlias(value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            const alias = sanitizeEntryAlias(value, getEntryAlias(entry, 'CustomProjectile'));
            entry.aliases[0] = alias;
            renderCustomProjectileList();
        }

        function updateCustomProjectileObjClass(value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            entry.objclass = String(value || 'ProjectilePropertySheet').trim() || 'ProjectilePropertySheet';
        }

        function updateCustomProjectileNumberField(field, value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            const num = parseFloat(value);
            entry.objdata[field] = Number.isFinite(num) ? num : 0.0;
        }

        function updateCustomProjectileBoolField(field, checked) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            entry.objdata[field] = !!checked;
        }

        function updateCustomProjectileStringField(field, value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            entry.objdata[field] = String(value || '');
        }

        function addCustomProjectileCollisionFlag() {
            const entry = getSelectedCustomProjectile();
            const select = document.getElementById('newCustomProjectileCollisionFlagSelect');
            const customInput = document.getElementById('newCustomProjectileCollisionFlagCustomInput');
            if (!entry) return;
            const customValue = String(customInput?.value || '').trim();
            const selectedValue = String(select?.value || '').trim();
            const value = customValue || selectedValue;
            if (!value) return;
            if (!entry.objdata.CollisionFlags.includes(value)) {
                entry.objdata.CollisionFlags.push(value);
            }
            if (customInput) customInput.value = '';
            renderCustomProjectileEditor();
        }

        function removeCustomProjectileCollisionFlag(index) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            entry.objdata.CollisionFlags.splice(index, 1);
            renderCustomProjectileEditor();
        }

        function addCustomProjectileDamageFlag() {
            const entry = getSelectedCustomProjectile();
            const select = document.getElementById('newCustomProjectileDamageFlagSelect');
            const customInput = document.getElementById('newCustomProjectileDamageFlagCustomInput');
            if (!entry) return;
            const customValue = String(customInput?.value || '').trim();
            const selectedValue = String(select?.value || '').trim();
            const value = customValue || selectedValue;
            if (!value) return;
            if (!entry.objdata.DamageFlags.includes(value)) {
                entry.objdata.DamageFlags.push(value);
            }
            if (customInput) customInput.value = '';
            renderCustomProjectileEditor();
        }

        function removeCustomProjectileDamageFlag(index) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            entry.objdata.DamageFlags.splice(index, 1);
            renderCustomProjectileEditor();
        }

        function updateCustomProjectileMinMaxArrayField(arrayField, index, minmaxField, value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            const obj = entry.objdata;
            if (!Array.isArray(obj[arrayField])) {
                obj[arrayField] = [];
            }
            while (obj[arrayField].length <= index) {
                obj[arrayField].push({ Min: 0.0, Max: 0.0 });
            }
            if (!isSimpleMinMaxObject(obj[arrayField][index])) {
                obj[arrayField][index] = { Min: 0.0, Max: 0.0 };
            }
            const num = parseFloat(value);
            obj[arrayField][index][minmaxField] = Number.isFinite(num) ? num : 0.0;
        }

        function updateCustomProjectileMinMaxField(field, minmaxField, value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            if (!isSimpleMinMaxObject(entry.objdata[field])) {
                entry.objdata[field] = { Min: 0.0, Max: 0.0 };
            }
            const num = parseFloat(value);
            entry.objdata[field][minmaxField] = Number.isFinite(num) ? num : 0.0;
        }

        function updateCustomProjectileCoordField(field, coordKey, value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            if (!entry.objdata[field] || typeof entry.objdata[field] !== 'object' || Array.isArray(entry.objdata[field])) {
                entry.objdata[field] = {};
            }
            const num = parseFloat(value);
            entry.objdata[field][coordKey] = Number.isFinite(num) ? num : 0.0;
        }

        function updateCustomProjectileRectField(field, rectKey, value) {
            const entry = getSelectedCustomProjectile();
            if (!entry) return;
            if (!entry.objdata[field] || typeof entry.objdata[field] !== 'object' || Array.isArray(entry.objdata[field])) {
                entry.objdata[field] = { mX: 0.0, mY: 0.0, mWidth: 0.0, mHeight: 0.0 };
            }
            const num = parseFloat(value);
            entry.objdata[field][rectKey] = Number.isFinite(num) ? num : 0.0;
        }

        function updateCustomProjectileAdvancedField(key, value, mode) {
            const entry = getSelectedCustomProjectile();
            if (!entry || !entry.objdata) return;
            if (!key) return;
            const obj = entry.objdata;

            if (mode === 'bool') obj[key] = !!value;
            else if (mode === 'number') obj[key] = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            else if (mode === 'string') obj[key] = String(value || '');
            else if (mode === 'string_array') obj[key] = String(value || '').split(',').map(v => v.trim()).filter(Boolean);
            else if (mode === 'minmax_min') {
                if (!isSimpleMinMaxObject(obj[key])) obj[key] = { Min: 0, Max: 0 };
                obj[key].Min = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            } else if (mode === 'minmax_max') {
                if (!isSimpleMinMaxObject(obj[key])) obj[key] = { Min: 0, Max: 0 };
                obj[key].Max = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            } else if (mode.startsWith('coord_')) {
                const axis = mode.replace('coord_', '');
                if (!isSimpleCoordObject(obj[key])) obj[key] = {};
                obj[key][axis] = Number.isFinite(parseFloat(value)) ? parseFloat(value) : 0;
            } else if (mode === 'json') {
                try { obj[key] = JSON.parse(value); } catch (e) { return; }
            }
        }
