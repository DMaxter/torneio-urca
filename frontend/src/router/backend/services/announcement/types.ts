export interface Announcement {
  id: string;
  title: string;
  content: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export class CreateAnnouncement {
  title: string = "";
  content: string = "";
  is_active: boolean = true;
}

export class UpdateAnnouncement {
  title?: string = undefined;
  content?: string = undefined;
  is_active?: boolean = undefined;
}