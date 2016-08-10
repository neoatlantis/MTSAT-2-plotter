define(['jquery', 'leaflet'], function($){
//////////////////////////////////////////////////////////////////////////////
L.Control.MousePosition = L.Control.extend({
  options: {
    position: 'bottomleft',
    separator: ' : ',
    emptyString: 'Unavailable',
    lngFirst: false,
    numDigits: 5,
    lngFormatter: undefined,
    latFormatter: undefined,
    prefix: ""
  },

  onAdd: function (map) {
    this._container = L.DomUtil.create('div', 'leaflet-control-mouseposition');
    L.DomEvent.disableClickPropagation(this._container);
    map.on('mousemove', this._onMouseMove, this);
    this._container.innerHTML=this.options.emptyString;
    $(this._container).click(this._onClick);
    return this._container;
  },

  onRemove: function (map) {
    map.off('mousemove', this._onMouseMove);
    $(this._container).off('click', this._onClick);
  },

  _onClick: function(){
    $(this).data('useFormatter', !Boolean($(this).data('useFormatter')));
  },

  _onMouseMove: function (e) {
    var useFormatter = $(this._container).data('useFormatter');
    var lng = ((this.options.lngFormatter && useFormatter) ? 
        this.options.lngFormatter(e.latlng.lng) :
        L.Util.formatNum(e.latlng.lng, this.options.numDigits)
    );
    var lat = ((this.options.latFormatter && useFormatter) ? 
        this.options.latFormatter(e.latlng.lat) :
        L.Util.formatNum(e.latlng.lat, this.options.numDigits)
    );
    var value = this.options.lngFirst ? lng + this.options.separator + lat : lat + this.options.separator + lng;
    var prefixAndValue = this.options.prefix + ' ' + value;
//    prefixAndValue += ': (' + e.containerPoint.x + ',' + e.containerPoint.y + ')'
    this._container.innerHTML = prefixAndValue;
  }

});

L.Map.mergeOptions({
    positionControl: false
});

L.Map.addInitHook(function () {
    if (this.options.positionControl) {
        this.positionControl = new L.Control.MousePosition();
        this.addControl(this.positionControl);
    }
});

L.control.mousePosition = function (options) {
    return new L.Control.MousePosition(options);
};
//////////////////////////////////////////////////////////////////////////////
});
