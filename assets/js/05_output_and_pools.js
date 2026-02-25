        function generateJSON() {
            if (!selectedZombie) {
                alert('Select a zombie first');
                return;
            }

            const typeAlias = selectedZombie.aliases?.[0] || 'Custom';
            
            // Check if this is a Zomboss (has Stages in objdata)
            const isZomboss = editedPropsData?.Stages && Array.isArray(editedPropsData.Stages);
            
            // For Zomboss, ensure template is selected
            if (isZomboss && !selectedZombossTemplate) {
                alert('Please select a Zomboss template');
                return;
            }
            
            // Extract properties alias from the Properties field RTID (this is the source of truth)
            const propertiesRTID = editedTypeData['Properties'] || makeRTID('', '.');
            const propsAlias = extractRTIDName(propertiesRTID);
            
            // For Zomboss, use template format: ZombossmechTemplate(Worldname)Props
            let finalPropsAlias = propsAlias;
            if (isZomboss && selectedZombossTemplate) {
                // Use the selected template directly
                finalPropsAlias = `ZombossmechTemplate${selectedZombossTemplate}Props`;
            }
            
            // FORCE Properties to always use @. (CurrentLevel)
            const typeDataForOutput = JSON.parse(JSON.stringify(editedTypeData));
            typeDataForOutput['Properties'] = makeRTID(propsAlias, '.');
            // ImpType was experimental and should not be emitted from type output.
            delete typeDataForOutput['ImpType'];

            // Filter props data - include if originally present, explicitly allowed, or changed from base/default
            const selectedZombiePropertiesData = selectedZombieProperties?.objdata || {};
            const originalPropsKeys = Object.keys(selectedZombiePropertiesData);
            const alwaysAllowedProps = []; // Always include these even if new
            const hasOwn = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
            const valuesEqual = (a, b) => {
                if (a === b) return true;
                try {
                    return JSON.stringify(a) === JSON.stringify(b);
                } catch (e) {
                    return false;
                }
            };
            
            const propsDataFiltered = {};
            for (const [key, value] of Object.entries(editedPropsData)) {
                const existedInOriginal = originalPropsKeys.includes(key);
                const isAlwaysAllowed = alwaysAllowedProps.includes(key);
                const hasBaseValue = hasOwn(defaultPropsData, key);
                const baseValue = hasBaseValue ? defaultPropsData[key] : undefined;
                const changedFromBase = !hasBaseValue || !valuesEqual(value, baseValue);

                // Exclude only when it did not exist before and was not modified.
                if (existedInOriginal || isAlwaysAllowed || changedFromBase) {
                    propsDataFiltered[key] = value;
                }
            }

            // Handle Actions in Properties - only include if the original properties had Actions
            const propsDataWithActions = JSON.parse(JSON.stringify(propsDataFiltered));
            const originalHadActions = selectedZombieProperties?.objdata?.Actions && Array.isArray(selectedZombieProperties.objdata.Actions);
            
            if (originalHadActions && editedPropsData.Actions && Array.isArray(editedPropsData.Actions)) {
                propsDataWithActions.Actions = editedPropsData.Actions.map(action => {
                    // Handle both RTID strings and full action objects (for backwards compatibility)
                    const actionName = typeof action === 'string' ? extractRTIDName(action) : action.name;
                    const isModified = modifiedActions.has(actionName);
                    // If modified, use @CurrentLevel, otherwise use @ZombieActions
                    return makeRTID(actionName, isModified ? '.' : 'ZombieActions');
                });
            } else {
                // Remove Actions if the original didn't have it
                delete propsDataWithActions.Actions;
            }

            // Also update any action RTIDs inside Stages (Zomboss) to point to current-level if modified
            if (propsDataWithActions.Stages && Array.isArray(propsDataWithActions.Stages)) {
                propsDataWithActions.Stages = propsDataWithActions.Stages.map(stage => {
                    const newStage = JSON.parse(JSON.stringify(stage));

                    if (Array.isArray(newStage.Actions)) {
                        newStage.Actions = newStage.Actions.map(a => {
                            const actionName = extractRTIDName(a);
                            const isModified = modifiedActions.has(actionName);
                            return makeRTID(actionName, isModified ? '.' : 'ZombieActions');
                        });
                    }

                    if (newStage.RetreatAction) {
                        const retreatName = extractRTIDName(newStage.RetreatAction);
                        const isRetreatModified = modifiedActions.has(retreatName);
                        newStage.RetreatAction = makeRTID(retreatName, isRetreatModified ? '.' : 'ZombieActions');
                    }

                    return newStage;
                });
            }

            // Build output as array of objects (for pasting into list)
            const outputObjects = [];

            // For Zomboss and template mode, output props + actions only (no type)
            // For regular zombies, output type + props + actions
            if (!isZomboss && !templateModeEnabled) {
                // Add ZombieType only for non-Zomboss zombies
                outputObjects.push({
                    "objclass": "ZombieType",
                    "aliases": editedTypeAliases && editedTypeAliases.length > 0 ? editedTypeAliases : [typeAlias],
                    "objdata": typeDataForOutput
                });
            }

            // Add ZombiePropertySheet - use template alias for Zomboss
            outputObjects.push({
                "aliases": [finalPropsAlias],
                "objclass": selectedZombieProperties?.objclass || "ZombiePropertySheet",
                "objdata": propsDataWithActions
            });

            // Add actions to output: include those marked modified OR whose data differs from the original
            const modifiedActionEntries = Object.entries(editedActionsData).filter(([actionName, actionData]) => {
                if (modifiedActions.has(actionName)) return true;
                const original = allZombieActions[actionName]?.objdata || {};
                try {
                    return JSON.stringify(actionData) !== JSON.stringify(original);
                } catch (e) {
                    return modifiedActions.has(actionName);
                }
            });

            for (const [actionName, actionData] of modifiedActionEntries) {
                const actionDef = allZombieActions[actionName];
                outputObjects.push({
                    "objclass": actionDef?.objclass || "ZombieActionDefinition",
                    "aliases": [actionName],
                    "objdata": actionData
                });
            }

            // Include custom armor/projectile entries from dedicated tabs in main export.
            const armorEntries = (typeof customArmorEntries !== 'undefined' && Array.isArray(customArmorEntries)) ? customArmorEntries : [];
            const projectileEntries = (typeof customProjectileEntries !== 'undefined' && Array.isArray(customProjectileEntries)) ? customProjectileEntries : [];
            if (armorEntries.length > 0) {
                armorEntries.forEach(entry => {
                    if (!entry || typeof entry !== 'object') return;
                    outputObjects.push(JSON.parse(JSON.stringify(entry)));
                });
            }
            if (projectileEntries.length > 0) {
                projectileEntries.forEach(entry => {
                    if (!entry || typeof entry !== 'object') return;
                    outputObjects.push(JSON.parse(JSON.stringify(entry)));
                });
            }

            // Format as comma-separated JSON objects (with trailing comma on each)
            const jsonOutput = outputObjects.map(obj => JSON.stringify(obj, null, 2) + ',').join('\n');

            const textarea = document.getElementById('output');
            textarea.value = jsonOutput;
            textarea.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        function copyToClipboard() {
            const textarea = document.getElementById('output');
            if (!textarea.value) {
                alert('Generate JSON first');
                return;
            }
            textarea.select();
            document.execCommand('copy');
            alert('Copied!');
        }

        function getOutputAliasForFilename() {
            const candidates = [
                Array.isArray(editedTypeAliases) ? editedTypeAliases[0] : '',
                selectedZombie?.aliases?.[0],
                extractRTIDName(editedTypeData?.Properties || ''),
                'custom-zombie'
            ];
            const chosen = candidates.find(v => typeof v === 'string' && v.trim().length > 0) || 'custom-zombie';
            return chosen.trim();
        }

        function sanitizeOutputFilename(name) {
            return String(name || 'custom-zombie')
                .replace(/\.json$/i, '')
                .replace(/[<>:"/\\|?*\x00-\x1F]/g, '_')
                .replace(/\s+/g, '_')
                .replace(/\.+$/g, '')
                .slice(0, 120) || 'custom-zombie';
        }

        function downloadJSON() {
            const textarea = document.getElementById('output');
            if (!textarea.value) {
                alert('Generate JSON first');
                return;
            }

            const element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(textarea.value));
            const filename = `${sanitizeOutputFilename(getOutputAliasForFilename())}.json`;
            element.setAttribute('download', filename);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }

        function deepCloneJSON(value) {
            return JSON.parse(JSON.stringify(value));
        }

        function normalizeImportedObjects(parsedValue) {
            if (Array.isArray(parsedValue)) {
                return parsedValue.filter(v => v && typeof v === 'object');
            }
            if (parsedValue && typeof parsedValue === 'object' && Array.isArray(parsedValue.objects)) {
                return parsedValue.objects.filter(v => v && typeof v === 'object');
            }
            if (parsedValue && typeof parsedValue === 'object') {
                return [parsedValue];
            }
            return [];
        }

        function parseImportedOutputObjects(rawText) {
            const input = String(rawText || '').trim();
            if (!input) {
                throw new Error('Paste JSON first.');
            }

            const stripped = input.replace(/,\s*(\]|\})/g, '$1');
            const listBody = input.replace(/,\s*$/, '');
            const listBodyStripped = stripped.replace(/,\s*$/, '');

            const attempts = [
                input,
                stripped,
                `[${listBody}]`,
                `[${listBodyStripped}]`
            ];

            let lastError = null;
            for (const candidate of attempts) {
                try {
                    const parsed = JSON.parse(candidate);
                    const objects = normalizeImportedObjects(parsed);
                    if (objects.length > 0) {
                        return objects;
                    }
                } catch (e) {
                    lastError = e;
                }
            }

            throw lastError || new Error('Invalid JSON payload.');
        }

        function getActionClassSet() {
            const classes = new Set();
            Object.values(allZombieActions || {}).forEach(actionDef => {
                if (actionDef && typeof actionDef.objclass === 'string' && actionDef.objclass) {
                    classes.add(actionDef.objclass);
                }
            });
            return classes;
        }

        function isActionLikeImportObject(entry, actionClasses) {
            const alias = Array.isArray(entry.aliases) ? entry.aliases[0] : '';
            const objclass = String(entry.objclass || '');
            const lowerClass = objclass.toLowerCase();

            if (alias && allZombieActions[alias]) return true;
            if (objclass && actionClasses.has(objclass)) return true;
            if (lowerClass.includes('action')) return true;
            if (objclass === 'ZombieDropProps') return true;
            return false;
        }

        function isArmorLikeImportObject(entry) {
            const cls = String(entry?.objclass || '').toLowerCase();
            return cls.includes('armorpropertysheet') && !cls.includes('utils');
        }

        function isProjectileLikeImportObject(entry) {
            if (typeof isProjectileLikeObject === 'function') {
                return isProjectileLikeObject(entry);
            }
            const cls = String(entry?.objclass || '').toLowerCase();
            if (cls.includes('utils')) return false;
            return cls.includes('projectile') || cls.includes('leafprops');
        }

        function applyImportedCustomAssetEntries(armorObjects, projectileObjects) {
            const armorList = Array.isArray(armorObjects) ? armorObjects : [];
            const projectileList = Array.isArray(projectileObjects) ? projectileObjects : [];
            const hasArmorImports = armorList.length > 0;
            const hasProjectileImports = projectileList.length > 0;
            const canUseArmorState = typeof customArmorEntries !== 'undefined' && Array.isArray(customArmorEntries);
            const canUseProjectileState = typeof customProjectileEntries !== 'undefined' && Array.isArray(customProjectileEntries);

            let importedArmorCount = 0;
            let importedProjectileCount = 0;

            if (hasArmorImports && canUseArmorState) {
                customArmorEntries.length = 0;
                armorList.forEach(entry => {
                    if (!entry || typeof entry !== 'object') return;
                    const cloned = deepCloneJSON(entry);
                    if (typeof normalizeArmorEntry === 'function') {
                        normalizeArmorEntry(cloned);
                    }
                    customArmorEntries.push(cloned);
                });
                importedArmorCount = customArmorEntries.length;
                if (typeof selectedCustomArmorIndex !== 'undefined') {
                    selectedCustomArmorIndex = importedArmorCount > 0 ? 0 : -1;
                }
                if (typeof renderCustomArmorList === 'function') renderCustomArmorList();
                if (typeof renderCustomArmorEditor === 'function') renderCustomArmorEditor();
            }

            if (hasProjectileImports && canUseProjectileState) {
                customProjectileEntries.length = 0;
                projectileList.forEach(entry => {
                    if (!entry || typeof entry !== 'object') return;
                    const cloned = deepCloneJSON(entry);
                    if (typeof normalizeProjectileEntry === 'function') {
                        normalizeProjectileEntry(cloned);
                    }
                    customProjectileEntries.push(cloned);
                });
                importedProjectileCount = customProjectileEntries.length;
                if (typeof selectedCustomProjectileIndex !== 'undefined') {
                    selectedCustomProjectileIndex = importedProjectileCount > 0 ? 0 : -1;
                }
                if (typeof renderCustomProjectileList === 'function') renderCustomProjectileList();
                if (typeof renderCustomProjectileEditor === 'function') renderCustomProjectileEditor();
            }

            return {
                importedArmorCount,
                importedProjectileCount
            };
        }

        function selectImportedPropsObject(propsCandidates, typeObject) {
            const wantedAlias = typeObject ? extractRTIDName(typeObject.objdata?.Properties || '') : '';
            if (wantedAlias) {
                const matched = propsCandidates.find(obj => Array.isArray(obj.aliases) && obj.aliases.includes(wantedAlias));
                if (matched) return matched;
            }

            if (propsCandidates.length === 0) return null;
            if (propsCandidates.length === 1) return propsCandidates[0];

            const withScore = propsCandidates.map(obj => {
                const cls = String(obj.objclass || '').toLowerCase();
                let score = 0;
                if (cls.includes('property')) score += 3;
                if (cls.endsWith('props')) score += 2;
                if (cls.includes('sheet')) score += 1;
                return { obj, score };
            });

            withScore.sort((a, b) => b.score - a.score);
            return withScore[0].obj;
        }

        function importOutputJSON() {
            const output = document.getElementById('output');
            if (!output || !output.value.trim()) {
                alert('Paste JSON in Generated JSON first.');
                return;
            }

            let importedObjects = [];
            try {
                importedObjects = parseImportedOutputObjects(output.value);
            } catch (e) {
                alert(`Import failed: ${e.message}`);
                return;
            }

            const actionClasses = getActionClassSet();
            const typeObjects = [];
            const propsCandidates = [];
            const actionObjects = [];
            const armorObjects = [];
            const projectileObjects = [];

            importedObjects.forEach(entry => {
                if (!entry || typeof entry !== 'object') return;
                if (entry.objclass === 'ZombieType') {
                    typeObjects.push(entry);
                    return;
                }
                if (!entry.objdata || !Array.isArray(entry.aliases) || entry.aliases.length === 0) {
                    return;
                }
                if (isArmorLikeImportObject(entry)) {
                    armorObjects.push(entry);
                    return;
                }
                if (isProjectileLikeImportObject(entry)) {
                    projectileObjects.push(entry);
                    return;
                }
                if (isActionLikeImportObject(entry, actionClasses)) {
                    actionObjects.push(entry);
                } else {
                    propsCandidates.push(entry);
                }
            });

            const importedAssets = applyImportedCustomAssetEntries(armorObjects, projectileObjects);

            let importedTypeObject = typeObjects[0] || null;
            const importedPropsObject = selectImportedPropsObject(propsCandidates, importedTypeObject);

            if (!importedPropsObject) {
                if (importedAssets.importedArmorCount > 0 || importedAssets.importedProjectileCount > 0) {
                    const importedParts = [];
                    if (importedAssets.importedArmorCount > 0) {
                        importedParts.push(`${importedAssets.importedArmorCount} armor(s)`);
                    }
                    if (importedAssets.importedProjectileCount > 0) {
                        importedParts.push(`${importedAssets.importedProjectileCount} projectile(s)`);
                    }
                    if (importedAssets.importedArmorCount > 0 && typeof switchTab === 'function') {
                        switchTab('armor');
                    } else if (importedAssets.importedProjectileCount > 0 && typeof switchTab === 'function') {
                        switchTab('projectile');
                    }
                    alert(`Imported ${importedParts.join(', ')}. No zombie props/type found, so current zombie data was kept.`);
                    return;
                }
                alert('Import failed: no props object found in pasted JSON.');
                return;
            }

            const importedPropsAlias = Array.isArray(importedPropsObject.aliases) && importedPropsObject.aliases[0]
                ? importedPropsObject.aliases[0]
                : 'ImportedProps';
            const importedHasStages = Array.isArray(importedPropsObject.objdata?.Stages);
            const importedLooksTemplate = /template/i.test(importedPropsAlias);
            const shouldIgnoreType = importedHasStages || importedLooksTemplate;

            if (shouldIgnoreType) {
                importedTypeObject = null;
            }

            if (importedTypeObject && importedTypeObject.objdata) {
                selectedZombie = deepCloneJSON(importedTypeObject);
                editedTypeData = deepCloneJSON(importedTypeObject.objdata || {});
                editedTypeAliases = Array.isArray(importedTypeObject.aliases)
                    ? deepCloneJSON(importedTypeObject.aliases)
                    : ['ImportedZombie'];
                if (!editedTypeData.Properties) {
                    editedTypeData.Properties = makeRTID(importedPropsAlias, '.');
                }
                delete editedTypeData['ImpType'];
            } else {
                const syntheticAlias = importedPropsAlias.replace(/Props$/i, '') || 'ImportedZombie';
                selectedZombie = {
                    objclass: 'ZombieType',
                    aliases: [syntheticAlias],
                    objdata: {
                        Properties: makeRTID(importedPropsAlias, '.')
                    }
                };
                editedTypeData = deepCloneJSON(selectedZombie.objdata);
                editedTypeAliases = deepCloneJSON(selectedZombie.aliases);
            }

            selectedZombieProperties = deepCloneJSON(importedPropsObject);
            editedPropsData = deepCloneJSON(importedPropsObject.objdata || {});
            defaultPropsData = deepCloneJSON(importedPropsObject.objdata || {});
            editedActionsData = {};
            modifiedActions = new Set();

            actionObjects.forEach(actionObj => {
                const alias = Array.isArray(actionObj.aliases) ? actionObj.aliases[0] : '';
                if (!alias) return;

                const cloned = deepCloneJSON(actionObj);
                allZombieActions[alias] = cloned;
                editedActionsData[alias] = deepCloneJSON(cloned.objdata || {});
                modifiedActions.add(alias);
            });

            const referencedActions = new Set();
            if (Array.isArray(editedPropsData.Actions)) {
                editedPropsData.Actions.forEach(actionRef => {
                    referencedActions.add(extractRTIDName(actionRef));
                });
            }

            if (Array.isArray(editedPropsData.Stages)) {
                editedPropsData.Stages.forEach(stage => {
                    if (Array.isArray(stage.Actions)) {
                        stage.Actions.forEach(actionRef => referencedActions.add(extractRTIDName(actionRef)));
                    }
                    if (stage.RetreatAction) {
                        referencedActions.add(extractRTIDName(stage.RetreatAction));
                    }
                });
            }

            referencedActions.forEach(actionName => {
                if (!actionName) return;
                if (!allZombieActions[actionName]) {
                    allZombieActions[actionName] = {
                        objclass: 'ZombieActionDefinition',
                        aliases: [actionName],
                        objdata: {}
                    };
                }
                if (!editedActionsData[actionName]) {
                    editedActionsData[actionName] = deepCloneJSON(allZombieActions[actionName].objdata || {});
                }
            });

            selectedZombossTemplate = '';
            if (importedHasStages) {
                const worldMatch = importedPropsAlias.match(/^ZombossmechTemplate(.+)Props$/i);
                if (worldMatch && worldMatch[1]) {
                    const normalizedWorld = ZOMBOSS_TEMPLATES.find(t => t.toLowerCase() === worldMatch[1].toLowerCase());
                    selectedZombossTemplate = normalizedWorld || '';
                }
            }

            selectedTemplateFamily = typeof detectTemplateFamilyForZombie === 'function'
                ? (detectTemplateFamilyForZombie(selectedZombie) || '')
                : '';
            selectedTemplateIndex = 1;

            const firstAlias = Array.isArray(editedTypeAliases) && editedTypeAliases[0] ? editedTypeAliases[0] : '';
            const aliasIndexMatch = firstAlias.match(/_template_(\d+)/i);
            if (aliasIndexMatch) {
                selectedTemplateIndex = parseInt(aliasIndexMatch[1], 10) || 1;
            } else {
                const propsIndexMatch = importedPropsAlias.match(/Template(\d+)Props$/i);
                if (propsIndexMatch) {
                    selectedTemplateIndex = parseInt(propsIndexMatch[1], 10) || 1;
                }
            }

            templateModeEnabled = importedTypeObject ? /_template_/i.test(firstAlias) || importedLooksTemplate : true;

            if (!editedPropsData['ZombieArmorProps']) editedPropsData['ZombieArmorProps'] = [];
            if (!editedPropsData['ConditionImmunities']) editedPropsData['ConditionImmunities'] = [];
            if (!editedPropsData['HealthThresholdToImpAmmoLayers']) editedPropsData['HealthThresholdToImpAmmoLayers'] = [];

            loadActionsFromStages();

            const displayAlias = firstAlias || importedPropsAlias || 'ImportedZombie';
            const searchInput = document.getElementById('zombieSearch');
            if (searchInput) searchInput.value = displayAlias;
            const suggestions = document.getElementById('suggestions');
            if (suggestions) suggestions.classList.remove('active');

            const info = document.getElementById('selectedInfo');
            if (info) {
                info.innerHTML = `<p><strong>${displayAlias}</strong></p>
                    <p>Type: ${selectedZombie?.objdata?.ZombieClass || 'Imported JSON'}</p>
                    <p>Class: ${selectedZombie?.objclass || 'ZombieType'}</p>`;
                info.classList.add('active');
            }

            const editor = document.getElementById('editorContainer');
            if (editor) editor.classList.remove('hidden');

            buildPropertyForms();
            switchTab('props');

            alert(
                `Imported JSON: ${importedTypeObject ? 1 : 0} type, 1 props, ${actionObjects.length} action object(s), ` +
                `${importedAssets.importedArmorCount} armor object(s), ${importedAssets.importedProjectileCount} projectile object(s).`
            );
        }

        function addNewAction() {
            const input = document.getElementById('addActionInput');
            const rawActionName = (input?.value || '').trim();

            if (!rawActionName) {
                alert('Type or select an action name');
                return;
            }

            const allActionNames = Object.keys(allZombieActions || {});
            const actionName = allActionNames.find(name => name.toLowerCase() === rawActionName.toLowerCase());

            if (!actionName) {
                alert('Action not found. Pick one from autocomplete suggestions.');
                return;
            }

            if (!editedPropsData.Actions) {
                editedPropsData.Actions = [];
            }

            const actionDef = allZombieActions[actionName];
            if (actionDef) {
                const alreadyInUse = editedPropsData.Actions.some(action => {
                    const name = typeof action === 'string' ? extractRTIDName(action) : action.name;
                    return name === actionName;
                });

                let aliasToAdd = actionName;
                if (alreadyInUse) {
                    aliasToAdd = makeUniqueActionAlias(actionName);
                    allZombieActions[aliasToAdd] = JSON.parse(JSON.stringify(actionDef));
                    if (!Array.isArray(allZombieActions[aliasToAdd].aliases)) {
                        allZombieActions[aliasToAdd].aliases = [aliasToAdd];
                    } else {
                        allZombieActions[aliasToAdd].aliases[0] = aliasToAdd;
                    }
                }

                editedPropsData.Actions.push(makeRTID(aliasToAdd, 'ZombieActions'));
                modifiedActions.add(aliasToAdd);

                if (!editedActionsData[aliasToAdd]) {
                    editedActionsData[aliasToAdd] = JSON.parse(JSON.stringify(actionDef.objdata || {}));
                }
            }

            if (input) input.value = '';
            buildActionForm();
        }

        function removeAction(index) {
            if (editedPropsData.Actions && index >= 0 && index < editedPropsData.Actions.length) {
                const actionRTID = editedPropsData.Actions[index];
                const actionName = extractRTIDName(actionRTID);

                editedPropsData.Actions.splice(index, 1);

                const stillInMainActions = editedPropsData.Actions.some(action => {
                    const name = typeof action === 'string' ? extractRTIDName(action) : action.name;
                    return name === actionName;
                });

                const stillInStages = Array.isArray(editedPropsData?.Stages) && editedPropsData.Stages.some(stage => {
                    const inActions = Array.isArray(stage.Actions) && stage.Actions.some(a => extractRTIDName(a) === actionName);
                    const inRetreat = !!stage.RetreatAction && extractRTIDName(stage.RetreatAction) === actionName;
                    return inActions || inRetreat;
                });

                if (!stillInMainActions && !stillInStages) {
                    delete editedActionsData[actionName];
                    modifiedActions.delete(actionName);
                }

                buildActionForm();
            }
        }

        function setupZombieAutocomplete(actionName) {
            const input = document.getElementById(`zombieAutoSelect_${actionName}`);
            if (!input) return;

            const existingSuggestions = document.getElementById(`suggestions_${actionName}`);
            if (existingSuggestions) existingSuggestions.remove();

            const suggestionsList = document.createElement('div');
            suggestionsList.id = `suggestions_${actionName}`;
            suggestionsList.className = 'autocomplete-suggestions';
            suggestionsList.style.overflowY = 'auto';
            suggestionsList.style.display = 'none';
            suggestionsList.style.zIndex = '4000';
            suggestionsList.style.width = '100%';
            suggestionsList.style.marginTop = '2px';
            suggestionsList.style.left = '0';
            input.parentElement.style.position = 'relative';
            input.parentElement.appendChild(suggestionsList);

            input.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                suggestionsList.innerHTML = '';

                if (query.length < 1) {
                    suggestionsList.style.display = 'none';
                    return;
                }

                // Get currently added zombies to exclude them
                const currentZombies = editedActionsData[actionName]?.ZombieNames || [];
                const pool = getStrictZombieAliases();
                const matches = pool.filter(zombie =>
                    zombie.toLowerCase().includes(query) && !currentZombies.includes(zombie)
                ).slice(0, 10);

                if (matches.length === 0) {
                    suggestionsList.style.display = 'none';
                    return;
                }

                matches.forEach(zombie => {
                    const div = document.createElement('div');
                    div.className = 'autocomplete-item';
                    div.textContent = zombie;
                    div.style.cursor = 'pointer';
                    div.onclick = () => {
                        input.value = zombie;
                        suggestionsList.style.display = 'none';
                        input.focus();
                    };
                    suggestionsList.appendChild(div);
                });

                suggestionsList.style.display = 'block';
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest(`#zombieAutoSelect_${actionName}`) && !e.target.closest(`#suggestions_${actionName}`)) {
                    suggestionsList.style.display = 'none';
                }
            });
        }

        function renderZombieDropList(actionName) {
            const container = document.getElementById(`zombieDropList_${actionName}`);
            if (!container) return;

            container.innerHTML = '';

            if (!editedActionsData[actionName]) {
                editedActionsData[actionName] = {};
            }

            const zombieNames = editedActionsData[actionName].ZombieNames || [];
            const zombieWeights = editedActionsData[actionName].ZombieWeights || [];

            zombieNames.forEach((zombie, index) => {
                const weight = zombieWeights[index] || 10;
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.gap = '5px';
                div.style.marginBottom = '8px';
                div.style.padding = '8px';
                div.style.background = '#2a2a2a';
                div.style.border = '1px solid #4a4a4a';
                div.style.borderRadius = '3px';
                div.style.alignItems = 'center';

                div.innerHTML = `
                    <span style="flex: 1; color: #aaffaa; font-weight: bold;">${zombie}</span>
                    <input type="number" value="${weight}" min="0" step="1" 
                           data-action="${actionName}" data-zombie-index="${index}"
                           onchange="updateZombieWeight(this)" 
                           style="width: 60px; padding: 4px; background: #3a3a3a; border: 1px solid #4a4a4a; color: #e0e0e0; border-radius: 3px;">
                    <button onclick="removeZombieFromDrop('${actionName}', ${index})" 
                            style="padding: 4px 8px; background: #5a3a3a; color: #e0e0e0; border: 1px solid #6a4a4a; cursor: pointer; border-radius: 3px;">✕</button>
                `;
                container.appendChild(div);
            });

            if (zombieNames.length === 0) {
                container.innerHTML = '<p style="color: #999; margin: 0; font-size: 0.9em;">No zombies added yet</p>';
            }
        }

        function setupSpawnZombieAutocomplete(actionName, zombieList) {
        const input = document.getElementById(`spawnZombieSelect_${actionName}`);
        if (!input) return;

        input.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            let suggestions = zombieList.filter(z => z.toLowerCase().includes(value)).slice(0, 8);
            
            // Get existing spawn zombies from edited action data
            let existingList = editedActionsData[actionName]?.SpawnZombieTypes || [];
            suggestions = suggestions.filter(z => !existingList.includes(z));

            const dropdown = document.getElementById(`spawnZombieDropdown_${actionName}`);
            if (dropdown) dropdown.remove();

            if (suggestions.length > 0) {
                const ul = document.createElement('ul');
                ul.id = `spawnZombieDropdown_${actionName}`;
                ul.style.cssText = 'position: absolute; top: calc(100% + 2px); left: 0; background: #2a2a2a; border: 1px solid #4a4a4a; list-style: none; padding: 0; margin: 0; max-height: 220px; overflow-y: auto; z-index: 4000; width: 100%;';
                suggestions.forEach(z => {
                    const li = document.createElement('li');
                    li.textContent = z;
                    li.style.cssText = 'padding: 8px; cursor: pointer; color: #e0e0e0;';
                    li.onclick = () => {
                        input.value = z;
                        ul.remove();
                    };
                    li.onmouseover = () => li.style.background = '#3a3a3a';
                    li.onmouseout = () => li.style.background = 'transparent';
                    ul.appendChild(li);
                });
                input.parentElement.style.position = 'relative';
                input.parentElement.appendChild(ul);
            }
        });
    }

    function addZombieToSpawn(actionName) {
        const input = document.getElementById(`spawnZombieSelect_${actionName}`);
        if (!input || !input.value.trim()) {
            alert('Please enter a zombie name');
            return;
        }

        const zombieName = input.value.trim();
        if (!editedActionsData[actionName]) return;

        if (!editedActionsData[actionName].SpawnZombieTypes) {
            editedActionsData[actionName].SpawnZombieTypes = [];
        }

        if (editedActionsData[actionName].SpawnZombieTypes.includes(zombieName)) {
            alert('This zombie is already in the list');
            return;
        }

        editedActionsData[actionName].SpawnZombieTypes.push(zombieName);
        modifiedActions.add(actionName);
        input.value = '';
        renderSpawnZombieList(actionName);
        const dropdown = document.getElementById(`spawnZombieDropdown_${actionName}`);
        if (dropdown) dropdown.remove();
    }

    function removeZombieFromSpawn(actionName, index) {
        if (!editedActionsData[actionName]) return;

        if (editedActionsData[actionName].SpawnZombieTypes && index >= 0 && index < editedActionsData[actionName].SpawnZombieTypes.length) {
            editedActionsData[actionName].SpawnZombieTypes.splice(index, 1);
            modifiedActions.add(actionName);
            renderSpawnZombieList(actionName);
        }
    }

    function renderSpawnZombieList(actionName) {
        const listDiv = document.getElementById(`spawnZombieList_${actionName}`);
        if (!listDiv) return;

        const spawnZombies = editedActionsData[actionName]?.SpawnZombieTypes || [];

        listDiv.innerHTML = '';
        if (spawnZombies.length === 0) {
            listDiv.innerHTML = '<p style="color: #666; font-size: 0.9em; margin: 0;">No zombies to spawn</p>';
            return;
        }

        spawnZombies.forEach((zombie, index) => {
            const item = document.createElement('div');
            item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 8px; background: #2a3a2a; border: 1px solid #4a5a4a; margin-bottom: 5px; border-radius: 3px;';
            item.innerHTML = `
                <span style="color: #aaffaa;">${zombie}</span>
                <button onclick="removeZombieFromSpawn('${actionName}', ${index})" style="padding: 4px 8px; background: #5a3a3a; color: #e0e0e0; border: 1px solid #6a4a4a; cursor: pointer; border-radius: 2px; font-size: 0.85em;">Remove</button>
            `;
            listDiv.appendChild(item);
        });
    }

    function addZombieToDrop(actionName) {
        const input = document.getElementById(`zombieAutoSelect_${actionName}`);
        const weightInput = document.getElementById(`zombieWeight_${actionName}`);
        const zombieName = input?.value.trim();
        const weight = parseInt(weightInput?.value) || 10;

        if (!zombieName) {
            alert('Enter a zombie name');
            return;
        }

        if (!editedActionsData[actionName]) {
            editedActionsData[actionName] = {};
        }
        if (!Array.isArray(editedActionsData[actionName].ZombieNames)) {
            editedActionsData[actionName].ZombieNames = [];
        }
        if (!Array.isArray(editedActionsData[actionName].ZombieWeights)) {
            editedActionsData[actionName].ZombieWeights = [];
        }

        if (editedActionsData[actionName].ZombieNames.includes(zombieName)) {
            alert(`"${zombieName}" is already in the list`);
            return;
        }

        editedActionsData[actionName].ZombieNames.push(zombieName);
        editedActionsData[actionName].ZombieWeights.push(weight);
        modifiedActions.add(actionName);

        if (input) input.value = '';
        if (weightInput) weightInput.value = '10';

        renderZombieDropList(actionName);
    }

    function removeZombieFromDrop(actionName, index) {
        const actionData = editedActionsData[actionName];
        if (!actionData) return;

        if (Array.isArray(actionData.ZombieNames)) {
            actionData.ZombieNames.splice(index, 1);
        }
        if (Array.isArray(actionData.ZombieWeights)) {
            actionData.ZombieWeights.splice(index, 1);
        }

        modifiedActions.add(actionName);
        renderZombieDropList(actionName);
    }

    function updateZombieWeight(element) {
        const actionName = element.dataset.action;
        const index = parseInt(element.dataset.zombieIndex);
        const weight = parseInt(element.value) || 10;

        if (!editedActionsData[actionName]) {
            editedActionsData[actionName] = {};
        }
        if (!Array.isArray(editedActionsData[actionName].ZombieWeights)) {
            editedActionsData[actionName].ZombieWeights = [];
        }

        editedActionsData[actionName].ZombieWeights[index] = weight;
        modifiedActions.add(actionName);
    }

