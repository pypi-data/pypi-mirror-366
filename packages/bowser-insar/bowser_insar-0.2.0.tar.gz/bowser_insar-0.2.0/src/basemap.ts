// basemap.ts
// https://leaflet-extras.github.io/leaflet-providers/preview/
// https://github.com/geopandas/xyzservices/blob/main/provider_sources/leaflet-providers-parsed.json

interface BaseMapItem {
    url: string;
    attribution: string;
}

const baseMaps: { [key: string]: BaseMapItem } = {
    esriSatellite: {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attribution:
            'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    },
    openstreetmap: {
        url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution:
            '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    },
    topography: {
        url: 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
        attribution:
            'Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>',
    },
    openTopoMap: {
        url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attribution:
            'Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, '
            + '<a href="http://viewfinderpanoramas.org">SRTM</a> | Map style © '
            + '<a href="https://opentopomap.org">OpenTopoMap</a> '
            + '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
    },
    shadedRelief: {
        url: 'https://server.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
        attribution: 'USGS',
    },
};

export type { BaseMapItem };
export { baseMaps };
