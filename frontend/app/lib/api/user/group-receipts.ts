import { BaseCRUDAPI } from "../base/base-clients";
import type { ReceiptCreate, ReceiptOut } from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
  receipts: `${prefix}/households/receipts`,
  receiptsId: (id: string | number) => `${prefix}/households/receipts/${id}`,
};

export class ReceiptsApi extends BaseCRUDAPI<ReceiptCreate, ReceiptOut, ReceiptCreate> {
  baseRoute = routes.receipts;
  itemRoute = routes.receiptsId;

  async uploadImage(itemId: string | number, image: File) {
    const formData = new FormData();
    formData.append("image", image);

    return await this.requests.post<ReceiptOut>(`${this.itemRoute(itemId)}/image`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }
}
