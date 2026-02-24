        (async () => {
            await loadZombieData();
            if (typeof initCustomAssetEditors === 'function') {
                initCustomAssetEditors();
            }
            if (typeof initRawJsonBrowser === 'function') {
                initRawJsonBrowser();
            }
        })();
