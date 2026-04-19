import { type Ref } from "vue";
import type { AxiosError } from "axios";
import type { AxiosResponse } from "axios";
import type { APIResponse } from "@router/backend/types";

export interface Entity {
  id: string;
}

/* eslint-disable @typescript-eslint/no-empty-object-type */
export interface CreateEntity {
}
/* eslint-enable @typescript-eslint/no-empty-object-type */

export interface CRUDService<T extends Entity, C extends CreateEntity, E = unknown> {
  getAll(): Promise<AxiosResponse<T[] | E>>;
  create(data: C): Promise<AxiosResponse<T | E>>;
}

/**
 * Creates a generic Pinia-compatible CRUD store scaffolding, providing standard actions
 * for local state management corresponding to a REST backend service.
 *
 * @param storeName - Visual name identifier for the generic store, useful for context/errors.
 * @param items - A Vue `Ref` holding the array of entities specific to this store instance.
 * @param service - An implementation of the CRUDService responsible for backend calls.
 * @returns Generic CRUD functions tailored for manipulating the provided `items` state.
 */
export function createGenericStore<T extends Entity, C extends CreateEntity, E = unknown>(
  storeName: string,
  items: Ref<T[]>,
  service: CRUDService<T, C, E>
) {
  /** Replaces the local state array with parsed API data. */
  function init(data: T[]) {
    items.value = data;
  }

  /** Inserts a new entity strictly into local state tracking. */
  function add(item: T) {
    items.value.push(item);
  }

  /** Modifies an existing entity strictly within local tracking matching its ID. */
  function update(item: T) {
    const index = items.value.findIndex((i) => i.id === item.id);
    if (index !== -1) {
      items.value[index] = item;
    }
  }

  /** Deletes an existing entity strictly from local arrays by its ID. */
  function remove(id: string) {
    const index = items.value.findIndex((i) => i.id === id);
    if (index === -1) {
      console.error(`${storeName} ${id} not found`);
      return;
    }
    items.value.splice(index, 1);
  }

  /** 
   * Fetches the entity collection from the backend API unconditionally,
   * bypassing any local cache. Use this for explicit refresh actions.
   */
  async function forceGetAll(): Promise<APIResponse<string | null>> {
    try {
      const { status, data } = await service.getAll();
      if (status === 200) {
        init(data as T[]);
        return { success: true, content: null };
      } else {
        return { success: false, content: ((data as unknown) as Error).message, status };
      }
    } catch (error) {
      const _error = error as AxiosError<string>;
      return { success: false, status: _error.response?.status, content: null };
    }
  }

  /** 
   * Reloads the entity collection only if the local store is empty.
   * If data already exists, returns immediately without an API call.
   * Use `forceGetAll` for explicit refresh actions.
   */
  async function getAll(): Promise<APIResponse<string | null>> {
    if (items.value.length > 0) {
      return { success: true, content: null };
    }
    return forceGetAll();
  }

  /**
   * Pushes a new element entity creation request into the integrated backend API.
   * If successful, appends the newly returned entity entry into the array.
   * 
   * @param data - The Creation object implementing `CreateEntity`.
   * @returns Resolves the action APIStatus block representing the process outcome.
   */
  async function create(data: C): Promise<APIResponse<string | null, T>> {
    try {
      const response = await service.create(data);
      const successStatus = response.status === 200 || response.status === 201;
      if (successStatus) {
        add(response.data as T);
        return { success: true, content: null, entity: response.data as T };
      } else {
        return { success: false, content: ((response.data as unknown) as Error).message, status: response.status, entity: undefined };
      }
    } catch (_error: any) {
      if (_error.response) {
        return { success: false, status: _error.response?.status, content: null, entity: undefined };
      }
      return { success: false, status: 500, content: "Unknown error", entity: undefined };
    }
  }

  return { init, add, update, remove, getAll, forceGetAll, create };
}
