import L from 'leaflet';

// Use export type for interfaces with isolatedModules
export type MousePositionOptions = {
    position?: L.ControlPosition;
    separator?: string;
    emptyString?: string;
    lngFirst?: boolean;
    numDigits?: number;
    lngFormatter?: (lng: number) => string;
    latFormatter?: (lat: number) => string;
    prefix?: string;
};

class MousePositionControl extends L.Control {
    private _container: HTMLElement | null = null;
    // Make options public to match L.Control
    public options: MousePositionOptions;

    constructor(options?: MousePositionOptions) {
        super(options);
        this.options = {
            position: 'bottomleft',
            separator: ' : ',
            emptyString: 'Unavailable',
            lngFirst: false,
            numDigits: 5,
            lngFormatter: undefined,
            latFormatter: undefined,
            prefix: "",
            ...options
        };
    }

    onAdd(map: L.Map): HTMLElement {
        this._container = L.DomUtil.create('div', 'leaflet-control-mouseposition');
        L.DomEvent.disableClickPropagation(this._container);
        map.on('mousemove', this._onMouseMove, this);
        this._container.innerHTML = this.options.emptyString || '';
        return this._container;
    }

    onRemove(map: L.Map): void {
        map.off('mousemove', this._onMouseMove, this);
    }

    private _onMouseMove(e: L.LeafletMouseEvent): void {
        if (!this._container) return;

        const lng = this.options.lngFormatter
            ? this.options.lngFormatter(e.latlng.lng)
            : L.Util.formatNum(e.latlng.lng, this.options.numDigits || 5);

        const lat = this.options.latFormatter
            ? this.options.latFormatter(e.latlng.lat)
            : L.Util.formatNum(e.latlng.lat, this.options.numDigits || 5);

        // Format with labels "lon" and "lat"
        const formattedText = `lon ${lng}    lat ${lat}`;

        // Add prefix if it exists
        const prefixAndValue = this.options.prefix
            ? this.options.prefix + ' ' + formattedText
            : formattedText;

        this._container.innerHTML = prefixAndValue;
    }
}

// Add factory method to L.control namespace
declare module 'leaflet' {
    namespace control {
        function mousePosition(options?: MousePositionOptions): MousePositionControl;
    }
}

L.control.mousePosition = function (options?: MousePositionOptions): MousePositionControl {
    return new MousePositionControl(options);
};

export const mousePosition = L.control.mousePosition;
// Use export type for type-only exports with isolatedModules
export { MousePositionControl };
