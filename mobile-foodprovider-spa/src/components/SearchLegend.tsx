import {useEffect, useState} from 'react'
import type {FoodProviderDTO} from '../api'
import {searchByName, searchByStreet, closest} from '../api'
import {InputText} from 'primereact/inputtext'
import {Button} from 'primereact/button'
import {InputIcon} from "primereact/inputicon";
import {IconField} from "primereact/iconfield";
import StatusCheckboxes from './StatusCheckboxes';
import {SelectButton} from "primereact/selectbutton";

export type LatLng = { lat: number, lng: number }


interface SearchLegendProps {
    onResults: (providers: FoodProviderDTO[]) => void
    onHighlightChange: (ids: Set<string>) => void
    onMapViewChange: (center: LatLng, zoom: number) => void
    onDropPinChange: (coords: LatLng | null) => void
    onModeChange: (mode: string) => void
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
    const modes = ['name', 'street', 'pin']
    const [mode, setMode] = useState<string>('name')

    const [nameQuery, setNameQuery] = useState('')
    const [statuses, setStatuses] = useState<string[]>([])
    const [streetQuery, setStreetQuery] = useState('')

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)


    useEffect(() => {
        onModeChange(mode)
        // When leaving pin mode, clear drop pin and highlights
        if (mode !== 'pin') {
            onDropPinChange(null)
            onHighlightChange(new Set())
        }
        // Default status behavior per mode
        if (mode === 'pin') {
            if (statuses.length === 0) setStatuses(['APPROVED'])
        } else if (mode === 'name') {
            // No default for name mode
            if (statuses.length > 0) setStatuses([])
        }
    }, [mode])


    function fitToMarkers(items: FoodProviderDTO[]) {
        const coords = items.filter(p => p.coord?.latitude != null && p.coord?.longitude != null)
        if (coords.length === 0) return
        const avgLat = coords.reduce((s, p) => s + (p.coord?.latitude as number), 0) / coords.length
        const avgLng = coords.reduce((s, p) => s + (p.coord?.longitude as number), 0) / coords.length
        onMapViewChange({lat: avgLat, lng: avgLng}, 13)
    }

    const effectiveStatuses = () => {
        if (mode === 'pin') {
            return statuses.length ? statuses : ['APPROVED']
        }
        return statuses
    }

    // Register map click handler for pin mode (uses current statuses)
    useEffect(() => {
        const handler = async (coords: LatLng) => {
            setLoading(true)
            setError(null)
            try {
                onDropPinChange(coords)
                const res = await closest(coords.lng, coords.lat, 5, effectiveStatuses())
                onResults(res)
                fitToMarkers(res)
            } catch (e: any) {
                setError(e.message || 'Search failed')
            } finally {
                setLoading(false)
            }
        }
        registerClosestHandler(handler)
    }, [registerClosestHandler, statuses])

    async function runNameSearch() {
        if (!nameQuery.trim()) return
        setLoading(true);
        setError(null)
        try {
            const res = await searchByName(nameQuery.trim(), effectiveStatuses())
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
            <div className="p-card" style={{width: 400, boxShadow: '0 2px 8px rgba(0,0,0,0.2)'}}>
                <div className="p-card-header" style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0px 12px'
                }}>
                    <h3 style={{fontWeight: 600}}>Mobile Food Provider Search</h3>
                    <div style={{display: 'flex', gap: 12, alignItems: 'center'}}>
                        {collapsed && (
                            <Button icon={'pi pi-chevron-down'} rounded text aria-label="Expand"
                                    onClick={() => setCollapsed(false)}/>
                        )}
                    </div>
                </div>
                {!collapsed && (
                    <div className="p-card-body" style={{padding: 12}}>
                        <label style={{fontWeight: 600, flex: 1}}>Search Mode:</label>
                        <div className="p-formgroup-inline" style={{display: 'flex', alignItems: 'center', gap: 8}}>
                            <SelectButton style={{flex: 1}} defaultValue={mode} value={mode}
                                          onChange={(e) => setMode(e.value)} options={modes}></SelectButton>
                        </div>
                        <hr/>

                        {mode === 'name' && (
                            <div style={{marginBottom: 12}}>
                                <div style={{fontWeight: 600, marginBottom: 4}}>Search by Name</div>
                                <span className="p-input-icon-left" style={{width: '100%'}}>
                                <IconField iconPosition="left">
                                    <InputIcon className="pi pi-search"> </InputIcon>
                                    <InputText value={nameQuery} onChange={(e) => setNameQuery(e.target.value)}
                                               placeholder="e.g. Truly"
                                               style={{width: '100%'}}/>
                                </IconField>
                                </span>
                                <div style={{marginTop: 8}}>
                                    <div style={{fontWeight: 600, marginBottom: 4}}>Status (optional)</div>
                                    <StatusCheckboxes value={statuses} onChange={setStatuses}/>
                                </div>
                            </div>
                        )}

                        {mode === 'street' && (
                            <div style={{marginBottom: 12}}>
                                <div style={{fontWeight: 600, marginBottom: 4}}>Search by Street</div>
                                <InputText value={streetQuery} onChange={(e) => setStreetQuery(e.target.value)}
                                           placeholder="e.g. Market St" style={{width: '100%'}}/>

                            </div>
                        )}

                        {mode === 'pin' && (
                            <div style={{marginBottom: 12}}>
                                <div style={{fontWeight: 600, marginBottom: 4}}>Search by Dropping a Pin</div>
                                <div style={{marginBottom: 8, color: '#888'}}>Click on the map to drop a pin and find
                                    the closest providers.
                                </div>
                                <div>
                                    <div style={{fontWeight: 600, marginBottom: 4}}>Status (default: APPROVED)</div>
                                    <StatusCheckboxes value={statuses} onChange={setStatuses}/>
                                </div>
                            </div>
                        )}


                        {loading && <div style={{marginTop: 12}}>Loading...</div>}
                        {error && <div style={{color: 'red', marginTop: 8}}>{error}</div>}
                        <div style={{marginTop: 12, display: 'flex', justifyContent: 'space-between'}}>
                            {mode === 'name' && (
                                <Button label="Search" icon="pi pi-search" onClick={runNameSearch}
                                        style={{marginTop: 8}}/>
                            )}
                            {mode === 'street' && (
                                <Button label="Search" icon="pi pi-search" onClick={runStreetSearch}
                                        style={{marginTop: 8}}/>
                            )}
                            <Button label="Minimize" icon="pi pi-chevron-up" text onClick={() => setCollapsed(true)}/>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
