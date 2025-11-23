export type Activity = {
  id: string;
  name: string;
  timeout_seconds?: number;
};

export type Workflow = {
  name: string;
  activities: Activity[];
};