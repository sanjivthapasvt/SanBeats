import { writable } from "svelte/store";
import type { searchResultInterface, audioInfo } from "../interface/Interface";

export const baseUrl = 'http://localhost:8000/api'
export const searchResults = writable<searchResultInterface[]>([])
export const audioInfoResults = writable<audioInfo>()