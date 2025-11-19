// Simple client-side loader for GeoJSON and Leaflet display
// If you need to show large datasets, consider server-side tiling or clustering offline.

const map = L.map('map').setView([52.0, 5.0], 7);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const dataUrl = 'data/accidents_2022_2024_full.geojson';

async function loadGeoJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`);
  return res.json();
}

function prettyProps(props) {
  const labels = {
    'verkeersongeval_afloop': 'Outcome',
    'jaar_ongeval': 'Year',
    'aantal_partijen': 'Parties',
    'maximum_snelheid': 'Speed limit',
    'lichtgesteldheid': 'Light',
    'wegdek': 'Road surface'
  };

  const order = ['verkeersongeval_afloop','jaar_ongeval','aantal_partijen','maximum_snelheid','lichtgesteldheid','wegdek'];
  const parts = [];
  order.forEach(k => {
    if (k in props) {
      const label = labels[k] || k;
      const val = props[k] === null || props[k] === undefined ? '' : String(props[k]);
      parts.push(`<b>${label}</b>: ${val}`);
    }
  });
  // If there are any other properties (unexpected), append first few
  const extra = Object.keys(props).filter(k => !order.includes(k)).slice(0, 6);
  extra.forEach(k => parts.push(`<b>${k}</b>: ${props[k]}`));
  return parts.join('<br>');
}

(async function() {
  try {
    const data = await loadGeoJSON(dataUrl);
    const markers = L.markerClusterGroup();

    const geoLayer = L.geoJSON(data, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, { radius: 4, fillColor: '#d9534f', color: '#800', weight: 1, fillOpacity: 0.8 });
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        layer.bindPopup(prettyProps(props));
      }
    });

    markers.addLayer(geoLayer);
    map.addLayer(markers);

    // Fit to bounds if possible
    const bounds = geoLayer.getBounds();
    if (bounds.isValid()) map.fitBounds(bounds.pad(0.1));
  } catch (err) {
    console.error(err);
    const ctl = L.control({position: 'topright'});
    ctl.onAdd = function(){
      const div = L.DomUtil.create('div', 'error');
      div.innerHTML = `<strong>Error</strong><br>${err.message}`;
      return div;
    };
    ctl.addTo(map);
  }
})();
