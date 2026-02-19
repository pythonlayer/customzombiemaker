        function updateStageField(element) {
            const stageIdx = parseInt(element.dataset.stageIdx);
            const fieldName = element.dataset.stageField;
            const value = element.value;
            
            if (!editedPropsData['Stages'] || !editedPropsData['Stages'][stageIdx]) return;
            
            const numVal = fieldName.includes('HitPoints') ? parseInt(value) : parseFloat(value);
            editedPropsData['Stages'][stageIdx][fieldName] = isNaN(numVal) ? value : numVal;
        }

        function renderStageActions(stageIdx) {
            const container = document.getElementById(`stage${stageIdx}ActionsList`);
            if (!container) return;
            container.innerHTML = '';
            
            const stage = editedPropsData['Stages']?.[stageIdx];
            if (!stage || !Array.isArray(stage.Actions)) return;
            
            stage.Actions.forEach((actionRtid, actionIdx) => {
                const actionName = extractRTIDName(actionRtid);
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.gap = '5px';
                div.style.padding = '4px';
                div.style.background = '#1a2a1a';
                div.style.borderRadius = '2px';
                
                const input = document.createElement('input');
                input.type = 'text';
                input.value = actionName;
                input.style.cssText = 'flex: 1; padding: 4px; background: #2a2a2a; border: 1px solid #3a4a3a; color: #aaffaa; font-size: 0.9em; cursor: pointer;';
                input.title = 'Click to edit alias';
                
                input.addEventListener('click', () => {
                    editStageActionAlias(stageIdx, actionIdx, actionName);
                });
                
                const removeBtn = document.createElement('button');
                removeBtn.textContent = '✕';
                removeBtn.style.cssText = 'padding: 2px 8px; background: #5a3a3a; border: 1px solid #6a4a4a; color: #e0e0e0; cursor: pointer; border-radius: 2px; font-size: 0.85em;';
                removeBtn.onclick = () => removeStageAction(stageIdx, actionIdx);
                
                div.appendChild(input);
                div.appendChild(removeBtn);
                container.appendChild(div);
            });
        }
        
        function editStageActionAlias(stageIdx, actionIdx, currentAlias) {
            const action = allZombieActions[currentAlias];
            if (!action || !action.aliases) return;
            
            const div = document.createElement('div');
            div.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a1a; border: 2px solid #4a4a4a; border-radius: 5px; padding: 20px; z-index: 50000; box-shadow: 0 0 30px rgba(0,0,0,0.8);';
            
            const title = document.createElement('h3');
            title.textContent = 'Edit Action Alias';
            title.style.cssText = 'margin: 0 0 15px 0; color: #aaffaa; font-size: 1.1em;';
            
            const label = document.createElement('label');
            label.textContent = 'Alias:';
            label.style.cssText = 'display: block; margin-bottom: 8px; color: #e0e0e0;';
            
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentAlias;
            input.style.cssText = 'width: 100%; padding: 8px; background: #2a2a2a; border: 1px solid #4a4a4a; color: #aaffaa; font-size: 1em; margin-bottom: 15px; box-sizing: border-box;';
            
            const infoMsg = document.createElement('div');
            infoMsg.textContent = `Available aliases: ${action.aliases.join(', ')}`;
            infoMsg.style.cssText = 'color: #aaa; font-size: 0.85em; margin-bottom: 15px; font-style: italic;';
            
            const buttonContainer = document.createElement('div');
            buttonContainer.style.cssText = 'display: flex; gap: 10px; justify-content: flex-end;';
            
            const saveBtn = document.createElement('button');
            saveBtn.textContent = 'Save';
            saveBtn.style.cssText = 'padding: 8px 16px; background: #2a5a2a; border: 1px solid #4a7a4a; color: #aaffaa; cursor: pointer; border-radius: 3px; font-weight: bold;';
            saveBtn.onclick = () => {
                const newAlias = input.value.trim();
                if (newAlias && action.aliases.includes(newAlias)) {
                    const oldRtid = editedPropsData['Stages'][stageIdx].Actions[actionIdx];
                    editedPropsData['Stages'][stageIdx].Actions[actionIdx] = makeRTID(newAlias, 'ZombieActions');
                    loadAndAddStageActionToMain(newAlias);
                    renderStageActions(stageIdx);
                    document.body.removeChild(overlay);
                } else {
                    alert(`Invalid alias. Must be one of: ${action.aliases.join(', ')}`);
                }
            };
            
            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = 'Cancel';
            cancelBtn.style.cssText = 'padding: 8px 16px; background: #3a3a3a; border: 1px solid #5a5a5a; color: #e0e0e0; cursor: pointer; border-radius: 3px;';
            cancelBtn.onclick = () => {
                document.body.removeChild(overlay);
            };
            
            buttonContainer.appendChild(saveBtn);
            buttonContainer.appendChild(cancelBtn);
            
            div.appendChild(title);
            div.appendChild(label);
            div.appendChild(input);
            div.appendChild(infoMsg);
            div.appendChild(buttonContainer);
            
            const overlay = document.createElement('div');
            overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 49999;';
            overlay.onclick = () => {
                if (overlay.parentNode) document.body.removeChild(overlay);
            };
            overlay.appendChild(div);
            document.body.appendChild(overlay);
            
            input.focus();
            input.select();
        }

        function updateStageAction(actionName, stageIdx, actionIdx) {
            if (!editedPropsData['Stages'] || !editedPropsData['Stages'][stageIdx]) return;
            
            editedPropsData['Stages'][stageIdx].Actions[actionIdx] = makeRTID(actionName, 'ZombieActions');
            loadAndAddStageActionToMain(actionName);
            renderStageActions(stageIdx);
        }

        function removeStageAction(stageIdx, actionIdx) {
            if (!editedPropsData['Stages'] || !editedPropsData['Stages'][stageIdx]) return;
            editedPropsData['Stages'][stageIdx].Actions.splice(actionIdx, 1);
            renderStageActions(stageIdx);
        }

        function addStageAction(stageIdx) {
            if (!editedPropsData['Stages'] || !editedPropsData['Stages'][stageIdx]) return;
            if (!Array.isArray(editedPropsData['Stages'][stageIdx].Actions)) {
                editedPropsData['Stages'][stageIdx].Actions = [];
            }
            
            // Create autocomplete dropdown
            const input = document.createElement('input');
            input.type = 'text';
            input.placeholder = 'Search actions...';
            input.style.cssText = 'padding: 8px; background: #2a2a2a; border: 1px solid #4a4a4a; color: #e0e0e0; border-radius: 3px; width: 100%;';
            
            const dropdown = document.createElement('div');
            dropdown.style.cssText = 'position: absolute; background: #2a2a2a; border: 1px solid #4a4a4a; max-height: 200px; overflow-y: auto; z-index: 10000; width: 100%; margin-top: 5px; top: 100%;';
            
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            wrapper.style.display = 'block';
            wrapper.style.width = '100%';
            wrapper.appendChild(input);
            wrapper.appendChild(dropdown);
            
            const actionContainer = document.getElementById(`stage${stageIdx}ActionsList`);
            if (actionContainer) {
                actionContainer.appendChild(wrapper);
            }
            
            input.focus();
            
            input.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                dropdown.innerHTML = '';
                
                const availableActions = Object.keys(allZombieActions || {});
                const suggestions = availableActions.filter(a => a.toLowerCase().includes(searchTerm)).slice(0, 8);
                
                const stage = editedPropsData['Stages'][stageIdx];
                const addedActions = stage.Actions.map(rtid => extractRTIDName(rtid));
                const filteredSuggestions = suggestions.filter(s => !addedActions.includes(s));
                
                filteredSuggestions.forEach(action => {
                    const div = document.createElement('div');
                    div.textContent = action;
                    div.style.cssText = 'padding: 8px; cursor: pointer; color: #e0e0e0;';
                    div.onmouseover = () => div.style.background = '#3a3a3a';
                    div.onmouseout = () => div.style.background = 'transparent';
                    div.onclick = () => {
                        editedPropsData['Stages'][stageIdx].Actions.push(makeRTID(action, 'ZombieActions'));
                        loadAndAddStageActionToMain(action);
                        renderStageActions(stageIdx);
                        wrapper.remove();
                    };
                    dropdown.appendChild(div);
                });
            });
            
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') wrapper.remove();
            });
        }

        function addStage(defaultStage) {
            if (!editedPropsData['Stages']) editedPropsData['Stages'] = [];
            const idx = editedPropsData['Stages'].length;
            const newStage = defaultStage || {
                Actions: [],
                AnimRateModifier: 1,
                ChilledDurationFromFrozen: 0,
                DamageIndexFull: 0,
                DamageIndexHalf: 0,
                HitPoints: 1000,
                IdleTime: { Min: 0.5, Max: 1 },
                RetreatAction: undefined,
                StunDamageScale: 1,
                StunStaggerBackMovement: 0,
                StunStaggerBackTime: 0,
                StunTime: 0
            };
            editedPropsData['Stages'].push(newStage);
            // Load actions (none by default) and re-render
            loadActionsFromStages();
            buildPropertyForms();
        }

        function removeStage(stageIdx) {
            if (!editedPropsData['Stages'] || stageIdx < 0 || stageIdx >= editedPropsData['Stages'].length) return;
            editedPropsData['Stages'].splice(stageIdx, 1);
            // Recompute actions from remaining stages
            loadActionsFromStages();
            buildPropertyForms();
        }
        
        function loadAndAddStageActionToMain(actionName) {
            if (editedPropsData.Actions?.some(a => {
                const name = typeof a === 'string' ? extractRTIDName(a) : a.name;
                return name === actionName;
            })) {
                return;
            }
            
            const actionDef = allZombieActions?.[actionName];
            if (actionDef) {
                if (!editedPropsData.Actions) {
                    editedPropsData.Actions = [];
                }
                
                const actionRTID = makeRTID(actionName, 'ZombieActions');
                editedPropsData.Actions.push(actionRTID);
            }
        }

        function selectStageRetreatAction(stageIdx) {
            if (!editedPropsData['Stages'] || !editedPropsData['Stages'][stageIdx]) return;
            
            const input = document.createElement('input');
            input.type = 'text';
            input.placeholder = 'Search retreat action...';
            input.style.cssText = 'padding: 8px; background: #2a2a2a; border: 1px solid #4a4a4a; color: #e0e0e0; border-radius: 3px; width: 100%;';
            
            const dropdown = document.createElement('div');
            dropdown.style.cssText = 'position: absolute; background: #2a2a2a; border: 1px solid #4a4a4a; max-height: 200px; overflow-y: auto; z-index: 10000; width: 100%; margin-top: 5px; top: 100%;';
            
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            wrapper.style.display = 'inline-block';
            wrapper.appendChild(input);
            wrapper.appendChild(dropdown);
            
            const retreatField = document.getElementById(`retreatAction_${stageIdx}`);
            if (retreatField && retreatField.parentElement) {
                retreatField.parentElement.appendChild(wrapper);
            }
            
            input.focus();
            
            input.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                dropdown.innerHTML = '';
                
                const availableActions = Object.keys(allZombieActions || {});
                const suggestions = availableActions.filter(a => a.toLowerCase().includes(searchTerm) && a.toLowerCase().includes('retreat')).slice(0, 8);
                
                if (suggestions.length === 0) {
                    const allSuggestions = availableActions.filter(a => a.toLowerCase().includes(searchTerm)).slice(0, 8);
                    allSuggestions.forEach(action => {
                        const div = document.createElement('div');
                        div.textContent = action;
                        div.style.cssText = 'padding: 8px; cursor: pointer; color: #e0e0e0;';
                        div.onmouseover = () => div.style.background = '#3a3a3a';
                        div.onmouseout = () => div.style.background = 'transparent';
                        div.onclick = () => {
                            editedPropsData['Stages'][stageIdx].RetreatAction = makeRTID(action, 'ZombieActions');
                            document.getElementById(`retreatAction_${stageIdx}`).value = action;
                            loadAndAddStageActionToMain(action);
                            wrapper.remove();
                        };
                        dropdown.appendChild(div);
                    });
                } else {
                    suggestions.forEach(action => {
                        const div = document.createElement('div');
                        div.textContent = action;
                        div.style.cssText = 'padding: 8px; cursor: pointer; color: #e0e0e0;';
                        div.onmouseover = () => div.style.background = '#3a3a3a';
                        div.onmouseout = () => div.style.background = 'transparent';
                        div.onclick = () => {
                            editedPropsData['Stages'][stageIdx].RetreatAction = makeRTID(action, 'ZombieActions');
                            document.getElementById(`retreatAction_${stageIdx}`).value = action;
                            loadAndAddStageActionToMain(action);
                            wrapper.remove();
                        };
                        dropdown.appendChild(div);
                    });
                }
            });
            
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') wrapper.remove();
            });
        }

        function clearStageRetreatAction(stageIdx) {
            if (!editedPropsData['Stages'] || !editedPropsData['Stages'][stageIdx]) return;
            editedPropsData['Stages'][stageIdx].RetreatAction = undefined;
            document.getElementById(`retreatAction_${stageIdx}`).value = '';
        }

