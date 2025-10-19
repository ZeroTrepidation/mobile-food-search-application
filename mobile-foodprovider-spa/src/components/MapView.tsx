import { useEffect, useMemo } from 'react'
import L from 'leaflet'
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap, useMapEvents } from 'react-leaflet'
import type { FoodProviderDTO } from '../api'

export type LatLng = { lat: number, lng: number }

interface MapViewProps {
  center: LatLng
  zoom?: number
  markers: FoodProviderDTO[]
  highlightedIds?: Set<string>
  onMapClick?: (coords: LatLng) => void
  onMarkerClick?: (provider: FoodProviderDTO) => void
  dropPin?: LatLng | null
}

function ViewController({ center, zoom }: { center: LatLng, zoom: number }) {
  const map = useMap()
  useEffect(() => {
    map.setView([center.lat, center.lng], zoom)
  }, [map, center.lat, center.lng, zoom])
  return null
}

function MapClickHandler({ onMapClick }: { onMapClick?: (coords: LatLng) => void }) {
  useMapEvents({
    click(e) {
      onMapClick?.({ lat: e.latlng.lat, lng: e.latlng.lng })
    }
  })
  return null
}

export default function MapView({ center, zoom = 13, markers, highlightedIds, onMapClick, onMarkerClick, dropPin }: MapViewProps) {
  const pinIcon = useMemo(() => L.divIcon({
    className: 'custom-pin',
    html: '<div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:12px solid #1e88e5;"></div>'
  }), [])

  return (
    <MapContainer center={[center.lat, center.lng]} zoom={zoom} style={{ width: '100%', height: '100%' }} scrollWheelZoom>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      <ViewController center={center} zoom={zoom} />
      <MapClickHandler onMapClick={onMapClick} />

      {markers.filter(p => p.latitude != null && p.longitude != null).map(p => {
        const isHighlighted = highlightedIds?.has(p.locationId)
        const color = isHighlighted ? '#ff5252' : '#1e88e5'
        const radius = isHighlighted ? 8 : 6
        return (
          <CircleMarker
            key={p.locationId}
            center={[p.latitude as number, p.longitude as number]}
            radius={radius}
            pathOptions={{ color: isHighlighted ? '#ffffff' : color, weight: 2, fillColor: color, fillOpacity: isHighlighted ? 1 : 0.9 }}
            eventHandlers={{ click: () => onMarkerClick?.(p) }}
          >
            <Popup>
              <div>
                <strong>{p.name}</strong><br />
                {p.address ?? ''}<br />
                {p.foodItems ?? ''}
              </div>
            </Popup>
          </CircleMarker>
        )
      })}

      {dropPin && (
        <Marker position={[dropPin.lat, dropPin.lng]} icon={pinIcon} />
      )}
    </MapContainer>
  )
}
