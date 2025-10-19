export type PermitStatus = 'APPROVED' | 'REQUESTED' | 'SUSPEND' | 'EXPIRED' | string;

export interface PermitDTO {
  permitStatus: PermitStatus;
  expirationDate?: string | null;
}

export interface FoodProviderDTO {
  locationId: string;
  name: string;
  foodItems?: string;
  permit?: PermitDTO | null;
  longitude?: number | null;
  latitude?: number | null;
  locationDescription?: string | null;
  address?: string | null;
}

const BASE = '';

export async function searchByName(name: string, status?: string | string[]): Promise<FoodProviderDTO[]> {
  const params = new URLSearchParams();
  if (status && Array.isArray(status)) {
    if (status.length) params.set('status', status.join(','));
  } else if (status) {
    params.set('status', status);
  }
  const res = await fetch(`${BASE}/api/v1/food-providers/name/${encodeURIComponent(name)}?${params.toString()}`);
  if (!res.ok) throw new Error(`Search by name failed: ${res.status}`);
  return await res.json();
}

export async function searchByStreet(street: string): Promise<FoodProviderDTO[]> {
  const res = await fetch(`${BASE}/api/v1/food-providers/street/${encodeURIComponent(street)}`);
  if (!res.ok) throw new Error(`Search by street failed: ${res.status}`);
  return await res.json();
}

export async function closest(longitude: number, latitude: number, limit: number = 5, status?: string | string[]):
  Promise<FoodProviderDTO[]> {
  const params = new URLSearchParams({ lng: String(longitude), lat: String(latitude), limit: String(limit) });
  if (status && Array.isArray(status)) {
    if (status.length) params.set('status', status.join(','));
  } else if (status) {
    params.set('status', status);
  }
  const res = await fetch(`${BASE}/api/v1/food-providers/closest?${params.toString()}`);
  if (!res.ok) throw new Error(`Closest failed: ${res.status}`);
  return await res.json();
}

export async function searchByStatus(status?: string | string[]): Promise<FoodProviderDTO[]> {
  const params = new URLSearchParams();
  if (status && Array.isArray(status)) {
    if (status.length) params.set('status', status.join(','));
  } else if (status) {
    params.set('status', status);
  }
  const qs = params.toString();
  const url = `${BASE}/api/v1/food-providers/status${qs ? '?' + qs : ''}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Search by status failed: ${res.status}`);
  return await res.json();
}
