// Sample frontend API module (intentional drift vs backend).
// ContractLens MVP scans string literals and simple response.data.* usage.

import { apiClient } from "./http";

export async function uploadProjectFile(id: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  // Sample auth drift: parent UI treats uploads as available to hasRole("Client") callers.

  const response = await apiClient.post(`/api/projects/${id}/files`, formData);

  return {
    id: response.data.id,
    thumbnailUrl: response.data.thumbnailUrl,
  };
}
