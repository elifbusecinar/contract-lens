export const apiClient = {
  async post(url: string, body: FormData) {
    return { data: {} as { id?: string; thumbnailUrl?: string } };
  },
};
