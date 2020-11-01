import { writable } from "svelte/store";

const listKey = writable(0);

export function updateKey(key: number) {
  listKey.update((current) => Math.max(current, key));
  return listKey;
}
