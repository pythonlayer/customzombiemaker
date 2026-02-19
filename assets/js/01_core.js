let allZombieTypes = [];
        let allZombieProperties = [];
        let allZombieActions = {};
        let allPopAnims = [];
        let allResourceGroups = [];
        let allAudioGroups = [];
        let selectedZombie = null;
        let selectedZombieProperties = null;
        let editedTypeData = {};
        let editedTypeAliases = [];
        let editedPropsData = {};
        let editedActionsData = {};
        let modifiedActions = new Set();
        let allArmors = [];
        let defaultPropsData = {};
        let selectedZombossTemplate = '';
        let selectedTemplateFamily = '';
        let selectedTemplateIndex = 1;
        let templateModeEnabled = false;

        const ZOMBOSS_TEMPLATES = ['Egypt', 'Pirate', 'Cowboy', 'Future', 'Dark', 'Beach', 'IceAge', 'LostCity', 'Eighties', 'Dino', 'Modern', 'Holiday', 'Steam', 'Spongebob', 'Circus', 'SkyCity', 'Market'];
        const ZOMBIE_TEMPLATE_DEFS = [
            { key: 'basic', label: 'basic_template_(1-15)', typePrefix: 'basic_template_', propsBase: 'BasicTemplate', min: 1, max: 15 },
            { key: 'imp', label: 'imp_template_(1-15)', typePrefix: 'imp_template_', propsBase: 'ImpTemplate', min: 1, max: 15 },
            { key: 'healer', label: 'healer_template_(1-15)', typePrefix: 'healer_template_', propsBase: 'HealerTemplate', min: 1, max: 15 },
            { key: 'caketank', label: 'caketank_template_(1-15)', typePrefix: 'caketank_template_', propsBase: 'CaketankTemplate', min: 1, max: 15 },
            { key: 'barrel', label: 'barrel_template_(1-10)', typePrefix: 'barrel_template_', propsBase: 'BarrelTemplate', min: 1, max: 10 },
            { key: 'consultant', label: 'consultant_template_(1-10)', typePrefix: 'consultant_template_', propsBase: 'ConsultantTemplate', min: 1, max: 10 },
            { key: 'hunter', label: 'hunter_template_(1-10)', typePrefix: 'hunter_template_', propsBase: 'HunterTemplate', min: 1, max: 10 },
            { key: 'magician', label: 'magician_template_(1-10)', typePrefix: 'magician_template_', propsBase: 'MagicianTemplate', min: 1, max: 10 },
            { key: 'zmech', label: 'zmech_template_(1-15)', typePrefix: 'zmech_template_', propsBase: 'ZmechTemplate', min: 1, max: 15 },
            { key: 'caesar', label: 'caesar_template_(1-15)', typePrefix: 'caesar_template_', propsBase: 'CaesarTemplate', min: 1, max: 15 },
            { key: 'cardio', label: 'cardio_template_(1-15)', typePrefix: 'cardio_template_', propsBase: 'CardioTemplate', min: 1, max: 15 },
            { key: 'hamsterball', label: 'hamsterball_template_(1-10)', typePrefix: 'hamsterball_template_', propsBase: 'HamsterballTemplate', min: 1, max: 10 },
            { key: 'imptwin', label: 'imptwin_template_(1-10)', typePrefix: 'imptwin_template_', propsBase: 'ImptwinTemplate', min: 1, max: 10 },
            { key: 'bug', label: 'bug_template_(1-10)', typePrefix: 'bug_template_', propsBase: 'BugTemplate', min: 1, max: 10 },
            { key: 'weaselhoarder', label: 'weaselhoarder_template_(1-10)', typePrefix: 'weaselhoarder_template_', propsBase: 'WeaselhoarderTemplate', min: 1, max: 10 },
            { key: 'octopus', label: 'octopus_template_(1-10)', typePrefix: 'octopus_template_', propsBase: 'OctopusTemplate', min: 1, max: 10 },
            { key: 'bass', label: 'bass_template_(1-10)', typePrefix: 'bass_template_', propsBase: 'BassTemplate', min: 1, max: 10 },
            { key: 'boombox', label: 'boombox_template_(1-10)', typePrefix: 'boombox_template_', propsBase: 'BoomboxTemplate', min: 1, max: 10 },
            { key: 'breakdancer', label: 'breakdancer_template_(1-10)', typePrefix: 'breakdancer_template_', propsBase: 'BreakdancerTemplate', min: 1, max: 10 },
            { key: 'shield', label: 'shield_template_(1-10)', typePrefix: 'shield_template_', propsBase: 'ShieldTemplate', min: 1, max: 10 },
            { key: 'dove', label: 'dove_template_(1-10)', typePrefix: 'dove_template_', propsBase: 'DoveTemplate', min: 1, max: 10 },
            { key: 'fisherman', label: 'fisherman_template_(1-10)', typePrefix: 'fisherman_template_', propsBase: 'FishermanTemplate', min: 1, max: 10 },
            { key: 'footballmech', label: 'footballmech_template_(1-10)', typePrefix: 'footballmech_template_', propsBase: 'FootballmechTemplate', min: 1, max: 10 },
            { key: 'yeti', label: 'yeti_template_(1-10)', typePrefix: 'yeti_template_', propsBase: 'YetiTemplate', min: 1, max: 10 },
            { key: 'cannon', label: 'cannon_template_(1-10)', typePrefix: 'cannon_template_', propsBase: 'CannonTemplate', min: 1, max: 10 },
            { key: 'superfan', label: 'superfan_template_(1-10)', typePrefix: 'superfan_template_', propsBase: 'SuperfanTemplate', min: 1, max: 10 },
            { key: 'gargantuar', label: 'gargantuar_template_(1-10)', typePrefix: 'gargantuar_template_', propsBase: 'GargantuarTemplate', min: 1, max: 10 },
            { key: 'vendor', label: 'vendor_template_(1-10)', typePrefix: 'vendor_template_', propsBase: 'VendorTemplate', min: 1, max: 10 },
            { key: 'excavator', label: 'excavator_template_(1-10)', typePrefix: 'excavator_template_', propsBase: 'ExcavatorTemplate', min: 1, max: 10 },
            { key: 'battleplane', label: 'battleplane_template_(1-10)', typePrefix: 'battleplane_template_', propsBase: 'BattleplaneTemplate', min: 1, max: 10 },
            { key: 'electric', label: 'electric_template_(1-10)', typePrefix: 'electric_template_', propsBase: 'ElectricTemplate', min: 1, max: 10 },
            { key: 'rocket', label: 'rocket_template_(1-10)', typePrefix: 'rocket_template_', propsBase: 'RocketTemplate', min: 1, max: 10 },
            { key: 'troglobite', label: 'troglobite_template_(1-10)', typePrefix: 'troglobite_template_', propsBase: 'TroglobiteTemplate', min: 1, max: 10 },
            { key: 'carnivalhat', label: 'carnivalhat_template_(1-10)', typePrefix: 'carnivalhat_template_', propsBase: 'CarnivalhatTemplate', min: 1, max: 10 },
            { key: 'zombotany', label: 'zombotany_template_(1-30)', typePrefix: 'zombotany_template_', propsBase: 'ZombotanyTemplate', min: 1, max: 30 },
            { key: 'tombraiser', label: 'tombraiser_template_(1-10)', typePrefix: 'tombraiser_template_', propsBase: 'TombraiserTemplate', min: 1, max: 10 },
            { key: 'juggler', label: 'juggler_template_(1-10)', typePrefix: 'juggler_template_', propsBase: 'JugglerTemplate', min: 1, max: 10 },
            { key: 'servant', label: 'servant_template_(1-10)', typePrefix: 'servant_template_', propsBase: 'ServantTemplate', min: 1, max: 10 },
            { key: 'shikaisen', label: 'shikaisen_template_(1-10)', typePrefix: 'shikaisen_template_', propsBase: 'ShikaisenTemplate', min: 1, max: 10 }
        ];

        const CONDITION_LIST = [
            'speedup1', 'speedup2', 'speedup3', 'speedup4',
            'speeddown1', 'speeddown2', 'speeddown3', 'speeddown4',
            'potionspeed1', 'potionspeed2', 'potionspeed3',
            'potiontoughness1', 'potiontoughness2', 'potiontoughness3',
            'terrified', 'hungered', 'sapped', 'stalled', 'chilled', 'chill', 'freeze', 'stun',
            'butter', 'bleeding', 'lightning', 'rush', 'tossed', 'warpingIn', 'warpingOut',
            'hypnotized', 'sunbeaned', 'morphedtogargantuar', 'damageflash', 'zombossstun',
            'haunted', 'icecubed', 'unsuspendable', 'invincible', 'poisoned',
            'contagiouspoison', 'decaypoison', 'bloomingheartdebuff', 'solarflared',
            'shrinking', 'shrunken', 'present_boxed', 'knighted',
            'potionsuper1', 'potionsuper2', 'potionsuper3', 'dazeystunned', 'stackableslow',
            'gummed', 'hotedateattraction', 'suiciding', 'suncarrier50', 'suncarrier100',
            'suncarrier250', 'stoneblocked', 'petrified', 'hasplantfood', 'blownoff',
            'stickybombed', 'blockolistunned', 'bramblebushstunned', 'bramblebushgrabbed',
            'transparent', 'saucershrink', 'saucerpulled', 'loquatstunned', 'affectEatdps',
            'begoniachilled', 'begoniafire', 'begoniamixed', 'ranked', 'eatdpsUp', 'popsmart'
        ];

        function makeRTID(name, type) {
            return `RTID(${name}@${type})`;
        }

        function makeUniqueActionAlias(baseAlias) {
            const existing = new Set(Object.keys(allZombieActions || {}));
            let idx = 2;
            let candidate = `${baseAlias}_${idx}`;
            while (existing.has(candidate)) {
                idx++;
                candidate = `${baseAlias}_${idx}`;
            }
            return candidate;
        }

        function extractRTIDName(rtidString) {
            if (typeof rtidString !== 'string') {
                return String(rtidString);
            }
            const match = rtidString.match(/RTID\((.+?)@/);
            return match ? match[1] : rtidString;
        }

        function extractAllArmors() {
            allArmors = [];
            allZombieProperties.forEach(prop => {
                if (prop.objdata?.ZombieArmorProps && Array.isArray(prop.objdata.ZombieArmorProps)) {
                    prop.objdata.ZombieArmorProps.forEach(armor => {
                        const armorName = extractRTIDName(armor);
                        if (!allArmors.includes(armorName)) {
                            allArmors.push(armorName);
                        }
                    });
                }
            });
            allArmors.sort();
        }

        function getStrictZombieAliases() {
            const aliasSet = new Set();
            allZombieTypes.forEach(z => {
                const objclass = (z.objclass || '').toLowerCase();
                const aliases = Array.isArray(z.aliases) ? z.aliases : [];
                const isPlantClass = objclass.includes('plant');
                aliases.forEach(a => {
                    if (!a) return;
                    if (!isPlantClass) aliasSet.add(a);
                });
            });
            aliasSet.add('idiot');
            return Array.from(aliasSet).sort((a, b) => a.localeCompare(b));
        }

        async function loadZombieData() {
            try {
                const typesResponse = await fetch('ZOMBIETYPES_UPDATED.json');
                const propsResponse = await fetch('ZOMBIEPROPERTIES_UPDATED.json');
                
                const typesData = await typesResponse.json();
                const propsData = await propsResponse.json();

                allZombieTypes = typesData.objects || [];
                allZombieProperties = propsData.objects || [];

                // Try to load zombie actions
                try {
                    const actionsResponse = await fetch('ZombieActions.json');
                    const actionsData = await actionsResponse.json();
                    const actionsArray = actionsData.objects || [];
                    // Convert array to object keyed by action name
                    allZombieActions = {};
                    actionsArray.forEach(action => {
                        if (action.aliases && action.aliases.length > 0) {
                            const actionName = action.aliases[0];
                            allZombieActions[actionName] = action;
                        }
                    });
                    console.log('Loaded', Object.keys(allZombieActions).length, 'zombie actions');
                    // If we've already loaded properties with Stages, populate stage actions now
                    try {
                        if (editedPropsData && editedPropsData.Stages) {
                            loadActionsFromStages();
                            // Rebuild forms to reflect newly loaded actions
                            buildPropertyForms();
                        }
                    } catch (e) {
                        // ignore if functions not yet defined
                    }
                } catch (e) {
                    console.warn('ZombieActions.json file not found');
                }

                // Try to load PT.json for additional PopAnim and ResGroups/AudioGroups
                try {
                    const ptResponse = await fetch('PT.json');
                    const ptData = await ptResponse.json();
                    if (ptData.objects) {
                        allZombieTypes = allZombieTypes.concat(ptData.objects);
                    }
                    console.log('Loaded PT.json data');
                } catch (e) {
                    console.warn('PT.json file not found (optional)');
                }

                extractAllArmors();
                extractPopAnimsAndGroups();
                setupSearchFunctionality();
            } catch (error) {
                console.warn('Could not load JSON files:', error);
            }
        }

        function extractPopAnimsAndGroups() {
            allPopAnims = new Set();
            allResourceGroups = new Set();
            allAudioGroups = new Set();

            allZombieTypes.forEach(zombie => {
                if (zombie.objdata) {
                    // Extract PopAnim
                    if (zombie.objdata.PopAnim) {
                        allPopAnims.add(zombie.objdata.PopAnim);
                    }
                    // Extract ResourceGroups
                    if (Array.isArray(zombie.objdata.ResourceGroups)) {
                        zombie.objdata.ResourceGroups.forEach(rg => allResourceGroups.add(rg));
                    }
                    // Extract AudioGroups
                    if (Array.isArray(zombie.objdata.AudioGroups)) {
                        zombie.objdata.AudioGroups.forEach(ag => allAudioGroups.add(ag));
                    }
                }
            });

            // Convert to sorted arrays
            allPopAnims = Array.from(allPopAnims).sort();
            allResourceGroups = Array.from(allResourceGroups).sort();
            allAudioGroups = Array.from(allAudioGroups).sort();
            
            console.log('Extracted', allPopAnims.length, 'PopAnims,', allResourceGroups.length, 'ResourceGroups,', allAudioGroups.length, 'AudioGroups');
        }

        function setupSearchFunctionality() {
            const searchInput = document.getElementById('zombieSearch');
            const suggestionsContainer = document.getElementById('suggestions');

            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                suggestionsContainer.innerHTML = '';

                if (query.length < 1) {
                    suggestionsContainer.classList.remove('active');
                    return;
                }

                const matches = allZombieTypes.filter(zombie => {
                    const objclass = (zombie.objclass || '').toLowerCase();
                    if (objclass.includes('plant')) return false;
                    if (zombie.aliases && Array.isArray(zombie.aliases)) {
                        return zombie.aliases.some(alias => 
                            alias.toLowerCase().includes(query)
                        );
                    }
                    return false;
                });

                if (matches.length === 0) {
                    suggestionsContainer.innerHTML = '<div class="suggestion-item">No matches</div>';
                    suggestionsContainer.classList.add('active');
                    return;
                }

                matches.slice(0, 15).forEach(zombie => {
                    const alias = zombie.aliases?.[0] || 'Unknown';
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = alias;
                    div.onclick = () => selectZombie(zombie, alias);
                    suggestionsContainer.appendChild(div);
                });

                suggestionsContainer.classList.add('active');
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('.search-box')) {
                    suggestionsContainer.classList.remove('active');
                }
            });
        }

        function selectZombie(zombie, alias) {
            selectedZombie = zombie;
            editedTypeData = JSON.parse(JSON.stringify(zombie.objdata || {}));
            delete editedTypeData['ImpType'];
            editedTypeAliases = Array.isArray(zombie.aliases) ? JSON.parse(JSON.stringify(zombie.aliases)) : [];
            modifiedActions = new Set();
            selectedZombossTemplate = ''; // Reset template when selecting new zombie
            selectedTemplateFamily = detectTemplateFamilyForZombie(zombie);
            selectedTemplateIndex = 1;
            templateModeEnabled = false;
            
            document.getElementById('zombieSearch').value = alias;
            document.getElementById('suggestions').classList.remove('active');

            const info = document.getElementById('selectedInfo');
            info.innerHTML = `<p><strong>${alias}</strong></p>
                <p>Type: ${zombie.objdata?.ZombieClass || 'N/A'}</p>
                <p>Class: ${zombie.objclass || 'N/A'}</p>`;
            info.classList.add('active');

            // Load base properties
            loadBaseProperties(zombie.objdata?.Properties);

            // Ensure default arrays exist for armor and condition immunities
            if (!editedPropsData['ZombieArmorProps']) editedPropsData['ZombieArmorProps'] = [];
            if (!editedPropsData['ConditionImmunities']) editedPropsData['ConditionImmunities'] = [];
            if (!editedPropsData['HealthThresholdToImpAmmoLayers']) editedPropsData['HealthThresholdToImpAmmoLayers'] = [];

            // Show editor and build forms
            document.getElementById('editorContainer').classList.remove('hidden');
            buildPropertyForms();
        }

        function loadBaseProperties(propertiesRef) {
            if (!propertiesRef) return;

            // Extract the property name from RTID format: "RTID(PropertyName@ZombieProperties)"
            const match = propertiesRef.match(/RTID\((.+?)@/);
            const propertyName = match ? match[1] : null;

            if (!propertyName) return;

            // Find the props entry with an alias matching the exact property name
            const baseProps = allZombieProperties.find(prop => {
                return prop.aliases && prop.aliases.includes(propertyName);
            });

            if (baseProps?.objdata) {
                selectedZombieProperties = baseProps;
                editedPropsData = JSON.parse(JSON.stringify(baseProps.objdata));
                defaultPropsData = JSON.parse(JSON.stringify(baseProps.objdata));
                
                    // Auto-load actions from Stages if this is a Zomboss
                    loadActionsFromStages();
            } else {
                editedPropsData = {};
                defaultPropsData = {};
            }
        }

        function loadActionsFromStages() {
            // Extract all actions referenced in Stages and add them to Actions
            if (!editedPropsData['Stages'] || !Array.isArray(editedPropsData['Stages'])) {
                return;
            }

            if (!editedPropsData.Actions) {
                editedPropsData.Actions = [];
            }

            const stageActions = new Set();

            editedPropsData['Stages'].forEach(stage => {
                // Add stage actions
                if (Array.isArray(stage.Actions)) {
                    stage.Actions.forEach(actionRTID => {
                        const actionName = extractRTIDName(actionRTID);
                        stageActions.add(actionName);
                    });
                }

                // Add retreat action
                if (stage.RetreatAction) {
                    const actionName = extractRTIDName(stage.RetreatAction);
                    stageActions.add(actionName);
                }
            });

            // Add these actions to the main Actions array if not already present
            stageActions.forEach(actionName => {
                const alreadyAdded = editedPropsData.Actions.some(action => {
                    const name = typeof action === 'string' ? extractRTIDName(action) : action.name;
                    return name === actionName;
                });

                if (!alreadyAdded) {
                    const actionDef = allZombieActions[actionName];
                    if (actionDef) {
                        const actionRTID = makeRTID(actionName, 'ZombieActions');
                        editedPropsData.Actions.push(actionRTID);
                    }
                }
            });
        }

        function buildPropertyForms() {
            const isZomboss = editedPropsData?.Stages && Array.isArray(editedPropsData.Stages);
            if (isZomboss) {
                const typeContainer = document.getElementById('typeProperties');
                if (typeContainer) typeContainer.innerHTML = '';
            } else {
                buildTypeForm();
            }
            buildPropsForm();
            buildActionForm();
            if (typeof updateEditorTabs === 'function') {
                updateEditorTabs();
            }
        }

