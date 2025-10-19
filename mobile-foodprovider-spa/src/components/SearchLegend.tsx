import {useEffect, useMemo, useState} from 'react'
import type {FoodProviderDTO} from '../api'
import {closest, searchByName, searchByStreet} from '../api'
import {Dropdown} from 'primereact/dropdown'
import {InputText} from 'primereact/inputtext'
import {Button} from 'primereact/button'
import {InputIcon} from "primereact/inputicon";
import {IconField} from "primereact/iconfield";

export type LatLng = { lat: number, lng: number }

export type SearchMode = 'form' | 'pin'

const STATUSES: string[] = ['', 'APPROVED', 'REQUESTED', 'SUSPEND', 'EXPIRED']

interface SearchLegendProps {
    onResults: (providers: FoodProviderDTO[]) => void
    onHighlightChange: (ids: Set<string>) => void
    onMapViewChange: (center: LatLng, zoom: number) => void
    onDropPinChange: (coords: LatLng | null) => void
    onModeChange: (mode: SearchMode) => void
    registerClosestHandler: (handler: (coords: LatLng) => Promise<void>) => void
}

export default function SearchLegend({
                                         onResults,
                                         onHighlightChange,
                                         onMapViewChange,
                                         onDropPinChange,
                                         onModeChange,
                                         registerClosestHandler
                                     }: SearchLegendProps) {
    const [collapsed, setCollapsed] = useState(false)
    const [mode, setMode] = useState<SearchMode>('form')

    const [nameQuery, setNameQuery] = useState('')
    const [status, setStatus] = useState<string>('')
    const [streetQuery, setStreetQuery] = useState('')
    const [limit, setLimit] = useState(5)

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const statusOptions = useMemo(() => STATUSES.map(s => ({label: s || 'Any', value: s})), [])

    useEffect(() => {
        onModeChange(mode)
        // When leaving pin mode, clear drop pin and highlights
        if (mode !== 'pin') {
            onDropPinChange(null)
            onHighlightChange(new Set())
        }
    }, [mode])

    useEffect(() => {
        // Provide a handler for map clicks to App when we're in pin mode.
        const handler = async (coords: LatLng) => {
            setLoading(true);
            setError(null)
            try {
                onDropPinChange(coords)
                const nearest = await closest(coords.lng, coords.lat, limit, (status || 'APPROVED'))
                onResults(nearest)
                onHighlightChange(new Set(nearest.map(p => p.locationId)))
            } catch (e: any) {
                setError(e.message || 'Failed to find closest')
            } finally {
                setLoading(false)
            }
        }
        registerClosestHandler(handler)
    }, [limit, status])

    function fitToMarkers(items: FoodProviderDTO[]) {
        const coords = items.filter(p => p.latitude != null && p.longitude != null)
        if (coords.length === 0) return
        const avgLat = coords.reduce((s, p) => s + (p.latitude as number), 0) / coords.length
        const avgLng = coords.reduce((s, p) => s + (p.longitude as number), 0) / coords.length
        onMapViewChange({lat: avgLat, lng: avgLng}, 13)
    }

    async function runNameSearch() {
        if (!nameQuery.trim()) return
        setLoading(true);
        setError(null)
        try {
            const res = await searchByName(nameQuery.trim(), status || undefined)
            onResults(res)
            fitToMarkers(res)
        } catch (e: any) {
            setError(e.message || 'Search failed')
        } finally {
            setLoading(false)
        }
    }

    async function runStreetSearch() {
        if (!streetQuery.trim()) return
        setLoading(true);
        setError(null)
        try {
            const res = await searchByStreet(streetQuery.trim())
            onResults(res)
            fitToMarkers(res)
        } catch (e: any) {
            setError(e.message || 'Search failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <div className="p-card" style={{boxShadow: '0 2px 8px rgba(0,0,0,0.2)'}}>
                <div className="p-card-header" style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px'
                }}>
                    <div style={{fontWeight: 600}}>Search</div>
                    <div style={{display: 'flex', gap: 8, alignItems: 'center'}}>
                        <Dropdown value={mode}
                                  options={[{label: 'Form', value: 'form'}, {label: 'Drop a Pin', value: 'pin'}]}
                                  onChange={(e) => setMode(e.value)} style={{width: 140}}/>
                        <Button icon={collapsed ? 'pi pi-chevron-down' : 'pi pi-chevron-up'} rounded text
                                aria-label="Toggle" onClick={() => setCollapsed(c => !c)}/>
                    </div>
                </div>
                {!collapsed && (
                    <div className="p-card-body" style={{padding: 12}}>
                        {mode === 'form' && (
                            <div>
                                <div style={{marginBottom: 12}}>
                                    <div style={{fontWeight: 600, marginBottom: 4}}>Filter by Name</div>
                                    <span className="p-input-icon-left" style={{width: '100%'}}>
                                    <IconField iconPosition="left">
                                        <InputIcon className="pi pi-search"> </InputIcon>
                                        <InputText value={nameQuery} onChange={(e) => setNameQuery(e.target.value)}
                                                   placeholder="e.g. tacos"
                                                   style={{width: '100%'}}/>
                                    </IconField>

                                    </span>
                                    <div style={{marginTop: 8}}>
                                        <div style={{marginBottom: 4}}>Status (optional)</div>
                                        <Dropdown value={status} onChange={(e) => setStatus(e.value)}
                                                  options={statusOptions} style={{width: '100%'}}/>
                                    </div>
                                    <Button label="Search" icon="pi pi-search" onClick={runNameSearch}
                                            style={{marginTop: 8}}/>
                                </div>
                                <div style={{borderTop: '1px solid #eee', paddingTop: 12}}>
                                    <div style={{fontWeight: 600, marginBottom: 4}}>Find by Street</div>
                                    <InputText value={streetQuery} onChange={(e) => setStreetQuery(e.target.value)}
                                               placeholder="e.g. Market St" style={{width: '100%'}}/>
                                    <Button label="Search" icon="pi pi-search" onClick={runStreetSearch}
                                            style={{marginTop: 8}}/>
                                </div>
                            </div>
                        )}
                        {mode === 'pin' && (
                            <div>
                                <div style={{marginBottom: 8}}>Click on the map to drop a pin and find closest
                                    locations.
                                </div>
                                <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                                    <label htmlFor="limit">How many?</label>
                                    <InputText id="limit" type="number" value={String(limit)}
                                               onChange={(e: any) => setLimit(Math.max(1, Math.min(20, parseInt(e.target.value || '5', 10))))}
                                               style={{width: 80}}/>
                                </div>
                                <div style={{marginTop: 8}}>
                                    <div style={{marginBottom: 4}}>Status</div>
                                    <Dropdown value={status || 'APPROVED'} onChange={(e) => setStatus(e.value)}
                                              options={STATUSES.filter(Boolean).map(s => ({label: s, value: s}))}
                                              style={{width: '100%'}}/>
                                </div>
                            </div>
                        )}
                        {loading && <div style={{marginTop: 12}}>Loading...</div>}
                        {error && <div style={{color: 'red', marginTop: 8}}>{error}</div>}
                    </div>
                )}
            </div>
        </div>
    )
}
