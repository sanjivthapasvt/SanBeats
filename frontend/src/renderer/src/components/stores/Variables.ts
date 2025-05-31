import { writable } from "svelte/store";
import type { searchResultInterface, audioInfo } from "../interface/Interface";

export const clicked = writable(false)
export const currentTrackId = writable<string | null>(null)
export const baseUrl = 'http://localhost:8000/api'
export const searchResults = writable<searchResultInterface[]>([])
export const audioInfoResults = writable<audioInfo>()
export const trendingMusic = writable<searchResultInterface[]>([])
export const recommendedMusic = writable<searchResultInterface[]>([])