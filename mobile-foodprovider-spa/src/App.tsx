import {useEffect, useRef, useState} from 'react'
import MapView from './components/MapView'
import type {FoodProviderDTO} from './api'
import './index.css'
import SearchLegend, {type SearchMode} from './components/SearchLegend'

const SF_CENTER = {lat: 37.7749, lng: -122.4194}

type CityKey = 'San Francisco'

type LatLng = { lat: number, lng: number }

function App() {
    const [city, setCity] = useState<CityKey>('San Francisco')
    const [mapCenter, setMapCenter] = useState(SF_CENTER)
    const [zoom, setZoom] = useState(12)

    const [providers, setProviders] = useState<FoodProviderDTO[]>([])
    const [highlighted, setHighlighted] = useState<Set<string>>(new Set())
    const [dropPin, setDropPin] = useState<LatLng | null>(null)

    const [mode, setMode] = useState<SearchMode>('form')
    const closestHandlerRef = useRef<((coords: LatLng) => Promise<void>) | null>(null)

    useEffect(() => {
        // Only SF supported for now
        if (city === 'San Francisco') {
            setMapCenter(SF_CENTER)
            setZoom(12)
        }
    }, [city])

    function onMapClick(coords: LatLng) {
        if (mode === 'pin' && closestHandlerRef.current) {
            void closestHandlerRef.current(coords)
        }
    }

    return (
        <div style={{height: '100vh', width: '100vw', position: 'relative'}}>
            <div style={{position: 'absolute', top: 16, right: 16, zIndex: 1000, background: 'white', color: 'black', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.15)'}}>
                <div
                    style={{padding: 8, borderRadius: 4, boxShadow: '0 2px 8px rgba(0,0,0,0.15)'}}>
                    <label style={{marginRight: 8}}>City</label>
                    <select value={city} onChange={e => setCity(e.target.value as CityKey)}>
                        <option>San Francisco</option>
                    </select>
                </div>
                <SearchLegend
                    onResults={setProviders}
                    onHighlightChange={setHighlighted}
                    onMapViewChange={(center, z) => {
                        setMapCenter(center);
                        setZoom(z)
                    }}
                    onDropPinChange={setDropPin}
                    onModeChange={setMode}
                    registerClosestHandler={(handler) => {
                        closestHandlerRef.current = handler
                    }}
                />
            </div>


            <div style={{position: 'absolute', inset: 0}}>
                <MapView
                    center={mapCenter}
                    zoom={zoom}
                    markers={providers}
                    highlightedIds={highlighted}
                    onMapClick={onMapClick}
                    dropPin={dropPin}
                />
            </div>
        </div>
    )
}

export default App
