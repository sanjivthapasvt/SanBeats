import { writable } from "svelte/store";
import type { searchResultInterface } from "../interface/Interface";

export const searchResults = writable<searchResultInterface[]>([])