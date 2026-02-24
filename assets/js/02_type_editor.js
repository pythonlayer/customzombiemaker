        function buildTypeForm() {
            const container = document.getElementById('typeProperties');
            container.innerHTML = '';
            const objdata = editedTypeData;
            const skipKeys = ['PopAnim', 'ResourceGroups', 'AudioGroups', 'ImpType']; // These get custom UI below
            
            for (const [key, value] of Object.entries(objdata)) {
                if (skipKeys.includes(key)) continue; // Skip these - handled separately
                
                const group = document.createElement('div');
                group.className = 'form-group';

                if (isCommentKey(key)) {
                    group.className = 'form-group comment-field';
                    group.innerHTML = `<label>${escapeHtml(key)}</label><div class="comment-text">${escapeHtml(commentValueToText(value))}</div>`;
                    container.appendChild(group);
                    continue;
                }
                
                // Special handling for Properties field
                if (key === 'Properties') {
                    const propName = extractRTIDName(value);
                    group.innerHTML = `
                        <label>${key}</label>
                        <input type="text" data-type-key="${key}" value="${propName}" 
                               onchange="updatePropertiesField(this)">
                    `;
                } else if (isRectObject(value)) {
                    let rectHtml = `<label>${key}</label><div class="rect-fields">`;
                    const rect = value || { mHeight: 0, mWidth: 0, mX: 0, mY: 0 };
                    
                    for (const [subkey, subvalue] of Object.entries(rect)) {
                        rectHtml += `<div class="rect-field">
                            <label>${subkey}</label>
                            <input type="number" data-type-key="${key}" data-rect-field="${subkey}" 
                                   value="${subvalue}" onchange="updateRectTypeData(this)">
                        </div>`;
                    }
                    rectHtml += '</div>';
                    group.innerHTML = rectHtml;
                } else if (isCoordinateObject(value)) {
                    let coordHtml = `<label>${key}</label><div class="rect-fields">`;
                    
                    for (const [subkey, subvalue] of Object.entries(value)) {
                        coordHtml += `<div class="rect-field">
                            <label>${subkey}</label>
                            <input type="number" data-type-key="${key}" data-coord-field="${subkey}" 
                                   value="${subvalue}" step="0.01" onchange="updateCoordData(this, 'type')">
                        </div>`;
                    }
                    coordHtml += '</div>';
                    group.innerHTML = coordHtml;
                } else {
                    const valueType = typeof value;
                    let input;

                    if (valueType === 'object') {
                        input = `<textarea data-type-key="${key}" onchange="updateTypeData(this)" style="min-height: 60px;">${JSON.stringify(value, null, 2)}</textarea>`;
                    } else if (valueType === 'number') {
                        input = `<input type="number" data-type-key="${key}" value="${value}" step="0.01" onchange="updateTypeData(this)">`;
                    } else if (valueType === 'boolean') {
                        input = `<input type="checkbox" data-type-key="${key}" onchange="updateTypeData(this)" ${value ? 'checked' : ''}>`;
                    } else {
                        input = `<input type="text" data-type-key="${key}" value="${value}" onchange="updateTypeData(this)">`;
                    }

                    group.innerHTML = `<label>${key}</label>${input}`;
                    if (typeof value === 'boolean') {
                        group.className = 'form-group bool-row';
                    }
                }
                container.appendChild(group);
            }

            // Aliases editor (show instead of TypeName editing)
            const aliasGroup = document.createElement('div');
            aliasGroup.className = 'form-group';
            let aliasHtml = `<label>Aliases (first alias is used for search/display)</label>`;
            aliasHtml += `<div id="aliasesContainer" style="display:flex;flex-direction:column;gap:6px;margin-top:6px;"></div>`;
            aliasHtml += `<div style="display:flex;gap:6px;margin-top:6px;">
                <input type="text" id="newAliasInput" placeholder="add alias" style="flex:1;padding:6px;background:#3a3a3a;border:1px solid #4a4a4a;color:#e0e0e0;">
                <button onclick="addAlias()" style="padding:6px 10px;">Add</button>
            </div>`;
            aliasGroup.innerHTML = aliasHtml;
            container.prepend(aliasGroup);

            renderAliases();

            // Template helper (TypeName + matching Properties alias)
            const templateGroup = document.createElement('div');
            templateGroup.className = 'form-group';
            templateGroup.id = 'templateHelperBlock';
            let templateHtml = `<label style="font-weight:bold;color:#ffcc00;">Template Helper</label>`;
            const autoDetectedFamily = detectTemplateFamilyForZombie(selectedZombie);
            if (!selectedTemplateFamily && autoDetectedFamily) {
                selectedTemplateFamily = autoDetectedFamily;
            }
            const effectiveDef = getTemplateDefByKey(selectedTemplateFamily);
            if (effectiveDef) {
                if (selectedTemplateIndex < effectiveDef.min) selectedTemplateIndex = effectiveDef.min;
                if (selectedTemplateIndex > effectiveDef.max) selectedTemplateIndex = effectiveDef.max;
            }
            templateHtml += `<div style="font-size:0.82em;color:#aaa;margin-bottom:6px;">Auto detect: ${autoDetectedFamily ? autoDetectedFamily : 'none'}. You can override manually if this is wrong.</div>`;
            templateHtml += `<div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">`;
            templateHtml += `<select id="templateFamilySelect" style="flex:1;min-width:180px;padding:6px;background:#3a3a3a;border:1px solid #4a4a4a;color:#e0e0e0;" onchange="updateTemplatePreview()">`;
            templateHtml += `<option value="">-- no template --</option>`;
            ZOMBIE_TEMPLATE_DEFS.forEach(def => {
                templateHtml += `<option value="${def.key}" ${selectedTemplateFamily === def.key ? 'selected' : ''}>${def.label}</option>`;
            });
            templateHtml += `</select>`;
            templateHtml += `<input type="number" id="templateIndexInput" value="${selectedTemplateIndex}" min="${effectiveDef ? effectiveDef.min : 1}" max="${effectiveDef ? effectiveDef.max : 30}" step="1" style="width:90px;padding:6px;background:#3a3a3a;border:1px solid #4a4a4a;color:#e0e0e0;" onchange="updateTemplatePreview()">`;
            templateHtml += `<button id="templateApplyBtn" onclick="applySelectedTemplate()" style="padding:6px 10px;">Apply</button>`;
            templateHtml += `</div>`;
            if (!autoDetectedFamily) {
                templateHtml += `<div style="margin-top:6px;padding:6px;background:#3a2a2a;border:1px solid #5a3a3a;color:#ffb0b0;border-radius:3px;font-size:0.82em;">No auto template match. Use manual override only if this zombie supports template naming.</div>`;
            }
            templateHtml += `<div style="margin-top:6px;"><label style="display:flex;gap:8px;align-items:center;"><input id="templateModeCheckbox" type="checkbox" ${templateModeEnabled ? 'checked' : ''} ${selectedTemplateFamily ? '' : 'disabled'} onchange="setTemplateMode(this)">Template Mode (props only, lock Type tab)</label></div>`;
            templateHtml += `<div id="templatePreview" style="margin-top:6px;color:#aaa;font-size:0.85em;"></div>`;
            templateGroup.innerHTML = templateHtml;
            container.prepend(templateGroup);

            setTimeout(() => updateTemplatePreview(), 0);

            // Keep high-frequency edits visible; collapse noisy type-only settings.
            const advancedTypeDetails = document.createElement('details');
            advancedTypeDetails.style.marginTop = '10px';
            advancedTypeDetails.style.border = '1px solid #4a4a4a';
            advancedTypeDetails.style.borderRadius = '4px';
            advancedTypeDetails.style.padding = '10px';
            advancedTypeDetails.style.background = '#2b2b2b';
            advancedTypeDetails.innerHTML = `<summary style="cursor:pointer;color:#ddd;font-weight:bold;">Advanced Type Options</summary>`;
            const advancedTypeBody = document.createElement('div');
            advancedTypeBody.style.marginTop = '10px';
            advancedTypeDetails.appendChild(advancedTypeBody);
            container.appendChild(advancedTypeDetails);

            // Add PopAnim selector with autocomplete
            const popAnimGroup = document.createElement('div');
            popAnimGroup.className = 'form-group';
            const originalPopAnim = selectedZombie?.objdata?.PopAnim || '';
            const currentPopAnim = editedTypeData['PopAnim'] || '';
            const showCurrentPopAnim = currentPopAnim && currentPopAnim !== originalPopAnim;
            const popAnimInputValue = showCurrentPopAnim ? currentPopAnim : '';
            const popAnimPlaceholder = originalPopAnim ? `Original: ${originalPopAnim}` : 'Type to search or leave blank...';
            let popAnimHtml = `<label>PopAnim</label>`;
            popAnimHtml += `
                <div class="search-box" style="display: flex; gap: 5px; margin-bottom: 8px;">
                    <input type="text" id="popAnimInput" value="${escapeHtml(popAnimInputValue)}" placeholder="${escapeHtml(popAnimPlaceholder)}" class="search-input" style="flex: 1;">
                    <div id="popAnimSuggestions" class="suggestions"></div>
                    <button onclick="setPopAnim()" style="padding:6px 12px;background:#3a5a3a;border:1px solid #4a6a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;">Apply</button>
                </div>
                <div style="margin-top:10px;">
                    <label style="font-size:0.85em;color:#aaa;">Or add from another zombie:</label>
                    <div class="search-box" style="margin-top:6px;">
                        <input type="text" id="bulkAddZombieInputPopAnim" placeholder="Type zombie name..." class="search-input">
                        <div id="bulkAddZombieInputPopAnimSuggestions" class="suggestions"></div>
                    </div>
                    <button onclick="bulkAddPopAnimFromZombie()" style="padding:6px 12px;background:#3a5a3a;border:1px solid #4a6a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;margin-top:6px;width:100%;">Use PopAnim</button>
                </div>
            `;
            popAnimGroup.innerHTML = popAnimHtml;
            advancedTypeBody.appendChild(popAnimGroup);

            // Add ResourceGroups selector with autocomplete
            const resGroupGroup = document.createElement('div');
            resGroupGroup.className = 'form-group';
            let resGroupHtml = `<label>ResourceGroups</label>`;
            if (selectedZombie && selectedZombie.objdata && Array.isArray(selectedZombie.objdata.ResourceGroups) && selectedZombie.objdata.ResourceGroups.length > 0) {
                resGroupHtml += `<div style="padding:6px;background:#2a3a2a;border:1px solid #3a5a3a;border-radius:3px;margin-bottom:6px;font-size:0.9em;"><strong>Original:</strong> ${selectedZombie.objdata.ResourceGroups.join(', ')}</div>`;
            }
            resGroupHtml += `
                <div id="resGroupsList" style="display:flex;flex-direction:column;gap:6px;margin-bottom:10px;"></div>
                <div style="display:flex;gap:5px;margin-bottom:8px;">
                    <div class="search-box" style="flex:1;">
                        <input type="text" id="resGroupInput" placeholder="Type to search..." class="search-input">
                        <div id="resGroupSuggestions" class="suggestions"></div>
                    </div>
                    <button onclick="addResourceGroup()" style="padding:6px 12px;background:#3a5a3a;border:1px solid #4a6a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;">Add</button>
                </div>
                <div style="margin-top:10px;">
                    <label style="font-size:0.85em;color:#aaa;">Or add from another zombie:</label>
                    <div class="search-box" style="margin-top:6px;">
                        <input type="text" id="bulkAddZombieInput" placeholder="Type zombie name..." class="search-input">
                        <div id="bulkAddZombieInputSuggestions" class="suggestions"></div>
                    </div>
                    <button onclick="bulkAddResourceGroups()" style="padding:6px 12px;background:#3a5a3a;border:1px solid #4a6a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;margin-top:6px;width:100%;">Add All</button>
                </div>
            `;
            resGroupGroup.innerHTML = resGroupHtml;
            advancedTypeBody.appendChild(resGroupGroup);
            renderResourceGroups();

            // Add AudioGroups selector with autocomplete
            const audioGroupGroup = document.createElement('div');
            audioGroupGroup.className = 'form-group';
            let audioGroupHtml = `<label>AudioGroups</label>`;
            if (selectedZombie && selectedZombie.objdata && Array.isArray(selectedZombie.objdata.AudioGroups) && selectedZombie.objdata.AudioGroups.length > 0) {
                audioGroupHtml += `<div style="padding:6px;background:#2a3a2a;border:1px solid #3a5a3a;border-radius:3px;margin-bottom:6px;font-size:0.9em;"><strong>Original:</strong> ${selectedZombie.objdata.AudioGroups.join(', ')}</div>`;
            }
            audioGroupHtml += `
                <div id="audioGroupsList" style="display:flex;flex-direction:column;gap:6px;margin-bottom:10px;"></div>
                <div style="display:flex;gap:5px;margin-bottom:8px;">
                    <div class="search-box" style="flex:1;">
                        <input type="text" id="audioGroupInput" placeholder="Type to search..." class="search-input">
                        <div id="audioGroupSuggestions" class="suggestions"></div>
                    </div>
                    <button onclick="addAudioGroup()" style="padding:6px 12px;background:#3a5a3a;border:1px solid #4a6a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;">Add</button>
                </div>
                <div style="margin-top:10px;">
                    <label style="font-size:0.85em;color:#aaa;">Or add from another zombie:</label>
                    <div class="search-box" style="margin-top:6px;">
                        <input type="text" id="bulkAddZombieInputAudio" placeholder="Type zombie name..." class="search-input">
                        <div id="bulkAddZombieInputAudioSuggestions" class="suggestions"></div>
                    </div>
                    <button onclick="bulkAddAudioGroups()" style="padding:6px 12px;background:#3a5a3a;border:1px solid #4a6a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;margin-top:6px;width:100%;">Add All</button>
                </div>
            `;
            audioGroupGroup.innerHTML = audioGroupHtml;
            advancedTypeBody.appendChild(audioGroupGroup);
            renderAudioGroups();

            // Setup autocompletes
            setTimeout(() => {
                setupPopAnimAutocomplete();
                setupBulkAddPopAnimZombieAutocomplete();
                setupResourceGroupAutocomplete();
                setupAudioGroupAutocomplete();
                setupBulkAddZombieAutocomplete();
                setupBulkAddAudioZombieAutocomplete();
                applyTemplateTypeLock();
            }, 0);
        }

        function isRectObject(obj) {
            if (typeof obj !== 'object' || obj === null || Array.isArray(obj)) return false;
            const keys = Object.keys(obj);
            const rectKeys = ['mHeight', 'mWidth', 'mX', 'mY'];
            return keys.length === 4 && rectKeys.every(k => keys.includes(k));
        }

        function renderAliases() {
            const cont = document.getElementById('aliasesContainer');
            if (!cont) return;
            cont.innerHTML = '';
            editedTypeAliases = editedTypeAliases || [];
            if (editedTypeAliases.length === 0) {
                const p = document.createElement('div');
                p.style.color = '#999';
                p.textContent = 'No aliases set';
                cont.appendChild(p);
                return;
            }

            editedTypeAliases.forEach((a, i) => {
                const row = document.createElement('div');
                row.style.display = 'flex';
                row.style.gap = '6px';
                row.innerHTML = `<input type="text" value="${a}" data-alias-index="${i}" onchange="updateAlias(this)" style="flex:1;padding:6px;background:#3a3a3a;border:1px solid #4a4a4a;color:#e0e0e0;">
                    <button onclick="removeAlias(${i})" style="padding:6px 10px;">Remove</button>`;
                cont.appendChild(row);
            });
        }

        function setPopAnim() {
            const inp = document.getElementById('popAnimInput');
            if (!inp) return;
            const val = inp.value.trim();
            const original = selectedZombie?.objdata?.PopAnim || '';
            if (!val) {
                editedTypeData['PopAnim'] = original || '';
                inp.value = '';
                return;
            }
            if (original && val === original) {
                editedTypeData['PopAnim'] = original;
                inp.value = '';
                return;
            }
            editedTypeData['PopAnim'] = val;
        }

        function setupPopAnimAutocomplete() {
            const inp = document.getElementById('popAnimInput');
            const suggBox = document.getElementById('popAnimSuggestions');
            if (!inp || !suggBox) return;

            const renderSuggestions = (query) => {
                const q = query.toLowerCase();
                const source = q ? allPopAnims.filter(a => a.toLowerCase().includes(q)) : allPopAnims.slice();
                const matches = source.slice(0, 30);
                suggBox.innerHTML = '';
                if (matches.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }
                matches.forEach(m => {
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = m;
                    div.onclick = () => {
                        inp.value = m;
                        editedTypeData['PopAnim'] = m;
                        suggBox.classList.remove('active');
                    };
                    suggBox.appendChild(div);
                });
                suggBox.classList.add('active');
            };

            inp.addEventListener('input', (e) => {
                renderSuggestions(e.target.value || '');
            });

            inp.addEventListener('focus', () => {
                renderSuggestions(inp.value || '');
            });

            inp.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    setPopAnim();
                    suggBox.classList.remove('active');
                }
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('#popAnimInput') && !e.target.closest('#popAnimSuggestions')) {
                    suggBox.classList.remove('active');
                }
            });
        }

        function setupBulkAddPopAnimZombieAutocomplete() {
            const inp = document.getElementById('bulkAddZombieInputPopAnim');
            const suggBox = document.getElementById('bulkAddZombieInputPopAnimSuggestions');
            if (!inp || !suggBox) return;

            inp.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                suggBox.innerHTML = '';
                if (q.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }

                const matches = allZombieTypes.filter(zombie => {
                    if (!zombie || !zombie.objdata || !zombie.objdata.PopAnim) return false;
                    if (!Array.isArray(zombie.aliases)) return false;
                    return zombie.aliases.some(alias => alias.toLowerCase().includes(q));
                }).slice(0, 15);

                if (matches.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }

                matches.forEach(z => {
                    const alias = z.aliases?.[0] || 'Unknown';
                    const label = `${alias} (${z.objdata.PopAnim})`;
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = label;
                    div.title = z.objdata.PopAnim;
                    div.onclick = () => {
                        inp.value = alias;
                        suggBox.classList.remove('active');
                    };
                    suggBox.appendChild(div);
                });
                suggBox.classList.add('active');
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('#bulkAddZombieInputPopAnim') && !e.target.closest('#bulkAddZombieInputPopAnimSuggestions')) {
                    suggBox.classList.remove('active');
                }
            });
        }

        function setupResourceGroupAutocomplete() {
            const inp = document.getElementById('resGroupInput');
            const suggBox = document.getElementById('resGroupSuggestions');
            if (!inp || !suggBox) return;

            inp.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                suggBox.innerHTML = '';
                if (q.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }
                const matches = allResourceGroups.filter(a => a.toLowerCase().includes(q)).slice(0, 30);
                if (matches.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }
                matches.forEach(m => {
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = m;
                    div.onclick = () => {
                        inp.value = m;
                        suggBox.classList.remove('active');
                    };
                    suggBox.appendChild(div);
                });
                suggBox.classList.add('active');
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('#resGroupInput')) {
                    suggBox.classList.remove('active');
                }
            });
        }

        function setupAudioGroupAutocomplete() {
            const inp = document.getElementById('audioGroupInput');
            const suggBox = document.getElementById('audioGroupSuggestions');
            if (!inp || !suggBox) return;

            inp.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                suggBox.innerHTML = '';
                if (q.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }
                const matches = allAudioGroups.filter(a => a.toLowerCase().includes(q)).slice(0, 30);
                if (matches.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }
                matches.forEach(m => {
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = m;
                    div.onclick = () => {
                        inp.value = m;
                        suggBox.classList.remove('active');
                    };
                    suggBox.appendChild(div);
                });
                suggBox.classList.add('active');
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('#audioGroupInput')) {
                    suggBox.classList.remove('active');
                }
            });
        }

        function setupBulkAddZombieAutocomplete() {
            const inp = document.getElementById('bulkAddZombieInput');
            const suggBox = document.getElementById('bulkAddZombieInputSuggestions');
            if (!inp || !suggBox) return;

            inp.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                suggBox.innerHTML = '';
                if (q.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }

                // Find matching zombies by alias
                const matches = allZombieTypes.filter(zombie => {
                    if (zombie.aliases && Array.isArray(zombie.aliases)) {
                        return zombie.aliases.some(alias => alias.toLowerCase().includes(q));
                    }
                    return false;
                }).slice(0, 15);

                if (matches.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }

                matches.forEach(z => {
                    const alias = z.aliases?.[0] || 'Unknown';
                    const resGroups = (z.objdata?.ResourceGroups || []);
                    const label = resGroups.length > 0 ? `${alias} (${resGroups.length} groups)` : alias;
                    
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = label;
                    div.title = resGroups.join(', ');
                    div.onclick = () => {
                        inp.value = alias;
                        suggBox.classList.remove('active');
                    };
                    suggBox.appendChild(div);
                });
                suggBox.classList.add('active');
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('#bulkAddZombieInput')) {
                    suggBox.classList.remove('active');
                }
            });
        }

        function setupBulkAddAudioZombieAutocomplete() {
            const inp = document.getElementById('bulkAddZombieInputAudio');
            const suggBox = document.getElementById('bulkAddZombieInputAudioSuggestions');
            if (!inp || !suggBox) return;

            inp.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase();
                suggBox.innerHTML = '';
                if (q.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }

                // Find matching zombies by alias
                const matches = allZombieTypes.filter(zombie => {
                    if (zombie.aliases && Array.isArray(zombie.aliases)) {
                        return zombie.aliases.some(alias => alias.toLowerCase().includes(q));
                    }
                    return false;
                }).slice(0, 15);

                if (matches.length === 0) {
                    suggBox.classList.remove('active');
                    return;
                }

                matches.forEach(z => {
                    const alias = z.aliases?.[0] || 'Unknown';
                    const audioGroups = (z.objdata?.AudioGroups || []);
                    const label = audioGroups.length > 0 ? `${alias} (${audioGroups.length} groups)` : alias;
                    
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = label;
                    div.title = audioGroups.join(', ');
                    div.onclick = () => {
                        inp.value = alias;
                        suggBox.classList.remove('active');
                    };
                    suggBox.appendChild(div);
                });
                suggBox.classList.add('active');
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('#bulkAddZombieInputAudio')) {
                    suggBox.classList.remove('active');
                }
            });
        }

        function addAlias() {
            const inp = document.getElementById('newAliasInput');
            const v = inp.value.trim();
            if (!v) return;
            editedTypeAliases.push(v);
            inp.value = '';
            renderAliases();
        }

        function updateAlias(element) {
            const idx = parseInt(element.dataset.aliasIndex);
            editedTypeAliases[idx] = element.value;
        }

        function removeAlias(index) {
            editedTypeAliases.splice(index, 1);
            renderAliases();
        }

        function updatePropertiesField(element) {
            const value = element.value;
            editedTypeData['Properties'] = makeRTID(value, '.');
        }

        function getTemplateDefByKey(key) {
            return ZOMBIE_TEMPLATE_DEFS.find(def => def.key === key);
        }

        function detectTemplateFamilyForZombie(zombie) {
            if (!zombie) return '';
            const aliases = Array.isArray(zombie.aliases) ? zombie.aliases : [];
            const classText = (zombie.objdata?.ZombieClass || '').toLowerCase();

            // Primary: alias pattern match (stricter than "contains")
            for (const def of ZOMBIE_TEMPLATE_DEFS) {
                const matched = aliases.some(a => {
                    const low = String(a || '').toLowerCase();
                    return low.startsWith(def.key + '_') || low === def.key || low.includes('_' + def.key + '_');
                });
                if (matched) return def.key;
            }

            // Secondary: class-name hints for common families
            const classHints = [
                { key: 'basic', tokens: ['zombiebasic', 'zombielostcitybasic', 'zombieskycitybasic'] },
                { key: 'imp', tokens: ['imp'] },
                { key: 'gargantuar', tokens: ['gargantuar'] },
                { key: 'barrel', tokens: ['barrel'] },
                { key: 'cannon', tokens: ['cannon'] },
                { key: 'shield', tokens: ['protector'] },
                { key: 'footballmech', tokens: ['mechfootball', 'toycar'] },
                { key: 'zombotany', tokens: ['zombotany'] },
                { key: 'tombraiser', tokens: ['tombraiser'] },
                { key: 'troglobite', tokens: ['troglobite'] },
                { key: 'boombox', tokens: ['boombox'] },
                { key: 'breakdancer', tokens: ['disco', 'break'] },
                { key: 'fisherman', tokens: ['fisher'] },
                { key: 'yeti', tokens: ['yeti'] },
                { key: 'magician', tokens: ['magician'] },
                { key: 'weaselhoarder', tokens: ['weasel'] },
                { key: 'caesar', tokens: ['caesar'] },
                { key: 'cardio', tokens: ['cardio'] },
                { key: 'healer', tokens: ['healer'] },
                { key: 'rocket', tokens: ['rocket'] },
                { key: 'battleplane', tokens: ['battleplane', 'plane'] },
                { key: 'carnivalhat', tokens: ['carnivalhat'] },
                { key: 'shikaisen', tokens: ['shikaisen'] },
                { key: 'servant', tokens: ['servant', 'maid'] },
                { key: 'octopus', tokens: ['octopus'] },
                { key: 'hunter', tokens: ['hunter'] },
                { key: 'excavator', tokens: ['excavator'] },
                { key: 'vendor', tokens: ['vendor'] },
                { key: 'superfan', tokens: ['superfan'] },
                { key: 'electric', tokens: ['electric'] },
                { key: 'juggler', tokens: ['juggler'] },
                { key: 'consultant', tokens: ['consultant'] },
                { key: 'hamsterball', tokens: ['hamster'] },
                { key: 'imptwin', tokens: ['imptwin'] },
                { key: 'bug', tokens: ['bug'] },
                { key: 'bass', tokens: ['bass'] },
                { key: 'dove', tokens: ['dove'] },
                { key: 'zmech', tokens: ['zmech', 'futuremech', 'shikaisen', 'wealth'] }
            ];

            for (const hint of classHints) {
                if (hint.tokens.some(token => classText.includes(token))) {
                    return hint.key;
                }
            }

            return '';
        }

        function setTemplateMode(element) {
            templateModeEnabled = !!element?.checked;
            applyTemplateTypeLock();
        }

        function applyTemplateTypeLock() {
            const container = document.getElementById('typeProperties');
            if (!container) return;

            const controls = container.querySelectorAll('input, textarea, select, button');
            controls.forEach(ctrl => {
                if (ctrl.closest('#templateHelperBlock')) return;
                ctrl.disabled = !!templateModeEnabled;
            });
        }

        function updateTemplatePreview() {
            const familySelect = document.getElementById('templateFamilySelect');
            const indexInput = document.getElementById('templateIndexInput');
            const modeCheckbox = document.getElementById('templateModeCheckbox');
            const preview = document.getElementById('templatePreview');
            if (!indexInput || !preview) return;

            if (familySelect) {
                selectedTemplateFamily = familySelect.value || '';
            }

            let index = parseInt(indexInput.value, 10);
            if (isNaN(index)) index = 1;

            const def = getTemplateDefByKey(selectedTemplateFamily);
            if (!def) {
                preview.textContent = 'Template disabled. Select a family to enable template naming.';
                if (modeCheckbox) {
                    modeCheckbox.checked = false;
                    modeCheckbox.disabled = true;
                }
                templateModeEnabled = false;
                applyTemplateTypeLock();
                return;
            }

            if (index < def.min) index = def.min;
            if (index > def.max) index = def.max;
            indexInput.value = index;
            selectedTemplateIndex = index;
            if (modeCheckbox) modeCheckbox.disabled = false;

            const typeName = `${def.typePrefix}${index}`;
            const propsAlias = `${def.propsBase}${index}Props`;
            preview.textContent = `TypeName/Alias: ${typeName} | Properties: ${propsAlias}`;
        }

        function applySelectedTemplate() {
            const indexInput = document.getElementById('templateIndexInput');
            if (!indexInput) return;

            const def = getTemplateDefByKey(selectedTemplateFamily || '');
            if (!def) {
                alert('Select a template family first.');
                return;
            }

            let index = parseInt(indexInput.value, 10);
            if (isNaN(index)) index = def.min;
            if (index < def.min) index = def.min;
            if (index > def.max) index = def.max;
            indexInput.value = index;

            const typeName = `${def.typePrefix}${index}`;
            const propsAlias = `${def.propsBase}${index}Props`;

            if (!Array.isArray(editedTypeAliases) || editedTypeAliases.length === 0) {
                editedTypeAliases = [typeName];
            } else {
                editedTypeAliases[0] = typeName;
            }
            editedTypeData['Properties'] = makeRTID(propsAlias, '.');

            selectedTemplateFamily = def.key;
            selectedTemplateIndex = index;
            templateModeEnabled = true;

            buildTypeForm();
        }

        function updateZombossTemplate(element) {
            selectedZombossTemplate = element.value;
        }

        function renderResourceGroups() {
            const container = document.getElementById('resGroupsList');
            if (!container) return;
            container.innerHTML = '';
            const resGroups = editedTypeData['ResourceGroups'] || [];
            if (resGroups.length === 0) {
                container.innerHTML = '<p style="color:#999;font-size:0.85em;margin:0;">No ResourceGroups added</p>';
                return;
            }
            resGroups.forEach((rg, idx) => {
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.gap = '5px';
                div.style.padding = '6px';
                div.style.background = '#2a2a2a';
                div.style.borderRadius = '3px';
                div.innerHTML = `
                    <span style="flex:1;color:#aaffaa;">${rg}</span>
                    <button onclick="removeResourceGroup(${idx})" style="padding:4px 8px;background:#5a3a3a;border:1px solid #6a4a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;">✕</button>
                `;
                container.appendChild(div);
            });
        }

        function addResourceGroup() {
            const input = document.getElementById('resGroupInput');
            const rg = input.value.trim();
            if (!rg) {
                alert('Enter a ResourceGroup');
                return;
            }
            if (!editedTypeData['ResourceGroups']) {
                editedTypeData['ResourceGroups'] = [];
            }
            if (!editedTypeData['ResourceGroups'].includes(rg)) {
                editedTypeData['ResourceGroups'].push(rg);
                input.value = '';
                renderResourceGroups();
            } else {
                alert('This ResourceGroup is already added');
            }
        }

        function removeResourceGroup(index) {
            if (editedTypeData['ResourceGroups']) {
                editedTypeData['ResourceGroups'].splice(index, 1);
                renderResourceGroups();
            }
        }

        function bulkAddResourceGroups() {
            const input = document.getElementById('bulkAddZombieInput');
            const selectedAlias = input.value.trim();
            if (!selectedAlias) {
                alert('Enter a zombie name');
                return;
            }
            const zombie = allZombieTypes.find(z => z.aliases && z.aliases[0] === selectedAlias);
            if (!zombie || !zombie.objdata || !Array.isArray(zombie.objdata.ResourceGroups)) {
                alert('Zombie not found or has no ResourceGroups');
                return;
            }
            if (!editedTypeData['ResourceGroups']) {
                editedTypeData['ResourceGroups'] = [];
            }
            const added = [];
            zombie.objdata.ResourceGroups.forEach(rg => {
                if (!editedTypeData['ResourceGroups'].includes(rg)) {
                    editedTypeData['ResourceGroups'].push(rg);
                    added.push(rg);
                }
            });
            input.value = '';
            renderResourceGroups();
            alert(`Added ${added.length} ResourceGroups: ${added.join(', ')}`);
        }

        function bulkAddPopAnimFromZombie() {
            const input = document.getElementById('bulkAddZombieInputPopAnim');
            const popAnimInput = document.getElementById('popAnimInput');
            const selectedAlias = input?.value.trim();
            if (!selectedAlias) {
                alert('Enter a zombie name');
                return;
            }
            const zombie = allZombieTypes.find(z => z.aliases && z.aliases[0] === selectedAlias);
            const popAnim = zombie?.objdata?.PopAnim;
            if (!popAnim) {
                alert('Zombie not found or has no PopAnim');
                return;
            }

            editedTypeData['PopAnim'] = popAnim;
            if (popAnimInput) {
                popAnimInput.value = popAnim;
            }
            if (input) {
                input.value = '';
            }
        }

        function renderAudioGroups() {
            const container = document.getElementById('audioGroupsList');
            if (!container) return;
            container.innerHTML = '';
            const audioGroups = editedTypeData['AudioGroups'] || [];
            if (audioGroups.length === 0) {
                container.innerHTML = '<p style="color:#999;font-size:0.85em;margin:0;">No AudioGroups added</p>';
                return;
            }
            audioGroups.forEach((ag, idx) => {
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.gap = '5px';
                div.style.padding = '6px';
                div.style.background = '#2a2a2a';
                div.style.borderRadius = '3px';
                div.innerHTML = `
                    <span style="flex:1;color:#aaffaa;">${ag}</span>
                    <button onclick="removeAudioGroup(${idx})" style="padding:4px 8px;background:#5a3a3a;border:1px solid #6a4a4a;color:#e0e0e0;cursor:pointer;border-radius:3px;">✕</button>
                `;
                container.appendChild(div);
            });
        }

        function addAudioGroup() {
            const input = document.getElementById('audioGroupInput');
            const ag = input.value.trim();
            if (!ag) {
                alert('Enter an AudioGroup');
                return;
            }
            if (!editedTypeData['AudioGroups']) {
                editedTypeData['AudioGroups'] = [];
            }
            if (!editedTypeData['AudioGroups'].includes(ag)) {
                editedTypeData['AudioGroups'].push(ag);
                input.value = '';
                renderAudioGroups();
            } else {
                alert('This AudioGroup is already added');
            }
        }

        function removeAudioGroup(index) {
            if (editedTypeData['AudioGroups']) {
                editedTypeData['AudioGroups'].splice(index, 1);
                renderAudioGroups();
            }
        }

        function bulkAddAudioGroups() {
            const input = document.getElementById('bulkAddZombieInputAudio');
            const selectedAlias = input.value.trim();
            if (!selectedAlias) {
                alert('Enter a zombie name');
                return;
            }
            const zombie = allZombieTypes.find(z => z.aliases && z.aliases[0] === selectedAlias);
            if (!zombie || !zombie.objdata || !Array.isArray(zombie.objdata.AudioGroups)) {
                alert('Zombie not found or has no AudioGroups');
                return;
            }
            if (!editedTypeData['AudioGroups']) {
                editedTypeData['AudioGroups'] = [];
            }
            const added = [];
            zombie.objdata.AudioGroups.forEach(ag => {
                if (!editedTypeData['AudioGroups'].includes(ag)) {
                    editedTypeData['AudioGroups'].push(ag);
                    added.push(ag);
                }
            });
            input.value = '';
            renderAudioGroups();
            alert(`Added ${added.length} AudioGroups: ${added.join(', ')}`);
        }
        
