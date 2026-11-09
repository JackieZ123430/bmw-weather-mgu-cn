'use strict';

const fs = require('fs');
const path = require('path');
const api = require('./api');
const normalize = require('./normalize');

function create(dataDir, log) {
    const cacheFile = path.join(dataDir, 'weather-cache.json');
    let cached = null;
    try { cached = JSON.parse(fs.readFileSync(cacheFile, 'utf8')); } catch (e) {}

    function save(data) {
        const temp = cacheFile + '.tmp';
        try {
            fs.writeFileSync(temp, JSON.stringify(data));
            fs.renameSync(temp, cacheFile);
        } catch (e) {
            try { fs.unlinkSync(temp); } catch (ignore) {}
            if (log) log.warn('Nu am putut salva cache-ul meteo: ' + e.message);
        }
    }

    return {
        cached: function () { return cached; },
        refresh: function (location) {
            if (!location) return Promise.reject(new Error('Configurează coordonatele locației în Setări'));
            return api.fetchForecast(location.latitude, location.longitude).then(function (raw) {
                cached = normalize.normalize(raw);
                save(cached);
                return { data: cached, stale: false };
            }).catch(function (error) {
                if (cached) return { data: cached, stale: true, error: error };
                throw error;
            });
        }
    };
}

module.exports = { create: create };
