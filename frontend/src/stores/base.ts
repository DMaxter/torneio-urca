import { ref, type Ref } from "vue";
import type { AxiosError } from "axios";
import type { AxiosResponse } from "axios";
import type { APIResponse } from "@router/backend/types";

export interface Entity {
  id: string;
}

export interface CreateEntity {
  // marker interface for create DTOs
}

export interface CRUDService<T extends Entity, C extends CreateEntity, E = unknown> {
  getAll(): Promise<AxiosResponse<T[] | E>>;
  create(data: C): Promise<AxiosResponse<T | E>>;
}

export function createGenericStore<T extends Entity, C extends CreateEntity, E = unknown>(
  storeName: string,
  items: Ref<T[]>,
  service: CRUDService<T, C, E>
) {
  function init(data: T[]) {
    items.value = data;
  }

  function add(item: T) {
    items.value.push(item);
  }

  function update(item: T) {
    const index = items.value.findIndex((i) => i.id === item.id);
    if (index !== -1) {
      items.value[index] = item;
    }
  }

  function remove(id: string) {
    const index = items.value.findIndex((i) => i.id === id);
    if (index === -1) {
      console.error(`${storeName} ${id} not found`);
      return;
    }
    items.value.splice(index, 1);
  }

  async function getAll(): Promise<APIResponse<string | null>> {
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

  async function create(data: C): Promise<APIResponse<string | null>> {
    try {
      const response = await service.create(data);
      const successStatus = response.status === 200 || response.status === 201;
      if (successStatus) {
        add(response.data as T);
        return { success: true, content: null };
      } else {
        return { success: false, content: ((response.data as unknown) as Error).message, status: response.status };
      }
    } catch (error) {
      const _error = error as AxiosError<string>;
      return { success: false, status: _error.response?.status, content: null };
    }
  }

  return { init, add, update, remove, getAll, create };
}
