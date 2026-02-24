        function buildPropsForm() {
            const container = document.getElementById('propsProperties');
            container.innerHTML = '';

            // Add Zomboss template selector if this is a Zomboss
            const isZomboss = editedPropsData?.Stages && Array.isArray(editedPropsData.Stages);
            if (isZomboss) {
                const templateGroup = document.createElement('div');
                templateGroup.className = 'form-group';
                let templateHtml = `<label style="font-weight: bold; color: #ffcc00;">Zomboss Template</label>`;
                templateHtml += `<select id="zombossTemplateSelect" style="padding: 8px; background: #3a4a3a; border: 1px solid #5a6a5a; color: #e0e0e0; width: 100%;" onchange="updateZombossTemplate(this)">`;
                templateHtml += `<option value="">-- Select a world template --</option>`;
                ZOMBOSS_TEMPLATES.forEach(t => {
                    templateHtml += `<option value="${t}" ${selectedZombossTemplate === t ? 'selected' : ''}>${t}</option>`;
                });
                templateHtml += `</select>`;
                templateGroup.innerHTML = templateHtml;
                container.appendChild(templateGroup);
            }

            const objdata = editedPropsData;
            const skipKeys = ['ScaledProps', 'ZombieStats', 'Actions', 'Stages'];

            for (const [key, value] of Object.entries(objdata)) {
                if (skipKeys.includes(key)) continue;

                const group = document.createElement('div');
                group.className = 'form-group';

                if (isCommentKey(key)) {
                    group.className = 'form-group comment-field';
                    group.innerHTML = `<label>${escapeHtml(key)}</label><div class="comment-text">${escapeHtml(commentValueToText(value))}</div>`;
                    container.appendChild(group);
                    continue;
                }
                
                // Special handling for ZombieArmorProps
                if (key === 'ZombieArmorProps') {
                    let armorHtml = `<label>${key}</label><div style="display: flex; flex-direction: column; gap: 8px;">`;
                    const armorList = Array.isArray(value) ? value : [];
                    
                    armorList.forEach((armor, index) => {
                        const armorName = extractRTIDName(armor);
                        armorHtml += `<div style="display: flex; gap: 5px;">
                            <input type="text" value="${armorName}" 
                                   onchange="updateArmorItem(this, ${index})" 
                                   style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            <button onclick="removeArmor(${index})" style="padding: 5px 10px;">Remove</button>
                        </div>`;
                    });
                    
                    armorHtml += `<div style="display: flex; gap: 5px;">
                        <select id="armorSelect" style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            <option value="">-- Custom or select --</option>`;
                    
                    allArmors.forEach(armor => {
                        armorHtml += `<option value="${armor}">${armor}</option>`;
                    });
                    
                    armorHtml += `</select>
                        <input type="text" id="customArmor" placeholder="Custom armor" 
                               style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                        <button onclick="addArmor()" style="padding: 5px 10px;">Add</button>
                    </div></div>`;
                    
                    group.innerHTML = armorHtml;
                } else if (key === 'ConditionImmunities') {
                    let condHtml = `<label>${key}</label><div style="display: flex; flex-direction: column; gap: 8px;">`;
                    const condList = Array.isArray(value) ? value : [];
                    
                    condList.forEach((cond, index) => {
                        const condName = cond.Condition || '';
                        const percent = cond.Percent !== undefined ? cond.Percent : '';
                        condHtml += `<div style="display: flex; gap: 5px;">
                            <input type="text" value="${condName}" placeholder="Condition" data-cond-index="${index}" 
                                   onchange="updateConditionItem(this, ${index}, 'condition')" 
                                   style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            <input type="number" value="${percent}" step="0.01" min="0" max="1" placeholder="% (blank=infinite)" data-cond-index="${index}"
                                   onchange="updateConditionItem(this, ${index}, 'percent')"
                                   style="width: 140px; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            <button onclick="removeCondition(${index})" style="padding: 5px 10px;">Remove</button>
                        </div>`;
                    });
                    
                    condHtml += `<div style="display: flex; gap: 5px;">
                        <select id="conditionSelect" style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            <option value="">-- Select condition --</option>`;
                    
                    CONDITION_LIST.forEach(cond => {
                        condHtml += `<option value="${cond}">${cond}</option>`;
                    });
                    
                    condHtml += `</select>
                        <input type="number" id="conditionPercent" value="" step="0.01" min="0" max="1" placeholder="% (leave blank = infinite)" 
                               style="width: 140px; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                        <button onclick="addCondition()" style="padding: 5px 10px;">Add</button>
                    </div></div>`;
                    
                    group.innerHTML = condHtml;
                } else if (isIncludeExcludeListObject(value)) {
                    const listObj = value && typeof value === 'object' ? value : { List: [], ListType: 'includelist' };
                    const listValues = Array.isArray(listObj.List) ? listObj.List : [];
                    const listTypeRaw = typeof listObj.ListType === 'string' ? listObj.ListType : 'includelist';
                    const listTypeNorm = listTypeRaw.toLowerCase();
                    const includeSelected = listTypeNorm !== 'excludelist';
                    const excludeSelected = listTypeNorm === 'excludelist';
                    const customTypeOption =
                        listTypeNorm !== 'includelist' && listTypeNorm !== 'excludelist'
                            ? `<option value="${listTypeRaw}" selected>${listTypeRaw}</option>`
                            : '';

                    let listHtml = `<label>${key}</label><div style="display: flex; flex-direction: column; gap: 8px;">`;
                    listHtml += `<div style="display: flex; gap: 8px; align-items: center;">
                        <label style="min-width: 70px;">ListType</label>
                        <select data-props-key="${key}" onchange="updateIncludeExcludeListType(this)"
                                style="padding: 6px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            <option value="includelist" ${includeSelected ? 'selected' : ''}>includelist</option>
                            <option value="excludelist" ${excludeSelected ? 'selected' : ''}>excludelist</option>
                            ${customTypeOption}
                        </select>
                    </div>`;

                    listValues.forEach((item, index) => {
                        listHtml += `<div style="display: flex; gap: 5px;">
                            <input type="text" value="${item}" data-props-key="${key}" data-list-index="${index}"
                                   onchange="updateIncludeExcludeListItem(this)"
                                   style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            <button onclick="removeIncludeExcludeListItem('${key}', ${index})" style="padding: 5px 10px;">Remove</button>
                        </div>`;
                    });

                    if (listValues.length === 0) {
                        listHtml += `<div style="color: #999; font-size: 0.85em;">No entries in list</div>`;
                    }

                    listHtml += `<div style="display: flex; gap: 5px;">
                        <input type="text" placeholder="Add list entry"
                               style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                        <button onclick="addIncludeExcludeListItem('${key}', this)" style="padding: 5px 10px;">Add</button>
                    </div></div>`;

                    group.innerHTML = listHtml;
                } else if (isRectObject(value)) {
                    let rectHtml = `<label>${key}</label><div class="rect-fields">`;
                    const rect = value || { mHeight: 0, mWidth: 0, mX: 0, mY: 0 };
                    
                    for (const [subkey, subvalue] of Object.entries(rect)) {
                        rectHtml += `<div class="rect-field">
                            <label>${subkey}</label>
                            <input type="number" data-props-key="${key}" data-rect-field="${subkey}" 
                                   value="${subvalue}" onchange="updateRectData(this)">
                        </div>`;
                    }
                    rectHtml += '</div>';
                    group.innerHTML = rectHtml;
                } else if (isCoordinateObject(value)) {
                    let coordHtml = `<label>${key}</label><div class="rect-fields">`;
                    
                    for (const [subkey, subvalue] of Object.entries(value)) {
                        coordHtml += `<div class="rect-field">
                            <label>${subkey}</label>
                            <input type="number" data-props-key="${key}" data-coord-field="${subkey}" 
                                   value="${subvalue}" step="0.01" onchange="updateCoordData(this, 'props')">
                        </div>`;
                    }
                    coordHtml += '</div>';
                    group.innerHTML = coordHtml;
                } else if (isMinMaxObject(value)) {
                    let minmaxHtml = `<label>${key}</label><div class="rect-fields">`;
                    
                    for (const [subkey, subvalue] of Object.entries(value)) {
                        minmaxHtml += `<div class="rect-field">
                            <label>${subkey}</label>
                            <input type="number" data-props-key="${key}" data-minmax-field="${subkey}" 
                                   value="${subvalue}" step="0.01" onchange="updateMinMaxData(this, 'props')">
                        </div>`;
                    }
                    minmaxHtml += '</div>';
                    group.innerHTML = minmaxHtml;
                } else {
                    const valueType = typeof value;
                    let input;
                    const defaultVal = defaultPropsData[key] !== undefined ? defaultPropsData[key] : '';

                    if (valueType === 'object' && value !== null) {
                        input = `<textarea data-props-key="${key}" onchange="updatePropsData(this)" style="min-height: 60px;">${JSON.stringify(value, null, 2)}</textarea>`;
                    } else if (valueType === 'number') {
                        input = `<input type="number" data-props-key="${key}" value="${value}" step="0.01" placeholder="${defaultVal}" onchange="updatePropsData(this)">`;
                    } else if (valueType === 'boolean') {
                        input = `<input type="checkbox" data-props-key="${key}" onchange="updatePropsData(this)" ${value ? 'checked' : ''}>`;
                    } else {
                        input = `<input type="text" data-props-key="${key}" value="${value}" placeholder="${defaultVal}" onchange="updatePropsData(this)">`;
                    }

                    group.innerHTML = `<label>${key}</label>${input}`;
                }
                container.appendChild(group);
            }

            // Special handling for HealthThresholdToImpAmmoLayers (render if present in objdata)
            if ('HealthThresholdToImpAmmoLayers' in editedPropsData) {
                const group = document.createElement('div');
                group.className = 'form-group';
                const list = Array.isArray(editedPropsData['HealthThresholdToImpAmmoLayers']) ? editedPropsData['HealthThresholdToImpAmmoLayers'] : [];

                let html = `<label>HealthThresholdToImpAmmoLayers</label><div style="display:flex;flex-direction:column;gap:10px;">`;

                list.forEach((entry, ei) => {
                    const percent = entry.HealthPercentThrowImp !== undefined ? entry.HealthPercentThrowImp : '';
                    const layers = Array.isArray(entry.ProjectileLayersToHide) ? entry.ProjectileLayersToHide : [];

                    html += `<div style="padding:8px;background:#2a2a2a;border:1px solid #4a4a4a;border-radius:4px;">
                        <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
                            <label style="width:200px;">HealthPercentThrowImp</label>
                            <input type="number" data-health-entry="${ei}" value="${percent}" step="0.01" min="0" max="1" onchange="updateHealthLayerEntry(this, ${ei}, 'percent')" style="width:120px;padding:6px;background:#3a3a3a;border:1px solid #4a4a4a;color:#e0e0e0;">
                            <button onclick="removeHealthLayerEntry(${ei})" style="padding:6px 10px;margin-left:auto;">Remove Entry</button>
                        </div>
                        <div style="display:flex;flex-direction:column;gap:6px;">
                            <div id="healthLayersList_${ei}"></div>
                            <div style="display:flex;gap:6px;margin-top:6px;">
                                <input type="text" id="newLayerInput_${ei}" placeholder="add layer name" style="flex:1;padding:6px;background:#3a3a3a;border:1px solid #4a4a4a;color:#e0e0e0;">
                                <button onclick="addLayerToEntry(${ei})" style="padding:6px 10px;">Add Layer</button>
                            </div>
                        </div>
                    </div>`;
                });

                html += `<div style="display:flex;gap:6px;">
                    <button onclick="addHealthLayerEntry()" style="padding:8px 12px;">Add Health Threshold Entry</button>
                </div></div>`;

                group.innerHTML = html;
                container.appendChild(group);

                // Render layer lists after DOM insertion
                setTimeout(() => {
                    (editedPropsData['HealthThresholdToImpAmmoLayers'] || []).forEach((entry, ei) => {
                        renderHealthLayersList(ei);
                    });
                }, 0);
            }

                // Ensure ZombieArmorProps exists (empty by default)
                if (!('ZombieArmorProps' in editedPropsData)) {
                    editedPropsData['ZombieArmorProps'] = [];
                }

                // Add ChillInsteadOfFreeze if not present
            if (!('ChillInsteadOfFreeze' in editedPropsData)) {
                const group = document.createElement('div');
                group.className = 'form-group';
                group.innerHTML = `
                    <label>ChillInsteadOfFreeze</label>
                    <input type="checkbox" data-props-key="ChillInsteadOfFreeze" onchange="updatePropsData(this)">
                `;
                group.className = 'form-group bool-row';
                container.appendChild(group);
                editedPropsData['ChillInsteadOfFreeze'] = false;
                if (!('ChillInsteadOfFreeze' in defaultPropsData)) defaultPropsData['ChillInsteadOfFreeze'] = false;
            }

            // Add FireDamageMultiplier if not present
            if (!('FireDamageMultiplier' in editedPropsData)) {
                const group = document.createElement('div');
                group.className = 'form-group';
                group.innerHTML = `
                    <label>FireDamageMultiplier</label>
                    <input type="number" data-props-key="FireDamageMultiplier" value="1" step="0.01" onchange="updatePropsData(this)">
                `;
                container.appendChild(group);
                editedPropsData['FireDamageMultiplier'] = 1;
                if (!('FireDamageMultiplier' in defaultPropsData)) defaultPropsData['FireDamageMultiplier'] = 1;
            }

            // Add ArtScale if not present
            if (!('ArtScale' in editedPropsData)) {
                const group = document.createElement('div');
                group.className = 'form-group';
                group.innerHTML = `
                    <label>ArtScale</label>
                    <input type="number" data-props-key="ArtScale" value="1" step="0.01" onchange="updatePropsData(this)">
                `;
                container.appendChild(group);
                editedPropsData['ArtScale'] = 1;
                if (!('ArtScale' in defaultPropsData)) defaultPropsData['ArtScale'] = 1;
            }

            // Add LifetimeSeconds if not present
            if (!('LifetimeSeconds' in editedPropsData)) {
                const group = document.createElement('div');
                group.className = 'form-group';
                group.innerHTML = `
                    <label>LifetimeSeconds</label>
                    <input type="number" data-props-key="LifetimeSeconds" value="999999999" step="1" onchange="updatePropsData(this)">
                `;
                container.appendChild(group);
                editedPropsData['LifetimeSeconds'] = 999999999;
                if (!('LifetimeSeconds' in defaultPropsData)) defaultPropsData['LifetimeSeconds'] = 999999999;
            }

            // Add common boolean flags if not present (defaults are the inverse of the sample values provided)
            const booleanDefaults = {
                // sample listed false -> default true
                'CanTriggerZombieWin': true,
                'CanBePlantTossedWeak': true,
                // sample listed true -> default false
                'FlickIsLaneRestricted': false,
                'CanBePlantTossedStrong': true,
                'CanBeFlickedOff': true,
                'CanBeFlicked': true,
                // sample listed true -> default false
                'CanSurrender': false
            };

            for (const [key, defVal] of Object.entries(booleanDefaults)) {
                if (!(key in editedPropsData)) {
                    const group = document.createElement('div');
                    group.className = 'form-group bool-row';
                    group.innerHTML = `
                        <label>${key}</label>
                        <input type="checkbox" data-props-key="${key}" onchange="updatePropsData(this)" ${defVal ? 'checked' : ''}>
                    `; 
                    container.appendChild(group);
                    editedPropsData[key] = defVal;
                    if (!(key in defaultPropsData)) defaultPropsData[key] = defVal;
                }
            }

            // Add ConditionImmunities if not present
            if (!('ConditionImmunities' in editedPropsData)) {
                const group = document.createElement('div');
                group.className = 'form-group';
                let condHtml = `<label>ConditionImmunities</label><div style="display: flex; flex-direction: column; gap: 8px;">`;
                condHtml += `<div style="display: flex; gap: 5px;">
                    <select id="conditionSelect" style="flex: 1; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                        <option value="">-- Select condition --</option>`;

                CONDITION_LIST.forEach(cond => {
                    condHtml += `<option value="${cond}">${cond}</option>`;
                });

                condHtml += `</select>
                    <input type="number" id="conditionPercent" value="" step="0.01" min="0" max="1" placeholder="% (leave blank = infinite)" 
                           style="width: 140px; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                    <button onclick="addCondition()" style="padding: 5px 10px;">Add</button>
                </div></div>`;

                group.innerHTML = condHtml;
                container.appendChild(group);
                editedPropsData['ConditionImmunities'] = [];
                if (!('ConditionImmunities' in defaultPropsData)) defaultPropsData['ConditionImmunities'] = [];
            }

            // Add Stages editor for Zomboss (if Stages array exists)
            if ('Stages' in editedPropsData && Array.isArray(editedPropsData['Stages'])) {
                const stagesGroup = document.createElement('div');
                stagesGroup.className = 'form-group';
                stagesGroup.style.borderTop = '2px solid #4a6a4a';
                stagesGroup.style.paddingTop = '20px';
                stagesGroup.style.marginTop = '20px';
                
                let stagesHtml = `<label style="font-size: 1.1em; color: #aaffaa;">Zomboss Stages</label>`;
                
                editedPropsData['Stages'].forEach((stage, stageIdx) => {
                    const retreatActionName = stage.RetreatAction ? extractRTIDName(stage.RetreatAction) : '';
                    stagesHtml += `
                    <div style="background: #2a3a2a; padding: 12px; border-radius: 3px; margin-top: 10px; border-left: 3px solid #4a6a4a;">
                        <div style="color: #aaffaa; font-weight: bold; margin-bottom: 10px;">Stage ${stageIdx + 1}</div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px;">
                            <div>
                                <label style="font-size: 0.9em; color: #aaa;">HitPoints</label>
                                <input type="number" value="${stage.HitPoints || 0}" data-stage-idx="${stageIdx}" data-stage-field="HitPoints" 
                                       onchange="updateStageField(this)" style="width: 100%; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            </div>
                            <div>
                                <label style="font-size: 0.9em; color: #aaa;">StunTime</label>
                                <input type="number" value="${stage.StunTime || 0}" step="0.1" data-stage-idx="${stageIdx}" data-stage-field="StunTime" 
                                       onchange="updateStageField(this)" style="width: 100%; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            </div>
                            <div>
                                <label style="font-size: 0.9em; color: #aaa;">AnimRateModifier</label>
                                <input type="number" value="${stage.AnimRateModifier || 1}" step="0.1" data-stage-idx="${stageIdx}" data-stage-field="AnimRateModifier" 
                                       onchange="updateStageField(this)" style="width: 100%; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            </div>
                            <div>
                                <label style="font-size: 0.9em; color: #aaa;">StunDamageScale</label>
                                <input type="number" value="${stage.StunDamageScale || 1}" step="0.1" data-stage-idx="${stageIdx}" data-stage-field="StunDamageScale" 
                                       onchange="updateStageField(this)" style="width: 100%; padding: 5px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0;">
                            </div>
                        </div>
                        
                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #3a4a3a; margin-bottom: 10px;">
                            <label style="font-size: 0.9em; color: #aaa; display: block; margin-bottom: 6px;">Retreat Action</label>
                            <div style="display: flex; gap: 5px;">
                                <input type="text" id="retreatAction_${stageIdx}" value="${retreatActionName}" readonly
                                       style="flex: 1; padding: 5px; background: #2a2a2a; border: 1px solid #4a4a4a; color: #aaffaa;">
                                <button onclick="selectStageRetreatAction(${stageIdx})" style="padding: 5px 10px; background: #3a5a3a; border: 1px solid #4a6a4a; color: #e0e0e0; cursor: pointer; border-radius: 3px;">Choose</button>
                                <button onclick="clearStageRetreatAction(${stageIdx})" style="padding: 5px 10px; background: #5a3a3a; border: 1px solid #6a4a4a; color: #e0e0e0; cursor: pointer; border-radius: 3px;">Clear</button>
                            </div>
                        </div>
                        
                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #3a4a3a;">
                            <label style="font-size: 0.9em; color: #aaa; display: block; margin-bottom: 6px;">Actions (${(stage.Actions || []).length})</label>
                            <div id="stage${stageIdx}ActionsList" style="display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px; max-height: 200px; overflow-y: auto;"></div>
                            <div style="display:flex;gap:6px;margin-top:8px;">
                                <button onclick="addStageAction(${stageIdx})" style="flex:1;padding: 6px 10px; background: #3a5a3a; border: 1px solid #4a6a4a; color: #e0e0e0; cursor: pointer; border-radius: 3px;">+ Add Action</button>
                                <button onclick="removeStage(${stageIdx})" style="padding: 6px 10px; background: #5a3a3a; border: 1px solid #6a4a4a; color: #e0e0e0; cursor: pointer; border-radius: 3px;">Remove Stage</button>
                            </div>
                        </div>
                    </div>
                    `;
                });
                
                stagesGroup.innerHTML = stagesHtml;
                container.appendChild(stagesGroup);
                
                // Render stage actions after inserting HTML
                editedPropsData['Stages'].forEach((stage, stageIdx) => {
                    renderStageActions(stageIdx);
                });
                // Add global Add Stage button below stages
                const addStageBtn = document.createElement('div');
                addStageBtn.style.marginTop = '8px';
                addStageBtn.innerHTML = `<button onclick="addStage()" style="padding: 8px 10px; background: #3a7a3a; border: 1px solid #4a6a4a; color: #e0e0e0; cursor: pointer; border-radius: 3px; width: 100%;">+ Add Stage</button>`;
                stagesGroup.appendChild(addStageBtn);
            }
        }

        function updateArmorItem(element, index) {
            const armorName = element.value;
            if (!editedPropsData['ZombieArmorProps']) {
                editedPropsData['ZombieArmorProps'] = [];
            }
            editedPropsData['ZombieArmorProps'][index] = makeRTID(armorName, 'ArmorTypes');
        }

        function removeArmor(index) {
            editedPropsData['ZombieArmorProps'].splice(index, 1);
            buildPropsForm();
        }

        function addArmor() {
            const select = document.getElementById('armorSelect');
            const customInput = document.getElementById('customArmor');
            const armorName = select.value || customInput.value;
            
            if (!armorName) {
                alert('Select or enter an armor name');
                return;
            }
            
            if (!editedPropsData['ZombieArmorProps']) {
                editedPropsData['ZombieArmorProps'] = [];
            }
            
            editedPropsData['ZombieArmorProps'].push(makeRTID(armorName, 'ArmorTypes'));
            buildPropsForm();
        }

        function updateConditionItem(element, index, type) {
            if (!editedPropsData['ConditionImmunities']) {
                editedPropsData['ConditionImmunities'] = [];
            }
            if (!editedPropsData['ConditionImmunities'][index]) {
                editedPropsData['ConditionImmunities'][index] = { Condition: '' };
            }
            
            if (type === 'condition') {
                editedPropsData['ConditionImmunities'][index].Condition = element.value;
            } else if (type === 'percent') {
                const raw = element.value;
                if (raw === '' || raw === null) {
                    // Omit Percent for infinite immunity
                    delete editedPropsData['ConditionImmunities'][index].Percent;
                } else {
                    const v = parseFloat(raw);
                    editedPropsData['ConditionImmunities'][index].Percent = isNaN(v) ? raw : v;
                }
            }
        }

        function removeCondition(index) {
            if (editedPropsData['ConditionImmunities']) {
                editedPropsData['ConditionImmunities'].splice(index, 1);
                buildPropsForm();
            }
        }

        function addCondition() {
            const select = document.getElementById('conditionSelect');
            const percentInput = document.getElementById('conditionPercent');
            const condName = select.value;
            const percentRaw = percentInput.value;
            const percent = percentRaw === '' ? undefined : parseFloat(percentRaw);
            
            if (!condName) {
                alert('Select a condition');
                return;
            }
            
            if (!editedPropsData['ConditionImmunities']) {
                editedPropsData['ConditionImmunities'] = [];
            }
            const entry = { Condition: condName };
            if (percent !== undefined && !isNaN(percent)) entry.Percent = percent;
            editedPropsData['ConditionImmunities'].push(entry);
            buildPropsForm();
        }

        function isIncludeExcludeListObject(obj) {
            if (typeof obj !== 'object' || obj === null || Array.isArray(obj)) return false;
            return Array.isArray(obj.List) && (typeof obj.ListType === 'string' || obj.ListType === undefined);
        }

        function ensureIncludeExcludeListObject(key) {
            let obj = editedPropsData[key];
            if (typeof obj !== 'object' || obj === null || Array.isArray(obj)) {
                obj = {};
            }
            if (!Array.isArray(obj.List)) {
                obj.List = [];
            }
            if (typeof obj.ListType !== 'string') {
                obj.ListType = 'includelist';
            }
            editedPropsData[key] = obj;
            return obj;
        }

        function updateIncludeExcludeListType(element) {
            const key = element.dataset.propsKey;
            if (!key) return;
            const listObj = ensureIncludeExcludeListObject(key);
            listObj.ListType = element.value || 'includelist';
        }

        function updateIncludeExcludeListItem(element) {
            const key = element.dataset.propsKey;
            const listIndex = parseInt(element.dataset.listIndex, 10);
            if (!key || Number.isNaN(listIndex)) return;

            const listObj = ensureIncludeExcludeListObject(key);
            while (listObj.List.length <= listIndex) {
                listObj.List.push('');
            }
            listObj.List[listIndex] = element.value;
        }

        function addIncludeExcludeListItem(key, buttonElement) {
            if (!key) return;
            const listObj = ensureIncludeExcludeListObject(key);
            const input = buttonElement?.previousElementSibling;
            const value = (input?.value || '').trim();
            if (!value) {
                alert('Enter a value');
                return;
            }

            listObj.List.push(value);
            buildPropsForm();
        }

        function removeIncludeExcludeListItem(key, listIndex) {
            if (!key) return;
            const listObj = ensureIncludeExcludeListObject(key);
            if (listIndex < 0 || listIndex >= listObj.List.length) return;
            listObj.List.splice(listIndex, 1);
            buildPropsForm();
        }

        function isCoordinateObject(obj) {
            if (typeof obj !== 'object' || obj === null) return false;
            const keys = Object.keys(obj);
            const coordKeys = ['x', 'y', 'z'];
            return keys.every(k => coordKeys.includes(k)) && keys.length > 0 && keys.length <= 3;
        }

        function isRectObject(obj) {
            if (typeof obj !== 'object' || obj === null || Array.isArray(obj)) return false;
            const keys = Object.keys(obj);
            const rectKeys = ['mHeight', 'mWidth', 'mX', 'mY'];
            return keys.length === 4 && rectKeys.every(k => keys.includes(k));
        }

        function isMinMaxObject(obj) {
            if (typeof obj !== 'object' || obj === null) return false;
            const keys = Object.keys(obj);
            return keys.length === 2 && keys.includes('Min') && keys.includes('Max');
        }

        function updateCoordData(element, type) {
            const key = element.dataset[type === 'type' ? 'typeKey' : 'propsKey'];
            const coordField = element.dataset.coordField;
            const value = element.value;

            const data = type === 'type' ? editedTypeData : editedPropsData;
            if (!data[key]) {
                data[key] = {};
            }
            const numValue = parseFloat(value);
            data[key][coordField] = isNaN(numValue) ? value : numValue;
        }

        function updateRectData(element) {
            const key = element.dataset.propsKey;
            const rectField = element.dataset.rectField;
            const value = element.value;

            if (!editedPropsData[key]) {
                editedPropsData[key] = {};
            }
            editedPropsData[key][rectField] = parseInt(value);
        }

        function updateRectTypeData(element) {
            const key = element.dataset.typeKey;
            const rectField = element.dataset.rectField;
            const value = element.value;

            if (!editedTypeData[key]) {
                editedTypeData[key] = {};
            }
            editedTypeData[key][rectField] = parseInt(value);
        }

        function updateMinMaxData(element, type) {
            const key = element.dataset[type === 'type' ? 'typeKey' : type === 'props' ? 'propsKey' : 'action'];
            const minmaxField = element.dataset.minmaxField;
            const value = parseFloat(element.value);

            const data = type === 'type' ? editedTypeData : type === 'props' ? editedPropsData : editedActionsData[key];
            if (!data || !data[key]) return;

            data[key][minmaxField] = isNaN(value) ? element.value : value;

            // Validation: prevent Max from being lower than Min
            if (minmaxField === 'Max' && data[key].Min !== undefined && value < data[key].Min) {
                element.value = data[key].Min;
                data[key].Max = data[key].Min;
                alert('Max cannot be lower than Min');
            }
            // Validation: prevent Min from being higher than Max
            else if (minmaxField === 'Min' && data[key].Max !== undefined && value > data[key].Max) {
                element.value = data[key].Max;
                data[key].Min = data[key].Max;
                alert('Min cannot be higher than Max');
            }
        }

        function updateTypeData(element) {
            const key = element.dataset.typeKey;
            if (!key) return;
            if (element.type === 'checkbox') {
                editedTypeData[key] = !!element.checked;
                return;
            }
            const value = element.value;
            try {
                editedTypeData[key] = JSON.parse(value);
            } catch {
                editedTypeData[key] = value;
            }
        }

        function updatePropsData(element) {
            const key = element.dataset.propsKey;
            if (!key) return;
            // checkbox handling
            if (element.type === 'checkbox') {
                editedPropsData[key] = !!element.checked;
                return;
            }
            const value = element.value;
            try {
                editedPropsData[key] = JSON.parse(value);
            } catch {
                editedPropsData[key] = value;
            }
        }

        function isZombossSelection() {
            return !!(editedPropsData?.Stages && Array.isArray(editedPropsData.Stages));
        }

        function updateEditorTabs() {
            const typeTabButton = document.querySelector(`.tab[onclick="switchTab('type')"]`);
            const typeTabContent = document.getElementById('typeTab');
            const isZomboss = isZombossSelection();

            if (typeTabButton) {
                typeTabButton.style.display = isZomboss ? 'none' : '';
            }
            if (typeTabContent) {
                typeTabContent.style.display = isZomboss ? 'none' : '';
            }

            if (isZomboss && typeTabContent?.classList.contains('active')) {
                switchTab('props');
            }
        }

        function switchTab(tab) {
            if (tab === 'type' && isZombossSelection()) {
                tab = 'props';
            }

            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            const tabButton = document.querySelector(`.tab[onclick="switchTab('${tab}')"]`);
            const tabContent = document.getElementById(tab + 'Tab');
            if (!tabButton || !tabContent) return;

            tabButton.classList.add('active');
            tabContent.classList.add('active');
            
            // Auto-generate JSON when switching to output tab
            if (tab === 'output') {
                generateJSON();
            }

            if (tab === 'raw' && typeof onRawTabOpened === 'function') {
                onRawTabOpened();
            }
        }

