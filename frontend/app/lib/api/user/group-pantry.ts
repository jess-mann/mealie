import { BaseCRUDAPI } from "../base/base-clients";
import type { ApiRequestInstance } from "~/lib/api/types/non-generated";
import type {
  PantryItemCreate,
  PantryItemHistoryCreate,
  PantryItemHistoryOut,
  PantryItemOut,
  PantryItemPriceHistoryCreate,
  PantryItemPriceHistoryOut,
} from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
  pantryItems: `${prefix}/households/pantry/items`,
  pantryItemsId: (id: string | number) => `${prefix}/households/pantry/items/${id}`,
  pantryItemsHistory: (id: string | number) => `${prefix}/households/pantry/items/${id}/history`,
  pantryItemsPrices: (id: string | number) => `${prefix}/households/pantry/items/${id}/prices`,
};

export class PantryItemsApi extends BaseCRUDAPI<PantryItemCreate, PantryItemOut, PantryItemCreate> {
  baseRoute = routes.pantryItems;
  itemRoute = routes.pantryItemsId;

  async getHistory(itemId: string) {
    return await this.requests.get<PantryItemHistoryOut[]>(routes.pantryItemsHistory(itemId));
  }

  async createHistory(itemId: string, payload: PantryItemHistoryCreate) {
    return await this.requests.post<PantryItemHistoryOut, PantryItemHistoryCreate>(
      routes.pantryItemsHistory(itemId),
      payload,
    );
  }

  async getPrices(itemId: string) {
    return await this.requests.get<PantryItemPriceHistoryOut[]>(routes.pantryItemsPrices(itemId));
  }

  async createPrice(itemId: string, payload: PantryItemPriceHistoryCreate) {
    return await this.requests.post<PantryItemPriceHistoryOut, PantryItemPriceHistoryCreate>(
      routes.pantryItemsPrices(itemId),
      payload,
    );
  }
}

export class PantryApi {
  public items: PantryItemsApi;

  constructor(requests: ApiRequestInstance) {
    this.items = new PantryItemsApi(requests);
  }
}
