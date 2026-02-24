        function buildActionForm() {
            const container = document.getElementById('actionsProperties');
            container.innerHTML = '';

            let actionListHtml = '<div style="margin-bottom: 20px;"><h3 style="color: #e0e0e0; margin-top: 0; font-size: 1em;">Actions List</h3>';

            const zombieAutocompleteList = getStrictZombieAliases();

            if (editedPropsData?.Actions && Array.isArray(editedPropsData.Actions)) {
                editedPropsData.Actions.forEach((action, index) => {
                    const actionName = typeof action === 'string' ? extractRTIDName(action) : action.name;
                    const isModified = modifiedActions.has(actionName);
                    const modifiedBadge = isModified ? ' (Modified)' : '';
                    actionListHtml += `<div style="padding: 8px; background: ${isModified ? '#3a4a3a' : '#3a3a3a'}; margin: 5px 0; border-left: 3px solid ${isModified ? '#4a4' : '#666'}; display: flex; justify-content: space-between; align-items: center;">
                        <span>${actionName}${modifiedBadge}</span>
                        <button onclick="removeAction(${index})" style="padding: 4px 8px; background: #5a3a3a; color: #e0e0e0; border: 1px solid #6a4a4a; cursor: pointer; border-radius: 3px;">Remove</button>
                    </div>`;
                });
            }

            actionListHtml += '</div>';
            container.innerHTML = actionListHtml;

            const allActionNames = Object.keys(allZombieActions || {}).sort((a, b) => a.localeCompare(b));
            let addActionHtml = '<div style="margin-bottom: 20px;"><h3 style="color: #e0e0e0; margin-top: 0; font-size: 1em;">Add New Action</h3>';
            addActionHtml += `<input type="text" id="addActionInput" list="addActionDatalist" placeholder="Type action name..." style="padding: 8px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0; width: 100%; margin-bottom: 10px;">`;
            addActionHtml += '<datalist id="addActionDatalist">';
            allActionNames.forEach(actionName => {
                addActionHtml += `<option value="${actionName}"></option>`;
            });
            addActionHtml += '</datalist>';
            addActionHtml += '<button onclick="addNewAction()" style="padding: 8px 16px; background: #3a5a3a; color: #e0e0e0; border: 1px solid #4a6a4a; cursor: pointer; border-radius: 3px; width: 100%;">Add Action</button>';
            addActionHtml += '</div>';

            const addDiv = document.createElement('div');
            addDiv.innerHTML = addActionHtml;
            container.appendChild(addDiv);

            const uniqueActionNames = [];
            if (editedPropsData?.Actions && Array.isArray(editedPropsData.Actions)) {
                editedPropsData.Actions.forEach(action => {
                    const actionName = typeof action === 'string' ? extractRTIDName(action) : action.name;
                    if (actionName && !uniqueActionNames.includes(actionName)) {
                        uniqueActionNames.push(actionName);
                    }
                });
            }

            if (uniqueActionNames.length > 0) {
                const propsDiv = document.createElement('div');
                propsDiv.style.marginTop = '20px';
                propsDiv.style.borderTop = '1px solid #4a4a4a';
                propsDiv.style.paddingTop = '20px';

                uniqueActionNames.forEach(actionName => {
                    const actionDef = allZombieActions[actionName];
                    const baseActionData = actionDef?.objdata || {};
                    const actionClass = actionDef?.objclass || '';

                    if (!editedActionsData[actionName]) {
                        editedActionsData[actionName] = JSON.parse(JSON.stringify(baseActionData));
                    }
                    const actionData = editedActionsData[actionName] || {};

                    const actionGroup = document.createElement('div');
                    actionGroup.style.marginBottom = '20px';
                    actionGroup.style.padding = '10px';
                    actionGroup.style.background = '#3a3a3a';
                    actionGroup.style.border = '1px solid #4a4a4a';
                    actionGroup.style.borderRadius = '4px';

                    let actionHtml = `<h4 style="color: #e0e0e0; margin-top: 0; font-size: 0.95em;">${actionName} Properties</h4>`;
                    actionHtml += `<div class="form-group" style="margin-bottom: 12px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Alias</label>
                        <input type="text" data-action-alias="${actionName}" value="${actionName}" onchange="updateActionAlias(this)" style="width: 100%; padding: 6px; background: #2a2a2a; border: 1px solid #4a4a4a; color: #aaffaa;">
                    </div>`;
                    actionHtml += `<div class="form-group" style="margin-bottom: 12px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">ObjClass</label>
                        <input type="text" value="${actionClass || 'ZombieActionDefinition'}" readonly style="width: 100%; padding: 6px; background: #252525; border: 1px solid #444; color: #bbb;">
                    </div>`;

                    if (actionClass === 'ZombieDropZombiesOnBoardActionDefinition') {
                        actionHtml += `<div style="margin-bottom: 15px; padding: 10px; background: #2a2a2a; border-left: 3px solid #4a8a4a;">
                            <h5 style="color: #aaffaa; margin-top: 0; font-size: 0.9em;">Zombie Drop List</h5>
                            <div id="zombieDropList_${actionName}" style="margin-bottom: 10px;"></div>
                            <div style="display: flex; gap: 5px; margin-top: 10px;">
                                <input type="text" id="zombieAutoSelect_${actionName}" placeholder="Type zombie name..." 
                                       style="flex: 1; padding: 8px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0; border-radius: 3px;">
                                <input type="number" id="zombieWeight_${actionName}" placeholder="Weight" value="10" min="0" step="1"
                                       style="width: 80px; padding: 8px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0; border-radius: 3px;">
                                <button onclick="addZombieToDrop('${actionName}')" style="padding: 8px 16px; background: #3a5a3a; color: #e0e0e0; border: 1px solid #4a6a4a; cursor: pointer; border-radius: 3px;">Add</button>
                            </div>
                        </div>`;

                        for (const [key, value] of Object.entries(actionData)) {
                            if (['ZombieNames', 'ZombieWeights'].includes(key)) continue;
                            if (isCommentKey(key)) {
                                actionHtml += makeCommentFieldHTML(key, value);
                                continue;
                            }

                            const valueType = typeof value;
                            let input;

                            if (isCoordinateObject(value)) {
                                let coordHtml = `<label>${key}</label><div class="rect-fields">`;
                                for (const [subkey, subvalue] of Object.entries(value)) {
                                    coordHtml += `<div class="rect-field">
                                        <label>${subkey}</label>
                                        <input type="number" data-action="${actionName}" data-action-key="${key}" data-coord-field="${subkey}" 
                                               value="${subvalue}" step="0.01" onchange="updateActionCoord(this)">
                                    </div>`;
                                }
                                coordHtml += '</div>';
                                input = coordHtml;
                            } else if (isMinMaxObject(value)) {
                                let minmaxHtml = `<label>${key}</label><div class="rect-fields">`;
                                for (const [subkey, subvalue] of Object.entries(value)) {
                                    minmaxHtml += `<div class="rect-field">
                                        <label>${subkey}</label>
                                        <input type="number" data-action="${actionName}" data-action-key="${key}" data-minmax-field="${subkey}" 
                                               value="${subvalue}" step="0.01" onchange="updateActionMinMax(this)">
                                    </div>`;
                                }
                                minmaxHtml += '</div>';
                                input = minmaxHtml;
                            } else if (valueType === 'object' && value !== null && !isCoordinateObject(value)) {
                                input = `<label>${key}</label><textarea data-action="${actionName}" data-action-key="${key}" onchange="updateActionData(this)" style="min-height: 60px; width: 100%;">${JSON.stringify(value, null, 2)}</textarea>`;
                            } else if (valueType === 'number') {
                                input = `<label>${key}</label><input type="number" data-action="${actionName}" data-action-key="${key}" value="${value}" step="0.01" onchange="updateActionData(this)">`;
                            } else if (valueType === 'boolean') {
                                input = `<label>${key}</label><input type="checkbox" data-action="${actionName}" data-action-key="${key}" onchange="updateActionData(this)" ${value ? 'checked' : ''}>`;
                            } else {
                                input = `<label>${key}</label><input type="text" data-action="${actionName}" data-action-key="${key}" value="${value}" onchange="updateActionData(this)">`;
                            }

                            if (input.includes('type="checkbox"')) {
                                actionHtml += `<div class="form-group bool-row">${input}</div>`;
                            } else {
                                actionHtml += `<div class="form-group">${input}</div>`;
                            }
                        }

                        actionGroup.innerHTML = actionHtml;
                        propsDiv.appendChild(actionGroup);

                        setTimeout(() => {
                            setupZombieAutocomplete(actionName);
                            renderZombieDropList(actionName);
                        }, 0);
                    } else if (
                        actionClass === 'ZombossSpawnActionDefinition' ||
                        actionClass === 'ZombossSummonActionDefinition' ||
                        Object.prototype.hasOwnProperty.call(actionData || {}, 'SpawnZombieTypes')
                    ) {
                        actionHtml += `<div style="margin-bottom: 15px; padding: 10px; background: #2a3a2a; border-left: 3px solid #6a8a4a;">
                            <h5 style="color: #aaffaa; margin-top: 0; font-size: 0.9em;">Spawn Zombie Types</h5>
                            <div id="spawnZombieList_${actionName}" style="margin-bottom: 10px;"></div>
                            <div style="display: flex; gap: 5px; margin-top: 10px;">
                                <input type="text" id="spawnZombieSelect_${actionName}" placeholder="Type zombie name..." 
                                       style="flex: 1; padding: 8px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0; border-radius: 3px;">
                                <button onclick="addZombieToSpawn('${actionName}')" style="padding: 8px 16px; background: #3a5a3a; color: #e0e0e0; border: 1px solid #4a6a4a; cursor: pointer; border-radius: 3px;">Add</button>
                            </div>
                        </div>`;

                        for (const [key, value] of Object.entries(actionData)) {
                            if (['SpawnZombieTypes'].includes(key)) continue;
                            if (isCommentKey(key)) {
                                actionHtml += makeCommentFieldHTML(key, value);
                                continue;
                            }

                            const valueType = typeof value;
                            let input;

                            if (isMinMaxObject(value)) {
                                let minmaxHtml = `<label>${key}</label><div class="rect-fields">`;
                                for (const [subkey, subvalue] of Object.entries(value)) {
                                    minmaxHtml += `<div class="rect-field">
                                        <label>${subkey}</label>
                                        <input type="number" data-action="${actionName}" data-action-key="${key}" data-minmax-field="${subkey}" 
                                               value="${subvalue}" step="0.01" onchange="updateActionMinMax(this)">
                                    </div>`;
                                }
                                minmaxHtml += '</div>';
                                input = minmaxHtml;
                            } else if (valueType === 'number') {
                                input = `<label>${key}</label><input type="number" data-action="${actionName}" data-action-key="${key}" value="${value}" step="0.01" onchange="updateActionData(this)">`;
                            } else if (valueType === 'boolean') {
                                input = `<label>${key}</label><input type="checkbox" data-action="${actionName}" data-action-key="${key}" onchange="updateActionData(this)" ${value ? 'checked' : ''}>`;
                            } else if (valueType === 'object' && value !== null) {
                                input = `<label>${key}</label><textarea data-action="${actionName}" data-action-key="${key}" onchange="updateActionData(this)" style="min-height: 60px; width: 100%;">${JSON.stringify(value, null, 2)}</textarea>`;
                            } else {
                                input = `<label>${key}</label><input type="text" data-action="${actionName}" data-action-key="${key}" value="${value}" onchange="updateActionData(this)">`;
                            }

                            if (input) {
                                if (input.includes('type="checkbox"')) {
                                    actionHtml += `<div class="form-group bool-row">${input}</div>`;
                                } else {
                                    actionHtml += `<div class="form-group">${input}</div>`;
                                }
                            }
                        }

                        actionGroup.innerHTML = actionHtml;
                        propsDiv.appendChild(actionGroup);

                        const zombiesOnly = zombieAutocompleteList;

                        setTimeout(() => {
                            setupSpawnZombieAutocomplete(actionName, zombiesOnly);
                            renderSpawnZombieList(actionName);
                        }, 0);
                    } else {
                        for (const [key, value] of Object.entries(actionData)) {
                            if (isCommentKey(key)) {
                                actionHtml += makeCommentFieldHTML(key, value);
                                continue;
                            }

                            const valueType = typeof value;
                            let input;

                            if (isCoordinateObject(value)) {
                                let coordHtml = `<label>${key}</label><div class="rect-fields">`;
                                for (const [subkey, subvalue] of Object.entries(value)) {
                                    coordHtml += `<div class="rect-field">
                                        <label>${subkey}</label>
                                        <input type="number" data-action="${actionName}" data-action-key="${key}" data-coord-field="${subkey}" 
                                               value="${subvalue}" step="0.01" onchange="updateActionCoord(this)">
                                    </div>`;
                                }
                                coordHtml += '</div>';
                                input = coordHtml;
                            } else if (isMinMaxObject(value)) {
                                let minmaxHtml = `<label>${key}</label><div class="rect-fields">`;
                                for (const [subkey, subvalue] of Object.entries(value)) {
                                    minmaxHtml += `<div class="rect-field">
                                        <label>${subkey}</label>
                                        <input type="number" data-action="${actionName}" data-action-key="${key}" data-minmax-field="${subkey}" 
                                               value="${subvalue}" step="0.01" onchange="updateActionMinMax(this)">
                                    </div>`;
                                }
                                minmaxHtml += '</div>';
                                input = minmaxHtml;
                            } else if (valueType === 'object' && value !== null && !isCoordinateObject(value)) {
                                input = `<label>${key}</label><textarea data-action="${actionName}" data-action-key="${key}" onchange="updateActionData(this)" style="min-height: 60px; width: 100%;">${JSON.stringify(value, null, 2)}</textarea>`;
                            } else if (valueType === 'number') {
                                input = `<label>${key}</label><input type="number" data-action="${actionName}" data-action-key="${key}" value="${value}" step="0.01" onchange="updateActionData(this)">`;
                            } else if (valueType === 'boolean') {
                                input = `<label>${key}</label><input type="checkbox" data-action="${actionName}" data-action-key="${key}" onchange="updateActionData(this)" ${value ? 'checked' : ''}>`;
                            } else {
                                input = `<label>${key}</label><input type="text" data-action="${actionName}" data-action-key="${key}" value="${value}" onchange="updateActionData(this)">`;
                            }

                            if (input.includes('type="checkbox"')) {
                                actionHtml += `<div class="form-group bool-row">${input}</div>`;
                            } else {
                                actionHtml += `<div class="form-group">${input}</div>`;
                            }
                        }

                        actionGroup.innerHTML = actionHtml;
                        propsDiv.appendChild(actionGroup);
                    }
                });

                container.appendChild(propsDiv);
            }

            const addActionInput = document.getElementById('addActionInput');
            if (addActionInput) {
                addActionInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        addNewAction();
                    }
                });
            }
        }

        function updateActionData(element) {
            const actionName = element.dataset.action;
            const key = element.dataset.actionKey;
            if (!actionName || !key) return;

            // checkbox handling
            if (element.type === 'checkbox') {
                if (!editedActionsData[actionName]) editedActionsData[actionName] = {};
                editedActionsData[actionName][key] = !!element.checked;
                modifiedActions.add(actionName);
                return;
            }

            const value = element.value;
            modifiedActions.add(actionName);

            if (!editedActionsData[actionName]) {
                editedActionsData[actionName] = {};
            }

            try {
                editedActionsData[actionName][key] = JSON.parse(value);
            } catch {
                const numValue = parseFloat(value);
                editedActionsData[actionName][key] = isNaN(numValue) ? value : numValue;
            }
        }

        function updateActionCoord(element) {
            const actionName = element.dataset.action;
            const key = element.dataset.actionKey;
            const coordField = element.dataset.coordField;
            const value = parseFloat(element.value);
            modifiedActions.add(actionName);

            if (!editedActionsData[actionName]) {
                editedActionsData[actionName] = {};
            }
            if (!editedActionsData[actionName][key]) {
                editedActionsData[actionName][key] = {};
            }

            editedActionsData[actionName][key][coordField] = value;
        }

        function updateActionMinMax(element) {
            const actionName = element.dataset.action;
            const key = element.dataset.actionKey;
            const minmaxField = element.dataset.minmaxField;
            const value = parseFloat(element.value);
            modifiedActions.add(actionName);

            if (!editedActionsData[actionName]) {
                editedActionsData[actionName] = {};
            }
            if (!editedActionsData[actionName][key]) {
                editedActionsData[actionName][key] = {};
            }

            editedActionsData[actionName][key][minmaxField] = isNaN(value) ? element.value : value;

            // Validation: prevent Max from being lower than Min
            if (minmaxField === 'Max' && editedActionsData[actionName][key].Min !== undefined && value < editedActionsData[actionName][key].Min) {
                element.value = editedActionsData[actionName][key].Min;
                editedActionsData[actionName][key].Max = editedActionsData[actionName][key].Min;
                alert('Max cannot be lower than Min');
            }
            // Validation: prevent Min from being higher than Max
            else if (minmaxField === 'Min' && editedActionsData[actionName][key].Max !== undefined && value > editedActionsData[actionName][key].Max) {
                element.value = editedActionsData[actionName][key].Max;
                editedActionsData[actionName][key].Min = editedActionsData[actionName][key].Max;
                alert('Min cannot be higher than Max');
            }
        }

        function updateActionAlias(element) {
            const oldAlias = element.dataset.actionAlias;
            const newAliasRaw = element.value.trim();

            if (!oldAlias) return;
            if (!newAliasRaw) {
                element.value = oldAlias;
                return;
            }

            const newAlias = newAliasRaw;
            if (newAlias === oldAlias) return;

            const sourceDef = allZombieActions[oldAlias];
            if (!allZombieActions[newAlias]) {
                if (sourceDef) {
                    allZombieActions[newAlias] = JSON.parse(JSON.stringify(sourceDef));
                } else {
                    allZombieActions[newAlias] = {
                        objclass: 'ZombieActionDefinition',
                        aliases: [newAlias],
                        objdata: editedActionsData[oldAlias] ? JSON.parse(JSON.stringify(editedActionsData[oldAlias])) : {}
                    };
                }
            }

            if (!Array.isArray(allZombieActions[newAlias].aliases)) {
                allZombieActions[newAlias].aliases = [newAlias];
            } else {
                allZombieActions[newAlias].aliases[0] = newAlias;
            }

            if (editedActionsData[oldAlias]) {
                editedActionsData[newAlias] = JSON.parse(JSON.stringify(editedActionsData[oldAlias]));
            } else if (!editedActionsData[newAlias]) {
                editedActionsData[newAlias] = JSON.parse(JSON.stringify(allZombieActions[newAlias]?.objdata || {}));
            }

            if (editedPropsData?.Actions && Array.isArray(editedPropsData.Actions)) {
                editedPropsData.Actions = editedPropsData.Actions.map(action => {
                    const actionName = typeof action === 'string' ? extractRTIDName(action) : action.name;
                    return actionName === oldAlias ? makeRTID(newAlias, 'ZombieActions') : action;
                });
            }

            if (editedPropsData?.Stages && Array.isArray(editedPropsData.Stages)) {
                editedPropsData.Stages.forEach(stage => {
                    if (Array.isArray(stage.Actions)) {
                        stage.Actions = stage.Actions.map(action => {
                            const actionName = extractRTIDName(action);
                            return actionName === oldAlias ? makeRTID(newAlias, 'ZombieActions') : action;
                        });
                    }
                    if (stage.RetreatAction && extractRTIDName(stage.RetreatAction) === oldAlias) {
                        stage.RetreatAction = makeRTID(newAlias, 'ZombieActions');
                    }
                });
            }

            const stillInMainActions = Array.isArray(editedPropsData?.Actions) && editedPropsData.Actions.some(action => {
                const actionName = typeof action === 'string' ? extractRTIDName(action) : action.name;
                return actionName === oldAlias;
            });

            const stillInStages = Array.isArray(editedPropsData?.Stages) && editedPropsData.Stages.some(stage => {
                const inActions = Array.isArray(stage.Actions) && stage.Actions.some(a => extractRTIDName(a) === oldAlias);
                const inRetreat = !!stage.RetreatAction && extractRTIDName(stage.RetreatAction) === oldAlias;
                return inActions || inRetreat;
            });

            if (!stillInMainActions && !stillInStages) {
                delete editedActionsData[oldAlias];
                modifiedActions.delete(oldAlias);
            }

            modifiedActions.add(newAlias);
            buildPropertyForms();
        }

        // HealthThresholdToImpAmmoLayers handlers
        function addHealthLayerEntry() {
            if (!editedPropsData['HealthThresholdToImpAmmoLayers']) editedPropsData['HealthThresholdToImpAmmoLayers'] = [];
            editedPropsData['HealthThresholdToImpAmmoLayers'].push({ HealthPercentThrowImp: 0.5, ProjectileLayersToHide: [] });
            buildPropsForm();
        }

        function removeHealthLayerEntry(index) {
            if (!editedPropsData['HealthThresholdToImpAmmoLayers']) return;
            editedPropsData['HealthThresholdToImpAmmoLayers'].splice(index, 1);
            buildPropsForm();
        }

        function updateHealthLayerEntry(element, index, type) {
            if (!editedPropsData['HealthThresholdToImpAmmoLayers']) editedPropsData['HealthThresholdToImpAmmoLayers'] = [];
            if (!editedPropsData['HealthThresholdToImpAmmoLayers'][index]) editedPropsData['HealthThresholdToImpAmmoLayers'][index] = { ProjectileLayersToHide: [] };

            if (type === 'percent') {
                const raw = element.value;
                const v = raw === '' ? undefined : parseFloat(raw);
                if (v === undefined || isNaN(v)) {
                    delete editedPropsData['HealthThresholdToImpAmmoLayers'][index].HealthPercentThrowImp;
                } else {
                    editedPropsData['HealthThresholdToImpAmmoLayers'][index].HealthPercentThrowImp = v;
                }
            }
        }

        function addLayerToEntry(entryIndex) {
            const inp = document.getElementById(`newLayerInput_${entryIndex}`);
            if (!inp) return;
            const name = inp.value.trim();
            if (!name) return alert('Enter a layer name');

            if (!editedPropsData['HealthThresholdToImpAmmoLayers']) editedPropsData['HealthThresholdToImpAmmoLayers'] = [];
            if (!editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex]) editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex] = { ProjectileLayersToHide: [] };

            if (!editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex].ProjectileLayersToHide) editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex].ProjectileLayersToHide = [];
            editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex].ProjectileLayersToHide.push(name);
            inp.value = '';
            renderHealthLayersList(entryIndex);
        }

        function removeLayerFromEntry(entryIndex, layerIndex) {
            if (!editedPropsData['HealthThresholdToImpAmmoLayers'] || !editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex]) return;
            editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex].ProjectileLayersToHide.splice(layerIndex, 1);
            renderHealthLayersList(entryIndex);
        }

        function renderHealthLayersList(entryIndex) {
            const container = document.getElementById(`healthLayersList_${entryIndex}`);
            if (!container) return;
            container.innerHTML = '';
            const entry = (editedPropsData['HealthThresholdToImpAmmoLayers'] || [])[entryIndex] || { ProjectileLayersToHide: [] };
            const layers = entry.ProjectileLayersToHide || [];

            layers.forEach((ly, li) => {
                const row = document.createElement('div');
                row.style.display = 'flex';
                row.style.gap = '6px';
                row.style.alignItems = 'center';
                row.style.marginBottom = '6px';

                row.innerHTML = `<input type="text" value="${ly}" onchange="updateLayerName(this, ${entryIndex}, ${li})" style="flex:1;padding:6px;background:#3a3a3a;border:1px solid #4a4a4a;color:#e0e0e0;">
                    <button onclick="removeLayerFromEntry(${entryIndex}, ${li})" style="padding:6px 10px;">Remove</button>`;

                container.appendChild(row);
            });

            if (layers.length === 0) {
                const p = document.createElement('div');
                p.style.color = '#999';
                p.textContent = 'No projectile layers defined';
                container.appendChild(p);
            }
        }

        function updateLayerName(element, entryIndex, layerIndex) {
            const name = element.value.trim();
            if (!editedPropsData['HealthThresholdToImpAmmoLayers'] || !editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex]) return;
            if (!editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex].ProjectileLayersToHide) editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex].ProjectileLayersToHide = [];
            editedPropsData['HealthThresholdToImpAmmoLayers'][entryIndex].ProjectileLayersToHide[layerIndex] = name;
        }

